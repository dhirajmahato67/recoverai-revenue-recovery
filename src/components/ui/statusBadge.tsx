import React from "react";
import { Badge } from "./badge";
import { CheckCircle2, Clock, Play, AlertOctagon, XCircle, ArrowUpRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const normalized = status.toUpperCase();

  switch (normalized) {
    case "OPEN":
      return (
        <Badge variant="warning" className={cn("gap-1 font-medium", className)}>
          <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
          Open
        </Badge>
      );
    case "INVESTIGATING":
      return (
        <Badge variant="ai" className={cn("gap-1 font-medium", className)}>
          <span className="w-1.5 h-1.5 rounded-full bg-violet-500 animate-pulse" />
          Investigating
        </Badge>
      );
    case "RECOVERY_PLANNED":
      return (
        <Badge variant="info" className={cn("gap-1 font-medium", className)}>
          <Clock className="w-3 h-3" />
          Recovery Planned
        </Badge>
      );
    case "RECOVERING":
    case "RUNNING":
      return (
        <Badge variant="ai" className={cn("gap-1 font-medium", className)}>
          <Play className="w-2.5 h-2.5 fill-violet-600 dark:fill-violet-400" />
          Running
        </Badge>
      );
    case "PENDING_APPROVAL":
      return (
        <Badge variant="warning" className={cn("gap-1 font-medium", className)}>
          <Clock className="w-3 h-3 text-amber-600 dark:text-amber-400" />
          Pending Approval
        </Badge>
      );
    case "COMPLETED":
    case "RESOLVED":
    case "SUCCESS":
    case "APPROVED":
      return (
        <Badge variant="success" className={cn("gap-1 font-medium", className)}>
          <CheckCircle2 className="w-3 h-3" />
          {normalized === "RESOLVED" ? "Resolved" : normalized === "APPROVED" ? "Approved" : "Completed"}
        </Badge>
      );
    case "RECOVERED":
      return (
        <Badge variant="success" className={cn("gap-1 font-medium", className)}>
          <ArrowUpRight className="w-3 h-3" />
          Recovered
        </Badge>
      );
    case "STOPPED":
      return (
        <Badge variant="critical" className={cn("gap-1 font-semibold", className)}>
          <AlertOctagon className="w-3 h-3 text-rose-600 dark:text-rose-400" />
          STOPPED
        </Badge>
      );
    case "FAILED":
    case "REJECTED":
      return (
        <Badge variant="critical" className={cn("gap-1 font-medium", className)}>
          <XCircle className="w-3 h-3" />
          {normalized === "REJECTED" ? "Rejected" : "Failed"}
        </Badge>
      );
    default:
      return <Badge variant="neutral" className={className}>{status}</Badge>;
  }
}
