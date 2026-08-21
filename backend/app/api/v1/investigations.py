"""FastAPI router for Investigation Intelligence and Diagnostic Root-Cause Analysis."""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import AppException
from app.db.models import Investigation, RiskCase
from app.db.repositories.investigation import InvestigationRepository
from app.db.session import get_db
from app.schemas.investigation import (
    BusinessImpactSchema,
    EvidenceItemSchema,
    IncidentTimelineEventSchema,
    InvestigationCreateRequest,
    InvestigationDetailResponse,
    InvestigationListResponse,
    InvestigationSummaryResponse,
    RootCauseCandidateSchema,
)
from app.schemas.risk_engine import EvidenceNodeSchema, RootCauseTreeNodeSchema
from app.services.investigation.orchestrator import InvestigationOrchestrator

router = APIRouter(prefix="/investigations", tags=["Investigations"])


@router.post(
    "",
    response_model=InvestigationDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Initiate Diagnostic Investigation",
    description="Trigger an automated diagnostic investigation for a risk case or retrieve existing findings idempotently.",
)
async def create_or_run_investigation(
    payload: InvestigationCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> InvestigationDetailResponse:
    """Create or retrieve investigation findings for a risk case."""
    orchestrator = InvestigationOrchestrator(db)
    req_id = getattr(request.state, "request_id", None)
    return await orchestrator.run_investigation(
        merchant_id=payload.merchant_id,
        risk_case_id=payload.risk_case_id,
        force_reanalyze=payload.force_reanalyze,
        request_id=req_id,
    )


@router.get(
    "",
    response_model=InvestigationListResponse,
    summary="List Investigations",
    description="Retrieve all diagnostic investigations for a merchant.",
)
async def list_investigations(
    merchant_id: uuid.UUID = Query(uuid.UUID("00000000-0000-0000-0000-000000000001")),
    limit: int = Query(50, ge=1, le=100),
    page: int = Query(1, ge=1),
    db: AsyncSession = Depends(get_db),
) -> InvestigationListResponse:
    """List tenant investigations with pagination."""
    skip = (page - 1) * limit
    repo = InvestigationRepository(db)

    items_db = await repo.list_for_merchant(merchant_id=merchant_id, limit=limit, skip=skip)
    total = await repo.count_for_merchant(merchant_id=merchant_id)

    summaries: list[InvestigationSummaryResponse] = []
    for inv in items_db:
        case = inv.risk_case
        display_id = f"INV-{str(inv.id)[:8].upper()}"
        case_id_str = case.case_reference if case else "RC-001"
        conf_int = int(float(inv.confidence_score) * 100) if inv.confidence_score else 90

        summaries.append(
            InvestigationSummaryResponse(
                id=display_id,
                caseId=case_id_str,
                status=inv.status,  # type: ignore
                root_cause=inv.root_cause or "Pending diagnostic synthesis",
                finding=inv.summary or "Diagnostic investigation in progress",
                confidence_score=conf_int,
                revenue_at_risk=case.revenue_at_risk if case else 0.0,
                recoverable_revenue=case.estimated_recoverable_revenue if case else 0.0,
                affected_method="UPI",
                affected_bank="HDFC",
                dominant_error="GATEWAY_TIMEOUT",
                started_at=inv.started_at.isoformat() if inv.started_at else "",
                completed_at=inv.completed_at.isoformat() if inv.completed_at else None,
            )
        )

    return InvestigationListResponse(items=summaries, total=total)


@router.get(
    "/{investigation_id}",
    response_model=InvestigationDetailResponse,
    summary="Get Investigation Details",
    description="Retrieve comprehensive diagnostic investigation results including checklist, structured reasoning, timeline, and tool call traces.",
)
async def get_investigation_details(
    investigation_id: str,
    merchant_id: uuid.UUID = Query(uuid.UUID("00000000-0000-0000-0000-000000000001")),
    db: AsyncSession = Depends(get_db),
) -> InvestigationDetailResponse:
    """Retrieve full investigation details for a case or investigation ID."""
    orchestrator = InvestigationOrchestrator(db)

    # 1. Try finding direct RiskCase
    case_stmt = select(RiskCase).where(
        RiskCase.merchant_id == merchant_id,
        or_(
            RiskCase.case_reference.ilike(investigation_id),
            RiskCase.case_reference.ilike(investigation_id.replace("INV-", "RC-")),
        ),
    )
    case_res = (await db.execute(case_stmt)).scalars().first()
    if case_res:
        return await orchestrator.run_investigation(
            merchant_id=merchant_id,
            risk_case_id=case_res.case_reference,
            force_reanalyze=False,
        )

    # 2. Try finding Investigation by UUID or display prefix (e.g. INV-FE830C9E)
    clean_id = investigation_id.upper().replace("INV-", "").replace("-", "")
    inv_stmt = (
        select(Investigation)
        .join(RiskCase, Investigation.risk_case_id == RiskCase.id)
        .where(RiskCase.merchant_id == merchant_id)
        .options(selectinload(Investigation.risk_case))
    )
    all_invs = (await db.execute(inv_stmt)).scalars().all()
    for inv in all_invs:
        inv_hex = str(inv.id).replace("-", "").upper()
        if inv_hex.startswith(clean_id) or str(inv.id).lower() == investigation_id.lower():
            if inv.risk_case:
                return await orchestrator.run_investigation(
                    merchant_id=merchant_id,
                    risk_case_id=inv.risk_case.case_reference,
                    force_reanalyze=False,
                )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Investigation '{investigation_id}' not found.",
    )


