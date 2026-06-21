"""Settlements service — wraps the ALATPay Settlements API.

Used to enrich the payroll analytics with provider-side settlement data
(amounts actually settled to the merchant, fees, settlement timestamps).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

import httpx

from app.core.config import Settings, get_settings
from app.services.alatpay.client import AlatPayClient
from app.services.alatpay.exceptions import AlatPayError


def _to_decimal(value: object) -> Decimal:
    if value is None:
        return Decimal("0.00")
    try:
        return Decimal(str(value))
    except (ValueError, ArithmeticError):
        return Decimal("0.00")


@dataclass(slots=True)
class SettlementSummary:
    """Aggregated settlement totals over a window."""

    total_amount: Decimal = Decimal("0.00")
    total_fees: Decimal = Decimal("0.00")
    count: int = 0
    records: list[dict] = field(default_factory=list)


class SettlementsService:
    """Domain-facing wrapper over the ALATPay Settlements API."""

    def __init__(self, client: AlatPayClient) -> None:
        self._client = client

    async def fetch_settlements(
        self,
        *,
        start_at: date | None = None,
        end_at: date | None = None,
        status: str | None = None,
    ) -> SettlementSummary:
        params: dict[str, object] = {}
        if start_at:
            params["startAt"] = start_at.isoformat()
        if end_at:
            params["endAt"] = end_at.isoformat()
        if status:
            params["status"] = status

        try:
            raw = await self._client.get_settlements(params)
        except (AlatPayError, httpx.HTTPError):
            return SettlementSummary()

        records = _extract_records(raw)
        summary = SettlementSummary(records=records, count=len(records))
        for rec in records:
            summary.total_amount += _to_decimal(rec.get("amount"))
            summary.total_fees += _to_decimal(rec.get("feeAmount"))
        return summary


def _extract_records(raw: object) -> list[dict]:
    if not isinstance(raw, dict):
        return []
    data = raw.get("data", raw)
    if isinstance(data, list):
        return [r for r in data if isinstance(r, dict)]
    if isinstance(data, dict):
        # Some responses nest the list under a key; fall back to a single record.
        for value in data.values():
            if isinstance(value, list):
                return [r for r in value if isinstance(r, dict)]
        return [data]
    return []


def build_settlements_service(settings: Settings | None = None) -> SettlementsService:
    settings = settings or get_settings()
    client = AlatPayClient(
        base_url=settings.alatpay_base_url,
        api_key=settings.alatpay_api_key,
        public_key=settings.alatpay_public_key,
        business_id=settings.alatpay_business_id,
        timeout=settings.alatpay_timeout_seconds,
    )
    return SettlementsService(client)


def get_settlements_service() -> SettlementsService:
    """FastAPI dependency provider for the settlements service."""
    return build_settlements_service()
