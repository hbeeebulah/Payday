"""TransactionReceipt model — an immutable log of one employee payout."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import DistributionState

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.payroll_run import PayrollRun


class TransactionReceipt(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A permanent record of a single salary payout to a single employee.

    One row is created per employee per :class:`PayrollRun`. It stores the
    unique ALATPay transaction reference and the specific distribution state of
    that payout, providing a clean digital record of every salary ever paid.
    """

    __tablename__ = "transaction_receipts"

    payroll_run_id: Mapped[str] = mapped_column(
        ForeignKey("payroll_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[str] = mapped_column(
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Amount actually disbursed for this payout.
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="NGN")

    # Specific distribution state of this individual payout.
    distribution_state: Mapped[DistributionState] = mapped_column(
        SAEnum(DistributionState, name="distribution_state"),
        nullable=False,
        default=DistributionState.PENDING,
        index=True,
    )

    # Unique ALATPay transaction reference for this payout. Unique constraint
    # guarantees idempotency when reconciling webhook callbacks.
    alatpay_transaction_reference: Mapped[str | None] = mapped_column(
        String(128), nullable=True, unique=True, index=True
    )

    # Snapshot of the destination bank details at the time of payout, so the
    # receipt remains accurate even if the employee record later changes.
    bank_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    bank_account_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    bank_routing_code: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Execution timestamp for this individual payout + failure diagnostics.
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    payroll_run: Mapped[PayrollRun] = relationship(back_populates="receipts")
    employee: Mapped[Employee] = relationship(back_populates="receipts")

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return (
            f"<TransactionReceipt id={self.id!r} "
            f"ref={self.alatpay_transaction_reference!r} "
            f"state={self.distribution_state.value!r}>"
        )
