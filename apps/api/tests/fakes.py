"""In-memory fake of the ALATPay transport client for tests.

Builds the *real* service classes (`StaticWalletService`, `AlatPayService`,
`SettlementsService`) around a fake client so the real domain logic — header
injection aside — is exercised without any network access.
"""

from __future__ import annotations

from typing import Any


class FakeAlatPayClient:
    """Canned responses mirroring the documented ALATPay payloads."""

    def __init__(self, *, balance: str = "100000000.00") -> None:
        self.balance = balance
        # State returned by the bank-transfer rail (overridable per test).
        self.transfer_status = "successful"
        self.transaction_status = "successful"
        self.calls: list[str] = []

    # --- wallets ----------------------------------------------------------
    async def create_static_wallet(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.calls.append("create_static_wallet")
        return {
            "data": {
                "id": "wal_demo",
                "accountNumber": "9990001111",
                "accountName": "Payday Payroll Wallet",
            }
        }

    async def validate_and_create_wallet(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "data": {
                "id": payload.get("staticWalletId"),
                "accountNumber": "9990001111",
                "accountName": "Payday Payroll Wallet",
            }
        }

    async def get_static_wallet(self, wallet_id: str) -> dict[str, Any]:
        self.calls.append("get_static_wallet")
        return {
            "data": {
                "accountBalance": self.balance,
                "accountNumber": "9990001111",
                "accountName": "Payday Payroll Wallet",
            }
        }

    # --- disbursement -----------------------------------------------------
    async def pay_with_bank_transfer(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.calls.append("pay_with_bank_transfer")
        return {
            "data": {
                "transactionId": f"ALT-{payload.get('orderId', '')}",
                "status": self.transfer_status,
            }
        }

    async def bank_details_send_otp(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.calls.append("bank_details_send_otp")
        return {
            "data": {
                "transactionId": f"ALT-OTP-{payload.get('orderId', '')}",
                "message": "OTP sent",
            }
        }

    async def get_transaction(self, transaction_id: str) -> dict[str, Any]:
        self.calls.append("get_transaction")
        return {"data": {"status": self.transaction_status}}

    async def list_transactions(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"data": []}

    async def get_settlements(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self.calls.append("get_settlements")
        return {"data": [{"amount": "590000", "feeAmount": "500"}]}
