"""Pydantic v2 schemas for Phase 6 AI Copilot & Evidence-Grounded Reasoning."""

import datetime
import uuid
from typing import Any, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

AIResponseType = Literal[
    "EXPLANATION",
    "SUMMARY",
    "COMPARISON",
    "ROOT_CAUSE",
    "IMPACT",
    "RECOMMENDATION",
    "TIMELINE",
    "UNCERTAINTY",
    "UNKNOWN",
]

AIGroundingStatus = Literal["VERIFIED", "PARTIAL", "FALLBACK"]


class AIChatRequest(BaseModel):
    """Payload to query the AI Copilot regarding an active or historical incident."""

    investigation_id: str = Field(
        ...,
        description="Investigation identifier (e.g. INV-00000000) or linked Risk Case reference (RC-001)",
    )
    message: str = Field(..., min_length=1, max_length=2000, description="Natural language question from operator")
    conversation_id: Optional[str] = Field(
        default=None,
        description="Optional client conversation session UUID for multi-turn conversational context",
    )
    merchant_id: uuid.UUID = Field(
        default_factory=lambda: uuid.UUID("00000000-0000-0000-0000-000000000001"),
        description="Tenant merchant UUID identifier for multi-tenant isolation",
    )
    model_config = ConfigDict(extra="ignore")


class AIResponseAction(BaseModel):
    """Bounded recovery action proposal suggested by the AI Copilot based on verified policy."""

    action: str = Field(..., description="Action type identifier, e.g. PAYMENT_RETRY")
    rationale: str = Field(..., description="Evidence-backed justification for proposing this action")
    expected_impact: str = Field(..., description="Estimated recoverable revenue or risk reduction")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for this recommendation")
    evidence_refs: list[str] = Field(default_factory=list, description="Grounding evidence IDs")
    requires_approval: bool = Field(default=True, description="Strict safety guardrail: always requires merchant approval")
    can_execute: bool = Field(default=False, description="Strict safety guardrail: Phase 6 never directly executes actions")
    recommended_action_payload: Optional[dict[str, Any]] = Field(
        default=None, description="Structured policy bounds for frontend ActionProposalCard"
    )
    model_config = ConfigDict(extra="ignore")


class AIChatResponsePayload(BaseModel):
    """Structured, verified AI Copilot diagnostic answer and grounding metadata."""

    answer: str = Field(..., description="Clear, concise, operational explanation grounded strictly in evidence")
    response_type: AIResponseType = Field(default="EXPLANATION", description="Classified intent response category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0 to 1.0) derived from investigation")
    evidence_refs: list[str] = Field(
        default_factory=list, description="Referenced evidence node IDs backing the statements in the answer"
    )
    recommended_actions: list[AIResponseAction] = Field(
        default_factory=list, description="Bounded recovery proposals if relevant to question"
    )
    warnings: list[str] = Field(
        default_factory=list, description="Operational caveats, uncertainty notes, or safety disclosures"
    )
    can_execute_action: bool = Field(
        default=False, description="Strict flag confirming that execution is disabled in this tier"
    )
    grounding_status: AIGroundingStatus = Field(
        default="VERIFIED", description="Verification state of LLM response against facts"
    )
    model_config = ConfigDict(extra="ignore")


class AIChatResponse(BaseModel):
    """Envelope response returned by the AI Copilot API."""

    conversation_id: str = Field(..., description="Conversation session UUID")
    investigation_id: str = Field(..., description="Linked investigation identifier")
    provider: str = Field(..., description="AI provider used (mock, openai, etc.)")
    model: str = Field(..., description="Model identifier used for reasoning")
    latency_ms: int = Field(..., description="Total round-trip latency in milliseconds")
    response: AIChatResponsePayload = Field(..., description="Structured response payload")
    model_config = ConfigDict(extra="ignore")


class AIExecutiveSummaryResponse(BaseModel):
    """One-click executive briefing generated from verified investigation telemetry."""

    investigation_id: str
    incident_title: str
    impact_summary: str
    root_cause_summary: str
    evidence_summary: list[str]
    confidence_score: float
    recommended_action: str
    requires_approval: bool = True
    generated_at: str
    model_config = ConfigDict(extra="ignore")


class AIStatusResponse(BaseModel):
    """AI Copilot readiness probe response."""

    enabled: bool
    provider: str
    model: str
    mode: Literal["LIVE", "DEMO", "DISABLED"]
    healthy: bool
    model_config = ConfigDict(extra="ignore")
