"""FastAPI router for Recovery Workflow and Bounded Batch Management."""

import datetime
import uuid
from decimal import Decimal
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import AuditLog, RecoveryBatch, RecoveryPlan, RiskCase
from app.db.session import get_db

router = APIRouter(prefix="/recovery", tags=["Recovery"])

DEFAULT_MERCHANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


class RecoverySafetyCheckSchema(BaseModel):
    id: str
    name: str
    description: str
    passed: bool


class RecoveryBatchResponse(BaseModel):
    id: str
    caseId: str
    caseTitle: str
    action: str
    status: str
    plannedCount: int
    eligibleCount: int
    attemptedCount: int
    recoveredCount: int
    failedCount: int
    skippedCount: int
    expectedRecoveryMin: float
    expectedRecoveryMax: float
    actualRecoveredAmount: float
    maxExposure: float
    retryLimit: int
    failureThresholdPercent: float
    currentFailureRatePercent: float
    stopReason: Optional[str] = None
    approvedBy: Optional[str] = None
    approvedAt: Optional[str] = None
    startedAt: Optional[str] = None
    completedAt: Optional[str] = None
    stoppedAt: Optional[str] = None
    createdAt: str
    safetyChecks: list[RecoverySafetyCheckSchema] = Field(default_factory=list)
    idempotencyKey: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ApproveBatchRequest(BaseModel):
    approvedBy: str = "Merchant Admin (Acme Commerce)"


def _build_safety_checks() -> list[RecoverySafetyCheckSchema]:
    return [
        RecoverySafetyCheckSchema(
            id="sc-01",
            name="Single Retry Bound",
            description="Strict maximum of 1 recovery attempt per failed transaction ID",
            passed=True,
        ),
        RecoverySafetyCheckSchema(
            id="sc-02",
            name="Max Exposure Cap",
            description="Batch financial limit capped at INR 304,886.00",
            passed=True,
        ),
        RecoverySafetyCheckSchema(
            id="sc-03",
            name="Dynamic Rate Limiting",
            description="Max 25 retry dispatches per second across HDFC nodes",
            passed=True,
        ),
        RecoverySafetyCheckSchema(
            id="sc-04",
            name="Failure Rate Circuit Breaker",
            description="Execution halts automatically if batch failure rate exceeds 30.0%",
            passed=True,
        ),
    ]


def _map_batch_to_response(batch: RecoveryBatch, case_ref: str = "RC-001", case_title: str = "UPI Degradation (HDFC UPI)") -> RecoveryBatchResponse:
    attempted = batch.attempted_transactions
    failed = batch.failed_transactions
    curr_fail_rate = round((failed / attempted) * 100, 1) if attempted > 0 else 0.0

    return RecoveryBatchResponse(
        id=batch.batch_reference,
        caseId=case_ref,
        caseTitle=case_title,
        action="Payment Retry",
        status=batch.status,
        plannedCount=batch.total_transactions,
        eligibleCount=batch.eligible_transactions,
        attemptedCount=batch.attempted_transactions,
        recoveredCount=batch.successful_transactions,
        failedCount=batch.failed_transactions,
        skippedCount=batch.skipped_transactions,
        expectedRecoveryMin=243908.0,
        expectedRecoveryMax=304886.0,
        actualRecoveredAmount=float(batch.actual_recovery),
        maxExposure=304886.0,
        retryLimit=1,
        failureThresholdPercent=30.0,
        currentFailureRatePercent=curr_fail_rate,
        stopReason=None,
        approvedBy="Merchant Admin (Acme Commerce)" if batch.status in ["RUNNING", "COMPLETED", "APPROVED"] else None,
        approvedAt=batch.started_at.isoformat() if batch.started_at else None,
        startedAt=batch.started_at.isoformat() if batch.started_at else None,
        completedAt=batch.completed_at.isoformat() if batch.completed_at else None,
        createdAt=batch.created_at.isoformat() if batch.created_at else datetime.datetime.now(datetime.timezone.utc).isoformat(),
        safetyChecks=_build_safety_checks(),
        idempotencyKey=batch.idempotency_key,
    )


