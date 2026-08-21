"use client";

import React, { useState } from "react";
import { AlertCircle, X, ShieldAlert } from "lucide-react";

export function TestModeBanner() {
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return null;

  return (
    <div className="bg-amber-500/10 border-b border-amber-500/20 px-4 py-1.5 text-xs text-amber-800 dark:text-amber-300 flex items-center justify-between transition-all">
      <div className="flex items-center gap-2 max-w-4xl">
        <ShieldAlert className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400 shrink-0" />
        <span>
          <strong>Razorpay Test Mode Active:</strong> You are operating in a sandboxed financial environment. Simulated recovery transactions do not trigger real settlement debits.
        </span>
      </div>
      <button
        onClick={() => setDismissed(true)}
        className="text-amber-700 dark:text-amber-400 hover:opacity-75 p-0.5 rounded ml-2"
        aria-label="Dismiss test mode notice"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}
