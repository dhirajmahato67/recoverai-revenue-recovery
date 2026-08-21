"""Create RecoverAI initial domain schema with 16 domain tables and constraints.

Revision ID: 20260821_0001
Revises: 
Create Date: 2026-08-21 11:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260821_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Merchants
    op.create_table(
        "merchants",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("legal_name", sa.String(length=255), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="INR"),
        sa.Column("timezone", sa.String(length=50), nullable=False, server_default="Asia/Kolkata"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="ACTIVE"),
        sa.Column("external_reference", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_reference", name="uq_merchants_external_reference"),
    )
    op.create_index("ix_merchants_status", "merchants", ["status"])
    op.create_index("ix_merchants_created_at", "merchants", ["created_at"])

    # 2. Users
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("merchant_id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="MERCHANT"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("merchant_id", "email", name="uq_users_merchant_email"),
    )
    op.create_index("ix_users_merchant_role", "users", ["merchant_id", "role"])
    op.create_index("ix_users_merchant_status", "users", ["merchant_id", "status"])

    # 3. Customers
    op.create_table(
        "customers",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("merchant_id", sa.UUID(), nullable=False),
        sa.Column("external_customer_id", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone_last4", sa.String(length=10), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("merchant_id", "external_customer_id", name="uq_customers_merchant_external_id"),
    )
    op.create_index("ix_customers_merchant_email", "customers", ["merchant_id", "email"])
    op.create_index("ix_customers_merchant_status", "customers", ["merchant_id", "status"])

    # 4. Orders
    op.create_table(
        "orders",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("merchant_id", sa.UUID(), nullable=False),
        sa.Column("customer_id", sa.UUID(), nullable=False),
        sa.Column("external_order_id", sa.String(length=255), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="INR"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="CREATED"),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("amount >= 0", name="chk_orders_amount_positive"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("merchant_id", "external_order_id", name="uq_orders_merchant_external_id"),
    )
    op.create_index("ix_orders_merchant_status", "orders", ["merchant_id", "status"])
    op.create_index("ix_orders_merchant_created_at", "orders", ["merchant_id", "created_at"])

    # 5. Payments
    op.create_table(
        "payments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("merchant_id", sa.UUID(), nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("customer_id", sa.UUID(), nullable=False),
        sa.Column("external_payment_id", sa.String(length=255), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="INR"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="CREATED"),
        sa.Column("payment_method", sa.String(length=50), nullable=False),
        sa.Column("bank", sa.String(length=100), nullable=True),
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column("error_reason", sa.String(length=500), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("amount >= 0", name="chk_payments_amount_positive"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("merchant_id", "external_payment_id", name="uq_payments_merchant_external_id"),
    )
    op.create_index("ix_payments_merchant_status", "payments", ["merchant_id", "status"])
    op.create_index("ix_payments_merchant_method", "payments", ["merchant_id", "payment_method"])
    op.create_index("ix_payments_merchant_bank", "payments", ["merchant_id", "bank"])
    op.create_index("ix_payments_merchant_created_at", "payments", ["merchant_id", "created_at"])

    # 6. Payment Events
    op.create_table(
        "payment_events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("merchant_id", sa.UUID(), nullable=False),
        sa.Column("payment_id", sa.UUID(), nullable=True),
        sa.Column("event_id", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("signature_valid", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="RECEIVED"),
        sa.Column("received_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["payment_id"], ["payments.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id", name="uq_payment_events_event_id"),
    )
    op.create_index("ix_payment_events_merchant_event_type", "payment_events", ["merchant_id", "event_type"])
    op.create_index("ix_payment_events_merchant_status", "payment_events", ["merchant_id", "status"])
    op.create_index("ix_payment_events_merchant_received_at", "payment_events", ["merchant_id", "received_at"])

    # 7. Risk Cases
    op.create_table(
        "risk_cases",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("merchant_id", sa.UUID(), nullable=False),
        sa.Column("case_reference", sa.String(length=50), nullable=False),
        sa.Column("risk_type", sa.String(length=100), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False, server_default="MEDIUM"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="OPEN"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("revenue_at_risk", sa.Numeric(precision=18, scale=2), nullable=False, server_default="0.00"),
        sa.Column("estimated_recoverable_revenue", sa.Numeric(precision=18, scale=2), nullable=False, server_default="0.00"),
        sa.Column("confidence_score", sa.Numeric(precision=5, scale=4), nullable=False, server_default="0.9000"),
        sa.Column("detected_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("revenue_at_risk >= 0", name="chk_risk_cases_revenue_at_risk_positive"),
        sa.CheckConstraint("estimated_recoverable_revenue >= 0", name="chk_risk_cases_recoverable_positive"),
        sa.CheckConstraint("confidence_score >= 0 AND confidence_score <= 1", name="chk_risk_cases_confidence_range"),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("merchant_id", "case_reference", name="uq_risk_cases_merchant_reference"),
    )
    op.create_index("ix_risk_cases_merchant_type", "risk_cases", ["merchant_id", "risk_type"])
    op.create_index("ix_risk_cases_merchant_severity", "risk_cases", ["merchant_id", "severity"])
    op.create_index("ix_risk_cases_merchant_status", "risk_cases", ["merchant_id", "status"])
    op.create_index("ix_risk_cases_merchant_detected_at", "risk_cases", ["merchant_id", "detected_at"])

    # 8. Risk Signals
    op.create_table(
        "risk_signals",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("risk_case_id", sa.UUID(), nullable=False),
        sa.Column("signal_type", sa.String(length=100), nullable=False),
        sa.Column("metric_name", sa.String(length=100), nullable=False),
        sa.Column("baseline_value", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("observed_value", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("deviation_value", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("dimension", sa.String(length=100), nullable=True),
        sa.Column("dimension_value", sa.String(length=100), nullable=True),
        sa.Column("evidence", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["risk_case_id"], ["risk_cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_risk_signals_case_metric", "risk_signals", ["risk_case_id", "metric_name"])
    op.create_index("ix_risk_signals_case_type", "risk_signals", ["risk_case_id", "signal_type"])

    # 9. Investigations
    op.create_table(
        "investigations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("risk_case_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="PENDING"),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("root_cause", sa.Text(), nullable=False),
        sa.Column("confidence_score", sa.Numeric(precision=5, scale=4), nullable=False, server_default="0.9000"),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("confidence_score >= 0 AND confidence_score <= 1", name="chk_investigations_confidence_range"),
        sa.ForeignKeyConstraint(["risk_case_id"], ["risk_cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_investigations_case_status", "investigations", ["risk_case_id", "status"])

    # 10. Recovery Plans
    op.create_table(
        "recovery_plans",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("merchant_id", sa.UUID(), nullable=False),
        sa.Column("risk_case_id", sa.UUID(), nullable=False),
        sa.Column("action_type", sa.String(length=100), nullable=False),
        sa.Column("estimated_recovery", sa.Numeric(precision=18, scale=2), nullable=False, server_default="0.00"),
        sa.Column("maximum_exposure", sa.Numeric(precision=18, scale=2), nullable=False, server_default="0.00"),
        sa.Column("max_retries", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("failure_threshold", sa.Numeric(precision=5, scale=4), nullable=False, server_default="0.3000"),
        sa.Column("eligible_transaction_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="DRAFT"),
        sa.Column("recommendation", sa.Text(), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("estimated_recovery >= 0", name="chk_recovery_plans_estimated_positive"),
        sa.CheckConstraint("maximum_exposure >= 0", name="chk_recovery_plans_exposure_positive"),
        sa.CheckConstraint("max_retries >= 0", name="chk_recovery_plans_retries_positive"),
        sa.CheckConstraint("failure_threshold >= 0 AND failure_threshold <= 1", name="chk_recovery_plans_threshold_range"),
        sa.CheckConstraint("eligible_transaction_count >= 0", name="chk_recovery_plans_eligible_positive"),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["risk_case_id"], ["risk_cases.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_recovery_plans_merchant_status", "recovery_plans", ["merchant_id", "status"])

    # 11. Recovery Batches
    op.create_table(
        "recovery_batches",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("merchant_id", sa.UUID(), nullable=False),
        sa.Column("recovery_plan_id", sa.UUID(), nullable=False),
        sa.Column("batch_reference", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="CREATED"),
        sa.Column("total_transactions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("eligible_transactions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("attempted_transactions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("successful_transactions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_transactions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("skipped_transactions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("estimated_recovery", sa.Numeric(precision=18, scale=2), nullable=False, server_default="0.00"),
        sa.Column("actual_recovery", sa.Numeric(precision=18, scale=2), nullable=False, server_default="0.00"),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("total_transactions >= 0", name="chk_recovery_batches_total_positive"),
        sa.CheckConstraint("eligible_transactions >= 0", name="chk_recovery_batches_eligible_positive"),
        sa.CheckConstraint("attempted_transactions >= 0", name="chk_recovery_batches_attempted_positive"),
        sa.CheckConstraint("successful_transactions >= 0", name="chk_recovery_batches_successful_positive"),
        sa.CheckConstraint("failed_transactions >= 0", name="chk_recovery_batches_failed_positive"),
        sa.CheckConstraint("skipped_transactions >= 0", name="chk_recovery_batches_skipped_positive"),
        sa.CheckConstraint("estimated_recovery >= 0", name="chk_recovery_batches_estimated_positive"),
        sa.CheckConstraint("actual_recovery >= 0", name="chk_recovery_batches_actual_positive"),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["recovery_plan_id"], ["recovery_plans.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key", name="uq_recovery_batches_idempotency_key"),
        sa.UniqueConstraint("merchant_id", "batch_reference", name="uq_recovery_batches_merchant_reference"),
    )
    op.create_index("ix_recovery_batches_merchant_status", "recovery_batches", ["merchant_id", "status"])
    op.create_index("ix_recovery_batches_merchant_created_at", "recovery_batches", ["merchant_id", "created_at"])

    # 12. Recovery Attempts
    op.create_table(
        "recovery_attempts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("merchant_id", sa.UUID(), nullable=False),
        sa.Column("recovery_batch_id", sa.UUID(), nullable=False),
        sa.Column("payment_id", sa.UUID(), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="PENDING"),
        sa.Column("amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("external_reference", sa.String(length=255), nullable=True),
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column("error_reason", sa.String(length=500), nullable=True),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("attempt_number > 0", name="chk_recovery_attempts_number_positive"),
        sa.CheckConstraint("amount >= 0", name="chk_recovery_attempts_amount_positive"),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["payment_id"], ["payments.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["recovery_batch_id"], ["recovery_batches.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("recovery_batch_id", "payment_id", "attempt_number", name="uq_recovery_attempts_batch_payment_attempt"),
    )
    op.create_index("ix_recovery_attempts_merchant_status", "recovery_attempts", ["merchant_id", "status"])

    # 13. Approvals
    op.create_table(
        "approvals",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("merchant_id", sa.UUID(), nullable=False),
        sa.Column("recovery_plan_id", sa.UUID(), nullable=False),
        sa.Column("requested_by", sa.UUID(), nullable=True),
        sa.Column("approved_by", sa.UUID(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="PENDING"),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["recovery_plan_id"], ["recovery_plans.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_approvals_merchant_status", "approvals", ["merchant_id", "status"])

    # 14. Audit Logs
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("merchant_id", sa.UUID(), nullable=False),
        sa.Column("actor_type", sa.String(length=50), nullable=False),
        sa.Column("actor_id", sa.String(length=255), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=False),
        sa.Column("resource_id", sa.String(length=255), nullable=False),
        sa.Column("request_id", sa.String(length=255), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_merchant_action", "audit_logs", ["merchant_id", "action"])
    op.create_index("ix_audit_logs_merchant_resource", "audit_logs", ["merchant_id", "resource_type", "resource_id"])
    op.create_index("ix_audit_logs_merchant_created_at", "audit_logs", ["merchant_id", "created_at"])

    # 15. Agent Runs
    op.create_table(
        "agent_runs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("merchant_id", sa.UUID(), nullable=False),
        sa.Column("risk_case_id", sa.UUID(), nullable=True),
        sa.Column("model", sa.String(length=100), nullable=False, server_default="gemini-2.0-flash"),
        sa.Column("prompt_version", sa.String(length=50), nullable=False, server_default="v1.0"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="STARTED"),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["risk_case_id"], ["risk_cases.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_runs_merchant_status", "agent_runs", ["merchant_id", "status"])

    # 16. Agent Tool Calls
    op.create_table(
        "agent_tool_calls",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("agent_run_id", sa.UUID(), nullable=False),
        sa.Column("tool_name", sa.String(length=100), nullable=False),
        sa.Column("arguments", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("result", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="STARTED"),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["agent_run_id"], ["agent_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_tool_calls_run_tool", "agent_tool_calls", ["agent_run_id", "tool_name"])


def downgrade() -> None:
    op.drop_table("agent_tool_calls")
    op.drop_table("agent_runs")
    op.drop_table("audit_logs")
    op.drop_table("approvals")
    op.drop_table("recovery_attempts")
    op.drop_table("recovery_batches")
    op.drop_table("recovery_plans")
    op.drop_table("investigations")
    op.drop_table("risk_signals")
    op.drop_table("risk_cases")
    op.drop_table("payment_events")
    op.drop_table("payments")
    op.drop_table("orders")
    op.drop_table("customers")
    op.drop_table("users")
    op.drop_table("merchants")
