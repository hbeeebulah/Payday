"""Initial schema — businesses, employees, payroll runs, transaction receipts

Revision ID: 001
Revises:
Create Date: 2026-06-19

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "businesses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("registration_number", sa.String(length=100), nullable=True),
        sa.Column("tax_id", sa.String(length=100), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=2), nullable=False, server_default="NG"),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("registration_number"),
    )

    op.create_table(
        "employees",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("business_id", sa.UUID(), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("corporate_role", sa.String(length=100), nullable=False),
        sa.Column("salary_amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("salary_currency", sa.String(length=3), nullable=False, server_default="NGN"),
        sa.Column("bank_account_number", sa.String(length=20), nullable=False),
        sa.Column("bank_routing_number", sa.String(length=20), nullable=False),
        sa.Column("bank_name", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_employees_business_id", "employees", ["business_id"])

    payroll_run_status = sa.Enum(
        "draft", "funding", "processing", "completed", "partially_failed", "failed",
        name="payroll_run_status",
    )
    payroll_run_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "payroll_runs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("business_id", sa.UUID(), nullable=False),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cumulative_funding_total", sa.Numeric(precision=16, scale=2), nullable=False, server_default="0"),
        sa.Column("alatpay_batch_reference", sa.String(length=100), nullable=True),
        sa.Column("status", payroll_run_status, nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("alatpay_batch_reference"),
    )
    op.create_index("ix_payroll_runs_business_id", "payroll_runs", ["business_id"])

    distribution_state = sa.Enum(
        "pending", "processing", "completed", "failed",
        name="distribution_state",
    )
    distribution_state.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "transaction_receipts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("payroll_run_id", sa.UUID(), nullable=False),
        sa.Column("employee_id", sa.UUID(), nullable=False),
        sa.Column("alatpay_transaction_ref", sa.String(length=100), nullable=False),
        sa.Column("amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("distribution_state", distribution_state, nullable=False, server_default="pending"),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["payroll_run_id"], ["payroll_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("alatpay_transaction_ref"),
    )
    op.create_index("ix_transaction_receipts_payroll_run_id", "transaction_receipts", ["payroll_run_id"])
    op.create_index("ix_transaction_receipts_employee_id", "transaction_receipts", ["employee_id"])


def downgrade() -> None:
    op.drop_index("ix_transaction_receipts_employee_id", table_name="transaction_receipts")
    op.drop_index("ix_transaction_receipts_payroll_run_id", table_name="transaction_receipts")
    op.drop_table("transaction_receipts")
    op.drop_index("ix_payroll_runs_business_id", table_name="payroll_runs")
    op.drop_table("payroll_runs")
    op.drop_index("ix_employees_business_id", table_name="employees")
    op.drop_table("employees")
    op.drop_table("businesses")
    sa.Enum(name="distribution_state").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="payroll_run_status").drop(op.get_bind(), checkfirst=True)
