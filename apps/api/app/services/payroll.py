"""Payroll orchestration.

Coordinates the database (PayrollRun + TransactionReceipt) with the isolated
ALATPay service to execute a "pay everyone" run.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    DistributionState,
    Employee,
    EmployeeStatus,
    PayrollRun,
    PayrollRunStatus,
    TransactionReceipt,
)
from app.services.alatpay import AlatPayService, DisbursementRequest


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


async def execute_payroll_run(
    db: AsyncSession,
    *,
    run: PayrollRun,
    alatpay: AlatPayService,
) -> PayrollRun:
    """Disburse every pending payout in the run concurrently via ALATPay."""
    receipts = list(
        (
            await db.execute(
                select(TransactionReceipt).where(
                    TransactionReceipt.payroll_run_id == run.id,
                    TransactionReceipt.distribution_state == DistributionState.PENDING,
                )
            )
        )
        .scalars()
        .all()
    )

    run.status = PayrollRunStatus.PROCESSING
    run.executed_at = datetime.now(UTC)
    await db.commit()

    requests = [
        DisbursementRequest(
            reference=r.id,
            amount=r.amount,
            currency=r.currency,
            account_number=r.bank_account_number or "",
            bank_code=r.bank_routing_code or "",
            narration=f"Salary {run.period_label}",
            metadata={"payroll_run_id": run.id, "receipt_id": r.id},
        )
        for r in receipts
    ]

    results = await alatpay.disburse_batch(requests)
    results_by_ref = {res.reference: res for res in results}

    succeeded = 0
    for receipt in receipts:
        result = results_by_ref.get(receipt.id)
        if result is None:
            continue
        receipt.distribution_state = result.state
        receipt.alatpay_transaction_reference = result.provider_reference
        receipt.processed_at = datetime.now(UTC)
        if result.state == DistributionState.SUCCESSFUL:
            succeeded += 1
        elif result.state == DistributionState.FAILED:
            receipt.failure_reason = "ALATPay reported the transfer as failed"

    if succeeded == len(receipts):
        run.status = PayrollRunStatus.COMPLETED
        run.completed_at = datetime.now(UTC)
    elif succeeded == 0:
        run.status = PayrollRunStatus.FAILED
    else:
        run.status = PayrollRunStatus.PARTIALLY_COMPLETED

    await db.commit()
    await db.refresh(run)
    return run
