import React from "react";
import { Investigation } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/card";
import { Button } from "../ui/button";
import { formatINR } from "@/lib/utils";
import { Sparkles, ArrowRight, ShieldCheck, CheckCircle2, Zap, FileText } from "lucide-react";

interface StructuredReasoningPanelProps {
  investigation: Investigation;
  onReviewRecovery: () => void;
}

export function StructuredReasoningPanel({
  investigation,
  onReviewRecovery,
}: StructuredReasoningPanelProps) {
  return (
    <Card className="border-violet-500/30 bg-card shadow-xs h-full flex flex-col justify-between">
      <CardHeader className="pb-3 border-b border-border/60">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-md bg-violet-500/10 text-violet-600 dark:text-violet-400">
              <Sparkles className="w-4 h-4" />
            </div>
            <CardTitle className="text-sm font-semibold text-foreground">
              AI Structured Analysis
            </CardTitle>
          </div>
          <span className="inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded bg-violet-500/10 text-violet-700 dark:text-violet-300">
            <Zap className="w-3 h-3" />
            {investigation.confidenceScore}% Confidence
          </span>
        </div>
        <CardDescription className="text-xs text-muted-foreground">
          Structured diagnostic synthesis based on real-time gateway telemetry and error classification.
        </CardDescription>
      </CardHeader>

      <CardContent className="p-5 space-y-5 flex-1">
        {/* Finding */}
        <div className="space-y-1.5">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
            <FileText className="w-3 h-3 text-violet-500" />
            Primary Finding
          </span>
          <div className="p-3 rounded-lg border border-border/80 bg-muted/30">
            <p className="text-xs sm:text-sm font-medium text-foreground leading-relaxed">
              {investigation.finding}
            </p>
          </div>
        </div>

        {/* Evidence */}
        <div className="space-y-2">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
            <CheckCircle2 className="w-3 h-3 text-emerald-500" />
            Supporting Diagnostic Evidence
          </span>
          <ul className="space-y-1.5">
            {investigation.evidenceBullets.map((bullet, idx) => (
              <li
                key={idx}
                className="flex items-start gap-2 text-xs text-muted-foreground p-2 rounded-md bg-card border border-border/60"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-violet-500 mt-1.5 shrink-0" />
                <span className="leading-relaxed text-foreground">{bullet}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Conclusion */}
        <div className="space-y-1.5">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
            <ShieldCheck className="w-3 h-3 text-violet-500" />
            Diagnostic Conclusion
          </span>
          <div className="p-3 rounded-lg border border-violet-500/30 bg-violet-500/[0.03]">
            <p className="text-xs text-foreground font-medium leading-relaxed">
              {investigation.conclusion}
            </p>
          </div>
        </div>

        {/* Action Button */}
        <div className="pt-2 flex items-center justify-between border-t border-border/60">
          <div className="text-xs text-muted-foreground">
            <span className="font-semibold text-foreground font-mono">
              {investigation.recommendedRecovery.eligibleTransactions}
            </span>{" "}
            transactions eligible for recovery
          </div>
          <Button onClick={onReviewRecovery} variant="fintech" size="sm" className="gap-1.5 font-semibold text-xs">
            Review Recovery Plan
            <ArrowRight className="w-3.5 h-3.5" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