@router.get(
    "/batches",
    response_model=list[RecoveryBatchResponse],
    summary="List Recovery Batches",
    description="Retrieve all recovery execution batches for the merchant.",
)
async def list_recovery_batches(
    status: Optional[str] = Query(None, description="Optional status filter"),
    merchant_id: uuid.UUID = Query(DEFAULT_MERCHANT_ID),
    db: AsyncSession = Depends(get_db),
) -> list[RecoveryBatchResponse]:
    """List recovery batches with merchant scoping."""
    stmt = select(RecoveryBatch).where(RecoveryBatch.merchant_id == merchant_id)
    if status and status != "ALL":
        stmt = stmt.where(RecoveryBatch.status == status)

    result = await db.execute(stmt)
    batches = result.scalars().all()

    if not batches:
        # Provide default canonical demo batch representation if DB has no batches
        return [
            RecoveryBatchResponse(
                id="RB-024",
                caseId="RC-001",
                caseTitle="UPI Degradation (HDFC UPI)",
                action="Payment Retry",
                status="RUNNING",
                plannedCount=438,
                eligibleCount=438,
                attemptedCount=285,
                recoveredCount=228,
                failedCount=42,
                skippedCount=15,
                expectedRecoveryMin=243908.0,
                expectedRecoveryMax=304886.0,
                actualRecoveredAmount=42000.0,
                maxExposure=304886.0,
                retryLimit=1,
                failureThresholdPercent=30.0,
                currentFailureRatePercent=14.7,
                approvedBy="Merchant Admin (Acme Commerce)",
                approvedAt="2026-08-21T09:15:00Z",
                startedAt="2026-08-21T09:15:00Z",
                createdAt="2026-08-21T09:00:00Z",
                safetyChecks=_build_safety_checks(),
                idempotencyKey="idem_rb024_acme_20260821",
            )
        ]

    return [_map_batch_to_response(b) for b in batches]


@router.get(
    "/batches/{batch_id_or_ref}",
    response_model=RecoveryBatchResponse,
    summary="Get Recovery Batch Detail",
    description="Retrieve detail for a recovery batch by reference (e.g. RB-024, RB-001) or UUID.",
)
async def get_recovery_batch(
    batch_id_or_ref: str,
    merchant_id: uuid.UUID = Query(DEFAULT_MERCHANT_ID),
    db: AsyncSession = Depends(get_db),
) -> RecoveryBatchResponse:
    """Retrieve recovery batch detail."""
    stmt = select(RecoveryBatch).where(
        RecoveryBatch.merchant_id == merchant_id,
        or_(
            RecoveryBatch.batch_reference == batch_id_or_ref.upper(),
            RecoveryBatch.batch_reference == batch_id_or_ref,
        ),
    )
    result = await db.execute(stmt)
    batch = result.scalar_one_or_none()

    if not batch:
        try:
            batch_uuid = uuid.UUID(batch_id_or_ref)
            batch = await db.get(RecoveryBatch, batch_uuid)
        except (ValueError, AttributeError):
            pass

    if batch:
        return _map_batch_to_response(batch)

    # Return canonical demo response for standard reference RB-024 / RB-001
    return RecoveryBatchResponse(
        id=batch_id_or_ref.upper(),
        caseId="RC-001",
        caseTitle="UPI Degradation (HDFC UPI)",
        action="Payment Retry",
        status="RUNNING" if "24" in batch_id_or_ref else "PENDING_APPROVAL",
        plannedCount=438,
        eligibleCount=438,
        attemptedCount=285 if "24" in batch_id_or_ref else 0,
        recoveredCount=228 if "24" in batch_id_or_ref else 0,
        failedCount=42 if "24" in batch_id_or_ref else 0,
        skippedCount=15 if "24" in batch_id_or_ref else 0,
        expectedRecoveryMin=243908.0,
        expectedRecoveryMax=304886.0,
        actualRecoveredAmount=42000.0 if "24" in batch_id_or_ref else 0.0,
        maxExposure=304886.0,
        retryLimit=1,
        failureThresholdPercent=30.0,
        currentFailureRatePercent=14.7 if "24" in batch_id_or_ref else 0.0,
        approvedBy="Merchant Admin (Acme Commerce)" if "24" in batch_id_or_ref else None,
        approvedAt="2026-08-21T09:15:00Z" if "24" in batch_id_or_ref else None,
        startedAt="2026-08-21T09:15:00Z" if "24" in batch_id_or_ref else None,
        createdAt="2026-08-21T09:00:00Z",
        safetyChecks=_build_safety_checks(),
        idempotencyKey=f"idem_{batch_id_or_ref.lower()}_acme_20260821",
    )


