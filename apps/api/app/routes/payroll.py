"""Routes for creating, executing and inspecting payroll runs."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models import Business, PayrollRun, PayrollRunStatus
from app.schemas.payroll import PayrollRunCreate, PayrollRunDetail, PayrollRunRead
from app.services.alatpay import AlatPayService, get_alatpay_service
from app.services.payroll import create_payroll_run, execute_payroll_run

router = APIRouter(prefix="/businesses/{business_id}/payroll-runs", tags=["payroll"])


async def _ensure_business(db: AsyncSession, business_id: str) -> Business:
    business = await db.get(Business, business_id)
    if business is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Business not found")
    return business


async def _get_run_or_404(
    db: AsyncSession, business_id: str, run_id: str
) -> PayrollRun:
    run = await db.get(PayrollRun, run_id)
    if run is None or run.business_id != business_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Payroll run not found")
    return run


@router.post("", response_model=PayrollRunRead, status_code=status.HTTP_201_CREATED)
async def create_run(
    business_id: str,
    payload: PayrollRunCreate,
    db: AsyncSession = Depends(get_db),
) -> PayrollRun:
    await _ensure_business(db, business_id)
    try:
        return await create_payroll_run(
            db,
            business_id=business_id,
            period_label=payload.period_label,
            employee_ids=payload.employee_ids,
        )
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.get("", response_model=list[PayrollRunRead])
async def list_runs(
    business_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[PayrollRun]:
    await _ensure_business(db, business_id)
    result = await db.execute(
        select(PayrollRun)
        .where(PayrollRun.business_id == business_id)
        .order_by(PayrollRun.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{run_id}", response_model=PayrollRunDetail)
async def get_run(
    business_id: str,
    run_id: str,
    db: AsyncSession = Depends(get_db),
) -> PayrollRun:
    await _ensure_business(db, business_id)
    result = await db.execute(
        select(PayrollRun)
        .where(PayrollRun.id == run_id, PayrollRun.business_id == business_id)
        .options(selectinload(PayrollRun.receipts))
    )
    run = result.scalar_one_or_none()
    if run is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Payroll run not found")
    return run


@router.post("/{run_id}/execute", response_model=PayrollRunDetail)
async def execute_run(
    business_id: str,
    run_id: str,
    db: AsyncSession = Depends(get_db),
    alatpay: AlatPayService = Depends(get_alatpay_service),
) -> PayrollRun:
    await _ensure_business(db, business_id)
    run = await _get_run_or_404(db, business_id, run_id)
    if run.status not in {PayrollRunStatus.DRAFT, PayrollRunStatus.FAILED}:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail=f"Payroll run cannot be executed from state '{run.status.value}'",
        )

    await execute_payroll_run(db, run=run, alatpay=alatpay)

    result = await db.execute(
        select(PayrollRun)
        .where(PayrollRun.id == run_id)
        .options(selectinload(PayrollRun.receipts))
    )
    return result.scalar_one()
