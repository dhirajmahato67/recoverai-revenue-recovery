"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { getRiskCases } from "@/lib/api";
import {
  LayoutDashboard,
  AlertTriangle,
  FileSearch,
  RotateCcw,
  PlayCircle,
  Receipt,
  ShieldCheck,
  Bot,
  Settings,
  HelpCircle,
  ChevronLeft,
  ChevronRight,
  ShieldAlert,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { RazorpayIcon } from "@/components/icons/RazorpayLogo";

interface SidebarProps {
  isOpenMobile?: boolean;
  onCloseMobile?: () => void;
}

export function Sidebar({ isOpenMobile, onCloseMobile }: SidebarProps) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [activeRiskCount, setActiveRiskCount] = useState<number>(1);

  useEffect(() => {
    let isMounted = true;
    getRiskCases({ status: "OPEN" })
      .then((cases) => {
        if (isMounted) {
          const openCount = cases.filter((c) => c.status === "OPEN" || c.status === "INVESTIGATING").length;
          setActiveRiskCount(openCount);
        }
      })
      .catch(() => {
        if (isMounted) setActiveRiskCount(1);
      });
    return () => {
      isMounted = false;
    };
  }, [pathname]);

  const navSections = [
    {
      label: "Revenue",
      items: [
        {
          name: "Dashboard",
          href: "/dashboard",
          icon: LayoutDashboard,
        },
        {
          name: "Risk Cases",
          href: "/risk-cases",
          icon: AlertTriangle,
          badge: activeRiskCount > 0 ? String(activeRiskCount) : undefined,
          badgeColor: "bg-rose-500/10 text-rose-600 dark:text-rose-400",
        },
        {
          name: "Investigations",
          href: "/investigations/INV-00000000",
          icon: FileSearch,
        },
      ],
    },
    {
      label: "Recovery",
      items: [
        {
          name: "Recovery Batches",
          href: "/recovery",
          icon: RotateCcw,
        },
        {
          name: "Active Recovery",
          href: "/recovery/RB-024",
          icon: PlayCircle,
          badge: "Live",
          badgeColor: "bg-violet-500/10 text-violet-600 dark:text-violet-400",
        },
      ],
    },
    {
      label: "Operations",
      items: [
        {
          name: "Transactions",
          href: "/transactions",
          icon: Receipt,
        },
        {
          name: "Audit Trail",
          href: "/audit",
          icon: ShieldCheck,
        },
      ],
    },
    {
      label: "AI",
      items: [
        {
          name: "AI Assistant",
          href: "/ai-assistant",
          icon: Bot,
          badge: "AI",
          badgeColor: "bg-violet-600 text-white",
        },
      ],
    },
  ];

  const sidebarContent = (
    <div className="flex h-full flex-col justify-between overflow-y-auto py-3">
      <div className="space-y-4 px-3">
        {/* Brand Header */}
        <div className="flex items-center justify-between px-2 py-1.5">
          <Link href="/dashboard" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-[#0C2451] text-[#3395FF] flex items-center justify-center shadow-md transition-transform group-hover:scale-105 shrink-0 border border-sky-500/20">
              <RazorpayIcon className="w-4.5 h-4.5 fill-current text-[#3395FF]" aria-label="Razorpay" />
            </div>
            {!collapsed && (
              <div className="flex flex-col">
                <span className="font-bold text-sm tracking-tight text-foreground flex items-center gap-1">
                  RecoverAI
                </span>
                <span className="text-[10px] text-muted-foreground font-medium truncate max-w-[130px]">
                  Revenue Recovery
                </span>
              </div>
            )}
          </Link>
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="hidden lg:flex p-1 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted/80 transition-colors"
            aria-label="Toggle sidebar collapse"
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        <div className="h-px bg-border/80 my-2" />

        {/* Nav Sections */}
        <nav className="space-y-4">
          {navSections.map((section) => (
            <div key={section.label} className="space-y-1">
              {!collapsed && (
                <p className="px-2.5 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground/70">
                  {section.label}
                </p>
              )}
              <div className="space-y-0.5">
                {section.items.map((item) => {
                  const isActive =
                    pathname === item.href ||
                    (item.href !== "/dashboard" && pathname.startsWith(item.href));
                  const Icon = item.icon;

                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={onCloseMobile}
                      className={cn(
                        "group flex items-center gap-2.5 rounded-md px-2.5 py-1.5 text-xs font-medium transition-all",
                        isActive
                          ? "bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-950 font-semibold shadow-xs"
                          : "text-muted-foreground hover:bg-muted hover:text-foreground",
                        collapsed && "justify-center px-0"
                      )}
                      title={collapsed ? item.name : undefined}
                    >
                      <Icon
                        className={cn(
                          "h-4 w-4 shrink-0 transition-colors",
                          isActive
                            ? "text-white dark:text-neutral-950"
                            : "text-muted-foreground group-hover:text-foreground"
                        )}
                      />
                      {!collapsed && (
                        <div className="flex flex-1 items-center justify-between">
                          <span className="truncate">{item.name}</span>
                          {item.badge && (
                            <span
                              className={cn(
                                "rounded px-1.5 py-0.2 text-[10px] font-semibold tracking-tight",
                                item.badgeColor
                              )}
                            >
                              {item.badge}
                            </span>
                          )}
                        </div>
                      )}
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>
      </div>

      {/* Footer Info & Settings */}
      <div className="space-y-3 px-3 pt-3 border-t border-border/80">
        {!collapsed && (
          <div className="rounded-lg border border-border/80 bg-muted/40 p-2.5">
            <div className="flex items-center justify-between mb-1">
              <span className="text-[11px] font-bold text-foreground">Acme Commerce</span>
              <span className="text-[9px] px-1.5 py-0.2 rounded bg-amber-500/10 text-amber-700 dark:text-amber-400 font-bold border border-amber-500/20">
                TEST MODE
              </span>
            </div>
            <p className="text-[10px] text-muted-foreground">Gateway: Razorpay (Sandbox)</p>
          </div>
        )}

        <div className="space-y-0.5">
          <Link
            href="/settings"
            onClick={onCloseMobile}
            className={cn(
              "flex items-center gap-2.5 rounded-md px-2.5 py-1.5 text-xs font-medium text-muted-foreground hover:bg-muted hover:text-foreground transition-colors",
              pathname === "/settings" && "bg-muted text-foreground font-semibold",
              collapsed && "justify-center px-0"
            )}
            title={collapsed ? "Settings" : undefined}
          >
            <Settings className="w-4 h-4 text-muted-foreground" />
            {!collapsed && <span>Settings</span>}
          </Link>
          <a
            href="https://github.com"
            target="_blank"
            rel="noreferrer"
            className={cn(
              "flex items-center gap-2.5 rounded-md px-2.5 py-1.5 text-xs font-medium text-muted-foreground hover:bg-muted hover:text-foreground transition-colors",
              collapsed && "justify-center px-0"
            )}
            title={collapsed ? "Documentation & API" : undefined}
          >
            <HelpCircle className="w-4 h-4 text-muted-foreground" />
            {!collapsed && <span>Docs & API</span>}
          </a>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Persistent Sidebar */}
      <aside
        className={cn(
          "hidden lg:block border-r border-border/80 bg-card h-screen sticky top-0 transition-all duration-200 z-40 select-none",
          collapsed ? "w-16" : "w-60"
        )}
      >
        {sidebarContent}
      </aside>

      {/* Mobile Drawer */}
      {isOpenMobile && (
        <div className="fixed inset-0 z-50 lg:hidden flex">
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-xs"
            onClick={onCloseMobile}
          />
          <div className="relative flex flex-col w-64 max-w-[80vw] bg-card h-full z-50 border-r border-border shadow-2xl">
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  );
}