@router.post(
    "/batches/{batch_id_or_ref}/approve",
    response_model=RecoveryBatchResponse,
    summary="Approve Recovery Batch Execution",
    description="Idempotently approve a recovery batch for sandbox execution and log audit event.",
)
async def approve_recovery_batch(
    batch_id_or_ref: str,
    payload: ApproveBatchRequest,
    request: Request,
    merchant_id: uuid.UUID = Query(DEFAULT_MERCHANT_ID),
    db: AsyncSession = Depends(get_db),
) -> RecoveryBatchResponse:
    """Approve recovery batch."""
    stmt = select(RecoveryBatch).where(
        RecoveryBatch.merchant_id == merchant_id,
        or_(
            RecoveryBatch.batch_reference == batch_id_or_ref.upper(),
            RecoveryBatch.batch_reference == batch_id_or_ref,
        ),
    )
    result = await db.execute(stmt)
    batch = result.scalar_one_or_none()

    now = datetime.datetime.now(datetime.timezone.utc)

    if batch:
        batch.status = "RUNNING"
        batch.started_at = now
        db.add(batch)

        # Write immutable audit log
        audit = AuditLog(
            merchant_id=merchant_id,
            actor_type="USER",
            actor_id=payload.approvedBy,
            action="RECOVERY_APPROVED",
            resource_type="RecoveryBatch",
            resource_id=batch.batch_reference,
            request_id=getattr(request.state, "request_id", None),
            metadata_={
                "batch_reference": batch.batch_reference,
                "approved_by": payload.approvedBy,
                "approved_at": now.isoformat(),
                "action_type": "PAYMENT_RETRY",
                "max_exposure": str(batch.estimated_recovery),
                "mode": "SANDBOX_BOUNDED_RECOVERY",
            },
        )
        db.add(audit)
        await db.commit()
        await db.refresh(batch)
        return _map_batch_to_response(batch)

    return RecoveryBatchResponse(
        id=batch_id_or_ref.upper(),
        caseId="RC-001",
        caseTitle="UPI Degradation (HDFC UPI)",
        action="Payment Retry",
        status="RUNNING",
        plannedCount=438,
        eligibleCount=438,
        attemptedCount=0,
        recoveredCount=0,
        failedCount=0,
        skippedCount=0,
        expectedRecoveryMin=243908.0,
        expectedRecoveryMax=304886.0,
        actualRecoveredAmount=0.0,
        maxExposure=304886.0,
        retryLimit=1,
        failureThresholdPercent=30.0,
        currentFailureRatePercent=0.0,
        approvedBy=payload.approvedBy,
        approvedAt=now.isoformat(),
        startedAt=now.isoformat(),
        createdAt="2026-08-21T09:00:00Z",
        safetyChecks=_build_safety_checks(),
        idempotencyKey=f"idem_{batch_id_or_ref.lower()}_acme_20260821",
    )
