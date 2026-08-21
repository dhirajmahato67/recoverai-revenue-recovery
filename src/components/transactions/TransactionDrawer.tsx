import React from "react";
import { Transaction } from "@/lib/types";
import { formatINR, formatDateTime } from "@/lib/utils";
import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
  DrawerDescription,
  DrawerBody,
  DrawerFooter,
} from "../ui/drawer";
import { StatusBadge } from "../ui/statusBadge";
import { Button } from "../ui/button";
import {
  Receipt,
  User,
  CreditCard,
  Building2,
  Clock,
  AlertTriangle,
  RotateCcw,
  CheckCircle2,
  XCircle,
  ExternalLink,
  ShieldCheck,
} from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

interface TransactionDrawerProps {
  transaction: Transaction | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function TransactionDrawer({
  transaction,
  open,
  onOpenChange,
}: TransactionDrawerProps) {
  if (!transaction) return null;

  return (
    <Drawer open={open} onOpenChange={onOpenChange}>
      <DrawerContent>
        <DrawerHeader>
          <div className="flex items-center justify-between">
            <span className="font-mono text-xs font-bold text-muted-foreground uppercase">
              Transaction Details
            </span>
            <StatusBadge status={transaction.status} />
          </div>
          <DrawerTitle className="text-xl font-bold font-mono text-foreground mt-1">
            {transaction.id}
          </DrawerTitle>
          <DrawerDescription>
            {formatINR(transaction.amount)} • Order {transaction.orderId}
          </DrawerDescription>
        </DrawerHeader>

        <DrawerBody className="space-y-6">
          {/* Amount & Status Hero */}
          <div className="rounded-lg border border-border/80 bg-muted/30 p-4 flex items-center justify-between">
            <div>
              <span className="text-[10px] uppercase font-semibold text-muted-foreground">Transaction Amount</span>
              <p className="text-2xl font-bold font-mono text-foreground mt-0.5">
                {formatINR(transaction.amount)}
              </p>
            </div>
            <div className="text-right">
              <span className="text-[10px] uppercase font-semibold text-muted-foreground">Settlement State</span>
              <p className="text-xs font-semibold text-foreground mt-0.5">{transaction.status}</p>
            </div>
          </div>

          {/* Payment Metadata Grid */}
          <div className="space-y-2">
            <h4 className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
              Payment & Customer Attributes
            </h4>
            <div className="grid grid-cols-2 gap-2.5 text-xs">
              <div className="p-3 rounded-md bg-card border border-border/60 space-y-1">
                <span className="text-[10px] text-muted-foreground uppercase flex items-center gap-1">
                  <CreditCard className="w-3 h-3" /> Method & Bank
                </span>
                <p className="font-semibold text-foreground">
                  {transaction.method} ({transaction.bank})
                </p>
                {transaction.upiApp && (
                  <span className="text-[10px] text-muted-foreground">App: {transaction.upiApp}</span>
                )}
                {transaction.cardLast4 && (
                  <span className="text-[10px] text-muted-foreground">Ending in {transaction.cardLast4}</span>
                )}
              </div>

              <div className="p-3 rounded-md bg-card border border-border/60 space-y-1">
                <span className="text-[10px] text-muted-foreground uppercase flex items-center gap-1">
                  <User className="w-3 h-3" /> Customer
                </span>
                <p className="font-semibold text-foreground truncate">{transaction.customerName}</p>
                <p className="text-[10px] text-muted-foreground truncate">{transaction.customerEmail}</p>
              </div>

              <div className="p-3 rounded-md bg-card border border-border/60 space-y-1">
                <span className="text-[10px] text-muted-foreground uppercase flex items-center gap-1">
                  <Clock className="w-3 h-3" /> Timestamp
                </span>
                <p className="font-semibold text-foreground text-[11px]">
                  {formatDateTime(transaction.createdAt)}
                </p>
              </div>

              <div className="p-3 rounded-md bg-card border border-border/60 space-y-1">
                <span className="text-[10px] text-muted-foreground uppercase flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3 text-rose-500" /> Failure Reason
                </span>
                <p className="font-semibold text-rose-600 dark:text-rose-400 truncate">
                  {transaction.failureReason || "None (Success)"}
                </p>
                {transaction.failureCode && (
                  <span className="text-[9px] font-mono text-muted-foreground">{transaction.failureCode}</span>
                )}
              </div>
            </div>
          </div>

          {/* Lifecycle Timeline */}
          <div className="space-y-3">
            <h4 className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
              Event Lifecycle Timeline
            </h4>
            <div className="relative pl-6 space-y-4 border-l border-border/80 ml-2 text-xs">
              {[
                { title: "Order created", time: "12:31:45 PM", desc: `Order ${transaction.orderId} created for ${formatINR(transaction.amount)}`, status: "completed" },
                { title: "Payment attempted", time: "12:32:00 PM", desc: `${transaction.method} collect routed to ${transaction.bank}`, status: "completed" },
                { title: transaction.status === "SUCCESS" ? "Payment captured" : "Payment failed", time: "12:32:08 PM", desc: transaction.failureReason || "Successfully authorized", status: transaction.status === "SUCCESS" ? "completed" : "failed" },
                { title: "Risk case created", time: "12:32:15 PM", desc: "Flagged under Risk Case RC-001", status: "completed" },
                { title: "Recovery workflow", time: "12:32:20 PM", desc: transaction.status === "RECOVERED" ? "Recovered via batch RB-024" : "Queued for bounded retry", status: transaction.status === "RECOVERED" ? "completed" : "pending" },
              ].map((step, idx) => (
                <div key={idx} className="relative">
                  <div
                    className={cn(
                      "absolute -left-[31px] top-0.5 w-3.5 h-3.5 rounded-full border-2 bg-card flex items-center justify-center",
                      step.status === "completed"
                        ? "border-emerald-500 text-emerald-500"
                        : step.status === "failed"
                        ? "border-rose-500 text-rose-500"
                        : "border-muted-foreground/40 text-muted-foreground"
                    )}
                  >
                    <span className="w-1 h-1 rounded-full bg-current" />
                  </div>
                  <div>
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-foreground">{step.title}</span>
                      <span className="text-[10px] text-muted-foreground font-mono">{step.time}</span>
                    </div>
                    <p className="text-[11px] text-muted-foreground mt-0.5">{step.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </DrawerBody>

        <DrawerFooter>
          {transaction.riskCaseId && (
            <Link href={`/risk-cases/${transaction.riskCaseId}`} onClick={() => onOpenChange(false)}>
              <Button variant="outline" size="sm" className="text-xs gap-1">
                View Risk Case <ExternalLink className="w-3 h-3" />
              </Button>
            </Link>
          )}
          {transaction.recoveryBatchId && (
            <Link href={`/recovery/${transaction.recoveryBatchId}`} onClick={() => onOpenChange(false)}>
              <Button variant="fintech" size="sm" className="text-xs gap-1">
                View Recovery Batch <ExternalLink className="w-3 h-3" />
              </Button>
            </Link>
          )}
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  );
}
