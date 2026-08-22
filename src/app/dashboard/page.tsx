"use client";

import React, { useEffect, useState } from "react";
import { useScenarioStore } from "@/lib/store/scenarioStore";
import { getDashboardMetrics, getRiskCases, getInvestigationById } from "@/lib/api";
import { DashboardMetrics, DashboardTimeframe, RiskCase } from "@/lib/types";
import { formatINR } from "@/lib/utils";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { RevenueTrendChart } from "@/components/dashboard/RevenueTrendChart";
import { PaymentHealthSection } from "@/components/dashboard/PaymentHealthSection";
import { AIInsightCard } from "@/components/dashboard/AIInsightCard";
import { ActiveRisksTable } from "@/components/dashboard/ActiveRisksTable";
import { RecoveryPerformanceSection } from "@/components/dashboard/RecoveryPerformanceSection";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import Link from "next/link";
import {
  RotateCcw,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  TrendingUp,
  ShieldAlert,
  Sparkles,
  ArrowRight,
} from "lucide-react";

const TIMEFRAME_LABELS: Record<DashboardTimeframe, string> = {
  "24h": "Last 24 hours",
  "7d": "Last 7 days",
  "30d": "Last 30 days",
  "90d": "Last 90 days",
};

export default function DashboardPage() {
  const { currentScenario, setScenario, scenarioData } = useScenarioStore();
  const [timeframe, setTimeframe] = useState<DashboardTimeframe>("24h");
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [riskCases, setRiskCases] = useState<RiskCase[]>([]);
  const [aiConfidence, setAiConfidence] = useState<number>(83);
  const [loading, setLoading] = useState(true);
  const [chartLoading, setChartLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isSimulationScenario =
    currentScenario !== "PAYMENT_DEGRADATION" && currentScenario !== "UPI_DEGRADATION";

  const [isInitialLoad, setIsInitialLoad] = useState(true);

  const loadData = React.useCallback(
    async (targetTimeframe: DashboardTimeframe, isInitial = false) => {
      if (isInitial) {
        setLoading(true);
      } else {
        setChartLoading(true);
      }
      setError(null);
      try {
        const [m, cases, inv] = await Promise.all([
          getDashboardMetrics("UPI_DEGRADATION", targetTimeframe),
          getRiskCases(),
          getInvestigationById("INV-00000000").catch(() => null),
        ]);
        const activeCasesCount = cases.filter(
          (c) => c.status !== "RESOLVED" && c.status !== "DISMISSED"
        ).length;
        const highPriorityCount = cases.filter(
          (c) =>
            c.status !== "RESOLVED" &&
            c.status !== "DISMISSED" &&
            (c.severity === "HIGH" || c.severity === "CRITICAL")
        ).length;

        const synchronizedMetrics = {
          ...m,
          activeRiskCasesCount: activeCasesCount > 0 ? activeCasesCount : m.activeRiskCasesCount,
          highPriorityCasesCount: highPriorityCount > 0 ? highPriorityCount : m.highPriorityCasesCount,
        };
        setMetrics(synchronizedMetrics);
        setRiskCases(cases);
        if (inv && typeof inv.confidenceScore === "number") {
          setAiConfidence(inv.confidenceScore);
        }
      } catch (err) {
        console.error("Failed to load dashboard data:", err);
        setError(err instanceof Error ? err.message : "Failed to load live metrics from backend API.");
      } finally {
        setLoading(false);
        setChartLoading(false);
      }
    },
    []
  );

  useEffect(() => {
    loadData(timeframe, isInitialLoad);
    if (isInitialLoad) {
      setIsInitialLoad(false);
    }
  }, [loadData, timeframe]);

  const handleTimeframeChange = (newTimeframe: DashboardTimeframe) => {
    if (newTimeframe !== timeframe) {
      setTimeframe(newTimeframe);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadData(timeframe, false);
    setRefreshing(false);
  };

  if (error && !metrics) {
    return (
      <div className="p-8 rounded-lg border border-destructive/30 bg-destructive/5 text-center space-y-4 my-8">
        <AlertTriangle className="w-10 h-10 text-destructive mx-auto" />
        <div className="space-y-1">
          <h3 className="font-semibold text-lg text-foreground">Failed to Load Dashboard Metrics</h3>
          <p className="text-sm text-muted-foreground max-w-md mx-auto">
            Unable to connect to the live backend API service. Please verify that the backend container is running and healthy.
          </p>
        </div>
        <Button onClick={handleRefresh} disabled={refreshing} variant="outline" className="gap-2">
          <RotateCcw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
          Retry Connection
        </Button>
      </div>
    );
  }

  if (loading || !metrics) {
    return (
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <Skeleton className="h-8 w-40" />
            <Skeleton className="h-4 w-72" />
          </div>
          <div className="flex gap-2">
            <Skeleton className="h-8 w-32" />
            <Skeleton className="h-8 w-24" />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-32 rounded-lg" />
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Skeleton className="h-80 rounded-lg lg:col-span-2" />
          <Skeleton className="h-80 rounded-lg" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-border/60">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-foreground">
            Overview
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground mt-0.5">
            Monitor revenue risk, recovery opportunities, and AI activity.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Synchronized Timeframe Dropdown */}
          <div className="relative inline-flex items-center">
            <div className="flex items-center gap-1.5 h-8 px-2.5 rounded-md border border-border bg-background text-xs text-foreground shadow-xs">
              <Calendar className="w-3.5 h-3.5 text-muted-foreground shrink-0" />
              <select
                value={timeframe}
                onChange={(e) => handleTimeframeChange(e.target.value as DashboardTimeframe)}
                className="bg-transparent text-xs font-medium text-foreground focus:outline-none cursor-pointer pr-1"
                aria-label="Select dashboard timeframe"
              >
                <option value="24h">Last 24 hours</option>
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
                <option value="90d">Last 90 days</option>
              </select>
            </div>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={refreshing}
            className="h-8 gap-1.5 text-xs"
          >
            <RotateCcw className={`w-3.5 h-3.5 ${refreshing ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Simulation Scenario Context Banner */}
      {isSimulationScenario && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 rounded-lg border border-violet-500/30 bg-violet-500/10 text-xs text-foreground animate-in fade-in-50">
          <div className="flex items-start sm:items-center gap-2.5">
            <Sparkles className="w-4 h-4 text-violet-600 dark:text-violet-400 shrink-0 mt-0.5 sm:mt-0" />
            <div>
              <span className="font-semibold text-violet-950 dark:text-violet-200">
                Simulation Profile Selected: {scenarioData.name}
              </span>
              <p className="text-muted-foreground mt-0.5">
                This scenario profile is configured for synthetic stream generation and stress-testing. The live dashboard telemetry is grounded in the active PostgreSQL incident <strong>HDFC UPI Degradation (RC-001)</strong>.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <Button
              size="sm"
              variant="outline"
              onClick={() => setScenario("PAYMENT_DEGRADATION")}
              className="h-7 text-xs border-violet-500/40 bg-background hover:bg-violet-500/10 text-violet-700 dark:text-violet-300 gap-1.5"
            >
              <ShieldAlert className="w-3 h-3 text-rose-500" />
              View Active Incident (RC-001)
            </Button>
            <Link href="/transactions">
              <Button size="sm" className="h-7 text-xs gap-1 bg-violet-600 hover:bg-violet-700 text-white">
                <span>Transactions Stream</span>
                <ArrowRight className="w-3 h-3" />
              </Button>
            </Link>
          </div>
        </div>
      )}

      {/* KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Revenue at Risk"
          value={formatINR(metrics.revenueAtRisk)}
          change={`${metrics.revenueAtRiskDeltaPercent >= 0 ? "+" : ""}${metrics.revenueAtRiskDeltaPercent}%`}
          subtitle="vs previous period"
          isPositive={false}
          variant={metrics.revenueAtRisk > 0 ? "critical" : "default"}
          icon={AlertTriangle}
        />

        <MetricCard
          title="Recoverable Revenue"
          value={formatINR(metrics.recoverableRevenue)}
          subtitle={`${metrics.recoverablePercentOfRisk}% of revenue at risk`}
          isNeutral={true}
          icon={TrendingUp}
        />

        <MetricCard
          title="Revenue Recovered"
          value={formatINR(metrics.revenueRecovered)}
          change={`+${metrics.revenueRecoveredDeltaPercent}%`}
          subtitle="Recovered this period"
          isPositive={true}
          variant="success"
          icon={CheckCircle2}
        />

        <MetricCard
          title="Active Risk Cases"
          value={String(metrics.activeRiskCasesCount)}
          subtitle={`${metrics.highPriorityCasesCount} high priority requiring attention`}
          isNeutral={metrics.activeRiskCasesCount === 0}
          variant={metrics.activeRiskCasesCount > 0 ? "warning" : "default"}
          icon={ShieldAlert}
        />
      </div>

      {/* Primary Trend & AI Insight Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        <div className="lg:col-span-2">
          <RevenueTrendChart
            data={metrics.trendData}
            timeframe={timeframe}
            onTimeframeChange={handleTimeframeChange}
            hasSufficientHistory={metrics.hasSufficientHistory}
            availableFrom={metrics.availableFrom}
            availableTo={metrics.availableTo}
            isLoading={chartLoading}
          />
        </div>
        <div className="lg:col-span-1">
          <AIInsightCard
            dropPercentage={Math.abs(metrics.successRateDeltaPercentagePoints)}
            revenueAtRisk={metrics.revenueAtRisk}
            confidenceScore={aiConfidence}
            investigationRoute="/investigations/INV-00000000"
          />
        </div>
      </div>

      {/* Payment Health & Recovery Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PaymentHealthSection
          currentSuccessRate={metrics.paymentSuccessRate}
          baselineSuccessRate={metrics.baselineSuccessRate}
          deltaPercentagePoints={metrics.successRateDeltaPercentagePoints}
          methods={metrics.paymentMethods}
        />

        <RecoveryPerformanceSection
          attempts={metrics.recoveryAttempts}
          successful={metrics.successfulRecoveries}
          recoveryRate={metrics.recoverySuccessRatePercent}
          recoveredAmount={metrics.revenueRecovered}
          trendData={metrics.recoveryTrendData}
        />
      </div>

      {/* Active Revenue Risks Table */}
      <ActiveRisksTable riskCases={riskCases} />
    </div>
  );
}
