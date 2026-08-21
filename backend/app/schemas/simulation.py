"""Pydantic schemas for synthetic transaction generation and scenario simulation."""

import datetime
import uuid
from decimal import Decimal
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

ScenarioType = Literal[
    "NORMAL_BASELINE",
    "UPI_DEGRADATION",
    "RECOVERY_AUTO_STOP",
    "CHECKOUT_DROPOFF",
    "SUBSCRIPTION_FAILURES",
    "GATEWAY_LATENCY",
]

PaymentMethodType = Literal["UPI", "CARD", "NETBANKING", "WALLET"]
BankType = Literal["HDFC", "ICICI", "SBI", "AXIS", "KOTAK", "OTHER"]


class ScenarioConfig(BaseModel):
    """Configuration definition for a synthetic payment scenario."""

    scenario_id: ScenarioType = Field(..., description="Scenario identifier")
    name: str = Field(..., description="Human-readable scenario name")
    description: str = Field(..., description="Description of the simulated behavior")
    target_success_rate: float = Field(..., ge=0.0, le=1.0, description="Overall expected success rate")
    method_success_rates: dict[str, float] = Field(
        default_factory=dict, description="Override success rates per payment method"
    )
    bank_success_rates: dict[str, float] = Field(
        default_factory=dict, description="Override success rates per issuing bank"
    )
    primary_failure_error_code: str | None = Field(
        default=None, description="Dominant error code for injected failures"
    )
    primary_failure_reason: str | None = Field(
        default=None, description="Dominant failure explanation message"
    )
    model_config = ConfigDict(extra="ignore")


class GenerateTransactionsRequest(BaseModel):
    """Request payload to generate synthetic transactions."""

    merchant_id: uuid.UUID = Field(..., description="Target merchant UUID")
    count: int = Field(default=100, ge=1, le=100000, description="Number of transactions to synthesize")
    scenario: ScenarioType = Field(default="NORMAL_BASELINE", description="Scenario to execute")
    seed: int | None = Field(default=None, description="PRNG seed for deterministic reproducibility")
    start_time: datetime.datetime | None = Field(default=None, description="Earliest transaction timestamp (UTC)")
    end_time: datetime.datetime | None = Field(default=None, description="Latest transaction timestamp (UTC)")
    persist: bool = Field(default=False, description="Whether to immediately ingest and persist to database")
    model_config = ConfigDict(extra="ignore")


class SyntheticTransactionItem(BaseModel):
    """Individual synthesized payment payload prior to ingestion."""

    external_order_id: str
    external_payment_id: str
    external_customer_id: str
    customer_name: str
    customer_email: str
    customer_phone: str | None = None
    amount: Decimal = Field(..., decimal_places=2, max_digits=18)
    currency: str = "INR"
    status: Literal["CAPTURED", "FAILED", "CREATED", "AUTHORIZED", "REFUNDED"]
    payment_method: PaymentMethodType
    bank: BankType
    error_code: str | None = None
    error_reason: str | None = None
    created_at: datetime.datetime
    captured_at: datetime.datetime | None = None
    event_id: str
    event_type: str
    model_config = ConfigDict(extra="ignore")


class GenerateTransactionsResponse(BaseModel):
    """Response payload containing summary or preview of generated transactions."""

    merchant_id: uuid.UUID
    scenario: ScenarioType
    seed: int
    count: int
    success_count: int
    failed_count: int
    overall_success_rate: float
    total_volume_inr: Decimal
    failed_volume_inr: Decimal
    persisted: bool
    ingestion_summary: dict[str, Any] | None = None
    sample_transactions: list[SyntheticTransactionItem] = Field(default_factory=list)
    model_config = ConfigDict(extra="ignore")


class ScenarioInfo(BaseModel):
    """Metadata describing an available simulation scenario."""

    id: ScenarioType
    name: str
    badge: str
    description: str
    target_success_rate: float
    primary_risk_title: str
    revenue_at_risk_estimate_inr: Decimal
    recoverable_revenue_estimate_inr: Decimal
    model_config = ConfigDict(extra="ignore")
