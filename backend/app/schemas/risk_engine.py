"""Pydantic schemas for the Risk Detection Engine, rules, signals, and cases."""

import datetime
import uuid
from decimal import Decimal
from typing import Any, Literal, Optional, List
from pydantic import BaseModel, ConfigDict, Field

RiskSeverity = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
RiskStatus = Literal[
    "OPEN",
    "INVESTIGATING",
    "RECOVERY_PLANNED",
    "RECOVERING",
    "RESOLVED",
    "DISMISSED",
]
RiskType = Literal[
    "PAYMENT_DEGRADATION",
    "CHECKOUT_ABANDONMENT",
    "SUBSCRIPTION_FAILURES",
    "GATEWAY_LATENCY",
    "BANK_DOWNTIME",
]


class EvidenceNodeSchema(BaseModel):
    """Structured evidence node for frontend tree visualization."""

    label: str
    baseline_value: str
    current_value: str
    delta: str
    is_negative: bool
    metric_type: Literal["percentage", "amount", "latency", "count"]
    model_config = ConfigDict(extra="ignore")


class RecommendedActionSchema(BaseModel):
    """Prescriptive recovery strategy recommendation."""

    action_type: str
    eligible_transactions: int
    expected_recovery_min: float
    expected_recovery_max: float
    max_exposure: float
    retry_limit: int
    stopping_condition: str
    stopping_threshold_percent: float
    model_config = ConfigDict(extra="ignore")


class RootCauseTreeNodeSchema(BaseModel):
    """Recursive node structure for UI root-cause tree visualization."""

    id: str
    label: str
    subtext: Optional[str] = None
    status: Literal["normal", "warning", "critical"] = "normal"
    children: Optional[list["RootCauseTreeNodeSchema"]] = None
    model_config = ConfigDict(extra="ignore")


RootCauseTreeNodeSchema.model_rebuild()


class RiskSignalCreate(BaseModel):
    """Schema for creating a deterministic telemetry risk signal."""

    signal_type: str
    metric_name: str
    baseline_value: Decimal | None = None
    observed_value: Decimal | None = None
    deviation_value: Decimal | None = None
    dimension: str | None = None
    dimension_value: str | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)
    severity: RiskSeverity = "MEDIUM"
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    model_config = ConfigDict(extra="ignore")


class RiskSignalResponse(BaseModel):
    """Response representation of a persisted RiskSignal."""

    id: uuid.UUID
    risk_case_id: uuid.UUID
    signal_type: str
    metric_name: str
    baseline_value: float | None
    observed_value: float | None
    deviation_value: float | None
    dimension: str | None
    dimension_value: str | None
    evidence: dict[str, Any]
    created_at: datetime.datetime
    model_config = ConfigDict(extra="ignore")


class RiskCaseResponse(BaseModel):
    """Comprehensive RiskCase response matching domain model and frontend components."""

    id: str
    merchant_id: str
    case_reference: str
    risk_type: str
    severity: RiskSeverity
    status: str
    title: str
    summary: str
    root_cause: str
    revenue_at_risk: float
    recoverable_revenue: float
    confidence_score: float
    affected_transactions_count: int
    detected_at: str
    resolved_at: str | None = None
    payment_method: str | None = None
    bank: str | None = None
    signals: list[RiskSignalResponse] = Field(default_factory=list)
    evidence_nodes: list[EvidenceNodeSchema] = Field(default_factory=list)
    recommended_action: RecommendedActionSchema | None = None
    model_config = ConfigDict(extra="ignore")


class RiskAnalysisRequest(BaseModel):
    """Trigger on-demand or automated risk detection evaluation for a merchant."""

    merchant_id: uuid.UUID
    current_window_minutes: int = Field(default=120, ge=5, le=10080, description="Evaluation window in minutes (default 2h)")
    baseline_window_minutes: int = Field(default=1440, ge=60, le=43200, description="Baseline historical comparison window in minutes (default 24h)")
    dry_run: bool = Field(default=False, description="If True, do not persist detected risk cases or signals")
    model_config = ConfigDict(extra="ignore")


class RiskAnalysisResponse(BaseModel):
    """Summary of risk detection engine execution."""

    merchant_id: uuid.UUID
    evaluated_at: datetime.datetime
    current_window_transactions: int
    baseline_window_transactions: int
    current_success_rate: float
    baseline_success_rate: float
    success_rate_delta: float
    signals_detected_count: int
    signals: list[RiskSignalCreate]
    composite_risk_score: float
    severity: RiskSeverity
    risk_case_created: bool
    risk_case_id: uuid.UUID | None = None
    case_reference: str | None = None
    revenue_at_risk: float
    recoverable_revenue: float
    duration_ms: float
    model_config = ConfigDict(extra="ignore")


class RiskMetricsResponse(BaseModel):
    """Aggregate risk telemetry and health indicators."""

    merchant_id: uuid.UUID
    active_cases_count: int
    high_priority_cases_count: int
    total_revenue_at_risk: float
    total_recoverable_revenue: float
    overall_health_score: float
    system_status: Literal["HEALTHY", "DEGRADED", "CRITICAL"]
    model_config = ConfigDict(extra="ignore")
