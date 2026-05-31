"""Pydantic schemas for the Payroll Wallet resource."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import WalletStatus


class WalletProvisionRequest(BaseModel):
    # Required only when provisioning an individual (OTP/BVN) wallet.
    bvn: str | None = Field(default=None, max_length=11)


class WalletValidateRequest(BaseModel):
    otp: str = Field(..., max_length=12)
    tracking_id: str = Field(..., max_length=128)


class WalletRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    business_id: str
    label: str
    alatpay_wallet_id: str | None
    wallet_type: int
    account_number: str | None
    account_name: str | None
    bank_name: str | None
    currency: str
    available_balance: Decimal
    status: WalletStatus
    created_at: datetime
    updated_at: datetime
