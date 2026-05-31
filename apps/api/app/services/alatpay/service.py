"""High-level ALATPay service.

Exposes payroll-oriented operations (disburse a batch of salaries, verify and
parse webhooks, reconcile a transaction) on top of :class:`AlatPayClient`.
Everything the rest of the app needs from ALATPay goes through here.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
from collections.abc import Iterable

import httpx

from app.core.config import Settings, get_settings
from app.models.enums import DistributionState
from app.services.alatpay.client import AlatPayClient
from app.services.alatpay.exceptions import (
    AlatPayError,
    AlatPayWebhookVerificationError,
)
from app.services.alatpay.models import (
    DisbursementRequest,
    DisbursementResult,
    WebhookEvent,
)

# Map raw provider status strings onto our internal distribution states.
_STATE_MAP: dict[str, DistributionState] = {
    "pending": DistributionState.PENDING,
    "processing": DistributionState.PROCESSING,
    "in_progress": DistributionState.PROCESSING,
    "success": DistributionState.SUCCESSFUL,
    "successful": DistributionState.SUCCESSFUL,
    "completed": DistributionState.SUCCESSFUL,
    "failed": DistributionState.FAILED,
    "declined": DistributionState.FAILED,
    "reversed": DistributionState.REVERSED,
}


def _map_state(raw_state: str | None) -> DistributionState:
    if not raw_state:
        return DistributionState.PENDING
    return _STATE_MAP.get(raw_state.strip().lower(), DistributionState.PROCESSING)


class AlatPayService:
    """Domain-facing ALATPay operations for the payroll workflow."""

    def __init__(self, client: AlatPayClient, *, webhook_secret: str = "") -> None:
        self._client = client
        self._webhook_secret = webhook_secret

    # --- Disbursement ------------------------------------------------------

    async def disburse_one(self, request: DisbursementRequest) -> DisbursementResult:
        """Push a single salary payout to ALATPay.

        Any transport or provider error is contained here and surfaced as a
        FAILED result so a single bad payout never aborts the whole batch.
        """
        payload = {
            "reference": request.reference,
            "amount": str(request.amount),
            "currency": request.currency,
            "accountNumber": request.account_number,
            "bankCode": request.bank_code,
            "accountName": request.account_name,
            "narration": request.narration or "Salary payment via Payday",
            "metadata": request.metadata,
        }
        try:
            raw = await self._client.create_transfer(payload)
        except (AlatPayError, httpx.HTTPError):
            return DisbursementResult(
                reference=request.reference,
                provider_reference=None,
                state=DistributionState.FAILED,
                raw={},
            )

        data = raw.get("data", raw) if isinstance(raw, dict) else {}
        return DisbursementResult(
            reference=request.reference,
            provider_reference=data.get("transactionId") or data.get("reference"),
            state=_map_state(data.get("status")),
            raw=raw if isinstance(raw, dict) else {},
        )

    async def disburse_batch(
        self,
        requests: Iterable[DisbursementRequest],
        *,
        concurrency: int = 10,
    ) -> list[DisbursementResult]:
        """Disburse many salaries concurrently.

        Transfers are fired in parallel (bounded by ``concurrency``) so a full
        payroll run for an entire company executes quickly rather than serially.
        """
        semaphore = asyncio.Semaphore(concurrency)

        async def _run(req: DisbursementRequest) -> DisbursementResult:
            async with semaphore:
                return await self.disburse_one(req)

        return await asyncio.gather(*(_run(req) for req in requests))

    async def get_status(self, provider_reference: str) -> DistributionState:
        """Reconcile a transaction by polling ALATPay for its current status."""
        raw = await self._client.get_transaction_status(provider_reference)
        data = raw.get("data", raw) if isinstance(raw, dict) else {}
        return _map_state(data.get("status"))

    # --- Webhook ingestion -------------------------------------------------

    def verify_signature(self, payload: bytes, signature: str | None) -> bool:
        """Verify an inbound webhook's HMAC-SHA256 signature.

        If no webhook secret is configured the check is skipped (useful for
        local development) but this should always be set in production.
        """
        if not self._webhook_secret:
            return True
        if not signature:
            return False
        expected = hmac.new(
            self._webhook_secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature.strip())

    def parse_webhook(self, payload: bytes, signature: str | None, body: dict) -> WebhookEvent:
        """Verify then normalise a raw ALATPay webhook into a ``WebhookEvent``."""
        if not self.verify_signature(payload, signature):
            raise AlatPayWebhookVerificationError("Invalid ALATPay webhook signature")

        data = body.get("data", body) if isinstance(body, dict) else {}
        return WebhookEvent(
            event_type=str(body.get("event") or body.get("type") or "transaction.update"),
            provider_reference=data.get("transactionId") or data.get("reference"),
            client_reference=data.get("clientReference") or data.get("merchantReference"),
            state=_map_state(data.get("status")),
            raw=body if isinstance(body, dict) else {},
        )


def build_alatpay_service(settings: Settings | None = None) -> AlatPayService:
    """Construct an :class:`AlatPayService` from application settings."""
    settings = settings or get_settings()
    client = AlatPayClient(
        base_url=settings.alatpay_base_url,
        api_key=settings.alatpay_api_key,
        business_id=settings.alatpay_business_id,
        timeout=settings.alatpay_timeout_seconds,
    )
    return AlatPayService(client, webhook_secret=settings.alatpay_webhook_secret)


def get_alatpay_service() -> AlatPayService:
    """FastAPI dependency provider for the ALATPay service."""
    return build_alatpay_service()
