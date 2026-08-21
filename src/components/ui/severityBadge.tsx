import React from "react";
import { RiskSeverity } from "@/lib/types";
import { Badge } from "./badge";
import { AlertCircle, AlertTriangle, Info } from "lucide-react";
import { cn } from "@/lib/utils";

interface SeverityBadgeProps {
  severity: RiskSeverity;
  className?: string;
}

export function SeverityBadge({ severity, className }: SeverityBadgeProps) {
  switch (severity) {
    case "CRITICAL":
      return (
        <Badge variant="critical" className={cn("font-semibold gap-1", className)}>
          <AlertCircle className="w-3 h-3 stroke-[2.5]" />
          CRITICAL
        </Badge>
      );
    case "HIGH":
      return (
        <Badge variant="critical" className={cn("font-semibold gap-1", className)}>
          <AlertCircle className="w-3 h-3 stroke-[2]" />
          HIGH
        </Badge>
      );
    case "MEDIUM":
      return (
        <Badge variant="warning" className={cn("font-medium gap-1", className)}>
          <AlertTriangle className="w-3 h-3 stroke-[2]" />
          MEDIUM
        </Badge>
      );
    case "LOW":
      return (
        <Badge variant="info" className={cn("font-normal gap-1", className)}>
          <Info className="w-3 h-3 stroke-[2]" />
          LOW
        </Badge>
      );
    default:
      return <Badge variant="neutral">{severity}</Badge>;
  }
}
