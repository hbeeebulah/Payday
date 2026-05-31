"""End-to-end tests of the payroll + ALATPay flow against the ASGI app."""

from __future__ import annotations

import pytest

API = "/api/v1"


async def _seed_business_with_staff(client) -> str:
    biz = await client.post(
        f"{API}/businesses",
        json={"name": "Jollof Foods Ltd", "email": "owner@jollof.ng"},
    )
    assert biz.status_code == 201, biz.text
    business_id = biz.json()["id"]

    # One Wema (035 -> bank details rail) and one non-Wema (058 -> bank transfer).
    employees = [
        {"role": "Chef", "bank_routing_code": "035", "salary": "200000.00"},
        {"role": "Cashier", "bank_routing_code": "058", "salary": "150000.00"},
    ]
    for i, extra in enumerate(employees):
        emp = await client.post(
            f"{API}/businesses/{business_id}/employees",
            json={
                "first_name": f"Staff{i}",
                "last_name": "Member",
                "email": f"staff{i}@jollof.ng",
                "bank_account_number": f"012345678{i}",
                **extra,
            },
        )
        assert emp.status_code == 201, emp.text
    return business_id


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get(f"{API}/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_provision_wallet(client):
    business_id = await _seed_business_with_staff(client)
    resp = await client.post(f"{API}/businesses/{business_id}/wallet", json={})
    assert resp.status_code == 201, resp.text
    wallet = resp.json()
    assert wallet["status"] == "active"
    assert wallet["account_number"] == "9990001111"


@pytest.mark.asyncio
async def test_execute_requires_wallet(client):
    business_id = await _seed_business_with_staff(client)
    run = await client.post(
        f"{API}/businesses/{business_id}/payroll-runs",
        json={"period_label": "2026-05"},
    )
    run_id = run.json()["id"]
    # No wallet provisioned yet -> conflict.
    resp = await client.post(
        f"{API}/businesses/{business_id}/payroll-runs/{run_id}/execute"
    )
    assert resp.status_code == 409, resp.text


@pytest.mark.asyncio
async def test_execute_blocks_on_insufficient_funds(client, fake_client):
    business_id = await _seed_business_with_staff(client)
    await client.post(f"{API}/businesses/{business_id}/wallet", json={})
    fake_client.balance = "1.00"  # wallet cannot cover the run

    run = await client.post(
        f"{API}/businesses/{business_id}/payroll-runs",
        json={"period_label": "2026-05"},
    )
    run_id = run.json()["id"]
    resp = await client.post(
        f"{API}/businesses/{business_id}/payroll-runs/{run_id}/execute"
    )
    assert resp.status_code == 402, resp.text


@pytest.mark.asyncio
async def test_full_payroll_lifecycle(client):
    business_id = await _seed_business_with_staff(client)
    await client.post(f"{API}/businesses/{business_id}/wallet", json={})

    run = await client.post(
        f"{API}/businesses/{business_id}/payroll-runs",
        json={"period_label": "2026-05"},
    )
    assert run.status_code == 201, run.text
    run_body = run.json()
    assert run_body["employee_count"] == 2
    assert run_body["total_funding_amount"] == "350000.00"
    run_id = run_body["id"]

    # Execute -> overdraft guard passes, disbursement scheduled in background.
    executed = await client.post(
        f"{API}/businesses/{business_id}/payroll-runs/{run_id}/execute"
    )
    assert executed.status_code == 202, executed.text
    detail = executed.json()
    assert detail["status"] == "processing"
    assert len(detail["receipts"]) == 2
    receipt_ids = [r["id"] for r in detail["receipts"]]

    # Simulate ALATPay webhooks flipping each payout from pending to paid.
    for rid in receipt_ids:
        hook = await client.post(
            f"{API}/webhooks/alatpay",
            json={
                "event": "transaction.update",
                "data": {
                    "orderId": rid,
                    "transactionId": f"ALT-{rid}",
                    "status": "successful",
                    "amount": "200000",
                },
            },
        )
        assert hook.status_code == 200, hook.text
        assert hook.json()["state"] == "successful"

    # The run should now be completed and analytics should reflect the spend.
    final = await client.get(
        f"{API}/businesses/{business_id}/payroll-runs/{run_id}"
    )
    assert final.json()["status"] == "completed"

    analytics = await client.get(
        f"{API}/businesses/{business_id}/analytics/payroll"
    )
    assert analytics.status_code == 200, analytics.text
    data = analytics.json()
    assert data["lifetime_disbursed"] == "350000.00"
    assert data["total_runs"] == 1
    assert data["months"][0]["successful_count"] == 2
    assert data["settlements"]["count"] == 1
