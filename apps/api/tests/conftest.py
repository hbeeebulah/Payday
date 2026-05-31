"""Shared pytest fixtures: an isolated in-memory database and HTTP client."""

from __future__ import annotations

import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("ALATPAY_WEBHOOK_SECRET", "")

from collections.abc import AsyncIterator  # noqa: E402

import httpx  # noqa: E402
import pytest_asyncio  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import create_app  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# A single shared in-memory engine for the whole test session.
_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
)
_Session = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app = create_app()

    async def _override_get_db() -> AsyncIterator[AsyncSession]:
        async with _Session() as session:
            yield session

    app.dependency_overrides[get_db] = _override_get_db

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
