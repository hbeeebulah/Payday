"""Payroll Wallet orchestration.

Bridges the ALATPay Static Wallets API (`StaticWalletService`) with the local
`PayrollWallet` records, and exposes the overdraft check used before any bulk
transfer is allowed to run.
"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Business, PayrollWallet, WalletStatus
from app.services.alatpay import StaticWalletService


async def get_wallet(db: AsyncSession, business_id: str) -> PayrollWallet | None:
    result = await db.execute(
        select(PayrollWallet).where(PayrollWallet.business_id == business_id)
    )
    return result.scalar_one_or_none()


async def provision_wallet(
    db: AsyncSession,
    *,
    business: Business,
    wallet_service: StaticWalletService,
    bvn: str | None = None,
) -> PayrollWallet:
    """Provision (or return the existing) dedicated Payroll Wallet for a business."""
    existing = await get_wallet(db, business.id)
    if existing and existing.status == WalletStatus.ACTIVE:
        return existing

    result = await wallet_service.provision_payroll_wallet(
        email=business.email, bvn=bvn
    )

    wallet = existing or PayrollWallet(business_id=business.id)
    wallet.alatpay_wallet_id = result.wallet_id or wallet.alatpay_wallet_id
    wallet.account_number = result.account_number
    wallet.account_name = result.account_name
    wallet.status = result.status
    wallet.otp_tracking_id = result.otp_tracking_id

    if existing is None:
        db.add(wallet)
    await db.commit()
    await db.refresh(wallet)
    return wallet


async def refresh_balance(
    db: AsyncSession,
    *,
    wallet: PayrollWallet,
    wallet_service: StaticWalletService,
) -> PayrollWallet:
    """Refresh the locally cached balance from ALATPay (best-effort)."""
    if not wallet.alatpay_wallet_id:
        return wallet
    try:
        balance = await wallet_service.fetch_balance(wallet.alatpay_wallet_id)
    except Exception:  # noqa: BLE001 - balance refresh is best-effort
        return wallet
    wallet.available_balance = balance.available_balance
    await db.commit()
    await db.refresh(wallet)
    return wallet


class InsufficientFundsError(Exception):
    """Raised when a wallet cannot cover a requested disbursement total."""

    def __init__(self, available: Decimal, required: Decimal) -> None:
        self.available = available
        self.required = required
        super().__init__(
            f"Insufficient wallet balance: available {available}, required {required}"
        )


def assert_sufficient_balance(wallet: PayrollWallet, required: Decimal) -> None:
    """Overdraft guard — raise if the wallet cannot fund ``required``."""
    if wallet.available_balance < required:
        raise InsufficientFundsError(wallet.available_balance, required)
