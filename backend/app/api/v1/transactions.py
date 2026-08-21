"""FastAPI router for Transaction ingestion and querying."""

import math
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import AppException
from app.db.models import Payment
from app.db.repositories.payment import PaymentRepository
from app.db.session import get_db
from app.schemas.transaction_ingest import (
    BatchIngestRequest,
    BatchIngestResponse,
    TransactionDetailResponse,
    TransactionIngestItem,
    TransactionListResponse,
    TransactionTimelineItem,
)
from app.services.ingestion.ingestor import TransactionIngestionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


def _format_payment_response(p: Payment) -> TransactionDetailResponse:
    """Helper to convert Payment model to frontend-compatible TransactionDetailResponse."""
    timeline = []
    created_str = p.created_at.strftime("%Y-%m-%d %H:%M:%S") if p.created_at else ""

    timeline.append(
        TransactionTimelineItem(
            step="ORDER_CREATED",
            title="Order Created",
            timestamp=created_str,
            description=f"Purchase order initiated for INR {p.amount:,.2f}",
            status="completed",
        )
    )

    if p.status == "CAPTURED":
        captured_str = p.captured_at.strftime("%Y-%m-%d %H:%M:%S") if p.captured_at else created_str
        timeline.append(
            TransactionTimelineItem(
                step="PAYMENT_CAPTURED",
                title="Payment Captured",
                timestamp=captured_str,
                description=f"Transaction settled via {p.payment_method} ({p.bank or 'Direct'})",
                status="completed",
            )
        )
    elif p.status == "FAILED":
        timeline.append(
            TransactionTimelineItem(
                step="PAYMENT_FAILED",
                title="Payment Failed",
                timestamp=created_str,
                description=p.error_reason or f"Declined with code {p.error_code or 'UNKNOWN'}",
                status="failed",
            )
        )

    # Determine is_recoverable
    is_recoverable = False
    if p.status == "FAILED":
        if p.error_code in ["GATEWAY_TIMEOUT", "BANK_TIMEOUT", "NETWORK_ERROR"]:
            is_recoverable = True

    return TransactionDetailResponse(
        id=p.external_payment_id,
        order_id=p.order.external_order_id if p.order else f"ord_{p.order_id}",
        customer_name=p.customer.name if p.customer else "Unknown Customer",
        customer_email=p.customer.email if p.customer else "customer@example.local",
        customer_phone=p.customer.phone_last4 if p.customer else None,
        amount=float(p.amount),
        method=p.payment_method,
        bank=p.bank,
        status="SUCCESS" if p.status == "CAPTURED" else p.status,
        failure_reason=p.error_reason,
        failure_code=p.error_code,
        is_recoverable=is_recoverable,
        created_at=p.created_at.isoformat() if p.created_at else "",
        captured_at=p.captured_at.isoformat() if p.captured_at else None,
        timeline=timeline,
    )


@router.post(
    "/ingest",
    response_model=BatchIngestResponse,
    status_code=status.HTTP_200_OK,
    summary="Ingest Single Transaction",
    description="Ingest a single transaction attempt idempotently.",
)
async def ingest_single_transaction(
    item: TransactionIngestItem,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BatchIngestResponse:
    """Ingest single transaction."""
    service = TransactionIngestionService(db)
    req_id = getattr(request.state, "request_id", None)
    return await service.ingest_batch(
        merchant_id=item.merchant_id,
        transactions=[item],
        request_id=req_id,
    )


@router.post(
    "/ingest/batch",
    response_model=BatchIngestResponse,
    status_code=status.HTTP_200_OK,
    summary="Batch Ingest Transactions",
    description="Ingest a batch of payment transactions idempotently.",
)
async def ingest_transaction_batch(
    payload: BatchIngestRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> BatchIngestResponse:
    """Ingest multiple transactions in batch."""
    service = TransactionIngestionService(db)
    req_id = getattr(request.state, "request_id", None)
    return await service.ingest_batch(
        merchant_id=payload.merchant_id,
        transactions=payload.transactions,
        request_id=req_id,
    )


@router.get(
    "",
    response_model=TransactionListResponse,
    summary="List Transactions",
    description="Query payments with filtering on status, method, bank, search, and pagination.",
)
async def list_transactions(
    merchant_id: uuid.UUID = Query(uuid.UUID("00000000-0000-0000-0000-000000000001")),
    status: Optional[str] = Query(None),
    method: Optional[str] = Query(None),
    bank: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    pageSize: Optional[int] = Query(None, description="CamelCase alias for pageSize"),
    db: AsyncSession = Depends(get_db),
) -> TransactionListResponse:
    """List tenant-isolated transactions with pagination and search."""
    actual_page_size = pageSize or page_size
    skip = (page - 1) * actual_page_size

    # Status mapping if UI sends SUCCESS
    db_status = "CAPTURED" if status == "SUCCESS" else status

    payment_repo = PaymentRepository(db)
    total = await payment_repo.count_payments_filtered(
        merchant_id=merchant_id,
        status=db_status,
        payment_method=method,
        bank=bank,
        search=search,
    )

    payments = await payment_repo.list_payments_filtered(
        merchant_id=merchant_id,
        status=db_status,
        payment_method=method,
        bank=bank,
        search=search,
        skip=skip,
        limit=actual_page_size,
    )

    items = [_format_payment_response(p) for p in payments]
    total_pages = max(1, math.ceil(total / actual_page_size))

    return TransactionListResponse(
        items=items,
        total=total,
        page=page,
        page_size=actual_page_size,
        total_pages=total_pages,
    )


@router.get(
    "/{transaction_id}",
    response_model=TransactionDetailResponse,
    summary="Get Transaction Details",
    description="Retrieve full details and timeline for a specific transaction ID.",
)
async def get_transaction_details(
    transaction_id: str,
    merchant_id: uuid.UUID = Query(uuid.UUID("00000000-0000-0000-0000-000000000001")),
    db: AsyncSession = Depends(get_db),
) -> TransactionDetailResponse:
    """Get single payment details."""
    where_clauses = [Payment.external_payment_id == transaction_id]
    try:
        parsed_uuid = uuid.UUID(transaction_id)
        where_clauses.append(Payment.id == parsed_uuid)
    except (ValueError, TypeError):
        pass

    from sqlalchemy import or_
    stmt = (
        select(Payment)
        .where(
            Payment.merchant_id == merchant_id,
            or_(*where_clauses),
        )
        .options(
            selectinload(Payment.order),
            selectinload(Payment.customer),
            selectinload(Payment.events),
        )
    )
    result = await db.execute(stmt)
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction '{transaction_id}' not found.",
        )

    return _format_payment_response(payment)
