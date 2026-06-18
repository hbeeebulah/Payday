"""Typed request/response contracts for the ALATPay integration.

These are deliberately decoupled from the ORM models so the integration layer
has its own stable surface.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from app.models.enums import DistributionState, WalletStatus


@dataclass(slots=True)
class CustomerInfo:
    """The recipient/customer block ALATPay expects on payment requests."""

    email: str
    phone: str
    first_name: str
    last_name: str
    metadata: str = ""

    def to_payload(self) -> dict:
        return {
            "email": self.email,
            "phone": self.phone,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "metadata": self.metadata,
        }


@dataclass(slots=True)
class DisbursementRequest:
    """A single salary payout to push to ALATPay."""

    reference: str            # our idempotent client reference (the receipt id)
    amount: Decimal
    currency: str
    account_number: str
    bank_code: str            # routing / NIP bank code
    customer: CustomerInfo
    narration: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class DisbursementResult:
    """Normalised outcome of a disbursement attempt."""

    reference: str
    provider_reference: str | None
    state: DistributionState
    channel: str = "bank_transfer"   # "bank_transfer" | "bank_details"
    message: str | None = None
    raw: dict = field(default_factory=dict)


@dataclass(slots=True)
class WalletProvisionResult:
    """Outcome of provisioning a static Payroll Wallet."""

    wallet_id: str | None
    account_number: str | None
    account_name: str | None
    status: WalletStatus
    otp_tracking_id: str | None = None
    message: str | None = None
    raw: dict = field(default_factory=dict)


@dataclass(slots=True)
class WalletBalance:
    """A point-in-time wallet balance read."""

    available_balance: Decimal
    account_number: str | None = None
    account_name: str | None = None
    raw: dict = field(default_factory=dict)


@dataclass(slots=True)
class WebhookEvent:
    """A verified, normalised inbound ALATPay webhook event."""

    event_type: str
    provider_reference: str | None
    client_reference: str | None
    state: DistributionState
    amount: Decimal | None = None
    raw: dict = field(default_factory=dict)
