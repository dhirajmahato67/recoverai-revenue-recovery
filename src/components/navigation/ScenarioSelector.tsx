"use client";

import React from "react";
import { useScenarioStore } from "@/lib/store/scenarioStore";
import { demoScenarios } from "@/lib/mock/scenarios";
import { ScenarioType } from "@/lib/types";
import { ShieldAlert, Sparkles, Check, ChevronDown, Activity, ArrowRight } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@radix-ui/react-dropdown-menu";
import { Button } from "../ui/button";

export function ScenarioSelector() {
  const { currentScenario, setScenario, scenarioData } = useScenarioStore();

  const isActiveIncident =
    currentScenario === "PAYMENT_DEGRADATION" || currentScenario === "UPI_DEGRADATION";

  // Filter non-active scenarios for simulation catalog
  const simulationScenarios = Object.values(demoScenarios).filter(
    (s) => s.id !== "PAYMENT_DEGRADATION" && s.id !== "UPI_DEGRADATION"
  );

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className={`h-8 text-xs gap-1.5 px-2.5 font-medium transition-colors shadow-xs ${
            isActiveIncident
              ? "border-rose-500/30 bg-rose-500/5 text-rose-700 dark:text-rose-300 dark:bg-rose-950/30 hover:bg-rose-500/10 focus:ring-rose-500/30"
              : "border-violet-500/30 bg-violet-500/5 text-violet-700 dark:text-violet-300 dark:bg-violet-950/30 hover:bg-violet-500/10 focus:ring-violet-500/30"
          }`}
          aria-label="Active Incident and Simulation Scenarios menu"
        >
          {isActiveIncident ? (
            <>
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-500"></span>
              </span>
              <span className="text-muted-foreground font-normal hidden sm:inline">Active Incident:</span>
              <span className="font-semibold truncate max-w-[140px]">UPI Degradation</span>
              <span className="text-[10px] font-mono px-1 py-0.5 rounded bg-rose-500/15 text-rose-700 dark:text-rose-300 font-bold">
                RC-001
              </span>
            </>
          ) : (
            <>
              <Sparkles className="w-3.5 h-3.5 text-violet-600 dark:text-violet-400 shrink-0" />
              <span className="text-muted-foreground font-normal hidden sm:inline">Simulation:</span>
              <span className="font-semibold truncate max-w-[140px]">{scenarioData.name.split("(")[0]}</span>
            </>
          )}
          <ChevronDown className="w-3 h-3 opacity-60 ml-0.5" />
        </Button>
      </DropdownMenuTrigger>

      <DropdownMenuContent
        align="end"
        className="w-96 rounded-xl border border-border bg-popover p-2 text-popover-foreground shadow-2xl z-50 text-xs animate-in fade-in-80 zoom-in-95"
      >
        {/* SECTION 1: LIVE ACTIVE INCIDENT */}
        <div className="px-2 pt-1.5 pb-1">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider text-rose-600 dark:text-rose-400 flex items-center gap-1.5">
              <ShieldAlert className="w-3.5 h-3.5" />
              Live Active Incident
            </span>
            <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-rose-500/10 text-rose-600 dark:text-rose-400 font-semibold border border-rose-500/20">
              PostgreSQL Telemetry
            </span>
          </div>
        </div>

        <DropdownMenuItem
          onClick={() => setScenario("PAYMENT_DEGRADATION")}
          className={`flex flex-col items-start gap-1 rounded-lg p-2.5 outline-none cursor-pointer transition-colors border my-1 ${
            isActiveIncident
              ? "bg-rose-500/10 border-rose-500/30 text-foreground"
              : "border-border/60 hover:bg-muted/60 focus:bg-muted/60"
          }`}
        >
          <div className="flex items-center justify-between w-full">
            <span className="font-semibold text-foreground flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-rose-500" />
              HDFC UPI Degradation · RC-001
            </span>
            {isActiveIncident && <Check className="w-4 h-4 text-rose-600 dark:text-rose-400 shrink-0" />}
          </div>
          <p className="text-[11px] text-muted-foreground leading-snug">
            1,251 transactions · 81.9% conversion · ₹12.20L revenue at risk. Backed by PostgreSQL transaction span and investigation INV-00000000.
          </p>
        </DropdownMenuItem>

        <DropdownMenuSeparator className="h-px bg-border/80 my-2" />

        {/* SECTION 2: SIMULATION SCENARIOS */}
        <div className="px-2 pt-1 pb-0.5">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
              <Sparkles className="w-3 h-3 text-violet-500" />
              Simulation Scenarios (Synthetic Engine)
            </span>
          </div>
          <p className="text-[10px] text-muted-foreground/80 mt-0.5">
            Synthetic stress-testing profiles evaluated through the transaction pipeline.
          </p>
        </div>

        <div className="space-y-1 mt-1">
          {simulationScenarios.map((scenario) => {
            const isSelected = scenario.id === currentScenario;
            return (
              <DropdownMenuItem
                key={scenario.id}
                onClick={() => setScenario(scenario.id as ScenarioType)}
                className={`flex flex-col items-start gap-1 rounded-lg p-2 outline-none cursor-pointer transition-colors ${
                  isSelected
                    ? "bg-violet-500/10 border border-violet-500/30 text-foreground"
                    : "hover:bg-muted focus:bg-muted"
                }`}
              >
                <div className="flex items-center justify-between w-full">
                  <span className="font-medium text-foreground flex items-center gap-1.5">
                    {scenario.name}
                  </span>
                  <span className="text-[9px] px-1.5 py-0.2 rounded bg-muted text-muted-foreground font-mono">
                    {scenario.badge}
                  </span>
                  {isSelected && <Check className="w-3.5 h-3.5 text-violet-600 shrink-0 ml-1" />}
                </div>
                <p className="text-[11px] text-muted-foreground leading-snug">{scenario.description}</p>
              </DropdownMenuItem>
            );
          })}
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
