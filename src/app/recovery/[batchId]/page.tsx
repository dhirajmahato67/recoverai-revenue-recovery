"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { getRecoveryBatchById } from "@/lib/api";
import { RecoveryBatch } from "@/lib/types";
import { useSimulationStore } from "@/lib/store/simulationStore";
import { formatINR } from "@/lib/utils";
import { LiveExecutionProgress } from "@/components/recovery/LiveExecutionProgress";
import { StreamingActivityLog } from "@/components/recovery/StreamingActivityLog";
import { AutoStopAlertBanner } from "@/components/recovery/AutoStopAlertBanner";
import { RecoveryReconciliationCard } from "@/components/recovery/RecoveryReconciliationCard";
import { SimulationControlBar } from "@/components/recovery/SimulationControlBar";
import { ApprovalModal } from "@/components/recovery/ApprovalModal";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/statusBadge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  ChevronLeft,
  RotateCcw,
  ShieldCheck,
  Play,
  AlertTriangle,
  Receipt,
  FileSearch,
  Lock,
} from "lucide-react";

export default function RecoveryExecutionPage() {
  const params = useParams();
  const router = useRouter();
  const batchId = (params.batchId as string) || "RB-024";

  const [batch, setBatch] = useState<RecoveryBatch | null>(null);
  const [loading, setLoading] = useState(true);
  const [approvalModalOpen, setApprovalModalOpen] = useState(false);

  const simulation = useSimulationStore();

  useEffect(() => {
    let isMounted = true;
    async function load() {
      setLoading(true);
      try {
        const b = await getRecoveryBatchById(batchId);
        if (!isMounted) return;
        setBatch(b);
        if (b) {
          const simState = useSimulationStore.getState();
          if (simState.batchId !== b.id || simState.totalEligible !== b.eligibleCount) {
            simState.initBatch(b.id, b.plannedCount, b.failureThresholdPercent);
            if (b.status === "COMPLETED") {
              simState.fastForwardSimulation();
            } else if (b.status === "STOPPED") {
              simState.startSimulation(true);
            }
          }
        }
      } catch (err) {
        console.error("Failed to load batch:", err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    load();
    return () => {
      isMounted = false;
    };
  }, [batchId]);

  if (loading || !batch) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-20 w-full rounded-lg" />
        <Skeleton className="h-44 w-full rounded-lg" />
        <Skeleton className="h-80 w-full rounded-lg" />
      </div>
    );
  }

  const isPendingApproval = simulation.status === "PENDING_APPROVAL";
  const isRunning = simulation.status === "RUNNING";
  const isStopped = simulation.status === "STOPPED";
  const isCompleted = simulation.status === "COMPLETED";

  return (
    <div className="space-y-6">
      {/* Back Link & Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-border/60">
        <div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
            <Link
              href="/recovery"
              className="inline-flex items-center gap-1 hover:text-foreground transition-colors"
            >
              <ChevronLeft className="w-3 h-3" />
              Recovery Operations
            </Link>
            <span>/</span>
            <span className="font-semibold text-foreground">{simulation.batchId}</span>
          </div>
          <div className="flex items-center gap-3">
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-foreground">
              Recovery Execution Monitor — {simulation.batchId}
            </h1>
            <StatusBadge status={simulation.status} />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Link href={`/risk-cases/${batch.caseId || "RC-001"}`}>
            <Button variant="outline" size="sm" className="h-8 gap-1.5 text-xs">
              <FileSearch className="w-3.5 h-3.5 text-violet-500" />
              View Risk Case ({batch.caseId})
            </Button>
          </Link>
          <Link href="/audit">
            <Button variant="outline" size="sm" className="h-8 gap-1.5 text-xs">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
              Audit Trail
            </Button>
          </Link>
        </div>
      </div>

      {/* Interactive Simulation Control Bar */}
      <SimulationControlBar
        status={simulation.status}
        isPaused={simulation.isPaused}
        onStart={(autoFail) => simulation.startSimulation(autoFail)}
        onPause={() => simulation.pauseSimulation()}
        onResume={() => simulation.resumeSimulation()}
        onStep={() => simulation.stepSimulation()}
        onFastForward={() => simulation.fastForwardSimulation()}
        onReset={() => simulation.resetSimulation()}
      />

      {/* If Pending Approval Banner */}
      {isPendingApproval && (
        <Card className="border-amber-500/30 bg-amber-500/[0.03]">
          <CardContent className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <Lock className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                <h3 className="font-bold text-foreground text-sm">
                  Batch Requires Merchant Authorization
                </h3>
              </div>
              <p className="text-xs text-muted-foreground">
                In compliance with fintech safety policies, {simulation.totalEligible} transactions are queued and awaiting merchant approval.
              </p>
            </div>

            <Button
              variant="fintech"
              size="sm"
              onClick={() => setApprovalModalOpen(true)}
              className="gap-1.5 font-semibold text-xs shrink-0"
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              Authorize & Start Batch
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Circuit Breaker Auto-Stop Alert Banner */}
      {isStopped && (
        <AutoStopAlertBanner
          currentFailureRate={simulation.failureRate}
          failureThreshold={simulation.failureThresholdPercent}
          stopReason={simulation.stopReason}
        />
      )}

      {/* Recovery Completed Reconciliation Card */}
      {isCompleted && (
        <RecoveryReconciliationCard
          actualRecoveredAmount={simulation.recoveredAmount || 286000}
          plannedCount={simulation.totalPlanned}
          eligibleCount={simulation.totalEligible}
          attemptedCount={simulation.processedCount || 391}
          recoveredCount={simulation.successCount || 167}
          failedCount={simulation.failedCount || 224}
          expectedMin={batch.expectedRecoveryMin}
          expectedMax={batch.expectedRecoveryMax}
        />
      )}

      {/* Live Execution Progress & Metric Counters */}
      <LiveExecutionProgress
        batchId={simulation.batchId}
        status={simulation.status}
        processedCount={simulation.processedCount}
        totalPlanned={simulation.totalPlanned}
        totalEligible={simulation.totalEligible}
        successCount={simulation.successCount}
        failedCount={simulation.failedCount}
        skippedCount={simulation.skippedCount}
        recoveredAmount={simulation.recoveredAmount}
        failureRate={simulation.failureRate}
        failureThresholdPercent={simulation.failureThresholdPercent}
      />

      {/* Live Streaming Activity Log */}
      <StreamingActivityLog
        logs={simulation.logs}
        isRunning={isRunning && !simulation.isPaused}
      />

      {/* Approval Modal */}
      <ApprovalModal
        batch={batch}
        open={approvalModalOpen}
        onOpenChange={setApprovalModalOpen}
        onApproved={() => {
          setApprovalModalOpen(false);
        }}
      />
    </div>
  );
}
