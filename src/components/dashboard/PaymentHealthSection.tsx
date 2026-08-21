import React from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/card";
import { ArrowDownRight, ArrowUpRight, Activity, Smartphone, CreditCard, Landmark, Wallet } from "lucide-react";
import { PaymentMethodHealth } from "@/lib/types";
import { cn } from "@/lib/utils";

interface PaymentHealthSectionProps {
  currentSuccessRate: number;
  baselineSuccessRate: number;
  deltaPercentagePoints: number;
  methods: PaymentMethodHealth[];
}

export function PaymentHealthSection({
  currentSuccessRate,
  baselineSuccessRate,
  deltaPercentagePoints,
  methods,
}: PaymentHealthSectionProps) {
  const getMethodIcon = (method: string) => {
    switch (method) {
      case "UPI":
        return <Smartphone className="w-4 h-4 text-violet-500" />;
      case "Card":
        return <CreditCard className="w-4 h-4 text-blue-500" />;
      case "Net Banking":
        return <Landmark className="w-4 h-4 text-emerald-500" />;
      default:
        return <Wallet className="w-4 h-4 text-amber-500" />;
    }
  };

  const isDegraded = deltaPercentagePoints < -2;

  return (
    <Card className="h-full flex flex-col justify-between">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-muted-foreground" />
            Payment Health
          </CardTitle>
          <span className="text-[11px] text-muted-foreground">Baseline: {baselineSuccessRate}%</span>
        </div>
        <CardDescription>
          Real-time payment gateway conversion health vs 7-day trailing baseline.
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-5">
        {/* Main Success Rate Metric */}
        <div className="rounded-lg border border-border/80 bg-muted/30 p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-muted-foreground font-medium">Overall Payment Success Rate</p>
            <p className="text-3xl font-bold tracking-tight text-foreground font-sans mt-0.5">
              {currentSuccessRate}%
            </p>
          </div>
          <div className="text-right">
            <span
              className={cn(
                "inline-flex items-center gap-1 font-semibold px-2 py-0.5 rounded text-xs",
                isDegraded
                  ? "bg-rose-500/10 text-rose-700 dark:text-rose-400"
                  : "bg-emerald-500/10 text-emerald-700 dark:text-emerald-400"
              )}
            >
              {deltaPercentagePoints < 0 ? (
                <ArrowDownRight className="w-3.5 h-3.5" />
              ) : (
                <ArrowUpRight className="w-3.5 h-3.5" />
              )}
              {Math.abs(deltaPercentagePoints).toFixed(1)}pp from baseline
            </span>
            <p className="text-[10px] text-muted-foreground mt-1">Live telemetry sample</p>
          </div>
        </div>

        {/* Method Breakdown */}
        <div className="space-y-3">
          <p className="text-xs font-semibold text-foreground uppercase tracking-wider">
            Payment Method Breakdown
          </p>

          <div className="space-y-2.5">
            {methods.map((m) => {
              const isCrit = m.status === "critical";
              return (
                <div
                  key={m.method}
                  className={cn(
                    "flex items-center justify-between p-2.5 rounded-md border text-xs transition-colors",
                    isCrit
                      ? "border-rose-500/30 bg-rose-500/[0.03] dark:bg-rose-950/20"
                      : "border-border/60 bg-card hover:bg-muted/30"
                  )}
                >
                  <div className="flex items-center gap-2.5">
                    {getMethodIcon(m.method)}
                    <div>
                      <p className="font-semibold text-foreground">{m.method}</p>
                      <p className="text-[10px] text-muted-foreground">
                        {isCrit ? "High degradation alert" : "Normal operating range"}
                      </p>
                    </div>
                  </div>

                  <div className="text-right">
                    <p className="font-mono font-bold text-foreground">{m.successRate}%</p>
                    <span
                      className={cn(
                        "text-[10px] font-semibold",
                        m.deltaPercent < 0
                          ? "text-rose-600 dark:text-rose-400"
                          : "text-emerald-600 dark:text-emerald-400"
                      )}
                    >
                      {m.deltaPercent < 0 ? "↓" : "↑"} {Math.abs(m.deltaPercent)}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
