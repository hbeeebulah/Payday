"""Payroll analytics computed from the local transaction ledger.

Gives business owners visibility over historical staff expenditure. The ledger
(PayrollRun + TransactionReceipt) is the source of truth; ALATPay settlement
data can be layered on top via the Settlements API wrapper at the route level.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import DistributionState, PayrollRun


@dataclass(slots=True)
class MonthlyBreakdown:
    period_label: str
    run_id: str
    status: str
    employee_count: int
    total_disbursed: Decimal      # successfully paid out
    total_planned: Decimal        # funding total for the run
    successful_count: int
    failed_count: int
    pending_count: int


@dataclass(slots=True)
class PayrollAnalytics:
    currency: str = "NGN"
    total_runs: int = 0
    lifetime_disbursed: Decimal = Decimal("0.00")
    months: list[MonthlyBreakdown] = field(default_factory=list)


async def compute_payroll_analytics(
    db: AsyncSession, *, business_id: str
) -> PayrollAnalytics:
    """Aggregate per-month payroll totals for a business."""
    runs = list(
        (
            await db.execute(
                select(PayrollRun)
                .where(PayrollRun.business_id == business_id)
                .order_by(PayrollRun.created_at.desc())
                .options(selectinload(PayrollRun.receipts))
            )
        )
        .scalars()
        .all()
    )

    analytics = PayrollAnalytics(total_runs=len(runs))
    if runs:
        analytics.currency = runs[0].currency

    for run in runs:
        disbursed = Decimal("0.00")
        successful = failed = pending = 0
        for receipt in run.receipts:
            if receipt.distribution_state == DistributionState.SUCCESSFUL:
                successful += 1
                disbursed += receipt.amount
            elif receipt.distribution_state == DistributionState.FAILED:
                failed += 1
            else:
                pending += 1

        analytics.lifetime_disbursed += disbursed
        analytics.months.append(
            MonthlyBreakdown(
                period_label=run.period_label,
                run_id=run.id,
                status=run.status.value,
                employee_count=run.employee_count,
                total_disbursed=disbursed,
                total_planned=run.total_funding_amount,
                successful_count=successful,
                failed_count=failed,
                pending_count=pending,
            )
        )

    return analytics
