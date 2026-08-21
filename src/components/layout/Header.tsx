"use client";

import React, { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import {
  ChevronRight,
  Sun,
  Moon,
  Building2,
  ChevronDown,
  Menu,
  Sparkles,
} from "lucide-react";
import { ScenarioSelector } from "../navigation/ScenarioSelector";
import { NotificationCenter } from "../navigation/NotificationCenter";
import { CommandMenu } from "../navigation/CommandMenu";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@radix-ui/react-dropdown-menu";
import { Button } from "../ui/button";

interface HeaderProps {
  onToggleSidebar?: () => void;
}

export function Header({ onToggleSidebar }: HeaderProps) {
  const pathname = usePathname();
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    const isDarkMode = document.documentElement.classList.contains("dark");
    setIsDark(isDarkMode);
  }, []);

  const toggleTheme = () => {
    if (document.documentElement.classList.contains("dark")) {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
      setIsDark(false);
    } else {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
      setIsDark(true);
    }
  };

  const getBreadcrumbTitle = () => {
    if (pathname === "/dashboard" || pathname === "/") return "Overview Dashboard";
    if (pathname.startsWith("/risk-cases/")) return "Risk Case Details";
    if (pathname === "/risk-cases") return "Revenue Risk Cases";
    if (pathname.startsWith("/investigations/")) return "AI Root Cause Investigation";
    if (pathname.startsWith("/recovery/")) return "Recovery Execution Monitor";
    if (pathname === "/recovery") return "Recovery Operations";
    if (pathname === "/transactions") return "Transaction Explorer";
    if (pathname === "/audit") return "Audit Trail";
    if (pathname === "/ai-assistant") return "RecoverAI Assistant";
    if (pathname === "/settings") return "Settings & Policy Controls";
    return "RecoverAI";
  };

  return (
    <header className="sticky top-0 z-30 flex h-14 w-full items-center justify-between border-b border-border/80 bg-card/95 px-4 backdrop-blur-md transition-colors">
      {/* Left: Mobile Toggle & Breadcrumb */}
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="lg:hidden p-1.5 rounded-md hover:bg-muted text-muted-foreground hover:text-foreground"
          aria-label="Toggle sidebar"
        >
          <Menu className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <span className="font-medium text-foreground/80">RecoverAI</span>
          <ChevronRight className="w-3 h-3 opacity-40" />
          <span className="font-semibold text-foreground">{getBreadcrumbTitle()}</span>
        </div>
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-2.5">
        <CommandMenu />

        <ScenarioSelector />

        {/* Test Mode Indicator */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-amber-500/30 bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400 text-xs font-semibold select-none shadow-xs">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
          </span>
          <span>Test Mode</span>
        </div>

        {/* Merchant Selector */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              className="h-8 gap-1.5 px-2.5 text-xs font-medium text-foreground bg-background hover:bg-muted"
            >
              <Building2 className="w-3.5 h-3.5 text-muted-foreground" />
              <span className="font-semibold">Acme Commerce</span>
              <ChevronDown className="w-3 h-3 opacity-60" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            align="end"
            className="w-56 rounded-lg border border-border bg-popover p-1 text-popover-foreground shadow-xl z-50 text-xs"
          >
            <DropdownMenuLabel className="px-3 py-2 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
              Connected Merchant
            </DropdownMenuLabel>
            <DropdownMenuItem className="flex items-center justify-between p-2 rounded-md bg-muted/60 font-medium">
              <div>
                <p className="font-semibold text-foreground">Acme Commerce</p>
                <p className="text-[10px] text-muted-foreground">ID: mer_acme_prod_01</p>
              </div>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-600 font-semibold">Active</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator className="h-px bg-border my-1" />
            <DropdownMenuItem className="p-2 rounded-md hover:bg-muted text-muted-foreground cursor-not-allowed opacity-60">
              + Connect Another Entity
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <NotificationCenter />

        {/* Theme Toggle */}
        <Button
          variant="ghost"
          size="iconSm"
          onClick={toggleTheme}
          className="text-muted-foreground hover:text-foreground"
          aria-label="Toggle theme"
        >
          {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4" />}
        </Button>

        {/* User Profile Avatar */}
        <div className="flex items-center gap-2 pl-1 border-l border-border/70">
          <div className="w-7 h-7 rounded-full bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-950 font-bold text-xs flex items-center justify-center shadow-xs">
            AS
          </div>
        </div>
      </div>
    </header>
  );
}
