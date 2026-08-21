"""AuditLog domain schemas for ledger events."""

import datetime
import uuid
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class AuditLogRead(BaseModel):
    """Schema for immutable audit trail events."""

    id: uuid.UUID
    merchant_id: uuid.UUID
    actor_type: str
    actor_id: str | None = None
    action: str
    resource_type: str
    resource_id: str
    request_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict, alias="metadata_")
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
