"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { getInvestigationById, getRecoveryBatchById } from "@/lib/api";
import { Investigation, RecoveryBatch } from "@/lib/types";
import { InvestigationChecklist } from "@/components/investigation/InvestigationChecklist";
import { StructuredReasoningPanel } from "@/components/investigation/StructuredReasoningPanel";
import { ToolExecutionTimeline } from "@/components/investigation/ToolExecutionTimeline";
import { ApprovalModal } from "@/components/recovery/ApprovalModal";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ChevronLeft, RotateCcw, ShieldCheck, Sparkles, FileSearch, Bot } from "lucide-react";


export default function InvestigationDetailPage() {
  const params = useParams();
  const router = useRouter();
  const investigationId = (params.investigationId as string) || "INV-001";

  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [batch, setBatch] = useState<RecoveryBatch | null>(null);
  const [loading, setLoading] = useState(true);
  const [approvalModalOpen, setApprovalModalOpen] = useState(false);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const inv = await getInvestigationById(investigationId);
        setInvestigation(inv);
        const b = await getRecoveryBatchById("RB-024");
        setBatch(b);
      } catch (err) {
        console.error("Failed to load investigation:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [investigationId]);

  if (loading || !investigation) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-6 w-32" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-96 rounded-lg" />
          <Skeleton className="h-96 rounded-lg" />
        </div>
        <Skeleton className="h-64 rounded-lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back Link & Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-border/60">
        <div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
            <Link
              href="/risk-cases"
              className="inline-flex items-center gap-1 hover:text-foreground transition-colors"
            >
              <ChevronLeft className="w-3 h-3" />
              Risk Cases
            </Link>
            <span>/</span>
            <Link
              href={`/risk-cases/${investigation.caseId}`}
              className="font-semibold text-foreground hover:underline"
            >
              {investigation.caseId}
            </Link>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-violet-600 dark:text-violet-400" />
            AI Root Cause Investigation — {investigation.id}
          </h1>
        </div>

        <div className="flex items-center gap-2">
          <Link href={`/ai-assistant?inv=${investigation.id}`}>
            <Button variant="outline" size="sm" className="h-8 gap-1.5 text-xs font-semibold border-violet-500/30 text-violet-600 dark:text-violet-400 hover:bg-violet-500/10">
              <Bot className="w-3.5 h-3.5" />
              Ask RecoverAI
            </Button>
          </Link>
          <Link href={`/risk-cases/${investigation.caseId}`}>
            <Button variant="outline" size="sm" className="h-8 text-xs">
              View Risk Case
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
      </div>


      {/* Split-Screen: Left Checklist + Right Structured Reasoning */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
        <InvestigationChecklist
          steps={investigation.steps}
          question={investigation.question}
        />

        <StructuredReasoningPanel
          investigation={investigation}
          onReviewRecovery={() => setApprovalModalOpen(true)}
        />
      </div>

      {/* Technical Tool Execution Activity */}
      <ToolExecutionTimeline tools={investigation.toolExecutions} />

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
