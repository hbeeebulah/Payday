"""Pydantic schemas for payroll analytics and settlements."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel


class MonthlyBreakdownSchema(BaseModel):
    period_label: str
    run_id: str
    status: str
    employee_count: int
    total_disbursed: Decimal
    total_planned: Decimal
    successful_count: int
    failed_count: int
    pending_count: int


class SettlementSummarySchema(BaseModel):
    total_amount: Decimal
    total_fees: Decimal
    count: int


class PayrollAnalyticsSchema(BaseModel):
    currency: str
    total_runs: int
    lifetime_disbursed: Decimal
    months: list[MonthlyBreakdownSchema]
    settlements: SettlementSummarySchema | None = None
