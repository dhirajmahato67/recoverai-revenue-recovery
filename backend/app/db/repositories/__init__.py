"""Repositories registry exporting all domain data-access repositories."""

from app.db.repositories.base import BaseRepository
from app.db.repositories.merchant import MerchantRepository
from app.db.repositories.customer import CustomerRepository
from app.db.repositories.order import OrderRepository
from app.db.repositories.payment import PaymentRepository
from app.db.repositories.payment_event import PaymentEventRepository
from app.db.repositories.risk_case import RiskCaseRepository
from app.db.repositories.risk_signal import RiskSignalRepository
from app.db.repositories.investigation import InvestigationRepository
from app.db.repositories.recovery_plan import RecoveryPlanRepository
from app.db.repositories.recovery_batch import RecoveryBatchRepository
from app.db.repositories.audit_log import AuditLogRepository

__all__ = [
    "BaseRepository",
    "MerchantRepository",
    "CustomerRepository",
    "OrderRepository",
    "PaymentRepository",
    "PaymentEventRepository",
    "RiskCaseRepository",
    "RiskSignalRepository",
    "InvestigationRepository",
    "RecoveryPlanRepository",
    "RecoveryBatchRepository",
    "AuditLogRepository",
]
