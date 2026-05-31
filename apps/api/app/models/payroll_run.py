"""PayrollRun model — a single batch execution of salary payments."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import PayrollRunStatus

if TYPE_CHECKING:
    from app.models.business import Business
    from app.models.transaction_receipt import TransactionReceipt


class PayrollRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One "pay everyone" execution for a business.

    Permanently logs the execution timestamp and the cumulative funding total
    for the batch. Per-employee payout detail lives in :class:`TransactionReceipt`.
    """

    __tablename__ = "payroll_runs"

    business_id: Mapped[str] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Human-readable label for the period being paid, e.g. "2026-05" or "May 2026".
    period_label: Mapped[str] = mapped_column(String(64), nullable=False)

    status: Mapped[PayrollRunStatus] = mapped_column(
        SAEnum(PayrollRunStatus, name="payroll_run_status"),
        nullable=False,
        default=PayrollRunStatus.DRAFT,
    )

    # Cumulative funding total required/used for this run (sum of all payouts).
    total_funding_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, default=Decimal("0.00")
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="NGN")
    employee_count: Mapped[int] = mapped_column(nullable=False, default=0)

    # Execution timestamp — set when the run is actually fired off to ALATPay.
    executed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Top-level ALATPay funding/batch reference for the wallet funding step.
    alatpay_funding_reference: Mapped[str | None] = mapped_column(
        String(128), nullable=True, unique=True
    )

    # Relationships
    business: Mapped[Business] = relationship(back_populates="payroll_runs")
    receipts: Mapped[list[TransactionReceipt]] = relationship(
        back_populates="payroll_run",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return (
            f"<PayrollRun id={self.id!r} period={self.period_label!r} "
            f"status={self.status.value!r}>"
        )
