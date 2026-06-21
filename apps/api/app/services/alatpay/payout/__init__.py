"""Wema Merchant Payout (NIP disbursement) integration.

This is the **real outbound payout** product (sending money OUT to arbitrary
Nigerian bank accounts over NIBSS Instant Payment), distinct from the ALATPay
collection rails. It uses token auth and AES/CBC encrypted payloads.

Kept fully isolated so the rest of the app depends only on the high-level
:class:`PayoutService` / :class:`PayoutDisbursementService`.
"""

from app.services.alatpay.payout.adapter import (
    PayoutDisbursementService,
    build_payout_disbursement_service,
)
from app.services.alatpay.payout.client import PayoutClient
from app.services.alatpay.payout.crypto import AesCipher
from app.services.alatpay.payout.models import (
    NameEnquiryResult,
    NipBank,
    TransferRequest,
    TransferResult,
    map_response_code,
)
from app.services.alatpay.payout.service import (
    PayoutService,
    build_payout_service,
    get_payout_service,
)

__all__ = [
    "AesCipher",
    "PayoutClient",
    "PayoutService",
    "PayoutDisbursementService",
    "build_payout_service",
    "build_payout_disbursement_service",
    "get_payout_service",
    "NipBank",
    "NameEnquiryResult",
    "TransferRequest",
    "TransferResult",
    "map_response_code",
]
