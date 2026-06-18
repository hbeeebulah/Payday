"""Typed contracts + NIP response-code mapping for the Wema payout API."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from app.models.enums import DistributionState

# NIBSS NIP response codes (subset relevant to disbursement). "00" == success.
NIP_RESPONSE_CODES: dict[str, str] = {
    "00": "Approved or completed successfully",
    "01": "Status unknown, await settlement report",
    "03": "Invalid sender",
    "05": "Do not honor",
    "06": "Dormant account",
    "07": "Invalid account",
    "08": "Account name mismatch",
    "09": "Request processing in progress",
    "12": "Invalid transaction",
    "13": "Invalid amount",
    "16": "Unknown bank code",
    "17": "Invalid channel",
    "20": "Transaction in progress, awaiting NIBSS confirmation",
    "25": "Unable to locate record",
    "26": "Duplicate record",
    "32": "Transaction failed, resend with new payment reference",
    "34": "Suspected fraud",
    "51": "Insufficient funds",
    "57": "Transaction not permitted to sender",
    "61": "Transfer limit exceeded",
    "63": "Security violation",
    "91": "Beneficiary bank not available",
    "94": "Duplicate transaction",
    "96": "System malfunction",
    "97": "Timeout waiting for destination",
}

_SUCCESS = {"00"}
_PENDING = {"01", "09", "20"}


def describe_code(code: str | None) -> str:
    if not code:
        return "Unknown response"
    return NIP_RESPONSE_CODES.get(code, f"NIP response {code}")


def map_response_code(code: str | None) -> DistributionState:
    """Map a NIP response code onto our internal distribution state."""
    if code in _SUCCESS:
        return DistributionState.SUCCESSFUL
    if code in _PENDING:
        return DistributionState.PROCESSING
    return DistributionState.FAILED


@dataclass(slots=True)
class NipBank:
    name: str
    code: str


@dataclass(slots=True)
class NameEnquiryResult:
    response_code: str
    account_name: str | None
    success: bool
    raw: str = ""


@dataclass(slots=True)
class TransferRequest:
    """A single outbound NIP transfer (the actual payout)."""

    destination_bank_code: str
    destination_account_number: str
    account_name: str
    amount: Decimal
    payment_reference: str  # unique per transaction
    narration: str
    originator_name: str
    source_account: str

    def to_plaintext(self) -> dict:
        # Send a whole-naira integer when possible, else a decimal number.
        is_whole = self.amount == self.amount.to_integral_value()
        amount: int | float = int(self.amount) if is_whole else float(self.amount)
        return {
            "myDestinationBankCode": self.destination_bank_code,
            "myDestinationAccountNumber": self.destination_account_number,
            "myAccountName": self.account_name,
            "myOriginatorName": self.originator_name,
            "myNarration": self.narration,
            "myPaymentReference": self.payment_reference,
            "myAmount": amount,
            "sourceAccountNo": self.source_account,
        }


@dataclass(slots=True)
class TransferResult:
    response_code: str | None
    provider_reference: str | None
    state: DistributionState
    success: bool
    message: str
    raw: str = ""
    extra: dict = field(default_factory=dict)
