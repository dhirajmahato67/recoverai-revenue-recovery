"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Command } from "cmdk";
import {
  LayoutDashboard,
  AlertTriangle,
  FileSearch,
  RotateCcw,
  Receipt,
  ShieldCheck,
  Bot,
  Settings,
  Search,
  ArrowRight,
} from "lucide-react";
import { Dialog, DialogContent } from "../ui/dialog";

export function CommandMenu() {
  const [open, setOpen] = React.useState(false);
  const router = useRouter();

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if ((e.key === "k" && (e.metaKey || e.ctrlKey)) || (e.key === "/" && !["INPUT", "TEXTAREA"].includes((e.target as HTMLElement)?.tagName))) {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
    };

    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  const runCommand = React.useCallback((command: () => void) => {
    setOpen(false);
    command();
  }, []);

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="hidden md:flex items-center gap-2 px-2.5 py-1 text-xs text-muted-foreground bg-muted/50 border border-border/80 rounded-md hover:bg-muted transition-colors w-48 sm:w-64 justify-between"
      >
        <span className="flex items-center gap-1.5">
          <Search className="w-3.5 h-3.5" />
          <span>Search or jump to...</span>
        </span>
        <kbd className="pointer-events-none inline-flex h-4 select-none items-center gap-0.5 rounded border border-border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
          <span className="text-xs">⌘</span>K
        </kbd>
      </button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="overflow-hidden p-0 max-w-xl shadow-2xl border-border bg-card">
          <Command className="[&_[cmdk-group-heading]]:px-3 [&_[cmdk-group-heading]]:py-1.5 [&_[cmdk-group-heading]]:text-[11px] [&_[cmdk-group-heading]]:font-semibold [&_[cmdk-group-heading]]:text-muted-foreground [&_[cmdk-group]]:px-1.5 [&_[cmdk-input-wrapper]_svg]:h-4 [&_[cmdk-input-wrapper]_svg]:w-4 [&_[cmdk-input]]:h-11 [&_[cmdk-item]]:px-3 [&_[cmdk-item]]:py-2 [&_[cmdk-item]]:text-xs [&_[cmdk-item]]:rounded-md">
            <div className="flex items-center border-b border-border px-3">
              <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
              <Command.Input
                placeholder="Type a command, risk case ID, transaction, or batch..."
                className="flex h-11 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
              />
            </div>

            <Command.List className="max-h-80 overflow-y-auto p-2">
              <Command.Empty className="py-6 text-center text-xs text-muted-foreground">
                No matching results found.
              </Command.Empty>

              <Command.Group heading="Risk Cases & Investigations">
                <Command.Item
                  onSelect={() => runCommand(() => router.push("/risk-cases/RC-001"))}
                  className="flex items-center justify-between cursor-pointer hover:bg-muted/80"
                >
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-3.5 h-3.5 text-rose-500" />
                    <span>RC-001: UPI Degradation (HDFC UPI) — ₹8.40L Risk</span>
                  </div>
                  <ArrowRight className="w-3 h-3 opacity-40" />
                </Command.Item>
                <Command.Item
                  onSelect={() => runCommand(() => router.push("/investigations/INV-001"))}
                  className="flex items-center justify-between cursor-pointer hover:bg-muted/80"
                >
                  <div className="flex items-center gap-2">
                    <FileSearch className="w-3.5 h-3.5 text-violet-500" />
                    <span>INV-001: AI Root Cause Analysis (HDFC Gateway Latency)</span>
                  </div>
                  <ArrowRight className="w-3 h-3 opacity-40" />
                </Command.Item>
                <Command.Item
                  onSelect={() => runCommand(() => router.push("/risk-cases/RC-002"))}
                  className="flex items-center justify-between cursor-pointer hover:bg-muted/80"
                >
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
                    <span>RC-002: Mobile Checkout Drop-off — ₹3.20L Risk</span>
                  </div>
                  <ArrowRight className="w-3 h-3 opacity-40" />
                </Command.Item>
              </Command.Group>

              <Command.Group heading="Recovery Operations">
                <Command.Item
                  onSelect={() => runCommand(() => router.push("/recovery/RB-024"))}
                  className="flex items-center justify-between cursor-pointer hover:bg-muted/80"
                >
                  <div className="flex items-center gap-2">
                    <RotateCcw className="w-3.5 h-3.5 text-blue-500" />
                    <span>RB-024: Payment Retry Batch (438 Transactions)</span>
                  </div>
                  <ArrowRight className="w-3 h-3 opacity-40" />
                </Command.Item>
                <Command.Item
                  onSelect={() => runCommand(() => router.push("/recovery/RB-023"))}
                  className="flex items-center justify-between cursor-pointer hover:bg-muted/80"
                >
                  <div className="flex items-center gap-2">
                    <RotateCcw className="w-3.5 h-3.5 text-emerald-500" />
                    <span>RB-023: Completed Subscription Recovery (₹82.4K Recovered)</span>
                  </div>
                  <ArrowRight className="w-3 h-3 opacity-40" />
                </Command.Item>
              </Command.Group>

              <Command.Group heading="Navigation">
                <Command.Item
                  onSelect={() => runCommand(() => router.push("/dashboard"))}
                  className="flex items-center justify-between cursor-pointer hover:bg-muted/80"
                >
                  <div className="flex items-center gap-2">
                    <LayoutDashboard className="w-3.5 h-3.5" />
                    <span>Overview Dashboard</span>
                  </div>
                </Command.Item>
                <Command.Item
                  onSelect={() => runCommand(() => router.push("/transactions"))}
                  className="flex items-center justify-between cursor-pointer hover:bg-muted/80"
                >
                  <div className="flex items-center gap-2">
                    <Receipt className="w-3.5 h-3.5" />
                    <span>Transaction Explorer</span>
                  </div>
                </Command.Item>
                <Command.Item
                  onSelect={() => runCommand(() => router.push("/audit"))}
                  className="flex items-center justify-between cursor-pointer hover:bg-muted/80"
                >
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>Audit Trail</span>
                  </div>
                </Command.Item>
                <Command.Item
                  onSelect={() => runCommand(() => router.push("/ai-assistant"))}
                  className="flex items-center justify-between cursor-pointer hover:bg-muted/80"
                >
                  <div className="flex items-center gap-2">
                    <Bot className="w-3.5 h-3.5 text-violet-500" />
                    <span>RecoverAI Assistant</span>
                  </div>
                </Command.Item>
                <Command.Item
                  onSelect={() => runCommand(() => router.push("/settings"))}
                  className="flex items-center justify-between cursor-pointer hover:bg-muted/80"
                >
                  <div className="flex items-center gap-2">
                    <Settings className="w-3.5 h-3.5" />
                    <span>Settings & Safety Policies</span>
                  </div>
                </Command.Item>
              </Command.Group>
            </Command.List>
          </Command>
        </DialogContent>
      </Dialog>
    </>
  );
}
