"""Pydantic schemas for transaction ingestion and querying."""

import datetime
import uuid
from decimal import Decimal
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


class TransactionIngestItem(BaseModel):
    """Payload representing a single inbound payment attempt to ingest."""

    merchant_id: uuid.UUID
    external_order_id: str = Field(..., max_length=255)
    external_payment_id: str = Field(..., max_length=255)
    external_customer_id: str = Field(..., max_length=255)
    customer_name: str = Field(..., max_length=255)
    customer_email: str = Field(..., max_length=255)
    customer_phone: str | None = Field(default=None, max_length=20)
    amount: Decimal = Field(..., ge=Decimal("0.01"), decimal_places=2, max_digits=18)
    currency: str = Field(default="INR", max_length=10)
    status: Literal["CAPTURED", "FAILED", "CREATED", "AUTHORIZED", "REFUNDED", "CANCELLED"] = "CAPTURED"
    payment_method: Literal["UPI", "CARD", "NETBANKING", "WALLET", "OTHER"] = "UPI"
    bank: str | None = Field(default=None, max_length=100)
    error_code: str | None = Field(default=None, max_length=100)
    error_reason: str | None = Field(default=None, max_length=500)
    created_at: datetime.datetime | None = None
    captured_at: datetime.datetime | None = None
    event_id: str | None = Field(default=None, max_length=255)
    event_type: str | None = Field(default=None, max_length=100)
    raw_event_payload: dict[str, Any] | None = None
    model_config = ConfigDict(extra="ignore")


class BatchIngestRequest(BaseModel):
    """Payload for submitting a batch of transactions for bulk ingestion."""

    merchant_id: uuid.UUID
    transactions: list[TransactionIngestItem] = Field(..., min_length=1, max_length=10000)
    idempotency_key: str | None = Field(default=None, max_length=255)
    model_config = ConfigDict(extra="ignore")


class BatchIngestResponse(BaseModel):
    """Ingestion execution summary and telemetry statistics."""

    merchant_id: uuid.UUID
    requested: int
    accepted: int
    duplicates: int
    rejected: int
    duration_ms: float
    rejection_details: list[dict[str, Any]] = Field(default_factory=list)
    model_config = ConfigDict(extra="ignore")


class TransactionTimelineItem(BaseModel):
    """Structured event timeline item for a payment transaction."""

    step: str
    title: str
    timestamp: str
    description: str
    status: Literal["completed", "failed", "pending"]
    model_config = ConfigDict(extra="ignore")


class TransactionDetailResponse(BaseModel):
    """Detailed representation of a payment transaction matching frontend expectations."""

    id: str
    order_id: str
    customer_name: str
    customer_email: str
    customer_phone: str | None = None
    amount: float
    method: str
    bank: str | None = None
    status: str
    failure_reason: str | None = None
    failure_code: str | None = None
    is_recoverable: bool = False
    risk_case_id: str | None = None
    recovery_batch_id: str | None = None
    created_at: str
    captured_at: str | None = None
    timeline: list[TransactionTimelineItem] = Field(default_factory=list)
    model_config = ConfigDict(extra="ignore")


class TransactionListResponse(BaseModel):
    """Paginated list of transactions."""

    items: list[TransactionDetailResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    model_config = ConfigDict(extra="ignore")
