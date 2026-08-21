"""Database models registry exporting all SQLAlchemy 2.0 domain models for Alembic."""

from app.db.models.merchant import Merchant
from app.db.models.user import User
from app.db.models.customer import Customer
from app.db.models.order import Order
from app.db.models.payment import Payment
from app.db.models.payment_event import PaymentEvent
from app.db.models.risk_case import RiskCase
from app.db.models.risk_signal import RiskSignal
from app.db.models.investigation import Investigation
from app.db.models.recovery_plan import RecoveryPlan
from app.db.models.recovery_batch import RecoveryBatch
from app.db.models.recovery_attempt import RecoveryAttempt
from app.db.models.approval import Approval
from app.db.models.audit_log import AuditLog
from app.db.models.agent_run import AgentRun
from app.db.models.agent_tool_call import AgentToolCall

__all__ = [
    "Merchant",
    "User",
    "Customer",
    "Order",
    "Payment",
    "PaymentEvent",
    "RiskCase",
    "RiskSignal",
    "Investigation",
    "RecoveryPlan",
    "RecoveryBatch",
    "RecoveryAttempt",
    "Approval",
    "AuditLog",
    "AgentRun",
    "AgentToolCall",
]
