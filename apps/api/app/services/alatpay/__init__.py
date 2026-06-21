"""Isolated integration layer for ALATPay (Wema Bank).

This package is the *only* place in the codebase that knows how to talk to
ALATPay / Wema. Routes and business logic depend on the service classes here;
the raw HTTP details live in the client classes. Keeping the integration
isolated means the payment provider can be swapped or mocked without touching
the rest of the application.

Two disbursement backends are provided:
* the ALATPay collection rails (:class:`AlatPayService`), and
* the real Wema Merchant Payout / NIP disbursement API (``payout`` subpackage).
``build_disbursement_service`` selects between them based on settings.
"""

from app.services.alatpay.client import AlatPayClient
from app.services.alatpay.exceptions import (
    AlatPayError,
    AlatPayHTTPError,
    AlatPayWebhookVerificationError,
)
from app.services.alatpay.models import (
    CustomerInfo,
    DisbursementRequest,
    DisbursementResult,
    WalletBalance,
    WalletProvisionResult,
    WebhookEvent,
)
from app.services.alatpay.service import (
    AlatPayService,
    DisbursementBackend,
    build_alatpay_service,
    build_disbursement_service,
    get_alatpay_service,
)
from app.services.alatpay.settlements import (
    SettlementsService,
    SettlementSummary,
    build_settlements_service,
    get_settlements_service,
)
from app.services.alatpay.wallets import (
    StaticWalletService,
    build_static_wallet_service,
    get_static_wallet_service,
)

__all__ = [
    "AlatPayClient",
    "AlatPayService",
    "DisbursementBackend",
    "StaticWalletService",
    "SettlementsService",
    "SettlementSummary",
    "build_alatpay_service",
    "build_disbursement_service",
    "build_static_wallet_service",
    "build_settlements_service",
    "get_alatpay_service",
    "get_static_wallet_service",
    "get_settlements_service",
    "CustomerInfo",
    "DisbursementRequest",
    "DisbursementResult",
    "WalletBalance",
    "WalletProvisionResult",
    "WebhookEvent",
    "AlatPayError",
    "AlatPayHTTPError",
    "AlatPayWebhookVerificationError",
]
