"""Business model — company metadata for an employer using Payday."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.payroll_run import PayrollRun
    from app.models.payroll_wallet import PayrollWallet


class Business(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A small business / employer account.

    Captures the company metadata required to identify the employer and to
    associate them with their ALATPay merchant profile for disbursements.
    """

    __tablename__ = "businesses"

    # Company metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    legal_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Corporate Affairs Commission (CAC) registration number.
    registration_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # Primary contact
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    address: Mapped[str | None] = mapped_column(String(512), nullable=True)
    country: Mapped[str] = mapped_column(String(2), nullable=False, default="NG")

    # Link to the employer's ALATPay merchant/business profile.
    alatpay_business_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # Relationships
    employees: Mapped[list[Employee]] = relationship(
        back_populates="business",
        cascade="all, delete-orphan",
    )
    payroll_runs: Mapped[list[PayrollRun]] = relationship(
        back_populates="business",
        cascade="all, delete-orphan",
    )
    payroll_wallet: Mapped[PayrollWallet | None] = relationship(
        back_populates="business",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Business id={self.id!r} name={self.name!r}>"
