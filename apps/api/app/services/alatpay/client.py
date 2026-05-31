"""Thin async HTTP client around the ALATPay (Wema Bank) REST API.

The client concerns itself purely with transport: it injects the merchant
credentials into every request (the subscription key as a header and the
business id into the body/query), executes the call and surfaces errors. All
domain mapping lives one layer up in the service classes.

Endpoint paths follow the service-prefixed forms documented at
``https://docs.alatpay.ng`` under ``https://apibox.alatpay.ng``.
"""

from __future__ import annotations

from typing import Any

import httpx

from app.services.alatpay.exceptions import AlatPayHTTPError

# Service-prefixed API segments.
WALLET_PREFIX = "/alatpay-wallet/api/v1/staticaccount"
BANK_TRANSFER_PREFIX = "/bank-transfer/api/v1/bankTransfer"
BANK_DETAILS_PREFIX = "/alatpayaccountnumber/api/v1/accountNumber"
TRANSACTION_PREFIX = "/alatpaytransaction/api/v1/transactions"
SETTLEMENT_PREFIX = "/payment-settlement/api/v1/settlements"


class AlatPayClient:
    """Async transport client for ALATPay."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        business_id: str,
        public_key: str = "",
        timeout: float = 30.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._public_key = public_key
        self._business_id = business_id
        self._timeout = timeout

    @property
    def business_id(self) -> str:
        return self._business_id

    def _headers(self) -> dict[str, str]:
        # Secure header injection: the subscription key authenticates the call.
        # The public key is forwarded for parity with the checkout SDK.
        return {
            "Ocp-Apim-Subscription-Key": self._api_key,
            "X-Business-Public-Key": self._public_key,
            "Content-Type": "application/json",
        }

    def _with_business_body(self, body: dict[str, Any] | None) -> dict[str, Any]:
        merged = dict(body or {})
        merged.setdefault("businessId", self._business_id)
        return merged

    def _with_business_params(self, params: dict[str, Any] | None) -> dict[str, Any]:
        merged = dict(params or {})
        merged.setdefault("BusinessId", self._business_id)
        return merged

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

    # --- Static Wallets ----------------------------------------------------

    async def create_static_wallet(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request(
            "POST", WALLET_PREFIX, json=self._with_business_body(payload)
        )

    async def validate_and_create_wallet(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"{WALLET_PREFIX}/validateAndCreate",
            json=self._with_business_body(payload),
        )

    async def get_static_wallet(self, wallet_id: str) -> dict[str, Any]:
        return await self._request(
            "GET",
            f"{WALLET_PREFIX}/staticAccountId",
            params={"StaticAccountId": wallet_id},
        )

    async def list_static_wallets(
        self, *, page: int = 1, limit: int = 20
    ) -> dict[str, Any]:
        return await self._request(
            "GET",
            WALLET_PREFIX,
            params=self._with_business_params({"PageNumber": page, "Limit": limit}),
        )

    async def wallet_collection_history(
        self, *, page: int = 1, limit: int = 20
    ) -> dict[str, Any]:
        return await self._request(
            "GET",
            f"{WALLET_PREFIX}/collectionhistory",
            params=self._with_business_params({"PageNumber": page, "Limit": limit}),
        )

    # --- Pay with Bank Transfer -------------------------------------------

    async def pay_with_bank_transfer(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"{BANK_TRANSFER_PREFIX}/virtualAccount",
            json=self._with_business_body(payload),
        )

    async def get_bank_transfer_status(self, transaction_id: str) -> dict[str, Any]:
        return await self._request(
            "GET", f"{BANK_TRANSFER_PREFIX}/transactions/{transaction_id}"
        )

    # --- Pay with Bank Details (Wema direct debit) ------------------------

    async def bank_details_send_otp(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"{BANK_DETAILS_PREFIX}/sendOtp",
            json=self._with_business_body(payload),
        )

    async def bank_details_validate_and_pay(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request(
            "POST", f"{BANK_DETAILS_PREFIX}/validateAndPay", json=payload
        )

    # --- Transactions & Settlements ---------------------------------------

    async def get_transaction(self, transaction_id: str) -> dict[str, Any]:
        return await self._request("GET", f"{TRANSACTION_PREFIX}/{transaction_id}")

    async def list_transactions(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
        merged = self._with_business_params(params)
        merged.setdefault("Page", 1)
        return await self._request("GET", TRANSACTION_PREFIX, params=merged)

    async def get_settlements(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
        merged = dict(params or {})
        merged.setdefault("businessId", self._business_id)
        return await self._request("GET", SETTLEMENT_PREFIX, params=merged)


def _safe_json(response: httpx.Response) -> dict[str, Any] | None:
    try:
        return response.json()
    except (ValueError, httpx.DecodingError):
        return None
