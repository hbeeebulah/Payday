"""Exception hierarchy for the ALATPay integration."""

from __future__ import annotations


class AlatPayError(Exception):
    """Base class for all ALATPay-related errors."""


class AlatPayHTTPError(AlatPayError):
    """Raised when ALATPay returns a non-success HTTP response."""

    def __init__(self, status_code: int, message: str, payload: object | None = None) -> None:
        self.status_code = status_code
        self.payload = payload
        super().__init__(f"ALATPay HTTP {status_code}: {message}")


class AlatPayWebhookVerificationError(AlatPayError):
    """Raised when an inbound webhook fails signature verification."""
