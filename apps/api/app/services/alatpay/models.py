"""Typed request/response contracts for the ALATPay integration.

These are deliberately decoupled from the ORM models so the integration layer
has its own stable surface.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from app.models.enums import DistributionState


@dataclass(slots=True)
class DisbursementRequest:
    """A single salary transfer to push to ALATPay."""

    reference: str            # our idempotent client reference
    amount: Decimal
    currency: str
    account_number: str
    bank_code: str            # routing / NIP bank code
    account_name: str | None = None
    narration: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class DisbursementResult:
    """Normalised outcome of a disbursement attempt."""

    reference: str
    provider_reference: str | None
    state: DistributionState
    raw: dict = field(default_factory=dict)


@dataclass(slots=True)
class WebhookEvent:
    """A verified, normalised inbound ALATPay webhook event."""

    event_type: str
    provider_reference: str | None
    client_reference: str | None
    state: DistributionState
    raw: dict = field(default_factory=dict)
