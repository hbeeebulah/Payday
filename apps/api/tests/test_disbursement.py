"""Unit tests for payroll disbursement rail routing (Wema vs. bank transfer)."""

from __future__ import annotations

from decimal import Decimal

import pytest
from app.models import Business, Employee, TransactionReceipt
from app.models.enums import DistributionState
from app.services.alatpay import AlatPayService
from app.services.payroll import create_payroll_run, process_payroll_disbursement
from sqlalchemy import select

from tests.fakes import FakeAlatPayClient


async def _make_business_with_two_banks(db) -> str:
    business = Business(name="Test Co", email="test@co.ng")
    db.add(business)
    await db.flush()

    db.add_all(
        [
            Employee(
                business_id=business.id,
                first_name="Wema",
                last_name="Worker",
                role="Chef",
                salary=Decimal("200000"),
                bank_account_number="0011223344",
                bank_routing_code="035",  # Wema -> bank details rail
            ),
            Employee(
                business_id=business.id,
                first_name="Other",
                last_name="Worker",
                role="Cashier",
                salary=Decimal("150000"),
                bank_account_number="0055667788",
                bank_routing_code="058",  # non-Wema -> bank transfer rail
            ),
        ]
    )
    await db.commit()
    return business.id


@pytest.mark.asyncio
async def test_disbursement_routes_wema_to_bank_details(db_session):
    fake = FakeAlatPayClient()
    service = AlatPayService(fake, wema_bank_code="035")

    business_id = await _make_business_with_two_banks(db_session)
    run = await create_payroll_run(
        db_session, business_id=business_id, period_label="2026-05"
    )

    await process_payroll_disbursement(db_session, run=run, alatpay=service)

    # Both rails were exercised.
    assert "bank_details_send_otp" in fake.calls
    assert "pay_with_bank_transfer" in fake.calls

    receipts = list(
        (
            await db_session.execute(
                select(TransactionReceipt).where(
                    TransactionReceipt.payroll_run_id == run.id
                )
            )
        )
        .scalars()
        .all()
    )
    states = {r.bank_routing_code: r.distribution_state for r in receipts}
    # Wema direct-debit is authorized but pending webhook confirmation.
    assert states["035"] == DistributionState.PROCESSING
    # Bank transfer returned success immediately in the fake.
    assert states["058"] == DistributionState.SUCCESSFUL
    # Each receipt carries an ALATPay reference.
    assert all(r.alatpay_transaction_reference for r in receipts)
