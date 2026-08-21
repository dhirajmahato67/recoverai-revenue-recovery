import React from "react";
import Link from "next/link";
import { AIMessage } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/card";
import { Button } from "../ui/button";
import { Sparkles, ArrowRight, ShieldCheck, TrendingUp, AlertTriangle, RotateCcw, Lock } from "lucide-react";
import { cn } from "@/lib/utils";

interface ActionProposalCardProps {
  card: NonNullable<AIMessage["structuredCard"]>;
  onTriggerApproval?: (batchId: string) => void;
}

export function ActionProposalCard({ card, onTriggerApproval }: ActionProposalCardProps) {
  const isRecoveryProposal = card.type === "RECOVERY_PROPOSAL";

  return (
    <Card className={cn(
      "border shadow-sm my-2 text-xs overflow-hidden",
      isRecoveryProposal ? "border-violet-500/40 bg-violet-500/[0.02]" : "border-border/80 bg-card"
    )}>
      <CardHeader className="p-3.5 pb-2 border-b border-border/60 flex flex-row items-center justify-between">
        <div className="flex items-center gap-1.5 font-bold text-foreground">
          {isRecoveryProposal ? (
            <ShieldCheck className="w-4 h-4 text-violet-600 dark:text-violet-400" />
          ) : (
            <Sparkles className="w-4 h-4 text-violet-500" />
          )}
          <span>{card.title}</span>
        </div>
        {card.confidenceScore && (
          <span className="text-[10px] font-semibold px-1.5 py-0.2 rounded bg-violet-500/10 text-violet-700 dark:text-violet-300 font-mono">
            {card.confidenceScore}% Confidence
          </span>
        )}
      </CardHeader>

      <CardContent className="p-3.5 space-y-3">
        {/* Metric Pills */}
        {card.metrics && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {card.metrics.map((m, i) => (
              <div key={i} className="p-2 rounded-md bg-muted/40 border border-border/60 space-y-0.5">
                <span className="text-[9px] uppercase font-semibold text-muted-foreground">{m.label}</span>
                <p className="font-bold text-foreground font-mono text-xs">{m.value}</p>
              </div>
            ))}
          </div>
        )}

        {/* Bullets */}
        {card.bullets && (
          <ul className="space-y-1 text-muted-foreground text-xs">
            {card.bullets.map((b, i) => (
              <li key={i} className="flex items-start gap-1.5">
                <span className="w-1 h-1 rounded-full bg-violet-500 mt-1.5 shrink-0" />
                <span className="leading-snug">{b}</span>
              </li>
            ))}
          </ul>
        )}

        {/* Compliance Note for recovery proposals */}
        {isRecoveryProposal && (
          <div className="p-2.5 rounded-md border border-border/60 bg-muted/30 text-[11px] text-muted-foreground flex items-center gap-2">
            <Lock className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400 shrink-0" />
            <span>This recovery action requires explicit merchant financial authorization.</span>
          </div>
        )}

        {/* Action Button */}
        {card.actionLabel && (
          <div className="pt-1 flex justify-end">
            {card.actionRoute ? (
              <Link href={card.actionRoute}>
                <Button
                  variant={isRecoveryProposal ? "fintech" : "ai"}
                  size="sm"
                  className="h-7 text-xs gap-1 font-semibold"
                >
                  {card.actionLabel}
                  <ArrowRight className="w-3 h-3" />
                </Button>
              </Link>
            ) : (
              <Button
                variant="fintech"
                size="sm"
                onClick={() => onTriggerApproval && onTriggerApproval(card.batchId || "RB-024")}
                className="h-7 text-xs gap-1 font-semibold"
              >
                {card.actionLabel}
                <ArrowRight className="w-3 h-3" />
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
