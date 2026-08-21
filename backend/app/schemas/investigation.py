"""Pydantic v2 schemas for Investigation Intelligence and Root-Cause Analysis."""

import datetime
import uuid
from decimal import Decimal
from typing import Any, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.risk_engine import EvidenceNodeSchema, RecommendedActionSchema, RootCauseTreeNodeSchema

InvestigationStatusType = Literal["PENDING", "RUNNING", "COMPLETED", "FAILED"]


class InvestigationCreateRequest(BaseModel):
    """Payload to initiate or retrieve a diagnostic investigation for a risk case."""

    risk_case_id: str = Field(..., description="UUID or case reference (e.g. RC-001)")
    merchant_id: uuid.UUID = Field(
        default_factory=lambda: uuid.UUID("00000000-0000-0000-0000-000000000001"),
        description="Tenant merchant UUID identifier",
    )
    force_reanalyze: bool = Field(default=False, description="Re-run analysis if already completed")
    model_config = ConfigDict(extra="ignore")


class InvestigationStepSchema(BaseModel):
    """Checklist item representing an automated sub-agent analysis stage."""

    id: str
    title: str
    description: str
    status: Literal["COMPLETED", "IN_PROGRESS", "PENDING", "FAILED"]
    durationMs: int
    timestamp: str
    model_config = ConfigDict(extra="ignore")


class ToolExecutionSchema(BaseModel):
    """Execution trace of a sub-agent diagnostic tool invoked during investigation."""

    id: str
    toolName: str
    status: Literal["COMPLETED", "RUNNING", "FAILED"]
    durationMs: int
    timestamp: str
    resultSummary: str
    confidenceScore: Optional[int] = None
    inputPayload: dict[str, Any] = Field(default_factory=dict)
    outputPayload: dict[str, Any] = Field(default_factory=dict)
    model_config = ConfigDict(extra="ignore")


class EvidenceItemSchema(BaseModel):
    """Standardized evidence unit representation."""

    evidence_id: str
    type: str  # PAYMENT_METHOD_DEGRADATION, BANK_CONCENTRATION, ERROR_CODE_SPIKE, etc.
    source: str
    metric: str
    observed_value: float
    baseline_value: float
    delta: float
    unit: str
    confidence: float
    timestamp: str
    details: dict[str, Any] = Field(default_factory=dict)
    model_config = ConfigDict(extra="ignore")


class RootCauseCandidateSchema(BaseModel):
    """Ranked candidate root cause hypothesis."""

    rank: int
    cause: str
    score: float  # 0.0 to 1.0
    confidence: Literal["LOW", "MEDIUM", "HIGH", "VERY_HIGH"]
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    supporting_evidence: list[str]
    contradicting_evidence: list[str] = Field(default_factory=list)
    model_config = ConfigDict(extra="ignore")


class IncidentTimelineEventSchema(BaseModel):
    """Chronological milestone in incident evolution."""

    timestamp: str
    event_type: str
    severity: str
    title: str
    description: str
    evidence_ids: list[str] = Field(default_factory=list)
    model_config = ConfigDict(extra="ignore")


class BusinessImpactSchema(BaseModel):
    """Quantified financial and operational impact summary."""

    total_window_transactions: int
    affected_transactions_count: int
    failed_transactions_count: int
    overall_success_rate: float
    baseline_success_rate: float
    success_rate_delta_percentage_points: float
    revenue_at_risk_inr: Decimal
    recoverable_revenue_inr: Decimal
    primary_affected_payment_method: str
    primary_affected_bank: str
    primary_error_code: str
    model_config = ConfigDict(extra="ignore")


class InvestigationDetailResponse(BaseModel):
    """Complete investigation diagnostic response matching frontend Investigation interface."""

    id: str  # e.g. INV-001 or UUID
    caseId: str  # e.g. RC-001
    caseTitle: str
    question: str
    status: InvestigationStatusType
    steps: list[InvestigationStepSchema]
    finding: str
    evidenceBullets: list[str]
    conclusion: str
    confidenceScore: int  # 0 - 100
    createdAt: str
    completedAt: Optional[str] = None
    toolExecutions: list[ToolExecutionSchema]
    recommendedRecovery: RecommendedActionSchema
    evidence: list[EvidenceNodeSchema] = Field(default_factory=list)
    rootCauseTree: list[RootCauseTreeNodeSchema] = Field(default_factory=list)
    candidates: list[RootCauseCandidateSchema] = Field(default_factory=list)
    timeline: list[IncidentTimelineEventSchema] = Field(default_factory=list)
    impact: Optional[BusinessImpactSchema] = None
    model_config = ConfigDict(extra="ignore")


class InvestigationSummaryResponse(BaseModel):
    """Lightweight investigation summary card."""

    id: str
    caseId: str
    status: InvestigationStatusType
    root_cause: str
    finding: str
    confidence_score: int
    revenue_at_risk: Decimal
    recoverable_revenue: Decimal
    affected_method: str
    affected_bank: str
    dominant_error: str
    started_at: str
    completed_at: Optional[str] = None
    model_config = ConfigDict(extra="ignore")


class InvestigationListResponse(BaseModel):
    """Paginated collection of investigations."""

    items: list[InvestigationSummaryResponse]
    total: int
    model_config = ConfigDict(extra="ignore")
