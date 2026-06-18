"""High-level ALATPay disbursement & webhook service.

Exposes payroll-oriented operations on top of :class:`AlatPayClient`:

* ``pay_with_bank_transfer`` / ``pay_with_bank_details`` — the two payout rails.
* ``disburse_one`` — routes a payout to the correct rail (Wema accounts use the
  direct-debit "Pay with Bank Details" flow).
* ``disburse_batch`` — fans out many payouts in parallel.
* ``verify_signature`` / ``parse_webhook`` — inbound webhook ingestion.
* ``get_transaction_status`` — server-side re-verification of a transaction.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
from collections.abc import Iterable
from decimal import Decimal

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
    "paid": DistributionState.SUCCESSFUL,
    "true": DistributionState.SUCCESSFUL,
    "failed": DistributionState.FAILED,
    "declined": DistributionState.FAILED,
    "false": DistributionState.FAILED,
    "reversed": DistributionState.REVERSED,
}


def _map_state(raw_state: object) -> DistributionState:
    if raw_state is None:
        return DistributionState.PENDING
    if isinstance(raw_state, bool):
        return DistributionState.SUCCESSFUL if raw_state else DistributionState.FAILED
    return _STATE_MAP.get(str(raw_state).strip().lower(), DistributionState.PROCESSING)


def _to_decimal(value: object) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (ValueError, ArithmeticError):
        return None


class AlatPayService:
    """Domain-facing ALATPay payout + webhook operations."""

    def __init__(
        self,
        client: AlatPayClient,
        *,
        webhook_secret: str = "",
        wema_bank_code: str = "035",
    ) -> None:
        self._client = client
        self._webhook_secret = webhook_secret
        self._wema_bank_code = wema_bank_code

    # --- Payout rails ------------------------------------------------------

    async def pay_with_bank_transfer(
        self, request: DisbursementRequest
    ) -> DisbursementResult:
        """Pay a worker via the Pay with Bank Transfer rail."""
        payload = {
            "amount": str(request.amount),
            "currency": request.currency,
            "orderId": request.reference,
            "description": request.narration or "Salary payment via Payday",
            "accountNumber": request.account_number,
            "bankCode": request.bank_code,
            "customer": request.customer.to_payload(),
        }
        try:
            raw = await self._client.pay_with_bank_transfer(payload)
        except (AlatPayError, httpx.HTTPError) as exc:
            return _failed(request, channel="bank_transfer", message=str(exc))

        data = raw.get("data", raw) if isinstance(raw, dict) else {}
        return DisbursementResult(
            reference=request.reference,
            provider_reference=data.get("transactionId") or data.get("id"),
            state=_map_state(data.get("status")),
            channel="bank_transfer",
            message=data.get("statusReason") or data.get("message"),
            raw=raw if isinstance(raw, dict) else {},
        )

    async def pay_with_bank_details(
        self, request: DisbursementRequest
    ) -> DisbursementResult:
        """Pay a Wema-account worker via the Pay with Bank Details direct-debit rail.

        This initiates the OTP-gated authorization; the transfer reaches a
        terminal state asynchronously and is reconciled via webhook.
        """
        payload = {
            "amount": str(request.amount),
            "currency": request.currency,
            "orderId": request.reference,
            "description": request.narration or "Salary payment via Payday",
            "channel": "3",
            "accountNumber": request.account_number,
            "bankCode": request.bank_code,
            "customer": request.customer.to_payload(),
        }
        try:
            raw = await self._client.bank_details_send_otp(payload)
        except (AlatPayError, httpx.HTTPError) as exc:
            return _failed(request, channel="bank_details", message=str(exc))

        data = raw.get("data", raw) if isinstance(raw, dict) else {}
        return DisbursementResult(
            reference=request.reference,
            provider_reference=data.get("transactionId") or data.get("id"),
            # The payout is authorized and in flight until the webhook confirms.
            state=DistributionState.PROCESSING,
            channel="bank_details",
            message=data.get("message"),
            raw=raw if isinstance(raw, dict) else {},
        )

    async def disburse_one(self, request: DisbursementRequest) -> DisbursementResult:
        """Route a single payout to the correct rail.

        Wema Bank accounts (bank code ``035``) are paid via direct debit;
        everyone else goes through Pay with Bank Transfer.
        """
        if request.bank_code == self._wema_bank_code:
            return await self.pay_with_bank_details(request)
        return await self.pay_with_bank_transfer(request)

    async def disburse_batch(
        self,
        requests: Iterable[DisbursementRequest],
        *,
        concurrency: int = 10,
    ) -> list[DisbursementResult]:
        """Disburse many salaries concurrently (bounded by ``concurrency``)."""
        semaphore = asyncio.Semaphore(concurrency)

        async def _run(req: DisbursementRequest) -> DisbursementResult:
            async with semaphore:
                return await self.disburse_one(req)

        return await asyncio.gather(*(_run(req) for req in requests))

    async def get_transaction_status(self, provider_reference: str) -> DistributionState:
        """Reconcile a transaction by polling ALATPay for its current status."""
        raw = await self._client.get_transaction(provider_reference)
        data = raw.get("data", raw) if isinstance(raw, dict) else {}
        return _map_state(data.get("status"))

    # --- Webhook ingestion -------------------------------------------------

    def verify_signature(self, payload: bytes, signature: str | None) -> bool:
        """Verify an inbound webhook's HMAC-SHA256 signature.

        ALATPay does not document a signing header, so when no secret is
        configured the check is skipped. When a secret *is* configured we
        enforce an HMAC-SHA256 over the raw body, and callers are expected to
        additionally re-verify via :meth:`get_transaction_status`.
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
            provider_reference=data.get("transactionId") or data.get("id"),
            client_reference=data.get("orderId")
            or data.get("clientReference")
            or data.get("merchantReference"),
            state=_map_state(data.get("status")),
            amount=_to_decimal(data.get("amount")),
            raw=body if isinstance(body, dict) else {},
        )


def _failed(
    request: DisbursementRequest, *, channel: str, message: str | None
) -> DisbursementResult:
    return DisbursementResult(
        reference=request.reference,
        provider_reference=None,
        state=DistributionState.FAILED,
        channel=channel,
        message=message,
        raw={},
    )


def build_alatpay_service(settings: Settings | None = None) -> AlatPayService:
    """Construct an :class:`AlatPayService` from application settings."""
    settings = settings or get_settings()
    client = AlatPayClient(
        base_url=settings.alatpay_base_url,
        api_key=settings.alatpay_api_key,
        public_key=settings.alatpay_public_key,
        business_id=settings.alatpay_business_id,
        timeout=settings.alatpay_timeout_seconds,
    )
    return AlatPayService(
        client,
        webhook_secret=settings.alatpay_webhook_secret,
        wema_bank_code=settings.wema_bank_code,
    )


def get_alatpay_service() -> AlatPayService:
    """FastAPI dependency provider for the ALATPay service."""
    return build_alatpay_service()
