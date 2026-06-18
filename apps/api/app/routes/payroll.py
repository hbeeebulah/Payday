"""Routes for creating, executing and inspecting payroll runs."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models import Business, PayrollRun, PayrollRunStatus
from app.schemas.payroll import PayrollRunCreate, PayrollRunDetail, PayrollRunRead
from app.services.alatpay import StaticWalletService, get_static_wallet_service
from app.services.payroll import create_payroll_run, run_payroll_disbursement_task
from app.services.wallet import (
    InsufficientFundsError,
    assert_sufficient_balance,
    get_wallet,
    refresh_balance,
)

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


async def _load_detail(db: AsyncSession, run_id: str) -> PayrollRun:
    result = await db.execute(
        select(PayrollRun)
        .where(PayrollRun.id == run_id)
        .options(selectinload(PayrollRun.receipts))
    )
    return result.scalar_one()


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
    await _get_run_or_404(db, business_id, run_id)
    return await _load_detail(db, run_id)


@router.post(
    "/{run_id}/execute",
    response_model=PayrollRunDetail,
    status_code=status.HTTP_202_ACCEPTED,
)
async def execute_run(
    business_id: str,
    run_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    wallet_service: StaticWalletService = Depends(get_static_wallet_service),
) -> PayrollRun:
    """Kick off a payroll run.

    Performs the overdraft guard synchronously (so the caller is told
    immediately if the wallet can't cover the batch), then fans the per-worker
    ALATPay calls out in a background task.
    """
    await _ensure_business(db, business_id)
    run = await _get_run_or_404(db, business_id, run_id)
    if run.status not in {PayrollRunStatus.DRAFT, PayrollRunStatus.FAILED}:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail=f"Payroll run cannot be executed from state '{run.status.value}'",
        )

    # Overdraft protection: the wallet must exist and cover the funding total.
    wallet = await get_wallet(db, business_id)
    if wallet is None:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="No payroll wallet provisioned for this business",
        )
    wallet = await refresh_balance(db, wallet=wallet, wallet_service=wallet_service)
    try:
        assert_sufficient_balance(wallet, run.total_funding_amount)
    except InsufficientFundsError as exc:
        raise HTTPException(
            status.HTTP_402_PAYMENT_REQUIRED,
            detail=str(exc),
        ) from exc

    # Mark as processing up front, then disburse in the background.
    run.status = PayrollRunStatus.PROCESSING
    await db.commit()

    background_tasks.add_task(run_payroll_disbursement_task, run.id)

    return await _load_detail(db, run_id)
