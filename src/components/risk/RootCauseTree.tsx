import React from "react";
import { RootCauseTreeNode } from "@/lib/types";
import { ArrowDown, AlertCircle, AlertTriangle, CheckCircle2, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface RootCauseTreeProps {
  tree: RootCauseTreeNode[];
}

export function RootCauseTree({ tree }: RootCauseTreeProps) {
  const renderNode = (node: RootCauseTreeNode, depth: number = 0) => {
    const isCritical = node.status === "critical";
    const isWarning = node.status === "warning";

    return (
      <div key={node.id} className="flex flex-col items-center w-full">
        {/* Node Box */}
        <div
          className={cn(
            "w-full max-w-xl p-3.5 rounded-lg border text-xs transition-all shadow-xs",
            isCritical
              ? "border-rose-500/40 bg-rose-500/[0.04] dark:bg-rose-950/20"
              : isWarning
              ? "border-amber-500/40 bg-amber-500/[0.04] dark:bg-amber-950/20"
              : "border-border bg-card"
          )}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {isCritical ? (
                <AlertCircle className="w-4 h-4 text-rose-600 dark:text-rose-400 shrink-0" />
              ) : isWarning ? (
                <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0" />
              ) : (
                <CheckCircle2 className="w-4 h-4 text-muted-foreground shrink-0" />
              )}
              <span className="font-semibold text-foreground text-xs sm:text-sm">{node.label}</span>
            </div>
            <span className="text-[10px] px-1.5 py-0.2 rounded font-mono font-semibold bg-muted text-muted-foreground">
              Level {depth + 1}
            </span>
          </div>

          {node.subtext && (
            <p className="text-muted-foreground text-[11px] mt-1 pl-6">{node.subtext}</p>
          )}
        </div>

        {/* Down Arrow connector if has children */}
        {node.children && node.children.length > 0 && (
          <div className="my-1.5 flex flex-col items-center text-muted-foreground/60">
            <div className="w-px h-3 bg-border" />
            <ArrowDown className="w-3.5 h-3.5" />
          </div>
        )}

        {/* Render children */}
        {node.children &&
          node.children.map((child) => renderNode(child, depth + 1))}
      </div>
    );
  };

  if (!tree || tree.length === 0) {
    return (
      <div className="p-6 text-center text-xs text-muted-foreground">
        No root cause tree data available for this case.
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center py-2 space-y-2 w-full">
      {tree.map((root) => renderNode(root, 0))}
    </div>
  );
}
