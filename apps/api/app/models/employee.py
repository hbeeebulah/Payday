"""Employee model — staff personal details, role, salary and bank details."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import EmployeeStatus

if TYPE_CHECKING:
    from app.models.business import Business
    from app.models.transaction_receipt import TransactionReceipt


class Employee(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A member of staff belonging to a :class:`Business`.

    Stores personal details, the assigned corporate role, the exact salary
    level, and the destination bank account used for disbursement.

    NOTE: bank account numbers are sensitive PII. They are stored here for the
    disbursement flow; in a production deployment these columns should be
    encrypted at rest (e.g. application-level field encryption / KMS) and
    access tightly audited.
    """

    __tablename__ = "employees"
    __table_args__ = (
        Index("ix_employees_business_id_status", "business_id", "status"),
    )

    business_id: Mapped[str] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Personal details
    first_name: Mapped[str] = mapped_column(String(128), nullable=False)
    last_name: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Assigned corporate role / job title
    role: Mapped[str] = mapped_column(String(128), nullable=False)
    department: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # Exact salary level (monthly gross), in the smallest practical precision.
    salary: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="NGN")

    # Bank / payout destination details.
    bank_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    bank_account_number: Mapped[str] = mapped_column(String(32), nullable=False)
    bank_account_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Routing details: in the Nigerian NIP system this is the destination
    # bank code; kept generic to also accommodate routing/sort codes.
    bank_routing_code: Mapped[str] = mapped_column(String(32), nullable=False)

    status: Mapped[EmployeeStatus] = mapped_column(
        SAEnum(EmployeeStatus, name="employee_status"),
        nullable=False,
        default=EmployeeStatus.ACTIVE,
    )

    # Relationships
    business: Mapped[Business] = relationship(back_populates="employees")
    receipts: Mapped[list[TransactionReceipt]] = relationship(
        back_populates="employee",
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Employee id={self.id!r} name={self.full_name!r} role={self.role!r}>"
