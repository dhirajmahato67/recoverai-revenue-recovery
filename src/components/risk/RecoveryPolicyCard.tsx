import React from "react";
import { RecommendedAction } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/card";
import { Button } from "../ui/button";
import { formatINR } from "@/lib/utils";
import { ShieldCheck, ArrowRight, RotateCcw, AlertOctagon, CheckCircle2, Lock } from "lucide-react";

interface RecoveryPolicyCardProps {
  action: RecommendedAction;
  onReviewPlan: () => void;
  batchId?: string;
}

export function RecoveryPolicyCard({
  action,
  onReviewPlan,
  batchId = "RB-024",
}: RecoveryPolicyCardProps) {
  return (
    <Card className="border-violet-500/30 bg-card shadow-xs">
      <CardHeader className="pb-3 border-b border-border/60">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-sm font-semibold">
            <ShieldCheck className="w-4 h-4 text-violet-600 dark:text-violet-400" />
            Recommended Recovery Action
          </CardTitle>
          <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-violet-500/10 text-violet-700 dark:text-violet-300">
            Batch {batchId}
          </span>
        </div>
        <CardDescription>
          Algorithmic bounded recovery policy synthesized by AI Diagnostics and validated by Safety Engine.
        </CardDescription>
      </CardHeader>

      <CardContent className="p-5 space-y-4">
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
          <div className="p-3 rounded-md bg-muted/40 border border-border/60 space-y-1">
            <span className="text-[10px] uppercase font-semibold text-muted-foreground">Action Type</span>
            <p className="font-bold text-foreground flex items-center gap-1">
              <RotateCcw className="w-3 h-3 text-violet-500" />
              {action.actionType}
            </p>
          </div>

          <div className="p-3 rounded-md bg-muted/40 border border-border/60 space-y-1">
            <span className="text-[10px] uppercase font-semibold text-muted-foreground">Eligible Transactions</span>
            <p className="font-bold text-foreground font-mono">{action.eligibleTransactions} tx</p>
          </div>

          <div className="p-3 rounded-md bg-emerald-500/10 border border-emerald-500/20 space-y-1">
            <span className="text-[10px] uppercase font-semibold text-emerald-800 dark:text-emerald-300">Expected Recovery</span>
            <p className="font-bold text-emerald-700 dark:text-emerald-400 font-mono">
              {formatINR(action.expectedRecoveryMin)} – {formatINR(action.expectedRecoveryMax)}
            </p>
          </div>

          <div className="p-3 rounded-md bg-muted/40 border border-border/60 space-y-1">
            <span className="text-[10px] uppercase font-semibold text-muted-foreground">Maximum Exposure</span>
            <p className="font-bold text-foreground font-mono">{formatINR(action.maxExposure)}</p>
          </div>

          <div className="p-3 rounded-md bg-muted/40 border border-border/60 space-y-1">
            <span className="text-[10px] uppercase font-semibold text-muted-foreground">Retry Limit</span>
            <p className="font-bold text-foreground font-mono">{action.retryLimit} attempt per transaction</p>
          </div>

          <div className="p-3 rounded-md bg-amber-500/10 border border-amber-500/20 space-y-1">
            <span className="text-[10px] uppercase font-semibold text-amber-800 dark:text-amber-300">Auto Stop Condition</span>
            <p className="font-bold text-amber-800 dark:text-amber-300 font-mono text-[11px]">
              Failure rate &gt; {action.stoppingThresholdPercent}%
            </p>
          </div>
        </div>

        {/* Safety Guarantees */}
        <div className="rounded-md border border-border/60 bg-muted/20 p-3 space-y-1.5 text-xs text-muted-foreground">
          <div className="flex items-center gap-1.5 font-semibold text-foreground text-[11px]">
            <Lock className="w-3 h-3 text-emerald-500" />
            Fintech Safety Bounds & Idempotency Controls Active
          </div>
          <p className="text-[11px]">
            This action requires merchant approval. Idempotency keys will prevent duplicate charges. If the failure threshold is crossed during execution, the system will immediately halt further transactions.
          </p>
        </div>

        <div className="pt-2 flex justify-end">
          <Button onClick={onReviewPlan} variant="fintech" size="default" className="gap-1.5 font-semibold">
            Review Recovery Plan
            <ArrowRight className="w-3.5 h-3.5" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
