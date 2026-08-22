"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { getRiskCases } from "@/lib/api";
import { RiskCase, RiskSeverity, RiskStatus, RiskType } from "@/lib/types";
import { formatINR, formatDateTime } from "@/lib/utils";
import {
  Table,
  TableHeader,
  TableRow,
  TableHead,
  TableBody,
  TableCell,
} from "@/components/ui/table";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { SeverityBadge } from "@/components/ui/severityBadge";
import { StatusBadge } from "@/components/ui/statusBadge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Search,
  Filter,
  ArrowUpDown,
  RotateCcw,
  AlertTriangle,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";

export default function RiskCasesPage() {
  const router = useRouter();
  const [cases, setCases] = useState<RiskCase[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState<RiskSeverity | "ALL">("ALL");
  const [statusFilter, setStatusFilter] = useState<RiskStatus | "ALL">("ALL");
  const [riskTypeFilter, setRiskTypeFilter] = useState<RiskType | "ALL">("ALL");

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const data = await getRiskCases({
          search,
          severity: severityFilter,
          status: statusFilter,
          riskType: riskTypeFilter,
        });
        setCases(data);
      } catch (err) {
        console.error("Failed to load risk cases:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [search, severityFilter, statusFilter, riskTypeFilter]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-border/60">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-foreground">
            Revenue Risk Cases
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground mt-0.5">
            Identify, prioritize, and investigate revenue leakage across merchant payment channels.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Link href="/investigations/INV-001">
            <Button variant="outline" size="sm" className="h-8 gap-1.5 text-xs">
              <ShieldCheck className="w-3.5 h-3.5 text-violet-500" />
              Latest AI Investigation
            </Button>
          </Link>
        </div>
      </div>

      {/* Filter Bar */}
      <Card className="p-3 bg-card border-border/80 shadow-xs">
        <div className="flex flex-col md:flex-row items-center gap-3">
          {/* Search Input */}
          <div className="relative flex-1 w-full">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search by case ID, title, root cause, or bank..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full h-8 pl-8 pr-3 text-xs bg-background border border-input rounded-md focus:outline-none focus:ring-1 focus:ring-ring text-foreground placeholder:text-muted-foreground"
            />
          </div>

          {/* Select Filters */}
          <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
            {/* Severity Filter */}
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value as RiskSeverity | "ALL")}
              className="h-8 px-2.5 text-xs bg-background border border-input rounded-md text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as RiskStatus | "ALL")}
              className="h-8 px-2.5 text-xs bg-background border border-input rounded-md text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            >
              <option value="ALL">All Statuses</option>
              <option value="OPEN">Open</option>
              <option value="INVESTIGATING">Investigating</option>
              <option value="RECOVERY_PLANNED">Recovery Planned</option>
              <option value="RECOVERING">Recovering</option>
              <option value="RESOLVED">Resolved</option>
            </select>

            {/* Risk Type Filter */}
            <select
              value={riskTypeFilter}
              onChange={(e) => setRiskTypeFilter(e.target.value as RiskType | "ALL")}
              className="h-8 px-2.5 text-xs bg-background border border-input rounded-md text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            >
              <option value="ALL">All Risk Types</option>
              <option value="PAYMENT_DEGRADATION">Payment Degradation</option>
              <option value="CHECKOUT_ABANDONMENT">Checkout Abandonment</option>
              <option value="SUBSCRIPTION_FAILURES">Subscription Failures</option>
              <option value="GATEWAY_LATENCY">Gateway Latency</option>
            </select>

            {(search || severityFilter !== "ALL" || statusFilter !== "ALL" || riskTypeFilter !== "ALL") && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setSearch("");
                  setSeverityFilter("ALL");
                  setStatusFilter("ALL");
                  setRiskTypeFilter("ALL");
                }}
                className="h-8 px-2 text-xs text-muted-foreground hover:text-foreground"
              >
                Reset
              </Button>
            )}
          </div>
        </div>
      </Card>

      {/* Risk Cases Table */}
      <Card className="border-border/80 shadow-xs overflow-hidden">
        {loading ? (
          <div className="p-6 space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-12 w-full rounded" />
            ))}
          </div>
        ) : (
          <div className="overflow-x-auto w-full">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[100px]">Case ID</TableHead>
                  <TableHead>Risk Type & Details</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Root Cause</TableHead>
                  <TableHead className="text-right">Revenue at Risk</TableHead>
                  <TableHead className="text-right">Recoverable</TableHead>
                  <TableHead className="text-center">Confidence</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {cases.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center py-12 text-muted-foreground">
                      <div className="flex flex-col items-center justify-center space-y-2">
                        <AlertTriangle className="w-8 h-8 opacity-30" />
                        <p className="font-semibold text-sm">No revenue risk cases found</p>
                        <p className="text-xs text-muted-foreground">
                          Try adjusting your filters or search criteria.
                        </p>
                      </div>
                    </TableCell>
                  </TableRow>
                ) : (
                  cases.map((rc) => (
                    <TableRow
                      key={rc.id}
                      onClick={() => router.push(`/risk-cases/${rc.id}`)}
                      className="cursor-pointer transition-colors hover:bg-muted/50"
                    >
                      <TableCell className="font-mono font-bold text-foreground">
                        {rc.id}
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-col">
                          <span className="font-semibold text-foreground">{rc.title}</span>
                          <span className="text-[11px] text-muted-foreground">
                            {rc.riskType.replace("_", " ")}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <SeverityBadge severity={rc.severity} />
                      </TableCell>
                      <TableCell className="max-w-[240px] truncate text-muted-foreground text-xs" title={rc.rootCause}>
                        {rc.rootCause}
                      </TableCell>
                      <TableCell className="text-right font-mono font-semibold text-rose-600 dark:text-rose-400">
                        {formatINR(rc.revenueAtRisk)}
                      </TableCell>
                      <TableCell className="text-right font-mono font-semibold text-emerald-600 dark:text-emerald-400">
                        {formatINR(rc.recoverableRevenue)}
                      </TableCell>
                      <TableCell className="text-center">
                        <span className="font-mono text-xs font-semibold px-1.5 py-0.5 rounded bg-muted">
                          {rc.confidenceScore}%
                        </span>
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={rc.status} />
                      </TableCell>
                      <TableCell className="text-right" onClick={(e) => e.stopPropagation()}>
                        <Link href={`/risk-cases/${rc.id}`}>
                          <Button size="sm" variant="outline" className="h-7 text-xs gap-1">
                            Investigate <ArrowRight className="w-3 h-3" />
                          </Button>
                        </Link>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        )}
      </Card>
    </div>
  );
}
