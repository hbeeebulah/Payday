"""Routes exposing historical payroll analytics and settlements."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Business
from app.schemas.analytics import (
    MonthlyBreakdownSchema,
    PayrollAnalyticsSchema,
    SettlementSummarySchema,
)
from app.services.alatpay import SettlementsService, get_settlements_service
from app.services.analytics import compute_payroll_analytics

router = APIRouter(prefix="/businesses/{business_id}/analytics", tags=["analytics"])


async def _ensure_business(db: AsyncSession, business_id: str) -> Business:
    business = await db.get(Business, business_id)
    if business is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Business not found")
    return business


@router.get("/payroll", response_model=PayrollAnalyticsSchema)
async def payroll_analytics(
    business_id: str,
    include_settlements: bool = True,
    db: AsyncSession = Depends(get_db),
    settlements_service: SettlementsService = Depends(get_settlements_service),
) -> PayrollAnalyticsSchema:
    """Monthly payroll analytics from the ledger, enriched with settlements."""
    await _ensure_business(db, business_id)
    analytics = await compute_payroll_analytics(db, business_id=business_id)

    settlements_schema: SettlementSummarySchema | None = None
    if include_settlements:
        summary = await settlements_service.fetch_settlements()
        settlements_schema = SettlementSummarySchema(
            total_amount=summary.total_amount,
            total_fees=summary.total_fees,
            count=summary.count,
        )

    return PayrollAnalyticsSchema(
        currency=analytics.currency,
        total_runs=analytics.total_runs,
        lifetime_disbursed=analytics.lifetime_disbursed,
        months=[
            MonthlyBreakdownSchema(
                period_label=m.period_label,
                run_id=m.run_id,
                status=m.status,
                employee_count=m.employee_count,
                total_disbursed=m.total_disbursed,
                total_planned=m.total_planned,
                successful_count=m.successful_count,
                failed_count=m.failed_count,
                pending_count=m.pending_count,
            )
            for m in analytics.months
        ],
        settlements=settlements_schema,
    )
