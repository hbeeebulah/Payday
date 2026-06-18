"""Unit tests for the isolated ALATPay service."""

from __future__ import annotations

import hashlib
import hmac
import json

from app.models.enums import DistributionState
from app.services.alatpay import AlatPayService
from app.services.alatpay.client import AlatPayClient


def _service(secret: str = "topsecret") -> AlatPayService:
    client = AlatPayClient(
        base_url="https://example.test",
        api_key="k",
        business_id="b",
    )
    return AlatPayService(client, webhook_secret=secret)


def test_signature_verification_roundtrip():
    svc = _service()
    body = json.dumps({"event": "transaction.update"}).encode()
    sig = hmac.new(b"topsecret", body, hashlib.sha256).hexdigest()
    assert svc.verify_signature(body, sig) is True
    assert svc.verify_signature(body, "bad") is False


def test_parse_webhook_maps_state():
    svc = _service(secret="")  # signature check skipped when no secret
    body = {
        "event": "transaction.update",
        "data": {
            "transactionId": "ALT-123",
            "clientReference": "receipt-1",
            "status": "successful",
        },
    }
    event = svc.parse_webhook(json.dumps(body).encode(), None, body)
    assert event.provider_reference == "ALT-123"
    assert event.client_reference == "receipt-1"
    assert event.state == DistributionState.SUCCESSFUL
