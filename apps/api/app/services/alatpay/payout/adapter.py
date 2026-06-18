"""Adapter exposing the Wema payout service as a disbursement backend.

Implements the same ``disburse_one`` / ``disburse_batch`` /
``get_transaction_status`` surface as :class:`AlatPayService`, so the payroll
orchestration can swap the real payout rail in without any other changes.
"""

from __future__ import annotations

import asyncio
from collections.abc import Iterable

from app.core.config import Settings, get_settings
from app.models.enums import DistributionState
from app.services.alatpay.models import DisbursementRequest, DisbursementResult
from app.services.alatpay.payout.models import TransferRequest
from app.services.alatpay.payout.service import PayoutService, build_payout_service


class PayoutDisbursementService:
    """Disbursement backend backed by the real Wema NIP payout API."""

    def __init__(
        self,
        payout: PayoutService,
        *,
        originator_name: str,
        source_account: str,
    ) -> None:
        self._payout = payout
        self._originator_name = originator_name
        self._source_account = source_account

    def _build_transfer(self, req: DisbursementRequest) -> TransferRequest:
        name = f"{req.customer.first_name} {req.customer.last_name}".strip()
        return TransferRequest(
            destination_bank_code=req.bank_code,
            destination_account_number=req.account_number,
            account_name=name or "Beneficiary",
            amount=req.amount,
            payment_reference=req.reference,
            narration=req.narration or "Salary payment via Payday",
            originator_name=self._originator_name,
            source_account=self._source_account,
        )

    async def disburse_one(self, request: DisbursementRequest) -> DisbursementResult:
        result = await self._payout.payout(self._build_transfer(request))
        return DisbursementResult(
            reference=request.reference,
            provider_reference=result.provider_reference,
            state=result.state,
            channel="nip_transfer",
            message=result.message,
            raw={"response_code": result.response_code or "", "detail": result.raw},
        )

    async def disburse_batch(
        self,
        requests: Iterable[DisbursementRequest],
        *,
        concurrency: int = 10,
    ) -> list[DisbursementResult]:
        semaphore = asyncio.Semaphore(concurrency)

        async def _run(req: DisbursementRequest) -> DisbursementResult:
            async with semaphore:
                return await self.disburse_one(req)

        return await asyncio.gather(*(_run(req) for req in requests))

    async def get_transaction_status(self, provider_reference: str) -> DistributionState:
        return await self._payout.get_status(provider_reference)


def build_payout_disbursement_service(
    settings: Settings | None = None,
) -> PayoutDisbursementService:
    settings = settings or get_settings()
    payout = build_payout_service(settings)
    return PayoutDisbursementService(
        payout,
        originator_name=settings.payout_originator_name,
        source_account=settings.payout_source_account,
    )
