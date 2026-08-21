import React from "react";
import { RecoveryLogEvent } from "@/lib/types";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/card";
import { Terminal, CheckCircle2, XCircle, AlertTriangle, Play, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

interface StreamingActivityLogProps {
  logs: RecoveryLogEvent[];
  isRunning?: boolean;
}

export function StreamingActivityLog({ logs, isRunning }: StreamingActivityLogProps) {
  const getLogIcon = (status: string, eventType: string) => {
    if (eventType === "THRESHOLD_STOPPED") {
      return <AlertTriangle className="w-3.5 h-3.5 text-rose-500 shrink-0" />;
    }
    if (status === "success") {
      return <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0" />;
    }
    if (status === "failure") {
      return <XCircle className="w-3.5 h-3.5 text-rose-500 shrink-0" />;
    }
    return <Play className="w-3 h-3 text-violet-500 shrink-0" />;
  };

  return (
    <Card className="border-border/80 shadow-xs h-full flex flex-col justify-between">
      <CardHeader className="pb-3 border-b border-border/60">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-violet-600 dark:text-violet-400" />
            <CardTitle className="text-sm font-semibold">
              Live Activity Stream
            </CardTitle>
          </div>
          {isRunning && (
            <span className="flex items-center gap-1 text-[11px] font-mono text-violet-600 dark:text-violet-400">
              <span className="w-1.5 h-1.5 rounded-full bg-violet-500 animate-ping" />
              Streaming events
            </span>
          )}
        </div>
        <CardDescription className="text-xs text-muted-foreground">
          Individual transaction retry dispatch events, latency benchmarks, and idempotency status.
        </CardDescription>
      </CardHeader>

      <CardContent className="p-0 flex-1 overflow-hidden">
        <div className="h-80 overflow-y-auto divide-y divide-border/40 font-mono text-xs p-2 space-y-0.5">
          {logs.length === 0 ? (
            <div className="p-8 text-center text-xs text-muted-foreground font-sans">
              No live activity yet. Click &quot;Start Recovery&quot; or &quot;Step 1 Tx&quot; to begin dispatch.
            </div>
          ) : (
            logs.map((log) => (
              <div
                key={log.id}
                className={cn(
                  "p-2 rounded-md flex items-center justify-between gap-3 text-[11px] transition-colors",
                  log.status === "failure"
                    ? "bg-rose-500/[0.04] text-rose-800 dark:text-rose-300"
                    : log.status === "success"
                    ? "bg-emerald-500/[0.03] text-emerald-900 dark:text-emerald-300"
                    : log.eventType === "THRESHOLD_STOPPED"
                    ? "bg-rose-500/10 font-bold text-rose-700 dark:text-rose-400 border border-rose-500/30"
                    : "text-muted-foreground"
                )}
              >
                <div className="flex items-center gap-2 truncate">
                  <span className="text-[10px] text-muted-foreground opacity-70 shrink-0 font-sans">
                    {log.timeDisplay}
                  </span>
                  {getLogIcon(log.status, log.eventType)}
                  <span className="truncate">{log.message}</span>
                </div>

                {log.latencyMs && (
                  <span className="text-[10px] text-muted-foreground shrink-0 opacity-60">
                    {log.latencyMs}ms
                  </span>
                )}
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
