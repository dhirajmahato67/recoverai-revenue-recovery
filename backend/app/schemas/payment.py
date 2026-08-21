"""Payment domain schemas with exact Decimal financial precision."""

import datetime
import uuid
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class PaymentRead(BaseModel):
    """Schema for returning payment transaction details."""

    id: uuid.UUID
    merchant_id: uuid.UUID
    order_id: uuid.UUID
    customer_id: uuid.UUID
    external_payment_id: str
    amount: Decimal = Field(description="Transaction monetary amount in base currency units", examples=[Decimal("2450.00")])
    currency: str
    status: str
    payment_method: str
    bank: str | None = None
    error_code: str | None = None
    error_reason: str | None = None
    captured_at: datetime.datetime | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
