"""Pydantic schemas for payroll runs and transaction receipts."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import DistributionState, PayrollRunStatus


class PayrollRunCreate(BaseModel):
    period_label: str = Field(..., max_length=64, examples=["2026-05"])
    # Optional explicit employee selection; defaults to all active employees.
    employee_ids: list[str] | None = None


class TransactionReceiptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    payroll_run_id: str
    employee_id: str
    amount: Decimal
    currency: str
    distribution_state: DistributionState
    alatpay_transaction_reference: str | None
    bank_name: str | None
    bank_account_number: str | None
    bank_routing_code: str | None
    processed_at: datetime | None
    failure_reason: str | None
    created_at: datetime
    updated_at: datetime


class PayrollRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    business_id: str
    period_label: str
    status: PayrollRunStatus
    total_funding_amount: Decimal
    currency: str
    employee_count: int
    executed_at: datetime | None
    completed_at: datetime | None
    alatpay_funding_reference: str | None
    created_at: datetime
    updated_at: datetime


class PayrollRunDetail(PayrollRunRead):
    receipts: list[TransactionReceiptRead] = []
