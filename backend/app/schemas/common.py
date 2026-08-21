"""Common response and request schemas for standardized API contracts."""

from typing import Any, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class HealthResponse(BaseModel):
    """Response model for the liveness health probe."""

    status: str = Field(default="ok", description="Service liveness state", examples=["ok"])


class ReadinessResponse(BaseModel):
    """Response model for the readiness probe verifying dependency health."""

    status: str = Field(description="Overall service readiness state", examples=["ok", "unavailable"])
    database: str = Field(description="Database connectivity status", examples=["ok", "unavailable"])


class ErrorDetail(BaseModel):
    """Detailed error payload structure."""

    code: str = Field(description="Machine-readable error classification code", examples=["NOT_FOUND", "VALIDATION_ERROR"])
    message: str = Field(description="Human-readable explanation of the error")
    request_id: str | None = Field(default=None, description="Unique correlation ID for tracing the request", examples=["3d12070e-dfc5-44a6"])
    details: Any = Field(default=None, description="Optional structured validation error details")


class ErrorResponse(BaseModel):
    """Standardized top-level error response envelope."""

    error: ErrorDetail


class PaginationParams(BaseModel):
    """Standard query parameters for paginated collection endpoints."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Number of records per page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard generic envelope for paginated collection responses."""

    items: list[T] = Field(description="Page records")
    total: int = Field(description="Total count of matching records in collection")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Requested page size")
    total_pages: int = Field(description="Total computed pages available")
