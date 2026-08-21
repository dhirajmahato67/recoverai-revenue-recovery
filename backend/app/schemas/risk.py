"""Risk case and signal schemas with exact Decimal financial metrics."""

import datetime
import uuid
from decimal import Decimal
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class RiskSignalRead(BaseModel):
    """Schema for diagnostic risk signals."""

    id: uuid.UUID
    signal_type: str
    metric_name: str
    baseline_value: Decimal | None = None
    observed_value: Decimal | None = None
    deviation_value: Decimal | None = None
    dimension: str | None = None
    dimension_value: str | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class RiskCaseRead(BaseModel):
    """Schema for revenue risk cases."""

    id: uuid.UUID
    merchant_id: uuid.UUID
    case_reference: str
    risk_type: str
    severity: str
    status: str
    title: str
    summary: str
    revenue_at_risk: Decimal = Field(description="Total monetary revenue exposed to risk", examples=[Decimal("840000.00")])
    estimated_recoverable_revenue: Decimal = Field(description="Conservative model recovery forecast", examples=[Decimal("210000.00")])
    confidence_score: Decimal
    detected_at: datetime.datetime
    resolved_at: datetime.datetime | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    signals: list[RiskSignalRead] = []

    model_config = ConfigDict(from_attributes=True)
