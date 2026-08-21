"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "../ui/dialog";
import { Button } from "../ui/button";
import { RecoveryBatch } from "@/lib/types";
import { formatINR } from "@/lib/utils";
import { approveRecoveryBatch } from "@/lib/api";
import { useSimulationStore } from "@/lib/store/simulationStore";
import { ShieldCheck, Check, AlertTriangle, Lock, RotateCcw } from "lucide-react";

interface ApprovalModalProps {
  batch: RecoveryBatch;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onApproved?: () => void;
}

export function ApprovalModal({
  batch,
  open,
  onOpenChange,
  onApproved,
}: ApprovalModalProps) {
  const router = useRouter();
  const [approving, setApproving] = useState(false);
  const { initBatch, startSimulation } = useSimulationStore();

  const handleApprove = async () => {
    setApproving(true);
    try {
      await approveRecoveryBatch(batch.id);
      initBatch(batch.id, batch.plannedCount, batch.failureThresholdPercent);
      startSimulation(batch.id === "RB-025"); // if auto-stop demo batch, trip failure

      onOpenChange(false);
      if (onApproved) {
        onApproved();
      } else {
        router.push(`/recovery/${batch.id}`);
      }
    } catch (err) {
      console.error("Failed to approve batch:", err);
    } finally {
      setApproving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-xl p-6">
        <DialogHeader>
          <div className="flex items-center gap-2 text-violet-600 dark:text-violet-400">
            <ShieldCheck className="w-5 h-5" />
            <span className="text-xs font-semibold uppercase tracking-wider">Financial Authorization</span>
          </div>
          <DialogTitle className="text-lg font-bold text-foreground mt-1">
            Approve Recovery Batch {batch.id}
          </DialogTitle>
          <DialogDescription className="text-xs text-muted-foreground">
            You are authorizing a bounded, safety-constrained automated recovery workflow.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 my-2 text-xs">
          {/* Summary Box */}
          <div className="rounded-lg border border-border/80 bg-muted/30 p-4 space-y-2.5">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <span className="text-[10px] uppercase font-semibold text-muted-foreground">Action</span>
                <p className="font-semibold text-foreground mt-0.5">{batch.action}</p>
              </div>
              <div>
                <span className="text-[10px] uppercase font-semibold text-muted-foreground">Eligible Transactions</span>
                <p className="font-semibold text-foreground mt-0.5 font-mono">{batch.eligibleCount} records</p>
              </div>
              <div>
                <span className="text-[10px] uppercase font-semibold text-muted-foreground">Estimated Recoverable</span>
                <p className="font-semibold text-emerald-600 dark:text-emerald-400 mt-0.5 font-mono">
                  {formatINR(batch.expectedRecoveryMin)} – {formatINR(batch.expectedRecoveryMax)}
                </p>
              </div>
              <div>
                <span className="text-[10px] uppercase font-semibold text-muted-foreground">Maximum Exposure</span>
                <p className="font-semibold text-foreground mt-0.5 font-mono">{formatINR(batch.maxExposure)}</p>
              </div>
              <div>
                <span className="text-[10px] uppercase font-semibold text-muted-foreground">Maximum Retries</span>
                <p className="font-semibold text-foreground mt-0.5 font-mono">{batch.retryLimit} attempt</p>
              </div>
              <div>
                <span className="text-[10px] uppercase font-semibold text-muted-foreground">Stopping Condition</span>
                <p className="font-semibold text-amber-700 dark:text-amber-400 mt-0.5 font-mono">
                  Auto-stop if failure &gt; {batch.failureThresholdPercent}%
                </p>
              </div>
            </div>
          </div>

          {/* Safety Checklist */}
          <div className="space-y-2">
            <p className="font-semibold text-foreground text-xs uppercase tracking-wider">
              Safety & Compliance Checks
            </p>
            <div className="space-y-1.5 rounded-lg border border-border/60 bg-card p-3">
              {[
                { label: "Policy limits satisfied", desc: `Total exposure (${formatINR(batch.maxExposure)}) complies with merchant cap.` },
                { label: "Merchant approval required", desc: "Two-step financial admin authorization satisfied." },
                { label: "Duplicate protection enabled", desc: "Idempotency keys generated for all eligible transactions." },
                { label: "Stop condition configured", desc: `Circuit breaker set to halt immediately at ${batch.failureThresholdPercent}% failure rate.` },
                { label: "Idempotency protection enabled", desc: "Guarantees zero duplicate debit attempts." },
              ].map((check, i) => (
                <div key={i} className="flex items-start gap-2 text-xs">
                  <div className="mt-0.5 p-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 shrink-0">
                    <Check className="w-3 h-3 stroke-[2.5]" />
                  </div>
                  <div>
                    <span className="font-medium text-foreground">{check.label}</span>
                    <span className="text-muted-foreground text-[11px] ml-1.5">— {check.desc}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <DialogFooter className="gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onOpenChange(false)}
            disabled={approving}
            className="text-xs"
          >
            Cancel
          </Button>
          <Button
            variant="fintech"
            size="sm"
            onClick={handleApprove}
            disabled={approving}
            className="gap-1.5 text-xs font-semibold"
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            {approving ? "Authorizing..." : "Approve & Start Recovery"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
