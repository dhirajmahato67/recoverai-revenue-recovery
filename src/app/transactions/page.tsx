"use client";

import React, { useState, useEffect } from "react";
import { getTransactions } from "@/lib/api";
import { Transaction, PaymentMethod, BankName, TransactionStatus } from "@/lib/types";
import { formatINR, formatDateTime } from "@/lib/utils";
import {
  Table,
  TableHeader,
  TableRow,
  TableHead,
  TableBody,
  TableCell,
} from "@/components/ui/table";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/statusBadge";
import { TransactionDrawer } from "@/components/transactions/TransactionDrawer";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Search,
  Filter,
  Receipt,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  Download,
} from "lucide-react";

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<TransactionStatus | "ALL">("ALL");
  const [methodFilter, setMethodFilter] = useState<PaymentMethod | "ALL">("ALL");
  const [bankFilter, setBankFilter] = useState<BankName | "ALL">("ALL");

  // Selected Transaction for Drawer
  const [selectedTx, setSelectedTx] = useState<Transaction | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const data = await getTransactions({
          search,
          status: statusFilter,
          method: methodFilter,
          bank: bankFilter,
          page,
          pageSize: 10,
        });
        setTransactions(data.items);
        setTotal(data.total);
        setTotalPages(data.totalPages);
      } catch (err) {
        console.error("Failed to load transactions:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [search, statusFilter, methodFilter, bankFilter, page]);

  const handleRowClick = (tx: Transaction) => {
    setSelectedTx(tx);
    setDrawerOpen(true);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-border/60">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            Transaction Explorer
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground mt-0.5">
            Explore live and historical payment attempts, inspect gateway error codes, and trace recovery eligibility.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => alert("Simulated CSV Export generated.")}
            className="h-8 gap-1.5 text-xs text-muted-foreground hover:text-foreground"
          >
            <Download className="w-3.5 h-3.5" />
            Export CSV
          </Button>
        </div>
      </div>

      {/* Filter Bar */}
      <Card className="p-3 bg-card border-border/80 shadow-xs">
        <div className="flex flex-col md:flex-row items-center gap-3">
          {/* Search Input */}
          <div className="relative flex-1 w-full">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search by Transaction ID (TX-103928), Order ID, or Customer name..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="w-full h-8 pl-8 pr-3 text-xs bg-background border border-input rounded-md focus:outline-none focus:ring-1 focus:ring-ring text-foreground placeholder:text-muted-foreground"
            />
          </div>

          {/* Filter Selects */}
          <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
            {/* Status */}
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value as TransactionStatus | "ALL");
                setPage(1);
              }}
              className="h-8 px-2.5 text-xs bg-background border border-input rounded-md text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            >
              <option value="ALL">All Statuses</option>
              <option value="FAILED">Failed</option>
              <option value="SUCCESS">Success</option>
              <option value="RECOVERED">Recovered</option>
              <option value="RETRY_SCHEDULED">Retry Scheduled</option>
            </select>

            {/* Method */}
            <select
              value={methodFilter}
              onChange={(e) => {
                setMethodFilter(e.target.value as PaymentMethod | "ALL");
                setPage(1);
              }}
              className="h-8 px-2.5 text-xs bg-background border border-input rounded-md text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            >
              <option value="ALL">All Methods</option>
              <option value="UPI">UPI</option>
              <option value="Card">Card</option>
              <option value="Net Banking">Net Banking</option>
              <option value="Wallet">Wallet</option>
            </select>

            {/* Bank */}
            <select
              value={bankFilter}
              onChange={(e) => {
                setBankFilter(e.target.value as BankName | "ALL");
                setPage(1);
              }}
              className="h-8 px-2.5 text-xs bg-background border border-input rounded-md text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            >
              <option value="ALL">All Banks</option>
              <option value="HDFC">HDFC Bank</option>
              <option value="ICICI">ICICI Bank</option>
              <option value="SBI">SBI</option>
              <option value="Axis">Axis Bank</option>
            </select>

            {(search || statusFilter !== "ALL" || methodFilter !== "ALL" || bankFilter !== "ALL") && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setSearch("");
                  setStatusFilter("ALL");
                  setMethodFilter("ALL");
                  setBankFilter("ALL");
                  setPage(1);
                }}
                className="h-8 px-2 text-xs text-muted-foreground hover:text-foreground"
              >
                Reset
              </Button>
            )}
          </div>
        </div>
      </Card>

      {/* Transactions Table */}
      <Card className="border-border/80 shadow-xs overflow-hidden">
        {loading ? (
          <div className="p-6 space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-12 w-full rounded" />
            ))}
          </div>
        ) : (
          <>
            <div className="overflow-x-auto w-full">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[120px]">Transaction ID</TableHead>
                    <TableHead>Order ID</TableHead>
                    <TableHead>Customer</TableHead>
                    <TableHead className="text-right">Amount</TableHead>
                    <TableHead>Method</TableHead>
                    <TableHead>Bank</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Failure Reason</TableHead>
                    <TableHead className="text-right">Created</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {transactions.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={9} className="text-center py-12 text-muted-foreground">
                        No matching transactions found.
                      </TableCell>
                    </TableRow>
                  ) : (
                    transactions.map((tx) => (
                      <TableRow
                        key={tx.id}
                        onClick={() => handleRowClick(tx)}
                        className="cursor-pointer transition-colors hover:bg-muted/50"
                      >
                        <TableCell className="font-mono font-bold text-foreground">
                          {tx.id}
                        </TableCell>
                        <TableCell className="font-mono text-muted-foreground text-xs">
                          {tx.orderId}
                        </TableCell>
                        <TableCell>
                          <div className="flex flex-col">
                            <span className="font-semibold text-foreground text-xs">{tx.customerName}</span>
                            <span className="text-[10px] text-muted-foreground truncate max-w-[140px]">
                              {tx.customerEmail}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell className="text-right font-mono font-bold text-foreground">
                          {formatINR(tx.amount)}
                        </TableCell>
                        <TableCell className="text-xs text-muted-foreground">
                          <span className="font-medium text-foreground">{tx.method}</span>
                          {tx.upiApp && <span className="text-[10px] block opacity-75">{tx.upiApp}</span>}
                        </TableCell>
                        <TableCell className="font-medium text-foreground text-xs">
                          {tx.bank}
                        </TableCell>
                        <TableCell>
                          <StatusBadge status={tx.status} />
                        </TableCell>
                        <TableCell className="text-xs text-rose-600 dark:text-rose-400 max-w-[160px] truncate">
                          {tx.failureReason || "—"}
                        </TableCell>
                        <TableCell className="text-right font-mono text-[11px] text-muted-foreground">
                          {formatDateTime(tx.createdAt)}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>

            {/* Pagination Controls */}
            <div className="flex items-center justify-between p-3 border-t border-border/60 bg-muted/20 text-xs">
              <span className="text-muted-foreground">
                Showing <strong className="text-foreground">{transactions.length}</strong> of{" "}
                <strong className="text-foreground">{total}</strong> transactions
              </span>

              <div className="flex items-center gap-1.5">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  className="h-7 w-7 p-0"
                >
                  <ChevronLeft className="w-3.5 h-3.5" />
                </Button>
                <span className="text-xs font-mono px-2">
                  Page {page} of {totalPages}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  className="h-7 w-7 p-0"
                >
                  <ChevronRight className="w-3.5 h-3.5" />
                </Button>
              </div>
            </div>
          </>
        )}
      </Card>

      {/* Transaction Detail Slide-Out Drawer */}
      <TransactionDrawer
        transaction={selectedTx}
        open={drawerOpen}
        onOpenChange={setDrawerOpen}
      />
    </div>
  );
}
