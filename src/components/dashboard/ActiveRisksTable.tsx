"use client";

import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
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
import { SeverityBadge } from "../ui/severityBadge";
import { StatusBadge } from "../ui/statusBadge";
import { formatINR } from "@/lib/utils";
import { RiskCase } from "@/lib/types";
import { ArrowRight, AlertTriangle } from "lucide-react";

interface ActiveRisksTableProps {
  riskCases: RiskCase[];
}

export function ActiveRisksTable({ riskCases }: ActiveRisksTableProps) {
  const router = useRouter();

  return (
    <Card className="col-span-full">
      <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 gap-2">
        <div>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-muted-foreground" />
            Active Revenue Risks
          </CardTitle>
          <CardDescription>
            Detected revenue leakage vectors ranked by priority, confidence, and recoverable value.
          </CardDescription>
        </div>
        <Link href="/risk-cases">
          <Button variant="ghost" size="sm" className="gap-1 text-xs">
            View all cases <ArrowRight className="w-3.5 h-3.5" />
          </Button>
        </Link>
      </CardHeader>

      <CardContent className="p-0 overflow-x-auto w-full">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[180px]">Risk</TableHead>
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
            {riskCases.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                  No active revenue risks detected.
                </TableCell>
              </TableRow>
            ) : (
              riskCases.map((rc) => (
                <TableRow
                  key={rc.id}
                  onClick={() => router.push(`/risk-cases/${rc.id}`)}
                  className="cursor-pointer transition-colors hover:bg-muted/50"
                >
                  <TableCell className="font-semibold text-foreground">
                    <div className="flex flex-col">
                      <span>{rc.title}</span>
                      <span className="text-[10px] text-muted-foreground font-mono">{rc.id}</span>
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
                        Investigate
                      </Button>
                    </Link>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
