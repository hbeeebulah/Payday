"""Isolated integration layer for ALATPay (Wema Bank).

This package is the *only* place in the codebase that knows how to talk to
ALATPay. Routes and business logic depend on :class:`AlatPayService`; the raw
HTTP details live in :class:`AlatPayClient`. Keeping the integration isolated
means the payment provider can be swapped or mocked without touching the rest
of the application.
"""

from app.services.alatpay.client import AlatPayClient
from app.services.alatpay.exceptions import (
    AlatPayError,
    AlatPayHTTPError,
    AlatPayWebhookVerificationError,
)
from app.services.alatpay.models import (
    DisbursementRequest,
    DisbursementResult,
    WebhookEvent,
)
from app.services.alatpay.service import AlatPayService, get_alatpay_service

__all__ = [
    "AlatPayClient",
    "AlatPayService",
    "get_alatpay_service",
    "DisbursementRequest",
    "DisbursementResult",
    "WebhookEvent",
    "AlatPayError",
    "AlatPayHTTPError",
    "AlatPayWebhookVerificationError",
]
