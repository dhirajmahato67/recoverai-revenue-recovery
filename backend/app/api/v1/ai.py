"""FastAPI router for Phase 6 AI Copilot & Evidence-Grounded Reasoning endpoints."""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.ai import (
    AIChatRequest,
    AIChatResponse,
    AIExecutiveSummaryResponse,
    AIStatusResponse,
)
from app.services.ai.copilot import AICopilotService

router = APIRouter(prefix="/ai", tags=["AI Copilot & Incident Reasoning"])


@router.post(
    "/chat",
    response_model=AIChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Query AI Copilot with Natural Language Question",
    description="Submit an operational question regarding an investigation and receive an evidence-grounded structured explanation.",
)
async def chat_with_copilot(
    request: AIChatRequest,
    db: AsyncSession = Depends(get_db),
) -> AIChatResponse:
    """Execute AI Copilot reasoning over verified incident telemetry."""
    service = AICopilotService(db)
    return await service.chat(request)


@router.get(
    "/investigations/{investigation_id}/summary",
    response_model=AIExecutiveSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get AI Executive Incident Summary",
    description="Generate a one-click structured executive briefing derived from verified telemetry.",
)
async def get_investigation_executive_summary(
    investigation_id: str,
    merchant_id: uuid.UUID = Query(
        default=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        description="Tenant merchant UUID identifier",
    ),
    db: AsyncSession = Depends(get_db),
) -> AIExecutiveSummaryResponse:
    """Generate executive briefing for an investigation."""
    service = AICopilotService(db)
    return await service.get_executive_summary(merchant_id=merchant_id, investigation_id=investigation_id)


@router.get(
    "/status",
    response_model=AIStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get AI Copilot Readiness Status",
    description="Check whether the AI Copilot is enabled, configured provider mode (LIVE or DEMO), and service health.",
)
async def get_ai_status(
    db: AsyncSession = Depends(get_db),
) -> AIStatusResponse:
    """Probe AI Copilot configuration and provider availability."""
    service = AICopilotService(db)
    return service.get_status()