@router.post(
    "/{investigation_id}/run",
    response_model=InvestigationDetailResponse,
    summary="Re-run Diagnostic Investigation",
)
async def rerun_investigation(
    investigation_id: str,
    merchant_id: uuid.UUID = Query(uuid.UUID("00000000-0000-0000-0000-000000000001")),
    request: Request = None,  # type: ignore
    db: AsyncSession = Depends(get_db),
) -> InvestigationDetailResponse:
    """Force re-run diagnostic investigation."""
    orchestrator = InvestigationOrchestrator(db)
    req_id = getattr(request.state, "request_id", None) if request else None
    case_ref = investigation_id.replace("INV-", "RC-") if investigation_id.startswith("INV-") else investigation_id

    return await orchestrator.run_investigation(
        merchant_id=merchant_id,
        risk_case_id=case_ref,
        force_reanalyze=True,
        request_id=req_id,
    )


@router.get(
    "/{investigation_id}/evidence",
    response_model=list[EvidenceNodeSchema],
    summary="Get Investigation Evidence Nodes",
)
async def get_investigation_evidence(
    investigation_id: str,
    merchant_id: uuid.UUID = Query(uuid.UUID("00000000-0000-0000-0000-000000000001")),
    db: AsyncSession = Depends(get_db),
) -> list[EvidenceNodeSchema]:
    """Retrieve evidence nodes for frontend card displays."""
    detail = await get_investigation_details(investigation_id=investigation_id, merchant_id=merchant_id, db=db)
    return detail.evidence


@router.get(
    "/{investigation_id}/timeline",
    response_model=list[IncidentTimelineEventSchema],
    summary="Get Incident Timeline",
)
async def get_investigation_timeline(
    investigation_id: str,
    merchant_id: uuid.UUID = Query(uuid.UUID("00000000-0000-0000-0000-000000000001")),
    db: AsyncSession = Depends(get_db),
) -> list[IncidentTimelineEventSchema]:
    """Retrieve chronological incident milestone timeline."""
    detail = await get_investigation_details(investigation_id=investigation_id, merchant_id=merchant_id, db=db)
    return detail.timeline


@router.get(
    "/{investigation_id}/root-cause",
    response_model=list[RootCauseCandidateSchema],
    summary="Get Root Cause Candidates",
)
async def get_investigation_root_cause(
    investigation_id: str,
    merchant_id: uuid.UUID = Query(uuid.UUID("00000000-0000-0000-0000-000000000001")),
    db: AsyncSession = Depends(get_db),
) -> list[RootCauseCandidateSchema]:
    """Retrieve ranked root cause hypotheses."""
    detail = await get_investigation_details(investigation_id=investigation_id, merchant_id=merchant_id, db=db)
    return detail.candidates


@router.get(
    "/{investigation_id}/impact",
    response_model=BusinessImpactSchema,
    summary="Get Business Impact Quantification",
)
async def get_investigation_impact(
    investigation_id: str,
    merchant_id: uuid.UUID = Query(uuid.UUID("00000000-0000-0000-0000-000000000001")),
    db: AsyncSession = Depends(get_db),
) -> BusinessImpactSchema:
    """Retrieve quantified financial exposure and affected transaction metrics."""
    detail = await get_investigation_details(investigation_id=investigation_id, merchant_id=merchant_id, db=db)
    if not detail.impact:
        raise HTTPException(status_code=404, detail="Impact analysis not available.")
    return detail.impact


@router.get(
    "/{investigation_id}/summary",
    response_model=InvestigationSummaryResponse,
    summary="Get Investigation Summary Card",
)
async def get_investigation_summary(
    investigation_id: str,
    merchant_id: uuid.UUID = Query(uuid.UUID("00000000-0000-0000-0000-000000000001")),
    db: AsyncSession = Depends(get_db),
) -> InvestigationSummaryResponse:
    """Retrieve high-level investigation summary card."""
    detail = await get_investigation_details(investigation_id=investigation_id, merchant_id=merchant_id, db=db)
    return InvestigationSummaryResponse(
        id=detail.id,
        caseId=detail.caseId,
        status=detail.status,
        root_cause=detail.conclusion,
        finding=detail.finding,
        confidence_score=detail.confidenceScore,
        revenue_at_risk=detail.impact.revenue_at_risk_inr if detail.impact else Decimal("0.00"),
        recoverable_revenue=detail.impact.recoverable_revenue_inr if detail.impact else Decimal("0.00"),
        affected_method=detail.impact.primary_affected_payment_method if detail.impact else "UPI",
        affected_bank=detail.impact.primary_affected_bank if detail.impact else "HDFC",
        dominant_error=detail.impact.primary_error_code if detail.impact else "GATEWAY_TIMEOUT",
        started_at=detail.createdAt,
        completed_at=detail.completedAt,
    )
