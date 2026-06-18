"""Payroll orchestration.

Coordinates the database (PayrollRun + TransactionReceipt) with the active
disbursement backend to execute a "pay everyone" run. Designed to run inside a
FastAPI background task: disbursement is fanned out in parallel and each payout
is routed to the correct rail.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.models import (
    DistributionState,
    Employee,
    EmployeeStatus,
    PayrollRun,
    PayrollRunStatus,
    TransactionReceipt,
)
from app.services.alatpay import (
    CustomerInfo,
    DisbursementBackend,
    DisbursementRequest,
    build_disbursement_service,
)

logger = logging.getLogger("payday.payroll")


async def create_payroll_run(
    db: AsyncSession,
    *,
    business_id: str,
    period_label: str,
    employee_ids: list[str] | None = None,
) -> PayrollRun:
    """Build a draft payroll run with one pending receipt per employee."""
    query = select(Employee).where(
        Employee.business_id == business_id,
        Employee.status == EmployeeStatus.ACTIVE,
    )
    if employee_ids:
        query = query.where(Employee.id.in_(employee_ids))

    employees = list((await db.execute(query)).scalars().all())
    if not employees:
        raise ValueError("No active employees to pay for this business")

    total = sum((e.salary for e in employees), Decimal("0.00"))
    currency = employees[0].currency

    run = PayrollRun(
        business_id=business_id,
        period_label=period_label,
        status=PayrollRunStatus.DRAFT,
        total_funding_amount=total,
        currency=currency,
        employee_count=len(employees),
    )
    db.add(run)
    await db.flush()  # assign run.id

    for emp in employees:
        db.add(
            TransactionReceipt(
                payroll_run_id=run.id,
                employee_id=emp.id,
                amount=emp.salary,
                currency=emp.currency,
                distribution_state=DistributionState.PENDING,
                bank_name=emp.bank_name,
                bank_account_number=emp.bank_account_number,
                bank_routing_code=emp.bank_routing_code,
            )
        )

    await db.commit()
    await db.refresh(run)
    return run


def _build_request(
    receipt: TransactionReceipt, employee: Employee, run: PayrollRun
) -> DisbursementRequest:
    return DisbursementRequest(
        reference=receipt.id,
        amount=receipt.amount,
        currency=receipt.currency,
        account_number=receipt.bank_account_number or "",
        bank_code=receipt.bank_routing_code or "",
        customer=CustomerInfo(
            email=employee.email or "payroll@payday.ng",
            phone=employee.phone or "",
            first_name=employee.first_name,
            last_name=employee.last_name,
            metadata=f"payroll_run:{run.id}",
        ),
        narration=f"Salary {run.period_label}",
        metadata={"payroll_run_id": run.id, "receipt_id": receipt.id},
    )


async def process_payroll_disbursement(
    db: AsyncSession,
    *,
    run: PayrollRun,
    alatpay: DisbursementBackend,
    concurrency: int = 10,
) -> PayrollRun:
    """Disburse every pending payout in the run, in parallel, via the backend."""
    receipts = list(
        (
            await db.execute(
                select(TransactionReceipt)
                .where(
                    TransactionReceipt.payroll_run_id == run.id,
                    TransactionReceipt.distribution_state.in_(
                        [DistributionState.PENDING, DistributionState.FAILED]
                    ),
                )
                .options(selectinload(TransactionReceipt.employee))
            )
        )
        .scalars()
        .all()
    )

    if not run.executed_at:
        run.executed_at = datetime.now(UTC)
    run.status = PayrollRunStatus.PROCESSING
    await db.commit()

    requests = [_build_request(r, r.employee, run) for r in receipts]
    results = await alatpay.disburse_batch(requests, concurrency=concurrency)
    results_by_ref = {res.reference: res for res in results}

    for receipt in receipts:
        result = results_by_ref.get(receipt.id)
        if result is None:
            continue
        receipt.distribution_state = result.state
        receipt.alatpay_transaction_reference = result.provider_reference
        receipt.processed_at = datetime.now(UTC)
        if result.state == DistributionState.FAILED:
            receipt.failure_reason = result.message or "Disbursement reported a failure"

    await db.commit()
    await _recompute_run_status(db, run)
    await db.commit()
    await db.refresh(run)
    return run


async def _recompute_run_status(db: AsyncSession, run: PayrollRun) -> None:
    states = [
        row[0]
        for row in (
            await db.execute(
                select(TransactionReceipt.distribution_state).where(
                    TransactionReceipt.payroll_run_id == run.id
                )
            )
        ).all()
    ]
    total = len(states)
    successful = sum(1 for s in states if s == DistributionState.SUCCESSFUL)
    terminal = sum(
        1
        for s in states
        if s
        in {
            DistributionState.SUCCESSFUL,
            DistributionState.FAILED,
            DistributionState.REVERSED,
        }
    )

    if total == 0 or terminal < total:
        run.status = PayrollRunStatus.PROCESSING
    elif successful == total:
        run.status = PayrollRunStatus.COMPLETED
        run.completed_at = datetime.now(UTC)
    elif successful == 0:
        run.status = PayrollRunStatus.FAILED
    else:
        run.status = PayrollRunStatus.PARTIALLY_COMPLETED


async def run_payroll_disbursement_task(run_id: str) -> None:
    """Background-task entrypoint.

    Opens its own database session (the request session is already closed by the
    time a background task runs) and disburses the run via the configured
    backend. All errors are contained so a failure never crashes the worker.
    """
    # Imported lazily to avoid binding the engine at import time / in tests.
    from app.db.session import AsyncSessionLocal

    settings = get_settings()
    try:
        async with AsyncSessionLocal() as session:
            run = await session.get(PayrollRun, run_id)
            if run is None:
                logger.warning("Payroll run %s not found for disbursement", run_id)
                return
            disburser = build_disbursement_service(settings)
            await process_payroll_disbursement(
                session,
                run=run,
                alatpay=disburser,
                concurrency=settings.alatpay_disbursement_concurrency,
            )
    except Exception:  # noqa: BLE001 - background tasks must not crash the worker
        logger.exception("Payroll disbursement task failed for run %s", run_id)
