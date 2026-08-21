"""Merchant domain schemas for API request and response validation."""

import datetime
import uuid
from pydantic import BaseModel, ConfigDict, Field


class MerchantBase(BaseModel):
    """Base merchant attributes."""

    name: str = Field(description="Business display name", examples=["Acme Commerce"])
    legal_name: str | None = Field(default=None, description="Registered corporate legal entity name")
    currency: str = Field(default="INR", description="Settlement currency code", examples=["INR"])
    timezone: str = Field(default="Asia/Kolkata", description="Operating timezone", examples=["Asia/Kolkata"])
    status: str = Field(default="ACTIVE", description="Account standing", examples=["ACTIVE"])


class MerchantRead(MerchantBase):
    """Schema for returning merchant details."""

    id: uuid.UUID
    external_reference: str | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
