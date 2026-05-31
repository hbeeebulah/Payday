"""Enumerations describing lifecycle states across the payroll domain."""

from __future__ import annotations

import enum


class EmployeeStatus(str, enum.Enum):
    """Whether an employee is included in payroll runs."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class PayrollRunStatus(str, enum.Enum):
    """Lifecycle of a whole payroll run (the batch)."""

    DRAFT = "draft"            # created, not yet funded/executed
    FUNDING = "funding"        # awaiting confirmation that the wallet is funded
    PROCESSING = "processing"  # disbursements are being pushed to ALATPay
    COMPLETED = "completed"    # every payout reached a terminal state successfully
    PARTIALLY_COMPLETED = "partially_completed"  # some payouts failed
    FAILED = "failed"          # the run could not be executed
    CANCELLED = "cancelled"


class DistributionState(str, enum.Enum):
    """Distribution state of a single employee payout.

    Mirrors the lifecycle reported by ALATPay for an individual transfer.
    """

    PENDING = "pending"        # queued, not yet sent
    PROCESSING = "processing"  # submitted to ALATPay, awaiting result
    SUCCESSFUL = "successful"  # funds delivered to the employee ("paid")
    FAILED = "failed"          # transfer rejected/failed
    REVERSED = "reversed"      # transfer reversed after the fact


class WalletStatus(str, enum.Enum):
    """Provisioning state of a business's dedicated Payroll Wallet."""

    PENDING = "pending"        # creation initiated, awaiting activation/OTP
    ACTIVE = "active"          # provisioned and usable
    FAILED = "failed"          # provisioning failed
