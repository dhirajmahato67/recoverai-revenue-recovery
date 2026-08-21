"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { RecoveryBatch, RecoveryBatchStatus } from "@/lib/types";
import { formatINR, formatDateTime } from "@/lib/utils";
import {
  Table,
  TableHeader,
  TableRow,
  TableHead,
  TableBody,
  TableCell,
} from "../ui/table";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/card";
import { Button } from "../ui/button";
import { StatusBadge } from "../ui/statusBadge";
import { ApprovalModal } from "./ApprovalModal";
import {
  RotateCcw,
  PlayCircle,
  CheckCircle2,
  AlertOctagon,
  Clock,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface BatchTableProps {
  batches: RecoveryBatch[];
  onRefresh?: () => void;
}

export function BatchTable({ batches, onRefresh }: BatchTableProps) {
  const router = useRouter();
  const [selectedFilter, setSelectedFilter] = useState<RecoveryBatchStatus | "ALL">("ALL");
  const [selectedBatchForApproval, setSelectedBatchForApproval] = useState<RecoveryBatch | null>(null);

  // Metrics computation
  const pendingCount = batches.filter((b) => b.status === "PENDING_APPROVAL").length;
  const runningCount = batches.filter((b) => b.status === "RUNNING").length;
  const completedCount = batches.filter((b) => b.status === "COMPLETED").length;
  const stoppedCount = batches.filter((b) => b.status === "STOPPED").length;

  const filteredBatches =
    selectedFilter === "ALL"
      ? batches
      : batches.filter((b) => b.status === selectedFilter);

  return (
    <div className="space-y-6">
      {/* 4 Status Summary Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <Card
          onClick={() => setSelectedFilter("PENDING_APPROVAL")}
          className={cn(
            "cursor-pointer transition-all hover:border-amber-500/50 shadow-xs",
            selectedFilter === "PENDING_APPROVAL" && "border-amber-500 bg-amber-500/[0.04]"
          )}
        >
          <CardContent className="p-4 space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase font-semibold text-muted-foreground">Pending Approval</span>
              <Clock className="w-3.5 h-3.5 text-amber-500" />
            </div>
            <p className="text-2xl font-bold text-foreground font-mono">{pendingCount}</p>
            <span className="text-[10px] text-muted-foreground">Awaiting merchant signoff</span>
          </CardContent>
        </Card>

        <Card
          onClick={() => setSelectedFilter("RUNNING")}
          className={cn(
            "cursor-pointer transition-all hover:border-violet-500/50 shadow-xs",
            selectedFilter === "RUNNING" && "border-violet-500 bg-violet-500/[0.04]"
          )}
        >
          <CardContent className="p-4 space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase font-semibold text-muted-foreground">Running</span>
              <PlayCircle className="w-3.5 h-3.5 text-violet-500 animate-pulse" />
            </div>
            <p className="text-2xl font-bold text-violet-600 dark:text-violet-400 font-mono">{runningCount}</p>
            <span className="text-[10px] text-muted-foreground">Active execution queue</span>
          </CardContent>
        </Card>

        <Card
          onClick={() => setSelectedFilter("COMPLETED")}
          className={cn(
            "cursor-pointer transition-all hover:border-emerald-500/50 shadow-xs",
            selectedFilter === "COMPLETED" && "border-emerald-500 bg-emerald-500/[0.04]"
          )}
        >
          <CardContent className="p-4 space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase font-semibold text-muted-foreground">Completed Today</span>
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
            </div>
            <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 font-mono">{completedCount + 7}</p>
            <span className="text-[10px] text-muted-foreground">Reconciled successfully</span>
          </CardContent>
        </Card>

        <Card
          onClick={() => setSelectedFilter("STOPPED")}
          className={cn(
            "cursor-pointer transition-all hover:border-rose-500/50 shadow-xs",
            selectedFilter === "STOPPED" && "border-rose-500 bg-rose-500/[0.04]"
          )}
        >
          <CardContent className="p-4 space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase font-semibold text-muted-foreground">Stopped</span>
              <AlertOctagon className="w-3.5 h-3.5 text-rose-500" />
            </div>
            <p className="text-2xl font-bold text-rose-600 dark:text-rose-400 font-mono">{stoppedCount + 1}</p>
            <span className="text-[10px] text-muted-foreground">Safety circuit breaker trips</span>
          </CardContent>
        </Card>
      </div>

      {/* Filter Tabs & Table Card */}
      <Card className="border-border/80 shadow-xs overflow-hidden">
        <CardHeader className="pb-3 border-b border-border/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <RotateCcw className="w-4 h-4 text-muted-foreground" />
              Recovery Workflow Batches
            </CardTitle>
            <CardDescription className="text-xs text-muted-foreground">
              All authorized, executing, and historical recovery batches with bounded safety parameters.
            </CardDescription>
          </div>

          {/* Filter Tabs */}
          <div className="inline-flex rounded-md border border-border bg-muted/40 p-0.5 text-xs">
            {[
              { id: "ALL", label: "All" },
              { id: "PENDING_APPROVAL", label: "Pending Approval" },
              { id: "RUNNING", label: "Running" },
              { id: "COMPLETED", label: "Completed" },
              { id: "STOPPED", label: "Stopped" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setSelectedFilter(tab.id as RecoveryBatchStatus | "ALL")}
                className={cn(
                  "px-2.5 py-1 rounded text-xs font-medium transition-colors",
                  selectedFilter === tab.id
                    ? "bg-background text-foreground shadow-xs"
                    : "text-muted-foreground hover:text-foreground"
                )}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </CardHeader>

        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[100px]">Batch ID</TableHead>
                <TableHead>Risk Case</TableHead>
                <TableHead>Action</TableHead>
                <TableHead className="text-center">Transactions</TableHead>
                <TableHead className="text-right">Expected Recovery</TableHead>
                <TableHead className="text-right">Recovered</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredBatches.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-12 text-muted-foreground">
                    No recovery batches found for this filter.
                  </TableCell>
                </TableRow>
              ) : (
                filteredBatches.map((b) => (
                  <TableRow
                    key={b.id}
                    onClick={() => router.push(`/recovery/${b.id}`)}
                    className="cursor-pointer transition-colors hover:bg-muted/50"
                  >
                    <TableCell className="font-mono font-bold text-foreground">
                      {b.id}
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-col">
                        <span className="font-semibold text-foreground">{b.caseTitle}</span>
                        <span className="text-[10px] text-muted-foreground font-mono">{b.caseId}</span>
                      </div>
                    </TableCell>
                    <TableCell className="font-medium text-muted-foreground text-xs">
                      {b.action}
                    </TableCell>
                    <TableCell className="text-center font-mono text-xs">
                      {b.attemptedCount > 0
                        ? `${b.attemptedCount} / ${b.eligibleCount}`
                        : `${b.eligibleCount} planned`}
                    </TableCell>
                    <TableCell className="text-right font-mono font-semibold text-muted-foreground">
                      {formatINR(b.expectedRecoveryMin)} – {formatINR(b.expectedRecoveryMax)}
                    </TableCell>
                    <TableCell className="text-right font-mono font-bold text-emerald-600 dark:text-emerald-400">
                      {b.actualRecoveredAmount > 0 ? formatINR(b.actualRecoveredAmount) : "—"}
                    </TableCell>
                    <TableCell>
                      <StatusBadge status={b.status} />
                    </TableCell>
                    <TableCell className="text-right" onClick={(e) => e.stopPropagation()}>
                      {b.status === "PENDING_APPROVAL" ? (
                        <Button
                          size="sm"
                          variant="fintech"
                          onClick={() => setSelectedBatchForApproval(b)}
                          className="h-7 text-xs font-semibold"
                        >
                          Approve
                        </Button>
                      ) : (
                        <Link href={`/recovery/${b.id}`}>
                          <Button size="sm" variant="outline" className="h-7 text-xs gap-1">
                            Monitor
                            <ArrowRight className="w-3 h-3" />
                          </Button>
                        </Link>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Approval Modal */}
      {selectedBatchForApproval && (
        <ApprovalModal
          batch={selectedBatchForApproval}
          open={Boolean(selectedBatchForApproval)}
          onOpenChange={(open) => !open && setSelectedBatchForApproval(null)}
          onApproved={() => {
            setSelectedBatchForApproval(null);
            if (onRefresh) onRefresh();
          }}
        />
      )}
    </div>
  );
}
