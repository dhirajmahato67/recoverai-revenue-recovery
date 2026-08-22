"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { getRiskCaseById, getRecoveryBatchById } from "@/lib/api";
import { RiskCase, RecoveryBatch } from "@/lib/types";
import { formatINR } from "@/lib/utils";
import { SeverityBadge } from "@/components/ui/severityBadge";
import { StatusBadge } from "@/components/ui/statusBadge";
import { EvidenceCard } from "@/components/risk/EvidenceCard";
import { RootCauseTree } from "@/components/risk/RootCauseTree";
import { RecoveryPolicyCard } from "@/components/risk/RecoveryPolicyCard";
import { ApprovalModal } from "@/components/recovery/ApprovalModal";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  ChevronLeft,
  FileSearch,
  AlertTriangle,
  RotateCcw,
  Sparkles,
  Receipt,
} from "lucide-react";

export function RiskCaseDetailClient({ caseId }: { caseId?: string }) {
  const params = useParams();
  const activeCaseId = caseId || (params?.caseId as string) || "RC-001";

  const [riskCase, setRiskCase] = useState<RiskCase | null>(null);
  const [batch, setBatch] = useState<RecoveryBatch | null>(null);
  const [loading, setLoading] = useState(true);
  const [approvalModalOpen, setApprovalModalOpen] = useState(false);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const rc = await getRiskCaseById(activeCaseId);
        setRiskCase(rc);
        if (rc?.associatedBatchId) {
          const b = await getRecoveryBatchById(rc.associatedBatchId);
          setBatch(b);
        }
      } catch (err) {
        console.error("Failed to load risk case:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [activeCaseId]);

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-20 w-full rounded-lg" />
        <div className="grid grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-lg" />
          ))}
        </div>
        <Skeleton className="h-64 rounded-lg" />
      </div>
    );
  }

  if (!riskCase) {
    return (
      <div className="p-12 text-center space-y-4">
        <AlertTriangle className="w-10 h-10 text-rose-500 mx-auto" />
        <h2 className="text-lg font-bold">Risk Case Not Found</h2>
        <p className="text-xs text-muted-foreground">The requested case {activeCaseId} does not exist.</p>
        <Link href="/risk-cases">
          <Button variant="outline" size="sm">
            Back to Risk Cases
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back Link */}
      <div>
        <Link
          href="/risk-cases"
          className="inline-flex items-center gap-1 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
        >
          <ChevronLeft className="w-3.5 h-3.5" />
          Back to Revenue Risk Cases
        </Link>
      </div>

      {/* Case Header Card */}
      <Card className="border-border/80 bg-card shadow-xs">
        <CardContent className="p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2.5 flex-wrap">
              <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-muted text-foreground">
                {riskCase.id}
              </span>
              <h1 className="text-xl font-bold tracking-tight text-foreground">
                {riskCase.title}
              </h1>
              <SeverityBadge severity={riskCase.severity} />
              <StatusBadge status={riskCase.status} />
            </div>
            <p className="text-xs text-muted-foreground max-w-2xl leading-relaxed">
              {riskCase.description}
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <Link href={`/investigations/${riskCase.investigationId || "INV-00000000"}`}>
              <Button variant="ai" size="sm" className="h-8 gap-1.5 text-xs font-semibold">
                <Sparkles className="w-3.5 h-3.5" />
                View AI Investigation
              </Button>
            </Link>

            <Button
              variant="fintech"
              size="sm"
              onClick={() => setApprovalModalOpen(true)}
              className="h-8 gap-1.5 text-xs font-semibold"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Review Recovery Plan
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Risk Summary 4-KPI Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <Card className="border-rose-500/20 bg-rose-500/[0.02]">
          <CardContent className="p-4 space-y-1">
            <span className="text-[10px] uppercase font-semibold text-muted-foreground">Revenue at Risk</span>
            <p className="text-xl sm:text-2xl font-bold text-rose-600 dark:text-rose-400 font-mono">
              {formatINR(riskCase.revenueAtRisk)}
            </p>
            <span className="text-[10px] text-muted-foreground">Direct financial exposure</span>
          </CardContent>
        </Card>

        <Card className="border-emerald-500/20 bg-emerald-500/[0.02]">
          <CardContent className="p-4 space-y-1">
            <span className="text-[10px] uppercase font-semibold text-muted-foreground">Estimated Recoverable</span>
            <p className="text-xl sm:text-2xl font-bold text-emerald-600 dark:text-emerald-400 font-mono">
              {formatINR(riskCase.recoverableRevenue)}
            </p>
            <span className="text-[10px] text-muted-foreground">
              {Math.round((riskCase.recoverableRevenue / riskCase.revenueAtRisk) * 100)}% recoverable ratio
            </span>
          </CardContent>
        </Card>

        <Card className="border-violet-500/20 bg-violet-500/[0.02]">
          <CardContent className="p-4 space-y-1">
            <span className="text-[10px] uppercase font-semibold text-muted-foreground">Diagnostic Confidence</span>
            <p className="text-xl sm:text-2xl font-bold text-violet-600 dark:text-violet-400 font-mono">
              {riskCase.confidenceScore}%
            </p>
            <span className="text-[10px] text-muted-foreground">Telemetry signal strength</span>
          </CardContent>
        </Card>

        <Card className="border-border/80 bg-card">
          <CardContent className="p-4 space-y-1">
            <span className="text-[10px] uppercase font-semibold text-muted-foreground">Affected Transactions</span>
            <p className="text-xl sm:text-2xl font-bold text-foreground font-mono">
              {riskCase.affectedTransactionsCount} tx
            </p>
            <Link href="/transactions" className="text-[10px] text-violet-600 dark:text-violet-400 hover:underline flex items-center gap-0.5">
              <Receipt className="w-2.5 h-2.5" /> View affected records
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Evidence Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider">
            Diagnostic Evidence & Signal Deltas
          </h3>
          <span className="text-xs text-muted-foreground">Compared with 7-day trailing baseline</span>
        </div>
        <EvidenceCard evidence={riskCase.evidence} />
      </div>

      {/* Root Cause Decision Tree */}
      <Card className="border-border/80 shadow-xs">
        <CardHeader className="pb-3 border-b border-border/60">
          <CardTitle className="text-sm font-semibold flex items-center gap-2">
            <FileSearch className="w-4 h-4 text-violet-600 dark:text-violet-400" />
            Root Cause Diagnosis Decision Tree
          </CardTitle>
          <CardDescription>
            Multi-stage root cause isolation performed by RecoverAI diagnostic pipelines.
          </CardDescription>
        </CardHeader>
        <CardContent className="p-6">
          <RootCauseTree tree={riskCase.rootCauseTree} />
        </CardContent>
      </Card>

      {/* Recommended Recovery Policy */}
      <RecoveryPolicyCard
        action={riskCase.recommendedAction}
        batchId={riskCase.associatedBatchId || "RB-024"}
        onReviewPlan={() => setApprovalModalOpen(true)}
      />

      {/* Approval Modal */}
      {batch && (
        <ApprovalModal
          batch={batch}
          open={approvalModalOpen}
          onOpenChange={setApprovalModalOpen}
        />
      )}
    </div>
  );
}
