"""Inbound webhook ingestion from ALATPay.

ALATPay calls this endpoint asynchronously as the state of each disbursement
changes. We verify the signature, reconcile the matching TransactionReceipt
and roll the parent PayrollRun's status forward.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import (
    DistributionState,
    PayrollRun,
    PayrollRunStatus,
    TransactionReceipt,
)
from app.services.alatpay import (
    AlatPayService,
    AlatPayWebhookVerificationError,
    get_alatpay_service,
)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/alatpay", status_code=status.HTTP_200_OK)
async def alatpay_webhook(
    request: Request,
    x_alatpay_signature: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
    alatpay: AlatPayService = Depends(get_alatpay_service),
) -> dict[str, str]:
    raw_body = await request.body()
    try:
        body = json.loads(raw_body or b"{}")
    except json.JSONDecodeError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid JSON") from exc

    try:
        event = alatpay.parse_webhook(raw_body, x_alatpay_signature, body)
    except AlatPayWebhookVerificationError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    receipt = await _find_receipt(db, event.client_reference, event.provider_reference)
    if receipt is None:
        # Acknowledge unknown references so ALATPay stops retrying; we log via
        # the response body for observability.
        return {"status": "ignored", "reason": "no matching receipt"}

    receipt.distribution_state = event.state
    if event.provider_reference:
        receipt.alatpay_transaction_reference = event.provider_reference
    receipt.processed_at = datetime.now(UTC)
    if event.state == DistributionState.FAILED:
        receipt.failure_reason = "ALATPay webhook reported failure"

    await db.flush()
    await _recompute_run_status(db, receipt.payroll_run_id)
    await db.commit()

    return {"status": "processed", "receipt_id": receipt.id}


async def _find_receipt(
    db: AsyncSession,
    client_reference: str | None,
    provider_reference: str | None,
) -> TransactionReceipt | None:
    # Our client reference is the receipt id; fall back to provider reference.
    if client_reference:
        receipt = await db.get(TransactionReceipt, client_reference)
        if receipt is not None:
            return receipt
    if provider_reference:
        result = await db.execute(
            select(TransactionReceipt).where(
                TransactionReceipt.alatpay_transaction_reference == provider_reference
            )
        )
        return result.scalar_one_or_none()
    return None


async def _recompute_run_status(db: AsyncSession, run_id: str) -> None:
    run = await db.get(PayrollRun, run_id)
    if run is None:
        return
    result = await db.execute(
        select(TransactionReceipt.distribution_state).where(
            TransactionReceipt.payroll_run_id == run_id
        )
    )
    states = [row[0] for row in result.all()]
    total = len(states)
    successful = sum(1 for s in states if s == DistributionState.SUCCESSFUL)
    terminal = sum(
        1
        for s in states
        if s in {DistributionState.SUCCESSFUL, DistributionState.FAILED, DistributionState.REVERSED}
    )

    if terminal < total:
        run.status = PayrollRunStatus.PROCESSING
    elif successful == total:
        run.status = PayrollRunStatus.COMPLETED
        run.completed_at = datetime.now(UTC)
    elif successful == 0:
        run.status = PayrollRunStatus.FAILED
    else:
        run.status = PayrollRunStatus.PARTIALLY_COMPLETED
