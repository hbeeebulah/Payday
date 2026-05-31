"""End-to-end smoke test of the core payroll flow against the ASGI app."""

from __future__ import annotations

import pytest

API = "/api/v1"


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get(f"{API}/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_full_payroll_lifecycle(client):
    # Create a business.
    biz = await client.post(
        f"{API}/businesses",
        json={"name": "Jollof Foods Ltd", "email": "owner@jollof.ng"},
    )
    assert biz.status_code == 201, biz.text
    business_id = biz.json()["id"]

    # Add two employees.
    for i in range(2):
        emp = await client.post(
            f"{API}/businesses/{business_id}/employees",
            json={
                "first_name": f"Staff{i}",
                "last_name": "Member",
                "role": "Cashier",
                "salary": "150000.00",
                "bank_account_number": f"012345678{i}",
                "bank_routing_code": "035",
            },
        )
        assert emp.status_code == 201, emp.text

    # Create a payroll run — should aggregate funding total + employee count.
    run = await client.post(
        f"{API}/businesses/{business_id}/payroll-runs",
        json={"period_label": "2026-05"},
    )
    assert run.status_code == 201, run.text
    run_body = run.json()
    assert run_body["employee_count"] == 2
    assert run_body["total_funding_amount"] == "300000.00"
    assert run_body["status"] == "draft"
    run_id = run_body["id"]

    # Execute the run (ALATPay calls fail/timeout in tests -> failed state,
    # but the orchestration + receipts must still be produced).
    executed = await client.post(
        f"{API}/businesses/{business_id}/payroll-runs/{run_id}/execute",
    )
    assert executed.status_code == 200, executed.text
    detail = executed.json()
    assert len(detail["receipts"]) == 2
    assert detail["executed_at"] is not None
