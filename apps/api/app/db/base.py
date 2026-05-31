"""Declarative base and shared column mixins for all ORM models."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for every SQLAlchemy model in the project."""


class UUIDPrimaryKeyMixin:
    """Adds a string-encoded UUID primary key.

    A string column is used (rather than a native UUID type) so the schema is
    portable across PostgreSQL and SQLite without dialect-specific handling.
    """

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )


class TimestampMixin:
    """Adds ``created_at`` / ``updated_at`` audit columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
