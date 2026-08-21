import React from "react";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/card";
import { Sparkles, ArrowRight, ShieldCheck, Zap } from "lucide-react";
import { Button } from "../ui/button";
import { formatINR } from "@/lib/utils";

interface AIInsightCardProps {
  title?: string;
  dropPercentage?: number;
  primaryContributor?: string;
  revenueAtRisk?: number;
  confidenceScore?: number;
  investigationRoute?: string;
}

export function AIInsightCard({
  title = "Revenue Degradation Detected",
  dropPercentage = 12.3,
  primaryContributor = "HDFC UPI transactions",
  revenueAtRisk = 1219544,
  confidenceScore = 83,
  investigationRoute = "/risk-cases/RC-001",
}: AIInsightCardProps) {
  return (
    <Card className="border-violet-500/30 bg-gradient-to-br from-violet-500/[0.04] via-card to-background shadow-xs relative overflow-hidden">
      <div className="absolute top-0 right-0 w-32 h-32 bg-violet-500/5 rounded-full blur-2xl pointer-events-none" />

      <CardHeader className="pb-3 flex flex-row items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-md bg-violet-500/10 text-violet-600 dark:text-violet-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <CardTitle className="text-sm font-semibold text-foreground">
            AI Revenue Insight
          </CardTitle>
        </div>
        <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded bg-violet-500/10 text-violet-700 dark:text-violet-300">
          <Zap className="w-3 h-3" />
          {confidenceScore}% Confidence
        </span>
      </CardHeader>

      <CardContent className="space-y-4">
        <div>
          <h4 className="font-semibold text-foreground text-sm mb-1">{title}</h4>
          <p className="text-xs text-muted-foreground leading-relaxed">
            RecoverAI telemetry diagnostics identified a{" "}
            <span className="font-semibold text-foreground">{dropPercentage} percentage-point</span> drop in payment success rate across gateway nodes.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="p-2.5 rounded-md bg-background/80 border border-border/80">
            <span className="text-[10px] text-muted-foreground uppercase font-semibold">Primary Contributor</span>
            <p className="font-semibold text-foreground mt-0.5 truncate">{primaryContributor}</p>
          </div>

          <div className="p-2.5 rounded-md bg-background/80 border border-border/80">
            <span className="text-[10px] text-muted-foreground uppercase font-semibold">Estimated Revenue at Risk</span>
            <p className="font-bold text-rose-600 dark:text-rose-400 mt-0.5">{formatINR(revenueAtRisk)}</p>
          </div>
        </div>

        <div className="pt-1 flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-[11px] text-muted-foreground">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
            <span>Bounded recovery policy ready</span>
          </div>

          <div className="flex items-center gap-2">
            <Link href="/ai-assistant?inv=INV-00000000">
              <Button size="sm" variant="outline" className="h-8 gap-1 text-xs border-violet-500/30 text-violet-600 dark:text-violet-400 hover:bg-violet-500/10">
                Ask Copilot
              </Button>
            </Link>
            <Link href={investigationRoute}>
              <Button size="sm" variant="ai" className="h-8 gap-1 text-xs">
                Investigate Anomaly
                <ArrowRight className="w-3.5 h-3.5 ml-0.5" />
              </Button>
            </Link>
          </div>
        </div>
      </CardContent>
    </Card>

  );
}
