"use client";

import React, { useState, useEffect } from "react";
import { getAuditLogs } from "@/lib/api";
import { AuditEvent, AuditActorType } from "@/lib/types";
import { formatDateTime } from "@/lib/utils";
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
import { StatusBadge } from "@/components/ui/statusBadge";
import { AuditDetailModal } from "@/components/audit/AuditDetailModal";
import { Skeleton } from "@/components/ui/skeleton";
import {
  ShieldCheck,
  Search,
  Lock,
  Cpu,
  User,
  Activity,
  ArrowRight,
  Filter,
} from "lucide-react";

export default function AuditTrailPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState("");
  const [actorFilter, setActorFilter] = useState<AuditActorType | "ALL">("ALL");

  // Selected event for modal
  const [selectedEvent, setSelectedEvent] = useState<AuditEvent | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const data = await getAuditLogs({
          search,
          actorType: actorFilter,
        });
        setEvents(data);
      } catch (err) {
        console.error("Failed to load audit logs:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [search, actorFilter]);

  const handleRowClick = (event: AuditEvent) => {
    setSelectedEvent(event);
    setModalOpen(true);
  };

  const getActorIcon = (actorType: string) => {
    switch (actorType) {
      case "AI_AGENT":
        return <Cpu className="w-3.5 h-3.5 text-violet-500" />;
      case "POLICY_ENGINE":
        return <Lock className="w-3.5 h-3.5 text-amber-500" />;
      case "MERCHANT_ADMIN":
        return <User className="w-3.5 h-3.5 text-blue-500" />;
      default:
        return <Activity className="w-3.5 h-3.5 text-emerald-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-border/60">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <ShieldCheck className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
            Audit Trail
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground mt-0.5">
            Every financial decision, AI diagnostic run, and recovery authorization is recorded with cryptographic integrity proofs.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs px-2.5 py-1 rounded bg-muted font-mono font-medium text-muted-foreground">
            Ledger: SHA-256 Verified
          </span>
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
              placeholder="Search by event ID (AUD-901), action, actor name, or target..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full h-8 pl-8 pr-3 text-xs bg-background border border-input rounded-md focus:outline-none focus:ring-1 focus:ring-ring text-foreground placeholder:text-muted-foreground"
            />
          </div>

          {/* Actor Select */}
          <div className="flex items-center gap-2 w-full md:w-auto">
            <select
              value={actorFilter}
              onChange={(e) => setActorFilter(e.target.value as AuditActorType | "ALL")}
              className="h-8 px-2.5 text-xs bg-background border border-input rounded-md text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            >
              <option value="ALL">All Actors</option>
              <option value="AI_AGENT">AI Agent</option>
              <option value="POLICY_ENGINE">Policy Engine</option>
              <option value="MERCHANT_ADMIN">Merchant Admin</option>
              <option value="SYSTEM">System Dispatcher</option>
            </select>

            {(search || actorFilter !== "ALL") && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setSearch("");
                  setActorFilter("ALL");
                }}
                className="h-8 px-2 text-xs text-muted-foreground hover:text-foreground"
              >
                Reset
              </Button>
            )}
          </div>
        </div>
      </Card>

      {/* Audit Table */}
      <Card className="border-border/80 shadow-xs overflow-hidden">
        {loading ? (
          <div className="p-6 space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-12 w-full rounded" />
            ))}
          </div>
        ) : (
          <div className="overflow-x-auto w-full">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[100px]">Time</TableHead>
                  <TableHead>Actor</TableHead>
                  <TableHead>Action</TableHead>
                  <TableHead>Target Entity</TableHead>
                  <TableHead>Summary / Details</TableHead>
                  <TableHead>Result</TableHead>
                  <TableHead className="text-right">Proof</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {events.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-12 text-muted-foreground">
                      No matching audit records found.
                    </TableCell>
                  </TableRow>
                ) : (
                  events.map((ev) => (
                    <TableRow
                      key={ev.id}
                      onClick={() => handleRowClick(ev)}
                      className="cursor-pointer transition-colors hover:bg-muted/50"
                    >
                      <TableCell className="font-mono text-xs text-foreground font-semibold">
                        {ev.timeDisplay}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1.5 font-medium text-foreground text-xs">
                          {getActorIcon(ev.actorType)}
                          <span>{ev.actorName}</span>
                        </div>
                      </TableCell>
                      <TableCell className="font-semibold text-foreground text-xs">
                        {ev.action}
                      </TableCell>
                      <TableCell>
                        <span className="font-mono text-xs text-muted-foreground">
                          {ev.targetDisplay}
                        </span>
                      </TableCell>
                      <TableCell className="max-w-[280px] truncate text-xs text-muted-foreground" title={ev.summary}>
                        {ev.summary}
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={ev.result} />
                      </TableCell>
                      <TableCell className="text-right font-mono text-[10px] text-muted-foreground opacity-60">
                        {ev.cryptographicHash.slice(0, 10)}...
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        )}
      </Card>

      {/* Audit Detail Modal */}
      <AuditDetailModal
        event={selectedEvent}
        open={modalOpen}
        onOpenChange={setModalOpen}
      />
    </div>
  );
}
