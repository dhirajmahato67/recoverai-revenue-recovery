"use client";

import React from "react";
import { Button } from "../ui/button";
import {
  Play,
  Pause,
  FastForward,
  RotateCcw,
  StepForward,
  AlertTriangle,
  Sparkles,
} from "lucide-react";

interface SimulationControlBarProps {
  status: string;
  isPaused: boolean;
  onStart: (autoFail?: boolean) => void;
  onPause: () => void;
  onResume: () => void;
  onStep: () => void;
  onFastForward: () => void;
  onReset: () => void;
}

export function SimulationControlBar({
  status,
  isPaused,
  onStart,
  onPause,
  onResume,
  onStep,
  onFastForward,
  onReset,
}: SimulationControlBarProps) {
  const isRunning = status === "RUNNING";
  const isStopped = status === "STOPPED";
  const isCompleted = status === "COMPLETED";

  return (
    <div className="rounded-xl border border-border/80 bg-card p-3 shadow-xs flex flex-wrap items-center justify-between gap-3 text-xs">
      <div className="flex items-center gap-2">
        <span className="font-semibold text-foreground flex items-center gap-1.5 text-xs">
          <Sparkles className="w-3.5 h-3.5 text-violet-500" />
          Interactive Demo Controls:
        </span>
        <span className="text-[11px] text-muted-foreground hidden sm:inline">
          Test live transaction execution and safety circuit breakers.
        </span>
      </div>

      <div className="flex flex-wrap items-center gap-1.5">
        {/* Play / Pause / Resume */}
        {!isRunning && !isStopped && !isCompleted && (
          <Button
            variant="fintech"
            size="sm"
            onClick={() => onStart(false)}
            className="h-7 gap-1 text-xs font-semibold"
          >
            <Play className="w-3 h-3 fill-current" />
            Start Execution
          </Button>
        )}

        {isRunning && !isPaused && (
          <Button
            variant="outline"
            size="sm"
            onClick={onPause}
            className="h-7 gap-1 text-xs"
          >
            <Pause className="w-3 h-3" />
            Pause
          </Button>
        )}

        {isRunning && isPaused && (
          <Button
            variant="fintech"
            size="sm"
            onClick={onResume}
            className="h-7 gap-1 text-xs"
          >
            <Play className="w-3 h-3 fill-current" />
            Resume
          </Button>
        )}

        {/* Step 1 Tx */}
        <Button
          variant="outline"
          size="sm"
          onClick={onStep}
          disabled={isStopped || isCompleted}
          className="h-7 gap-1 text-xs"
          title="Process 1 transaction individually"
        >
          <StepForward className="w-3 h-3" />
          Step 1 Tx
        </Button>

        {/* Fast-Forward to Completed */}
        <Button
          variant="outline"
          size="sm"
          onClick={onFastForward}
          disabled={isCompleted}
          className="h-7 gap-1 text-xs font-medium text-emerald-700 dark:text-emerald-400 bg-emerald-500/5 hover:bg-emerald-500/10 border-emerald-500/30"
          title="Instantly reconcile 100% completed batch"
        >
          <FastForward className="w-3 h-3" />
          Fast-Forward
        </Button>

        {/* Trigger Failure Spike (Auto-Stop Circuit Breaker Demo) */}
        <Button
          variant="outline"
          size="sm"
          onClick={() => onStart(true)}
          disabled={isStopped}
          className="h-7 gap-1 text-xs font-medium text-rose-700 dark:text-rose-400 bg-rose-500/5 hover:bg-rose-500/10 border-rose-500/30"
          title="Simulate high failure rate to trip safety circuit breaker (>30%)"
        >
          <AlertTriangle className="w-3 h-3" />
          Trigger Auto-Stop Demo
        </Button>

        {/* Reset */}
        <Button
          variant="ghost"
          size="sm"
          onClick={onReset}
          className="h-7 gap-1 text-xs text-muted-foreground hover:text-foreground"
        >
          <RotateCcw className="w-3 h-3" />
          Reset
        </Button>
      </div>
    </div>
  );
}
