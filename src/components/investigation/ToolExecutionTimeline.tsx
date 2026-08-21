"use client";

import React, { useState } from "react";
import { ToolExecution } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/card";
import { Terminal, CheckCircle2, Clock, ChevronDown, ChevronRight, Code2, Zap } from "lucide-react";
import { cn } from "@/lib/utils";

interface ToolExecutionTimelineProps {
  tools: ToolExecution[];
}

export function ToolExecutionTimeline({ tools }: ToolExecutionTimelineProps) {
  const [selectedToolId, setSelectedToolId] = useState<string | null>(tools[0]?.id || null);

  const selectedTool = tools.find((t) => t.id === selectedToolId) || tools[0];

  return (
    <Card className="border-border/80 shadow-xs col-span-full">
      <CardHeader className="pb-3 border-b border-border/60">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-violet-600 dark:text-violet-400" />
            <CardTitle className="text-sm font-semibold">
              AI Technical Tool Execution Audit
            </CardTitle>
          </div>
          <span className="text-xs font-mono text-muted-foreground">
            {tools.length} sub-agent tool calls executed
          </span>
        </div>
        <CardDescription className="text-xs text-muted-foreground">
          Deterministic execution trace and payload inspection of diagnostic tools invoked during root cause analysis.
        </CardDescription>
      </CardHeader>

      <CardContent className="p-5">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 items-start">
          {/* Tool List */}
          <div className="space-y-1.5 lg:col-span-1">
            {tools.map((tool) => {
              const isSelected = selectedTool?.id === tool.id;
              return (
                <button
                  key={tool.id}
                  onClick={() => setSelectedToolId(tool.id)}
                  className={cn(
                    "w-full flex items-center justify-between p-2.5 rounded-md border text-left text-xs transition-all",
                    isSelected
                      ? "border-violet-500/40 bg-violet-500/10 text-foreground font-semibold shadow-xs"
                      : "border-border/60 bg-card hover:bg-muted/40 text-muted-foreground"
                  )}
                >
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" />
                    <span className="font-mono text-xs">{tool.toolName}</span>
                  </div>
                  <span className="font-mono text-[10px] opacity-70">{tool.durationMs}ms</span>
                </button>
              );
            })}
          </div>

          {/* Tool Detail Inspector */}
          {selectedTool && (
            <div className="lg:col-span-2 rounded-lg border border-border/80 bg-muted/20 p-4 space-y-3 text-xs">
              <div className="flex items-center justify-between pb-2 border-b border-border/60">
                <div className="flex items-center gap-2">
                  <Code2 className="w-4 h-4 text-violet-500" />
                  <span className="font-mono font-bold text-foreground text-sm">
                    {selectedTool.toolName}
                  </span>
                  <span className="px-1.5 py-0.2 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-semibold text-[10px]">
                    {selectedTool.status}
                  </span>
                </div>
                <div className="flex items-center gap-3 text-muted-foreground font-mono text-[11px]">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {selectedTool.durationMs}ms
                  </span>
                  {selectedTool.confidenceScore && (
                    <span className="flex items-center gap-1 text-violet-600 dark:text-violet-400 font-semibold">
                      <Zap className="w-3 h-3" />
                      {selectedTool.confidenceScore}%
                    </span>
                  )}
                </div>
              </div>

              <div>
                <span className="text-[10px] font-semibold text-muted-foreground uppercase">Execution Summary</span>
                <p className="font-medium text-foreground mt-0.5">{selectedTool.resultSummary}</p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                {/* Input Payload */}
                <div className="space-y-1">
                  <span className="text-[10px] font-semibold text-muted-foreground uppercase font-mono">
                    Input Parameters
                  </span>
                  <pre className="p-2.5 rounded-md bg-neutral-950 text-neutral-200 font-mono text-[10px] overflow-x-auto max-h-36">
                    {JSON.stringify(selectedTool.inputPayload, null, 2)}
                  </pre>
                </div>

                {/* Output Payload */}
                <div className="space-y-1">
                  <span className="text-[10px] font-semibold text-muted-foreground uppercase font-mono">
                    Output Response
                  </span>
                  <pre className="p-2.5 rounded-md bg-neutral-950 text-neutral-200 font-mono text-[10px] overflow-x-auto max-h-36">
                    {JSON.stringify(selectedTool.outputPayload, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
