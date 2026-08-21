"""Recovery plan and batch schemas with bounded execution policies."""

import datetime
import uuid
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class RecoveryPlanRead(BaseModel):
    """Schema for bounded recovery plan proposals."""

    id: uuid.UUID
    merchant_id: uuid.UUID
    risk_case_id: uuid.UUID
    action_type: str
    estimated_recovery: Decimal = Field(examples=[Decimal("210000.00")])
    maximum_exposure: Decimal = Field(examples=[Decimal("210000.00")])
    max_retries: int
    failure_threshold: Decimal
    eligible_transaction_count: int
    status: str
    recommendation: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class RecoveryBatchRead(BaseModel):
    """Schema for recovery execution batches."""

    id: uuid.UUID
    merchant_id: uuid.UUID
    recovery_plan_id: uuid.UUID
    batch_reference: str
    status: str
    total_transactions: int
    eligible_transactions: int
    attempted_transactions: int
    successful_transactions: int
    failed_transactions: int
    skipped_transactions: int
    estimated_recovery: Decimal
    actual_recovery: Decimal
    idempotency_key: str
    started_at: datetime.datetime | None = None
    completed_at: datetime.datetime | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
