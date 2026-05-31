"""Static Wallets service.

Provisions and inspects the dedicated ALATPay static account ("Payroll Wallet")
that each business funds and disburses salaries from. The wallet balance read
here is what the payroll engine checks for overdraft protection before running a
bulk transfer.
"""

from __future__ import annotations

from decimal import Decimal

import httpx

from app.core.config import Settings, get_settings
from app.models.enums import WalletStatus
from app.services.alatpay.client import AlatPayClient
from app.services.alatpay.exceptions import AlatPayError
from app.services.alatpay.models import WalletBalance, WalletProvisionResult


def _to_decimal(value: object) -> Decimal:
    if value is None:
        return Decimal("0.00")
    try:
        return Decimal(str(value))
    except (ValueError, ArithmeticError):
        return Decimal("0.00")


class StaticWalletService:
    """Domain-facing operations over the ALATPay Static Wallets API."""

    def __init__(self, client: AlatPayClient, *, wallet_type: int = 2) -> None:
        self._client = client
        self._wallet_type = wallet_type

    async def provision_payroll_wallet(
        self,
        *,
        email: str,
        bvn: str | None = None,
    ) -> WalletProvisionResult:
        """Create the dedicated Payroll Wallet for a business.

        A collection wallet (type 2) is created directly; an individual wallet
        (type 1) returns an OTP tracking id that must be confirmed via
        :meth:`validate_wallet`.
        """
        payload: dict[str, object] = {
            "staticWalletType": self._wallet_type,
            "email": email,
        }
        if bvn:
            payload["bvn"] = bvn

        try:
            raw = await self._client.create_static_wallet(payload)
        except (AlatPayError, httpx.HTTPError) as exc:
            return WalletProvisionResult(
                wallet_id=None,
                account_number=None,
                account_name=None,
                status=WalletStatus.FAILED,
                message=str(exc),
            )

        return self._parse_provision(raw)

    async def validate_wallet(
        self, *, wallet_id: str, otp: str, tracking_id: str
    ) -> WalletProvisionResult:
        """Confirm an OTP-gated wallet and finalise its account number."""
        payload = {
            "staticWalletId": wallet_id,
            "otp": otp,
            "trackingId": tracking_id,
        }
        try:
            raw = await self._client.validate_and_create_wallet(payload)
        except (AlatPayError, httpx.HTTPError) as exc:
            return WalletProvisionResult(
                wallet_id=wallet_id,
                account_number=None,
                account_name=None,
                status=WalletStatus.FAILED,
                message=str(exc),
            )
        return self._parse_provision(raw)

    async def fetch_balance(self, wallet_id: str) -> WalletBalance:
        """Read the current available balance of a wallet from ALATPay."""
        raw = await self._client.get_static_wallet(wallet_id)
        data = raw.get("data", raw) if isinstance(raw, dict) else {}
        balance = (
            data.get("accountBalance")
            if data.get("accountBalance") is not None
            else data.get("availableBalance")
        )
        return WalletBalance(
            available_balance=_to_decimal(balance),
            account_number=data.get("accountNumber"),
            account_name=data.get("accountName"),
            raw=raw if isinstance(raw, dict) else {},
        )

    @staticmethod
    def _parse_provision(raw: dict) -> WalletProvisionResult:
        data = raw.get("data", raw) if isinstance(raw, dict) else {}
        account_number = data.get("accountNumber")
        otp_tracking = data.get("otpTrackingID") or data.get("otpTrackingId")
        # If we already have an account number the wallet is live; otherwise an
        # OTP confirmation step is still pending.
        status = WalletStatus.ACTIVE if account_number else WalletStatus.PENDING
        return WalletProvisionResult(
            wallet_id=data.get("id"),
            account_number=account_number,
            account_name=data.get("accountName"),
            status=status,
            otp_tracking_id=otp_tracking,
            message=data.get("message"),
            raw=raw if isinstance(raw, dict) else {},
        )


def build_static_wallet_service(settings: Settings | None = None) -> StaticWalletService:
    settings = settings or get_settings()
    client = AlatPayClient(
        base_url=settings.alatpay_base_url,
        api_key=settings.alatpay_api_key,
        public_key=settings.alatpay_public_key,
        business_id=settings.alatpay_business_id,
        timeout=settings.alatpay_timeout_seconds,
    )
    return StaticWalletService(client, wallet_type=settings.alatpay_wallet_type)


def get_static_wallet_service() -> StaticWalletService:
    """FastAPI dependency provider for the static wallet service."""
    return build_static_wallet_service()
