import React from "react";
import { EvidenceNode } from "@/lib/types";
import { Card, CardContent } from "../ui/card";
import { ArrowRight, ArrowDownRight, ArrowUpRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface EvidenceCardProps {
  evidence: EvidenceNode[];
}

export function EvidenceCard({ evidence }: EvidenceCardProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
      {evidence.map((node, index) => {
        return (
          <Card key={index} className="border-border/80 bg-card shadow-xs">
            <CardContent className="p-4 space-y-2">
              <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider block">
                {node.label}
              </span>

              <div className="flex items-baseline justify-between pt-1">
                <div className="flex items-center gap-1.5 font-mono text-sm font-semibold text-foreground">
                  <span className="text-muted-foreground line-through opacity-70">
                    {node.baselineValue}
                  </span>
                  <ArrowRight className="w-3 h-3 text-muted-foreground opacity-60" />
                  <span className="text-foreground font-bold">{node.currentValue}</span>
                </div>

                <span
                  className={cn(
                    "text-xs font-semibold px-1.5 py-0.5 rounded inline-flex items-center gap-0.5",
                    node.isNegative
                      ? "bg-rose-500/10 text-rose-600 dark:text-rose-400"
                      : "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                  )}
                >
                  {node.delta}
                </span>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
