"""Routes for provisioning and inspecting a business's Payroll Wallet."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Business
from app.schemas.wallet import (
    WalletProvisionRequest,
    WalletRead,
    WalletValidateRequest,
)
from app.services.alatpay import StaticWalletService, get_static_wallet_service
from app.services.wallet import get_wallet, provision_wallet, refresh_balance

router = APIRouter(prefix="/businesses/{business_id}/wallet", tags=["wallet"])


async def _ensure_business(db: AsyncSession, business_id: str) -> Business:
    business = await db.get(Business, business_id)
    if business is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Business not found")
    return business


@router.post("", response_model=WalletRead, status_code=status.HTTP_201_CREATED)
async def provision(
    business_id: str,
    payload: WalletProvisionRequest,
    db: AsyncSession = Depends(get_db),
    wallet_service: StaticWalletService = Depends(get_static_wallet_service),
) -> WalletRead:
    """Provision the dedicated Payroll Wallet for this business."""
    business = await _ensure_business(db, business_id)
    wallet = await provision_wallet(
        db, business=business, wallet_service=wallet_service, bvn=payload.bvn
    )
    return WalletRead.model_validate(wallet)


@router.get("", response_model=WalletRead)
async def get_wallet_details(
    business_id: str,
    refresh: bool = False,
    db: AsyncSession = Depends(get_db),
    wallet_service: StaticWalletService = Depends(get_static_wallet_service),
) -> WalletRead:
    """Return the Payroll Wallet, optionally refreshing its balance from ALATPay."""
    await _ensure_business(db, business_id)
    wallet = await get_wallet(db, business_id)
    if wallet is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="No payroll wallet provisioned"
        )
    if refresh:
        wallet = await refresh_balance(db, wallet=wallet, wallet_service=wallet_service)
    return WalletRead.model_validate(wallet)


@router.post("/validate", response_model=WalletRead)
async def validate(
    business_id: str,
    payload: WalletValidateRequest,
    db: AsyncSession = Depends(get_db),
    wallet_service: StaticWalletService = Depends(get_static_wallet_service),
) -> WalletRead:
    """Confirm an OTP-gated wallet (individual wallet type)."""
    await _ensure_business(db, business_id)
    wallet = await get_wallet(db, business_id)
    if wallet is None or not wallet.alatpay_wallet_id:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="No pending wallet to validate"
        )
    result = await wallet_service.validate_wallet(
        wallet_id=wallet.alatpay_wallet_id,
        otp=payload.otp,
        tracking_id=payload.tracking_id,
    )
    wallet.account_number = result.account_number or wallet.account_number
    wallet.account_name = result.account_name or wallet.account_name
    wallet.status = result.status
    await db.commit()
    await db.refresh(wallet)
    return WalletRead.model_validate(wallet)
