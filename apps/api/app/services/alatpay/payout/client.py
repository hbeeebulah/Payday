"""Async transport client for the Wema Merchant Payout API.

Handles token authentication (with caching + lock), the `VendorId` / bearer /
subscription-key headers, and the AES-encrypt-request / AES-decrypt-response
envelope. Business payloads are encrypted then wrapped in a single named JSON
string field; GET parameters are encrypted in place.
"""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from app.services.alatpay.exceptions import AlatPayHTTPError
from app.services.alatpay.payout.crypto import AesCipher

# Endpoint paths (relative to the configured base URL).
AUTH_PATH = "api/Authentication/authenticate"
REFRESH_PATH = "api/Authentication/RefreshToken"
BANKS_PATH = "api/WMServices/GetNIPBanks"
NAME_ENQUIRY_PATH = "api/WMServices/NIPNameEnquiry"
FUND_TRANSFER_PATH = "api/WMServices/NIPFundTransfer"
STATUS_PATH = "api/WMServices/GetTransactionStatus"
BALANCE_PATH = "api/GetBalance"

# Refresh a little before the documented 24h token lifetime.
_TOKEN_TTL = timedelta(hours=23)


class PayoutClient:
    """Low-level transport for the Wema payout product."""

    def __init__(
        self,
        *,
        base_url: str,
        username: str,
        password: str,
        vendor_id: str,
        cipher: AesCipher,
        subscription_key: str = "",
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._base_url = base_url if base_url.endswith("/") else base_url + "/"
        self._username = username
        self._password = password
        self._vendor_id = vendor_id
        self._cipher = cipher
        self._subscription_key = subscription_key
        self._timeout = timeout
        self._transport = transport

        self._token: str | None = None
        self._token_expiry: datetime | None = None
        self._auth_lock = asyncio.Lock()

    def _new_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
            transport=self._transport,
        )

    # --- Authentication ---------------------------------------------------

    def _token_valid(self) -> bool:
        return (
            self._token is not None
            and self._token_expiry is not None
            and datetime.now(UTC) < self._token_expiry
        )

    async def authenticate(self) -> str:
        async with self._new_client() as client:
            response = await client.post(
                AUTH_PATH,
                json={"username": self._username, "password": self._password},
                headers={"Content-Type": "application/json"},
            )
        if response.status_code >= 400:
            raise AlatPayHTTPError(response.status_code, response.text, _safe_json(response))

        data = _safe_json(response) or {}
        token = data.get("token")
        if not token:
            raise AlatPayHTTPError(response.status_code, "No token in auth response", data)
        self._token = token
        self._token_expiry = datetime.now(UTC) + _TOKEN_TTL
        return token

    async def _ensure_token(self) -> str:
        if self._token_valid():
            return self._token  # type: ignore[return-value]
        async with self._auth_lock:
            if self._token_valid():
                return self._token  # type: ignore[return-value]
            return await self.authenticate()

    async def _auth_headers(self) -> dict[str, str]:
        token = await self._ensure_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "VendorId": self._vendor_id,
            "Content-Type": "application/json",
        }
        if self._subscription_key:
            headers["Ocp-Apim-Subscription-Key"] = self._subscription_key
        return headers

    # --- Encrypted request helpers ----------------------------------------

    async def _post_encrypted(
        self, path: str, wrapper_field: str, plaintext: dict[str, Any]
    ) -> str:
        cipher_text = self._cipher.encrypt(json.dumps(plaintext))
        headers = await self._auth_headers()
        async with self._new_client() as client:
            response = await client.post(
                path, json={wrapper_field: cipher_text}, headers=headers
            )
        if response.status_code >= 400:
            raise AlatPayHTTPError(response.status_code, response.text, _safe_json(response))
        return self._cipher.decrypt(_extract_cipher(response))

    async def _get_encrypted(
        self, path: str, param: str | None = None, value: str | None = None
    ) -> str:
        headers = await self._auth_headers()
        params = {param: self._cipher.encrypt(value)} if param and value is not None else None
        async with self._new_client() as client:
            response = await client.get(path, params=params, headers=headers)
        if response.status_code >= 400:
            raise AlatPayHTTPError(response.status_code, response.text, _safe_json(response))
        return self._cipher.decrypt(_extract_cipher(response))

    # --- Endpoints --------------------------------------------------------

    async def get_nip_banks(self) -> str:
        return await self._get_encrypted(BANKS_PATH)

    async def name_enquiry(self, *, bank_code: str, account_number: str) -> str:
        return await self._post_encrypted(
            NAME_ENQUIRY_PATH,
            "NameEnquiryRequest",
            {
                "myDestinationBankCode": bank_code,
                "myDestinationAccountNumber": account_number,
            },
        )

    async def fund_transfer(self, plaintext: dict[str, Any]) -> str:
        return await self._post_encrypted(
            FUND_TRANSFER_PATH, "FundTransferRequest", plaintext
        )

    async def get_transaction_status(self, payment_reference: str) -> str:
        return await self._get_encrypted(
            STATUS_PATH, "TransactionReference", payment_reference
        )

    async def get_balance(self, account_number: str) -> str:
        return await self._get_encrypted(BALANCE_PATH, "AccountNumber", account_number)


def _safe_json(response: httpx.Response) -> dict[str, Any] | None:
    try:
        parsed = response.json()
    except (ValueError, httpx.DecodingError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _extract_cipher(response: httpx.Response) -> str:
    """Pull the base64 ciphertext out of an encrypted response body.

    Wema returns either a bare quoted string or an object wrapping the cipher.
    """
    text = response.text.strip()
    try:
        parsed = response.json()
    except (ValueError, httpx.DecodingError):
        return text.strip('"')

    if isinstance(parsed, str):
        return parsed
    if isinstance(parsed, dict):
        for value in parsed.values():
            if isinstance(value, str) and value:
                return value
    return text.strip('"')
