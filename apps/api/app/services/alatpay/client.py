"""Thin async HTTP client around the ALATPay REST API.

The client only concerns itself with transport: building authenticated
requests, executing them with a shared ``httpx.AsyncClient`` and surfacing
errors. All domain mapping is handled one layer up in :mod:`service`.
"""

from __future__ import annotations

from typing import Any

import httpx

from app.services.alatpay.exceptions import AlatPayHTTPError


class AlatPayClient:
    """Async transport client for ALATPay."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        business_id: str,
        timeout: float = 30.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._business_id = business_id
        self._timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Ocp-Apim-Subscription-Key": self._api_key,
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.request(
                method,
                url,
                json=json,
                params=params,
                headers=self._headers(),
            )

        if response.status_code >= 400:
            raise AlatPayHTTPError(
                status_code=response.status_code,
                message=response.text,
                payload=_safe_json(response),
            )
        return _safe_json(response) or {}

    async def create_transfer(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Submit a single transfer/disbursement to ALATPay."""
        return await self._request(
            "POST",
            "/alatpay/api/v1/transfers",
            json={**payload, "businessId": self._business_id},
        )

    async def get_transaction_status(self, provider_reference: str) -> dict[str, Any]:
        """Poll the status of a previously created transaction."""
        return await self._request(
            "GET",
            f"/alatpay/api/v1/transactions/{provider_reference}",
        )


def _safe_json(response: httpx.Response) -> dict[str, Any] | None:
    try:
        return response.json()
    except (ValueError, httpx.DecodingError):
        return None
