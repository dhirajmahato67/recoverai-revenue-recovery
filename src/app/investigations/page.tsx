"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { getInvestigations } from "@/lib/api";
import { Investigation } from "@/lib/types";
import { formatINR } from "@/lib/utils";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/statusBadge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  FileSearch,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  AlertTriangle,
  Bot,
} from "lucide-react";

export default function InvestigationsDirectoryPage() {
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    async function load() {
      setLoading(true);
      try {
        const list = await getInvestigations();
        if (!isMounted) return;
        setInvestigations(list);
      } catch (err) {
        console.error("Failed to load investigations:", err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    load();
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-border/60">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <FileSearch className="w-6 h-6 text-violet-600 dark:text-violet-400" />
            AI Root Cause Investigations
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground mt-0.5">
            Automated diagnostic investigations and structured telemetry analysis for active revenue risk cases.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Link href="/ai-assistant">
            <Button variant="outline" size="sm" className="h-8 gap-1.5 text-xs">
              <Bot className="w-3.5 h-3.5 text-violet-500" />
              Open AI Copilot
            </Button>
          </Link>
        </div>
      </div>

      {/* Directory Grid */}
      {loading ? (
        <div className="space-y-4">
          <Skeleton className="h-44 w-full rounded-lg" />
          <Skeleton className="h-44 w-full rounded-lg" />
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {investigations.map((inv) => (
            <Card key={inv.id} className="border-border/80 bg-card shadow-xs hover:border-violet-500/30 transition-all">
              <CardContent className="p-6 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                <div className="space-y-3 flex-1">
                  <div className="flex items-center gap-2.5 flex-wrap">
                    <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-violet-500/10 text-violet-600 dark:text-violet-400 border border-violet-500/20">
                      {inv.id}
                    </span>
                    <span className="text-xs font-semibold text-muted-foreground">
                      Case: <Link href={`/risk-cases/${inv.caseId}`} className="text-foreground hover:underline font-mono">{inv.caseId}</Link>
                    </span>
                    <StatusBadge status={inv.status} />
                    <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-muted text-foreground">
                      {inv.confidenceScore}% Confidence
                    </span>
                  </div>

                  <div>
                    <h2 className="text-base font-bold text-foreground">
                      {inv.caseTitle}
                    </h2>
                    <p className="text-xs text-muted-foreground mt-1">
                      <strong className="text-foreground font-semibold">Question:</strong> {inv.question}
                    </p>
                  </div>

                  <div className="p-3 rounded-md bg-muted/40 border border-border/60 text-xs space-y-1">
                    <div className="font-semibold text-foreground flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-violet-500" />
                      Key Finding & Conclusion
                    </div>
                    <p className="text-muted-foreground leading-relaxed">{inv.finding}</p>
                    <p className="text-foreground font-medium">{inv.conclusion}</p>
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row lg:flex-col items-start lg:items-end justify-between gap-4 shrink-0 border-t lg:border-t-0 lg:border-l border-border/60 pt-4 lg:pt-0 lg:pl-6">
                  <div className="space-y-1 text-left lg:text-right">
                    <span className="text-[10px] uppercase font-semibold text-muted-foreground">Eligible Transactions</span>
                    <p className="font-mono font-bold text-foreground text-sm">
                      {inv.recommendedRecovery.eligibleTransactions} tx
                    </p>
                    <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-semibold block">
                      Max Exposure: {formatINR(inv.recommendedRecovery.maxExposure)}
                    </span>
                  </div>

                  <Link href={`/investigations/${inv.id}`}>
                    <Button variant="ai" size="sm" className="h-9 px-4 text-xs gap-1.5 font-semibold">
                      View Investigation Trace
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
