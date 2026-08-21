import React from "react";
import { Card, CardContent } from "../ui/card";
import { ArrowUpRight, ArrowDownRight, Minus, LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: string;
  subtitle?: string;
  change?: string;
  isPositive?: boolean;
  isNeutral?: boolean;
  icon?: LucideIcon;
  variant?: "default" | "critical" | "warning" | "success" | "ai";
}

export function MetricCard({
  title,
  value,
  subtitle,
  change,
  isPositive = true,
  isNeutral = false,
  icon: Icon,
  variant = "default",
}: MetricCardProps) {
  const getBorderAccent = () => {
    switch (variant) {
      case "critical":
        return "border-rose-500/30 bg-rose-500/[0.02]";
      case "warning":
        return "border-amber-500/30 bg-amber-500/[0.02]";
      case "success":
        return "border-emerald-500/30 bg-emerald-500/[0.02]";
      case "ai":
        return "border-violet-500/30 bg-violet-500/[0.02]";
      default:
        return "";
    }
  };

  return (
    <Card className={cn("transition-all hover:border-border/90 shadow-xs", getBorderAccent())}>
      <CardContent className="p-5 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            {title}
          </span>
          {Icon && (
            <div className="p-1.5 rounded-md bg-muted/60 text-muted-foreground">
              <Icon className="w-3.5 h-3.5" />
            </div>
          )}
        </div>

        <div className="space-y-1">
          <div className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground font-sans">
            {value}
          </div>

          <div className="flex items-center gap-1.5 flex-wrap text-xs">
            {change && (
              <span
                className={cn(
                  "inline-flex items-center gap-0.5 font-semibold px-1 py-0.2 rounded text-[11px]",
                  isNeutral
                    ? "text-muted-foreground bg-muted"
                    : isPositive
                    ? "text-emerald-700 bg-emerald-500/10 dark:text-emerald-400"
                    : "text-rose-700 bg-rose-500/10 dark:text-rose-400"
                )}
              >
                {!isNeutral && isPositive && <ArrowUpRight className="w-3 h-3" />}
                {!isNeutral && !isPositive && <ArrowDownRight className="w-3 h-3" />}
                {isNeutral && <Minus className="w-3 h-3" />}
                {change}
              </span>
            )}
            {subtitle && <span className="text-muted-foreground text-[11px]">{subtitle}</span>}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
