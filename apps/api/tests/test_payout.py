"""Tests for the Wema Merchant Payout (real NIP disbursement) integration.

A mocked httpx transport stands in for the Wema gateway: it authenticates,
decrypts the AES request envelope to assert correctness, and returns encrypted
pipe-delimited responses exactly as the real API does.
"""

from __future__ import annotations

import json
from decimal import Decimal

import httpx
import pytest
from app.models.enums import DistributionState
from app.services.alatpay import CustomerInfo, DisbursementRequest
from app.services.alatpay.payout import (
    AesCipher,
    PayoutClient,
    PayoutDisbursementService,
    PayoutService,
    TransferRequest,
)

KEY = ")KCSWITHC%^$$%@H"
IV = "#$%#^%KCSWITC945"
CIPHER = AesCipher(KEY, IV)


class Recorder:
    def __init__(self) -> None:
        self.auth_calls = 0
        self.transfer_plaintext: dict | None = None


def make_handler(recorder: Recorder, *, transfer_response: str = "00|SESSION123"):
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path

        if path.endswith("Authentication/authenticate"):
            recorder.auth_calls += 1
            return httpx.Response(
                200,
                json={
                    "token": "jwt-token",
                    "refreshToken": "refresh-token",
                    "refreshTokenExpires": "12/31/2026 5:00:00 PM",
                },
            )

        # All business calls must carry the auth + vendor headers.
        assert request.headers.get("Authorization") == "Bearer jwt-token"
        assert request.headers.get("VendorId") == "Centrik"

        if path.endswith("NIPFundTransfer"):
            body = json.loads(request.content)
            recorder.transfer_plaintext = json.loads(
                CIPHER.decrypt(body["FundTransferRequest"])
            )
            return _encrypted(transfer_response)

        if path.endswith("NIPNameEnquiry"):
            return _encrypted("00|JOHN DOE")

        if path.endswith("GetNIPBanks"):
            return _encrypted(
                json.dumps([{"bankName": "Wema Bank", "bankCode": "000017"}])
            )

        if path.endswith("GetBalance"):
            return _encrypted("150000.00")

        if path.endswith("GetTransactionStatus"):
            return _encrypted("00|SESSION123")

        return httpx.Response(404)

    return handler


def _encrypted(plaintext: str) -> httpx.Response:
    # Wema returns the ciphertext as a bare JSON string.
    return httpx.Response(200, json=CIPHER.encrypt(plaintext))


def build_service(recorder: Recorder, **kwargs) -> PayoutService:
    client = PayoutClient(
        base_url="https://wema.test/WemaAPIService/",
        username="centrikgateway",
        password="test12345",
        vendor_id="Centrik",
        cipher=CIPHER,
        transport=httpx.MockTransport(make_handler(recorder, **kwargs)),
    )
    return PayoutService(client, originator_name="Payday", source_account="1300005957")


def test_aes_roundtrip():
    assert CIPHER.decrypt(CIPHER.encrypt("hello|world")) == "hello|world"
    assert CIPHER.encrypt("hello") != "hello"


@pytest.mark.asyncio
async def test_list_banks_and_balance():
    rec = Recorder()
    svc = build_service(rec)
    banks = await svc.list_banks()
    assert banks[0].name == "Wema Bank"
    assert banks[0].code == "000017"

    balance = await svc.get_balance()
    assert balance == Decimal("150000.00")


@pytest.mark.asyncio
async def test_name_enquiry():
    rec = Recorder()
    svc = build_service(rec)
    result = await svc.resolve_account(bank_code="000013", account_number="0011678314")
    assert result.success
    assert result.account_name == "JOHN DOE"


@pytest.mark.asyncio
async def test_payout_success_encrypts_request_and_parses_response():
    rec = Recorder()
    svc = build_service(rec)
    result = await svc.payout(
        TransferRequest(
            destination_bank_code="000013",
            destination_account_number="0011678314",
            account_name="John Doe",
            amount=Decimal("10000"),
            payment_reference="rcpt-1",
            narration="May salary",
            originator_name="Payday",
            source_account="1300005957",
        )
    )
    assert result.success
    assert result.state == DistributionState.SUCCESSFUL
    assert result.provider_reference == "SESSION123"

    # The encrypted envelope decrypted to the documented field names.
    assert rec.transfer_plaintext is not None
    assert rec.transfer_plaintext["myDestinationAccountNumber"] == "0011678314"
    assert rec.transfer_plaintext["myAmount"] == 10000
    assert rec.transfer_plaintext["sourceAccountNo"] == "1300005957"


@pytest.mark.asyncio
async def test_payout_failure_maps_to_failed():
    rec = Recorder()
    svc = build_service(rec, transfer_response="51|Insufficient funds")
    result = await svc.payout(
        TransferRequest(
            destination_bank_code="000013",
            destination_account_number="0011678314",
            account_name="John Doe",
            amount=Decimal("10000"),
            payment_reference="rcpt-2",
            narration="May salary",
            originator_name="Payday",
            source_account="1300005957",
        )
    )
    assert not result.success
    assert result.state == DistributionState.FAILED
    assert result.response_code == "51"


@pytest.mark.asyncio
async def test_token_is_cached_across_calls():
    rec = Recorder()
    svc = build_service(rec)
    await svc.list_banks()
    await svc.get_balance()
    await svc.resolve_account(bank_code="000013", account_number="0011678314")
    assert rec.auth_calls == 1


@pytest.mark.asyncio
async def test_disbursement_adapter_pays_batch():
    rec = Recorder()
    svc = build_service(rec)
    adapter = PayoutDisbursementService(
        svc, originator_name="Payday", source_account="1300005957"
    )
    requests = [
        DisbursementRequest(
            reference=f"rcpt-{i}",
            amount=Decimal("50000"),
            currency="NGN",
            account_number="0011678314",
            bank_code="000013",
            customer=CustomerInfo(
                email="w@x.ng",
                phone="+2348000000000",
                first_name="Worker",
                last_name=str(i),
            ),
            narration="Salary",
        )
        for i in range(3)
    ]
    results = await adapter.disburse_batch(requests, concurrency=5)
    assert len(results) == 3
    assert all(r.state == DistributionState.SUCCESSFUL for r in results)
    assert all(r.channel == "nip_transfer" for r in results)
