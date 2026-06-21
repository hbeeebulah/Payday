"""PayrollWallet model — a business's dedicated ALATPay static wallet.

Each onboarded business is provisioned exactly one Payroll Wallet (a static
ALATPay account) that funds its salary disbursements. The locally cached
``available_balance`` is the value checked for overdraft protection before a
bulk transfer is allowed to run.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import WalletStatus

if TYPE_CHECKING:
    from app.models.business import Business


class PayrollWallet(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A 1:1 dedicated wallet for a business."""

    __tablename__ = "payroll_wallets"

    business_id: Mapped[str] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    label: Mapped[str] = mapped_column(String(64), nullable=False, default="Payroll Wallet")

    # ALATPay static-account identifiers.
    alatpay_wallet_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    wallet_type: Mapped[int] = mapped_column(nullable=False, default=2)

    account_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    account_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bank_name: Mapped[str | None] = mapped_column(String(128), nullable=True, default="Wema Bank")

    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="NGN")
    # Locally cached balance, refreshed from ALATPay. Used for overdraft checks.
    available_balance: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, default=Decimal("0.00")
    )

    status: Mapped[WalletStatus] = mapped_column(
        SAEnum(WalletStatus, name="wallet_status"),
        nullable=False,
        default=WalletStatus.PENDING,
    )

    # Tracking id returned during OTP-gated (individual) wallet creation.
    otp_tracking_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    business: Mapped[Business] = relationship(back_populates="payroll_wallet")

    @property
    def is_active(self) -> bool:
        return self.status == WalletStatus.ACTIVE

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return (
            f"<PayrollWallet business_id={self.business_id!r} "
            f"account={self.account_number!r} balance={self.available_balance!r}>"
        )
