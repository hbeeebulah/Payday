"""High-level Wema Merchant Payout service.

Wraps :class:`PayoutClient` with typed, domain-facing operations: list banks,
name enquiry, balance, the NIP fund transfer (the actual payout), and status
requery. Pipe-delimited provider responses are normalised here.
"""

from __future__ import annotations

import json
from decimal import Decimal

import httpx

from app.core.config import Settings, get_settings
from app.models.enums import DistributionState
from app.services.alatpay.exceptions import AlatPayError
from app.services.alatpay.payout.client import PayoutClient
from app.services.alatpay.payout.crypto import AesCipher
from app.services.alatpay.payout.models import (
    NameEnquiryResult,
    NipBank,
    TransferRequest,
    TransferResult,
    describe_code,
    map_response_code,
)


def _parse_pipe(decrypted: str) -> tuple[str, str]:
    """Split a `responseCode|detail` string into (code, detail)."""
    parts = decrypted.split("|", 1)
    code = parts[0].strip()
    detail = parts[1].strip() if len(parts) > 1 else ""
    return code, detail


def _to_decimal(raw: str) -> Decimal:
    cleaned = raw.replace(",", "").strip()
    try:
        return Decimal(cleaned)
    except (ValueError, ArithmeticError):
        return Decimal("0.00")


class PayoutService:
    """Domain-facing Wema payout operations."""

    def __init__(self, client: PayoutClient, *, originator_name: str, source_account: str) -> None:
        self._client = client
        self._originator_name = originator_name
        self._source_account = source_account

    async def list_banks(self) -> list[NipBank]:
        decrypted = await self._client.get_nip_banks()
        try:
            items = json.loads(decrypted)
        except json.JSONDecodeError:
            return []
        banks: list[NipBank] = []
        for item in items if isinstance(items, list) else []:
            if not isinstance(item, dict):
                continue
            name = item.get("bankName") or item.get("name") or item.get("BankName") or ""
            code = (
                item.get("bankCode")
                or item.get("code")
                or item.get("nipBankCode")
                or item.get("BankCode")
                or ""
            )
            banks.append(NipBank(name=str(name), code=str(code)))
        return banks

    async def resolve_account(
        self, *, bank_code: str, account_number: str
    ) -> NameEnquiryResult:
        decrypted = await self._client.name_enquiry(
            bank_code=bank_code, account_number=account_number
        )
        code, name = _parse_pipe(decrypted)
        return NameEnquiryResult(
            response_code=code,
            account_name=name or None,
            success=code == "00",
            raw=decrypted,
        )

    async def get_balance(self, account_number: str | None = None) -> Decimal:
        account = account_number or self._source_account
        decrypted = await self._client.get_balance(account)
        return _to_decimal(decrypted)

    async def get_status(self, payment_reference: str) -> DistributionState:
        decrypted = await self._client.get_transaction_status(payment_reference)
        code, _ = _parse_pipe(decrypted)
        return map_response_code(code)

    async def payout(self, request: TransferRequest) -> TransferResult:
        """Execute a single outbound NIP transfer.

        Errors are contained and surfaced as a FAILED result so one bad payout
        never aborts a batch.
        """
        try:
            decrypted = await self._client.fund_transfer(request.to_plaintext())
        except (AlatPayError, httpx.HTTPError) as exc:
            return TransferResult(
                response_code=None,
                provider_reference=None,
                state=DistributionState.FAILED,
                success=False,
                message=str(exc),
            )

        code, detail = _parse_pipe(decrypted)
        state = map_response_code(code)
        return TransferResult(
            response_code=code,
            provider_reference=detail or None,
            state=state,
            success=code == "00",
            message=describe_code(code),
            raw=decrypted,
        )


def build_payout_service(settings: Settings | None = None) -> PayoutService:
    settings = settings or get_settings()
    cipher = AesCipher(settings.payout_encryption_key, settings.payout_encryption_iv)
    client = PayoutClient(
        base_url=settings.payout_base_url,
        username=settings.payout_username,
        password=settings.payout_password,
        vendor_id=settings.payout_vendor_id,
        cipher=cipher,
        subscription_key=settings.payout_subscription_key,
        timeout=settings.payout_timeout_seconds,
    )
    return PayoutService(
        client,
        originator_name=settings.payout_originator_name,
        source_account=settings.payout_source_account,
    )


def get_payout_service() -> PayoutService:
    """FastAPI dependency provider for the payout service."""
    return build_payout_service()
