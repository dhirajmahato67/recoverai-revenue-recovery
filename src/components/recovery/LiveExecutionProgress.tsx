import React from "react";
import { Progress } from "../ui/progress";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/card";
import { formatINR } from "@/lib/utils";
import { Activity, CheckCircle2, AlertOctagon, Clock, ShieldAlert, DollarSign } from "lucide-react";
import { cn } from "@/lib/utils";

interface LiveExecutionProgressProps {
  batchId: string;
  status: string;
  processedCount: number;
  totalPlanned: number;
  totalEligible: number;
  successCount: number;
  failedCount: number;
  skippedCount: number;
  recoveredAmount: number;
  failureRate: number;
  failureThresholdPercent: number;
}

export function LiveExecutionProgress({
  batchId,
  status,
  processedCount,
  totalPlanned,
  totalEligible,
  successCount,
  failedCount,
  skippedCount,
  recoveredAmount,
  failureRate,
  failureThresholdPercent,
}: LiveExecutionProgressProps) {
  const percentComplete = Math.min(100, Math.round((processedCount / (totalEligible || 1)) * 100));
  const remaining = Math.max(0, totalEligible - processedCount);
  const isRunning = status === "RUNNING";
  const isStopped = status === "STOPPED";
  const isCompleted = status === "COMPLETED";

  return (
    <Card className="border-border/80 shadow-xs">
      <CardHeader className="pb-3 border-b border-border/60">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
              Real-Time Execution Telemetry
            </span>
            <CardTitle className="text-sm font-bold text-foreground mt-0.5 flex items-center gap-2">
              <Activity className={cn("w-4 h-4", isRunning && "text-violet-500 animate-pulse")} />
              {batchId} — {processedCount} / {totalEligible} Transactions Processed
            </CardTitle>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-bold text-foreground">
              {percentComplete}% Complete
            </span>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-5 space-y-5">
        {/* Progress Bar */}
        <div className="space-y-1.5">
          <Progress
            value={percentComplete}
            className="h-2.5 bg-muted"
            indicatorClassName={cn(
              isStopped
                ? "bg-rose-500"
                : isCompleted
                ? "bg-emerald-500"
                : "bg-violet-600"
            )}
          />
        </div>

        {/* 5 Real-Time Metric Counters */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5 text-xs">
          <div className="p-3 rounded-lg bg-muted/40 border border-border/60 space-y-0.5">
            <span className="text-[10px] font-semibold text-muted-foreground uppercase">Successful</span>
            <p className="text-lg font-bold text-emerald-600 dark:text-emerald-400 font-mono">
              {successCount}
            </p>
            <span className="text-[10px] text-muted-foreground">Recovered to merchant</span>
          </div>

          <div className="p-3 rounded-lg bg-muted/40 border border-border/60 space-y-0.5">
            <span className="text-[10px] font-semibold text-muted-foreground uppercase">Failed</span>
            <p className="text-lg font-bold text-rose-600 dark:text-rose-400 font-mono">
              {failedCount}
            </p>
            <span className="text-[10px] text-muted-foreground">Gateway / bank timeout</span>
          </div>

          <div className="p-3 rounded-lg bg-muted/40 border border-border/60 space-y-0.5">
            <span className="text-[10px] font-semibold text-muted-foreground uppercase">Remaining</span>
            <p className="text-lg font-bold text-foreground font-mono">
              {remaining}
            </p>
            <span className="text-[10px] text-muted-foreground">Pending in queue</span>
          </div>

          <div className="p-3 rounded-lg bg-muted/40 border border-border/60 space-y-0.5">
            <span className="text-[10px] font-semibold text-muted-foreground uppercase">Failure Rate</span>
            <p
              className={cn(
                "text-lg font-bold font-mono",
                failureRate >= failureThresholdPercent
                  ? "text-rose-600 dark:text-rose-400"
                  : failureRate > 15
                  ? "text-amber-600 dark:text-amber-400"
                  : "text-foreground"
              )}
            >
              {failureRate}%
            </p>
            <span className="text-[10px] text-muted-foreground">Max limit: {failureThresholdPercent}%</span>
          </div>

          <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 space-y-0.5 col-span-2 sm:col-span-1">
            <span className="text-[10px] font-semibold text-emerald-800 dark:text-emerald-300 uppercase">Recovered ₹</span>
            <p className="text-lg font-bold text-emerald-700 dark:text-emerald-400 font-mono">
              {formatINR(recoveredAmount)}
            </p>
            <span className="text-[10px] text-emerald-700/80 dark:text-emerald-400/80">Net recovered funds</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
