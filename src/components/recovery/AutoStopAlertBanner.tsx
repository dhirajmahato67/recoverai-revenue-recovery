import React from "react";
import Link from "next/link";
import { AlertOctagon, ShieldAlert, ArrowRight, ShieldCheck } from "lucide-react";
import { Button } from "../ui/button";

interface AutoStopAlertBannerProps {
  currentFailureRate: number;
  failureThreshold: number;
  stopReason?: string;
}

export function AutoStopAlertBanner({
  currentFailureRate,
  failureThreshold,
  stopReason,
}: AutoStopAlertBannerProps) {
  return (
    <div className="rounded-xl border-2 border-rose-500/60 bg-rose-500/10 dark:bg-rose-950/40 p-6 text-foreground shadow-lg space-y-4 animate-in fade-in-50 duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-start gap-3.5">
          <div className="p-2.5 rounded-lg bg-rose-600 text-white shrink-0 shadow-md">
            <AlertOctagon className="w-6 h-6 stroke-[2.5]" />
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-rose-600 text-white">
                Circuit Breaker Tripped
              </span>
              <h2 className="text-lg sm:text-xl font-bold tracking-tight text-rose-700 dark:text-rose-400">
                RECOVERY STOPPED
              </h2>
            </div>
            <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed">
              Failure rate reached{" "}
              <strong className="text-rose-600 dark:text-rose-400 font-mono">
                {currentFailureRate}%
              </strong>
              . Configured safety limit is{" "}
              <strong className="text-foreground font-mono">{failureThreshold}%</strong>.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <Link href="/audit">
            <Button variant="outline" size="sm" className="h-9 gap-1.5 text-xs bg-background">
              <ShieldAlert className="w-4 h-4 text-rose-500" />
              Inspect in Audit Trail
            </Button>
          </Link>
        </div>
      </div>

      <div className="rounded-lg border border-rose-500/30 bg-background/80 p-3.5 text-xs space-y-1.5">
        <div className="flex items-center gap-1.5 font-semibold text-rose-700 dark:text-rose-400">
          <ShieldCheck className="w-4 h-4" />
          Zero Over-Exposure Guarantee Enforced
        </div>
        <p className="text-muted-foreground text-[11px] leading-relaxed">
          {stopReason ||
            "To safeguard customer trust and prevent chargeback degradation, no further transactions in this batch were attempted. Remaining queue records have been safely preserved."}
        </p>
      </div>
    </div>
  );
}
