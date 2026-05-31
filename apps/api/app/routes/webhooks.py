"""Inbound webhook ingestion from the ALATPay Transaction Monitoring system.

ALATPay POSTs asynchronous status updates here as each disbursement settles. We
verify the payload, re-confirm the status server-side (ALATPay does not document
a signing scheme, so the body alone is not trusted), locate the matching
TransactionReceipt, flip its payment flag from pending to paid, and roll the
parent PayrollRun's status forward.
"""

from __future__ import annotations

import json
import logging
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

logger = logging.getLogger("payday.webhooks")

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
        # Acknowledge unknown references so ALATPay stops retrying.
        return {"status": "ignored", "reason": "no matching receipt"}

    # Re-confirm the status directly with ALATPay rather than trusting the body.
    confirmed_state = event.state
    if event.provider_reference:
        try:
            confirmed_state = await alatpay.get_transaction_status(
                event.provider_reference
            )
        except Exception:  # noqa: BLE001 - fall back to the webhook-reported state
            logger.warning(
                "Could not re-verify ALATPay transaction %s; using webhook state",
                event.provider_reference,
            )

    receipt.distribution_state = confirmed_state
    if event.provider_reference:
        receipt.alatpay_transaction_reference = event.provider_reference
    receipt.processed_at = datetime.now(UTC)
    if confirmed_state == DistributionState.FAILED:
        receipt.failure_reason = "ALATPay webhook reported failure"

    await db.flush()
    await _recompute_run_status(db, receipt.payroll_run_id)
    await db.commit()

    return {
        "status": "processed",
        "receipt_id": receipt.id,
        "state": confirmed_state.value,
    }


async def _find_receipt(
    db: AsyncSession,
    client_reference: str | None,
    provider_reference: str | None,
) -> TransactionReceipt | None:
    # Our orderId / client reference is the receipt id; fall back to the
    # provider's transaction reference.
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
    states = [
        row[0]
        for row in (
            await db.execute(
                select(TransactionReceipt.distribution_state).where(
                    TransactionReceipt.payroll_run_id == run_id
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
