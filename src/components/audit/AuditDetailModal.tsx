import React from "react";
import { AuditEvent } from "@/lib/types";
import { formatDateTime } from "@/lib/utils";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "../ui/dialog";
import { StatusBadge } from "../ui/statusBadge";
import { Button } from "../ui/button";
import {
  ShieldCheck,
  Lock,
  Cpu,
  User,
  Activity,
  Copy,
  Check,
  CheckCircle2,
  ExternalLink,
} from "lucide-react";
import Link from "next/link";
import { useState } from "react";

interface AuditDetailModalProps {
  event: AuditEvent | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function AuditDetailModal({
  event,
  open,
  onOpenChange,
}: AuditDetailModalProps) {
  const [copied, setCopied] = useState(false);

  if (!event) return null;

  const copyHash = () => {
    navigator.clipboard.writeText(event.cryptographicHash);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getActorIcon = (actorType: string) => {
    switch (actorType) {
      case "AI_AGENT":
        return <Cpu className="w-4 h-4 text-violet-500" />;
      case "POLICY_ENGINE":
        return <Lock className="w-4 h-4 text-amber-500" />;
      case "MERCHANT_ADMIN":
        return <User className="w-4 h-4 text-blue-500" />;
      default:
        return <Activity className="w-4 h-4 text-emerald-500" />;
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-xl p-6">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <span className="font-mono text-xs font-bold text-muted-foreground uppercase">
              Audit Event Record
            </span>
            <StatusBadge status={event.result} />
          </div>
          <DialogTitle className="text-lg font-bold text-foreground mt-1 flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-500" />
            {event.action}
          </DialogTitle>
          <DialogDescription className="text-xs text-muted-foreground">
            Immutable financial audit record • Event ID {event.id}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 my-2 text-xs">
          {/* Summary Box */}
          <div className="rounded-lg border border-border/80 bg-muted/30 p-4 space-y-2">
            <span className="text-[10px] uppercase font-semibold text-muted-foreground">Decision Summary</span>
            <p className="text-xs text-foreground font-medium leading-relaxed">
              {event.summary}
            </p>
          </div>

          {/* Grid Metadata */}
          <div className="grid grid-cols-2 gap-2.5">
            <div className="p-3 rounded-md bg-card border border-border/60 space-y-1">
              <span className="text-[10px] text-muted-foreground uppercase flex items-center gap-1">
                {getActorIcon(event.actorType)} Actor
              </span>
              <p className="font-semibold text-foreground">{event.actorName}</p>
              <span className="text-[10px] font-mono text-muted-foreground">Type: {event.actorType}</span>
            </div>

            <div className="p-3 rounded-md bg-card border border-border/60 space-y-1">
              <span className="text-[10px] text-muted-foreground uppercase">Target Entity</span>
              <p className="font-semibold text-foreground">{event.targetDisplay}</p>
              <span className="text-[10px] font-mono text-muted-foreground">ID: {event.targetId}</span>
            </div>

            <div className="p-3 rounded-md bg-card border border-border/60 space-y-1">
              <span className="text-[10px] text-muted-foreground uppercase">Timestamp</span>
              <p className="font-semibold text-foreground font-mono">{formatDateTime(event.timestamp)}</p>
            </div>

            <div className="p-3 rounded-md bg-card border border-border/60 space-y-1">
              <span className="text-[10px] text-muted-foreground uppercase">Origin Node / IP</span>
              <p className="font-mono text-foreground font-medium text-[11px] truncate">
                {event.ipAddress || "internal-dispatch-worker"}
              </p>
            </div>
          </div>

          {/* Policy Checks Passed */}
          {event.policyChecksPassed && event.policyChecksPassed.length > 0 && (
            <div className="space-y-1.5">
              <span className="text-[10px] font-semibold text-muted-foreground uppercase">
                Verified Safety Constraints
              </span>
              <div className="p-3 rounded-lg border border-border/60 bg-card space-y-1">
                {event.policyChecksPassed.map((check, i) => (
                  <div key={i} className="flex items-center gap-2 text-[11px] text-muted-foreground">
                    <CheckCircle2 className="w-3 h-3 text-emerald-500 shrink-0" />
                    <span>{check}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Cryptographic SHA-256 Proof */}
          <div className="p-3 rounded-lg border border-border/70 bg-muted/40 space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase font-semibold text-muted-foreground font-mono flex items-center gap-1">
                <Lock className="w-3 h-3 text-emerald-500" />
                SHA-256 Ledger Signature
              </span>
              <button
                onClick={copyHash}
                className="text-[10px] text-violet-600 dark:text-violet-400 font-semibold hover:underline flex items-center gap-1"
              >
                {copied ? <Check className="w-3 h-3 text-emerald-500" /> : <Copy className="w-3 h-3" />}
                {copied ? "Copied!" : "Copy"}
              </button>
            </div>
            <p className="font-mono text-[11px] text-foreground break-all bg-background p-2 rounded border border-border/60">
              {event.cryptographicHash}
            </p>
          </div>
        </div>

        <DialogFooter className="gap-2">
          <Button variant="outline" size="sm" onClick={() => onOpenChange(false)} className="text-xs">
            Close
          </Button>
          {event.targetType === "RECOVERY_BATCH" && (
            <Link href={`/recovery/${event.targetId}`} onClick={() => onOpenChange(false)}>
              <Button variant="fintech" size="sm" className="text-xs gap-1">
                View Batch <ExternalLink className="w-3 h-3" />
              </Button>
            </Link>
          )}
          {event.targetType === "RISK_CASE" && (
            <Link href={`/risk-cases/${event.targetId}`} onClick={() => onOpenChange(false)}>
              <Button variant="fintech" size="sm" className="text-xs gap-1">
                View Risk Case <ExternalLink className="w-3 h-3" />
              </Button>
            </Link>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
