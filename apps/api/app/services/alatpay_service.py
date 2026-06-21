"""Isolated service for all ALATPay API communication."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import httpx

from app.core.config import settings


@dataclass(frozen=True)
class PayoutRequest:
    employee_id: str
    amount: Decimal
    bank_account_number: str
    bank_routing_number: str
    narration: str


@dataclass(frozen=True)
class PayoutResult:
    employee_id: str
    alatpay_transaction_ref: str
    status: str
    raw_response: dict[str, Any]


class ALATPayService:
    """Dedicated client for ALATPay disbursement and webhook verification."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        merchant_id: str | None = None,
        webhook_secret: str | None = None,
    ) -> None:
        self.base_url = (base_url or settings.alatpay_base_url).rstrip("/")
        self.api_key = api_key or settings.alatpay_api_key
        self.merchant_id = merchant_id or settings.alatpay_merchant_id
        self.webhook_secret = webhook_secret or settings.alatpay_webhook_secret

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Merchant-Id": self.merchant_id,
        }

    async def initiate_batch_payout(
        self,
        batch_reference: str,
        payouts: list[PayoutRequest],
    ) -> list[PayoutResult]:
        """Submit parallel payout requests to ALATPay for a payroll batch."""
        async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
            tasks = [
                self._submit_single_payout(client, batch_reference, payout) for payout in payouts
            ]

            return list(await asyncio.gather(*tasks))

    async def _submit_single_payout(
        self,
        client: httpx.AsyncClient,
        batch_reference: str,
        payout: PayoutRequest,
    ) -> PayoutResult:
        payload = {
            "batch_reference": batch_reference,
            "employee_id": payout.employee_id,
            "amount": str(payout.amount),
            "account_number": payout.bank_account_number,
            "bank_code": payout.bank_routing_number,
            "narration": payout.narration,
        }
        response = await client.post("/v1/disbursements", json=payload, headers=self._headers())
        response.raise_for_status()
        data = response.json()
        return PayoutResult(
            employee_id=payout.employee_id,
            alatpay_transaction_ref=data["transaction_reference"],
            status=data.get("status", "processing"),
            raw_response=data,
        )

    async def get_transaction_status(self, transaction_ref: str) -> dict[str, Any]:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=15.0) as client:
            response = await client.get(
                f"/v1/transactions/{transaction_ref}",
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        expected = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    def parse_webhook_event(self, body: dict[str, Any]) -> dict[str, Any]:
        return {
            "event_type": body.get("event"),
            "transaction_ref": body.get("transaction_reference"),
            "status": body.get("status"),
            "amount": body.get("amount"),
            "processed_at": body.get("processed_at"),
        }
