"""Auth endpoint tests."""

from __future__ import annotations

import httpx
import pytest


@pytest.mark.asyncio
async def test_register_and_login(client: httpx.AsyncClient) -> None:
    register = await client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Ada",
            "last_name": "Okafor",
            "role": "staff",
            "phone": "+2348000000001",
            "email": "ada@example.com",
            "password": "securepass1",
            "confirm_password": "securepass1",
        },
    )
    assert register.status_code == 201
    body = register.json()
    assert body["access_token"]
    assert body["user"]["email"] == "ada@example.com"
    assert body["user"]["role"] == "staff"

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "ada@example.com", "password": "securepass1"},
    )
    assert login.status_code == 200
    assert login.json()["user"]["first_name"] == "Ada"

    me = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["last_name"] == "Okafor"


@pytest.mark.asyncio
async def test_register_rejects_duplicate_email(client: httpx.AsyncClient) -> None:
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "role": "employer",
        "phone": "+2348000000002",
        "email": "john@example.com",
        "password": "securepass1",
        "confirm_password": "securepass1",
    }
    assert (await client.post("/api/v1/auth/register", json=payload)).status_code == 201
    dup = await client.post("/api/v1/auth/register", json=payload)
    assert dup.status_code == 409


@pytest.mark.asyncio
async def test_login_rejects_invalid_password(client: httpx.AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Jane",
            "last_name": "Smith",
            "role": "employer",
            "phone": "+2348000000003",
            "email": "jane@example.com",
            "password": "securepass1",
            "confirm_password": "securepass1",
        },
    )
    bad = await client.post(
        "/api/v1/auth/login",
        json={"email": "jane@example.com", "password": "wrongpassword"},
    )
    assert bad.status_code == 401


@pytest.mark.asyncio
async def test_employer_can_lookup_registered_staff(client: httpx.AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Chi",
            "last_name": "Okonkwo",
            "role": "staff",
            "phone": "+2348000000010",
            "email": "chi@example.com",
            "password": "securepass1",
            "confirm_password": "securepass1",
        },
    )
    employer = await client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Boss",
            "last_name": "Owner",
            "role": "employer",
            "phone": "+2348000000011",
            "email": "boss@example.com",
            "password": "securepass1",
            "confirm_password": "securepass1",
        },
    )
    token = employer.json()["access_token"]

    found = await client.post(
        "/api/v1/auth/staff/lookup",
        json={"email": "chi@example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert found.status_code == 200
    body = found.json()
    assert body["found"] is True
    assert body["user"]["first_name"] == "Chi"

    missing = await client.post(
        "/api/v1/auth/staff/lookup",
        json={"email": "nobody@example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert missing.status_code == 200
    assert missing.json()["found"] is False
