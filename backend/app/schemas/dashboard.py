"""Pydantic schemas for the Frontend Dashboard Metrics."""

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class PaymentMethodHealthItem(BaseModel):
    """Payment method breakdown with success rate and status."""

    method: str
    successRate: float
    deltaPercent: float
    volume: int
    status: Literal["normal", "warning", "critical"]
    model_config = ConfigDict(extra="ignore")


class RevenueTrendPointItem(BaseModel):
    """Time-series data point for revenue and loss trends."""

    date: str
    revenue: float
    revenueAtRisk: float
    recovered: float
    baseline: float
    model_config = ConfigDict(extra="ignore")


class RecoveryTrendPointItem(BaseModel):
    """Time-series data point for recovery attempts and yields."""

    date: str
    attempts: int
    successful: int
    recoveredAmount: float
    model_config = ConfigDict(extra="ignore")


class DashboardMetricsResponse(BaseModel):
    """Unified Dashboard Metrics matching frontend interface."""

    revenueAtRisk: float
    revenueAtRiskDeltaPercent: float
    recoverableRevenue: float
    recoverablePercentOfRisk: float
    revenueRecovered: float
    revenueRecoveredDeltaPercent: float
    activeRiskCasesCount: int
    highPriorityCasesCount: int
    paymentSuccessRate: float
    baselineSuccessRate: float
    successRateDeltaPercentagePoints: float
    recoveryAttempts: int
    successfulRecoveries: int
    recoverySuccessRatePercent: float
    paymentMethods: list[PaymentMethodHealthItem] = Field(default_factory=list)
    trendData: list[RevenueTrendPointItem] = Field(default_factory=list)
    recoveryTrendData: list[RecoveryTrendPointItem] = Field(default_factory=list)
    trendTimeframe: Literal["24h", "7d", "30d", "90d"] = "24h"
    hasSufficientHistory: bool = True
    availableFrom: str | None = None
    availableTo: str | None = None
    dataPointCount: int = 7
    model_config = ConfigDict(extra="ignore")
