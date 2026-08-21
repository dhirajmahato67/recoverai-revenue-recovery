"use client";

import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/card";
import { formatINR } from "@/lib/utils";
import { RecoveryTrendPoint } from "@/lib/types";
import { RotateCcw, CheckCircle2, TrendingUp, DollarSign } from "lucide-react";

interface RecoveryPerformanceSectionProps {
  attempts: number;
  successful: number;
  recoveryRate: number;
  recoveredAmount: number;
  trendData: RecoveryTrendPoint[];
}

export function RecoveryPerformanceSection({
  attempts,
  successful,
  recoveryRate,
  recoveredAmount,
  trendData,
}: RecoveryPerformanceSectionProps) {
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="rounded-lg border border-border bg-popover p-2.5 shadow-xl text-xs space-y-1 min-w-[150px]">
          <p className="font-semibold text-foreground border-b border-border/60 pb-1">{label} 2026</p>
          <div className="flex justify-between text-muted-foreground">
            <span>Attempts:</span>
            <span className="font-semibold text-foreground">{payload[0]?.value} tx</span>
          </div>
          <div className="flex justify-between text-muted-foreground">
            <span>Successful:</span>
            <span className="font-semibold text-emerald-600 dark:text-emerald-400">{payload[1]?.value} tx</span>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="h-full flex flex-col justify-between">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <RotateCcw className="w-4 h-4 text-muted-foreground" />
            Recovery Performance
          </CardTitle>
          <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400">
            {recoveryRate}% Conversion Rate
          </span>
        </div>
        <CardDescription>
          Cumulative execution metrics across authorized bounded recovery batches.
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* KPI Mini-Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          <div className="p-3 rounded-md bg-muted/40 border border-border/60 space-y-0.5">
            <span className="text-[10px] uppercase font-semibold text-muted-foreground">Recovery Attempts</span>
            <p className="text-lg font-bold text-foreground font-mono">{attempts.toLocaleString("en-IN")}</p>
          </div>

          <div className="p-3 rounded-md bg-muted/40 border border-border/60 space-y-0.5">
            <span className="text-[10px] uppercase font-semibold text-muted-foreground">Successful</span>
            <p className="text-lg font-bold text-emerald-600 dark:text-emerald-400 font-mono">
              {successful.toLocaleString("en-IN")}
            </p>
          </div>

          <div className="p-3 rounded-md bg-muted/40 border border-border/60 space-y-0.5">
            <span className="text-[10px] uppercase font-semibold text-muted-foreground">Recovery Rate</span>
            <p className="text-lg font-bold text-foreground font-mono">{recoveryRate}%</p>
          </div>

          <div className="p-3 rounded-md bg-emerald-500/10 border border-emerald-500/20 space-y-0.5">
            <span className="text-[10px] uppercase font-semibold text-emerald-800 dark:text-emerald-300">Recovered Revenue</span>
            <p className="text-lg font-bold text-emerald-700 dark:text-emerald-400 font-mono">
              {formatINR(recoveredAmount)}
            </p>
          </div>
        </div>

        {/* Daily Recovery Mini Chart */}
        <div>
          <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider mb-2">
            Recovery Volume by Day
          </p>
          <div className="h-40 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trendData} margin={{ top: 5, right: 0, left: -25, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" opacity={0.6} />
                <XAxis
                  dataKey="date"
                  stroke="hsl(var(--muted-foreground))"
                  fontSize={10}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  stroke="hsl(var(--muted-foreground))"
                  fontSize={10}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="attempts" name="Attempts" fill="hsl(var(--muted-foreground)/0.3)" radius={[3, 3, 0, 0]} />
                <Bar dataKey="successful" name="Successful" fill="#10b981" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
