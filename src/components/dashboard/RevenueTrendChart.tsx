"use client";

import React from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/card";
import { formatINR } from "@/lib/utils";
import { RevenueTrendPoint, DashboardTimeframe } from "@/lib/types";
import { Info, Loader2 } from "lucide-react";

interface RevenueTrendChartProps {
  data: RevenueTrendPoint[];
  timeframe?: DashboardTimeframe;
  onTimeframeChange?: (tf: DashboardTimeframe) => void;
  hasSufficientHistory?: boolean;
  availableFrom?: string;
  availableTo?: string;
  isLoading?: boolean;
}

export function RevenueTrendChart({
  data,
  timeframe = "24h",
  onTimeframeChange,
  hasSufficientHistory = true,
  availableFrom,
  availableTo,
  isLoading = false,
}: RevenueTrendChartProps) {
  const timeframeOptions: { label: string; value: DashboardTimeframe }[] = [
    { label: "24H", value: "24h" },
    { label: "7D", value: "7d" },
    { label: "30D", value: "30d" },
    { label: "90D", value: "90d" },
  ];

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="rounded-lg border border-border bg-popover p-3 shadow-xl text-xs space-y-1.5 min-w-[170px]">
          <p className="font-semibold text-foreground border-b border-border/60 pb-1">{label}</p>
          <div className="space-y-1">
            <div className="flex items-center justify-between text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-slate-800 dark:bg-slate-200" />
                Revenue:
              </span>
              <span className="font-semibold text-foreground">{formatINR(payload[0]?.value || 0)}</span>
            </div>
            <div className="flex items-center justify-between text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-rose-500" />
                Revenue at Risk:
              </span>
              <span className="font-semibold text-rose-600 dark:text-rose-400">{formatINR(payload[1]?.value || 0)}</span>
            </div>
            <div className="flex items-center justify-between text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                Recovered:
              </span>
              <span className="font-semibold text-emerald-600 dark:text-emerald-400">{formatINR(payload[2]?.value || 0)}</span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  const getNoticeMessage = () => {
    if (availableFrom && availableTo) {
      return `Showing available telemetry from ${availableFrom} to ${availableTo}.`;
    }
    switch (timeframe) {
      case "7d":
        return "Only the last 24 hours of telemetry are currently available. The selected 7-day view is therefore limited to available data.";
      case "30d":
        return "Only the last 24 hours of telemetry are currently available. The selected 30-day view is therefore limited to available data.";
      case "90d":
        return "Only the last 24 hours of telemetry are currently available. The selected 90-day view is therefore limited to available data.";
      default:
        return "Only the last 24 hours of telemetry are currently available. Visualizing available data for the active period.";
    }
  };

  return (
    <Card className="col-span-full">
      <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 gap-2">
        <div>
          <CardTitle className="flex items-center gap-2">
            <span>Revenue & Revenue at Risk</span>
            {timeframe !== "24h" && (
              <span className="text-xs font-normal text-amber-600 dark:text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                24H Telemetry Window
              </span>
            )}
          </CardTitle>
          <CardDescription>
            Historical processed volume compared with detected risk leakage and recovered funds.
          </CardDescription>
        </div>
        <div className="inline-flex rounded-md border border-border bg-muted/40 p-0.5 text-xs">
          {timeframeOptions.map((opt) => (
            <button
              key={opt.value}
              onClick={() => onTimeframeChange?.(opt.value)}
              className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                timeframe === opt.value
                  ? "bg-background text-foreground shadow-xs"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {(timeframe !== "24h" || !hasSufficientHistory) && (
          <div className="flex items-start sm:items-center gap-2 p-2.5 rounded-md bg-amber-500/10 border border-amber-500/20 text-xs text-amber-800 dark:text-amber-300">
            <Info className="w-4 h-4 shrink-0 text-amber-500 mt-0.5 sm:mt-0" />
            <span>
              <strong className="font-semibold">Limited historical data:</strong> {getNoticeMessage()}
            </span>
          </div>
        )}

        <div className="relative h-64 sm:h-72 w-full">
          {isLoading && (
            <div className="absolute inset-0 z-10 flex items-center justify-center bg-background/60 backdrop-blur-xs rounded-md">
              <Loader2 className="w-6 h-6 animate-spin text-primary" />
            </div>
          )}

          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#f43f5e" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="colorRecovered" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" opacity={0.6} />
              <XAxis
                dataKey="date"
                stroke="hsl(var(--muted-foreground))"
                fontSize={11}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                stroke="hsl(var(--muted-foreground))"
                fontSize={11}
                tickLine={false}
                axisLine={false}
                tickFormatter={(val) => formatINR(val, { decimals: 0 })}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="revenue"
                name="Total Revenue"
                stroke="hsl(var(--foreground))"
                strokeWidth={2}
                fillOpacity={0.04}
                fill="hsl(var(--foreground))"
              />
              <Area
                type="monotone"
                dataKey="revenueAtRisk"
                name="Revenue at Risk"
                stroke="#f43f5e"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorRisk)"
              />
              <Area
                type="monotone"
                dataKey="recovered"
                name="Recovered Revenue"
                stroke="#10b981"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorRecovered)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
