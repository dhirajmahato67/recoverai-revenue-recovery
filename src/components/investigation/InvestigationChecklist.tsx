"use client";

import React, { useState } from "react";
import { InvestigationStep } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/card";
import { CheckCircle2, ChevronDown, ChevronRight, Clock } from "lucide-react";
import { cn } from "@/lib/utils";

interface InvestigationChecklistProps {
  steps: InvestigationStep[];
  question: string;
}

export function InvestigationChecklist({ steps, question }: InvestigationChecklistProps) {
  const [expandedStepId, setExpandedStepId] = useState<string | null>(steps[0]?.id || null);

  const toggleStep = (id: string) => {
    setExpandedStepId((prev) => (prev === id ? null : id));
  };

  return (
    <Card className="border-border/80 shadow-xs h-full flex flex-col justify-between">
      <CardHeader className="pb-3 border-b border-border/60">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-semibold text-violet-600 dark:text-violet-400 uppercase tracking-wider">
            Diagnostic Investigation
          </span>
          <span className="text-[11px] font-mono text-muted-foreground">
            {steps.filter((s) => s.status === "COMPLETED").length}/{steps.length} completed
          </span>
        </div>
        <CardTitle className="text-sm font-bold text-foreground">
          {question}
        </CardTitle>
        <CardDescription className="text-xs text-muted-foreground">
          Step-by-step automated investigative pipeline executed by AI Diagnostic Agent.
        </CardDescription>
      </CardHeader>

      <CardContent className="p-4 space-y-2 flex-1 overflow-y-auto">
        {steps.map((step, idx) => {
          const isExpanded = expandedStepId === step.id;
          return (
            <div
              key={step.id}
              className={cn(
                "rounded-md border text-xs transition-all",
                isExpanded
                  ? "border-violet-500/30 bg-violet-500/[0.02]"
                  : "border-border/60 bg-card hover:bg-muted/30"
              )}
            >
              <button
                onClick={() => toggleStep(step.id)}
                className="w-full flex items-center justify-between p-3 text-left outline-none"
              >
                <div className="flex items-center gap-2.5">
                  <div className="p-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                  </div>
                  <span className="font-semibold text-foreground text-xs">{step.title}</span>
                </div>

                <div className="flex items-center gap-2 text-muted-foreground">
                  <span className="font-mono text-[10px] flex items-center gap-0.5">
                    <Clock className="w-2.5 h-2.5" />
                    {step.durationMs}ms
                  </span>
                  {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                </div>
              </button>

              {isExpanded && (
                <div className="px-3 pb-3 pt-0 border-t border-border/40 mt-1">
                  <p className="text-[11px] text-muted-foreground pt-2 pl-6 leading-relaxed">
                    {step.description}
                  </p>
                </div>
              )}
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
