"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { getRecoveryBatches } from "@/lib/api";
import { RecoveryBatch } from "@/lib/types";
import { BatchTable } from "@/components/recovery/BatchTable";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { RotateCcw, Plus, PlayCircle, ShieldCheck } from "lucide-react";

export default function RecoveryOperationsPage() {
  const [batches, setBatches] = useState<RecoveryBatch[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await getRecoveryBatches();
      setBatches(data);
    } catch (err) {
      console.error("Failed to load recovery batches:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-border/60">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            Recovery Operations
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground mt-0.5">
            Monitor approved and active recovery workflows, manage authorization queues, and inspect execution health.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Link href="/recovery/RB-024">
            <Button variant="ai" size="sm" className="h-8 gap-1.5 text-xs font-semibold">
              <PlayCircle className="w-3.5 h-3.5" />
              Live Execution Monitor (RB-024)
            </Button>
          </Link>
        </div>
      </div>

      {loading ? (
        <div className="space-y-6">
          <div className="grid grid-cols-4 gap-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-24 rounded-lg" />
            ))}
          </div>
          <Skeleton className="h-96 rounded-lg" />
        </div>
      ) : (
        <BatchTable batches={batches} onRefresh={loadData} />
      )}
    </div>
  );
}
