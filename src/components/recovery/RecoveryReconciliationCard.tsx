import React from "react";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/card";
import { Button } from "../ui/button";
import { formatINR } from "@/lib/utils";
import { CheckCircle2, ShieldCheck, ArrowRight, TrendingUp, DollarSign } from "lucide-react";

interface RecoveryReconciliationCardProps {
  actualRecoveredAmount: number;
  plannedCount: number;
  eligibleCount: number;
  attemptedCount: number;
  recoveredCount: number;
  failedCount: number;
  expectedMin: number;
  expectedMax: number;
}

export function RecoveryReconciliationCard({
  actualRecoveredAmount = 286000,
  plannedCount = 438,
  eligibleCount = 391,
  attemptedCount = 391,
  recoveredCount = 167,
  failedCount = 224,
  expectedMin = 160000,
  expectedMax = 210000,
}: RecoveryReconciliationCardProps) {
  const recoveryRate = Math.round((recoveredCount / (attemptedCount || 1)) * 1000) / 10;

  return (
    <Card className="border-emerald-500/40 bg-gradient-to-br from-emerald-500/[0.04] via-card to-background shadow-md">
      <CardHeader className="pb-4 border-b border-border/60">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-emerald-600 text-white shadow-sm">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">
                Execution Completed & Reconciled
              </span>
              <CardTitle className="text-lg font-bold text-foreground">
                Revenue Recovery Completed
              </CardTitle>
            </div>
          </div>

          <div className="text-right">
            <span className="text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400">
              {formatINR(actualRecoveredAmount)}
            </span>
            <p className="text-[11px] text-muted-foreground">Actual revenue recovered</p>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-6 space-y-6">
        {/* Metric Comparison Row */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs">
          <div className="p-3 rounded-lg bg-card border border-border/70 space-y-1">
            <span className="text-[10px] font-semibold text-muted-foreground uppercase">Planned</span>
            <p className="text-lg font-bold text-foreground font-mono">{plannedCount} records</p>
          </div>

          <div className="p-3 rounded-lg bg-card border border-border/70 space-y-1">
            <span className="text-[10px] font-semibold text-muted-foreground uppercase">Eligible</span>
            <p className="text-lg font-bold text-foreground font-mono">{eligibleCount} records</p>
          </div>

          <div className="p-3 rounded-lg bg-card border border-border/70 space-y-1">
            <span className="text-[10px] font-semibold text-muted-foreground uppercase">Attempted</span>
            <p className="text-lg font-bold text-foreground font-mono">{attemptedCount} records</p>
          </div>

          <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 space-y-1">
            <span className="text-[10px] font-semibold text-emerald-800 dark:text-emerald-300 uppercase">Recovered</span>
            <p className="text-lg font-bold text-emerald-700 dark:text-emerald-400 font-mono">
              {recoveredCount} tx ({recoveryRate}%)
            </p>
          </div>

          <div className="p-3 rounded-lg bg-card border border-border/70 space-y-1">
            <span className="text-[10px] font-semibold text-muted-foreground uppercase">Failed</span>
            <p className="text-lg font-bold text-rose-600 dark:text-rose-400 font-mono">{failedCount} tx</p>
          </div>
        </div>

        {/* Expected vs Actual Comparison Box */}
        <div className="rounded-lg border border-border/80 bg-muted/20 p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-xs">
          <div className="space-y-1">
            <span className="text-[11px] font-semibold text-foreground flex items-center gap-1.5">
              <TrendingUp className="w-3.5 h-3.5 text-emerald-500" />
              Financial Model Reconciliation
            </span>
            <p className="text-muted-foreground text-[11px]">
              Initial algorithmic estimate modeled recovery between{" "}
              <strong className="text-foreground font-mono">{formatINR(expectedMin)}</strong> and{" "}
              <strong className="text-foreground font-mono">{formatINR(expectedMax)}</strong>. Actual settled volume realized is{" "}
              <strong className="text-emerald-600 dark:text-emerald-400 font-mono">
                {formatINR(actualRecoveredAmount)}
              </strong>
              .
            </p>
          </div>

          <Link href="/audit">
            <Button variant="outline" size="sm" className="h-8 gap-1 text-xs shrink-0">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
              View Immutable Audit Trail
              <ArrowRight className="w-3 h-3 ml-0.5" />
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
