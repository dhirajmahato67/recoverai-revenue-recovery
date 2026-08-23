"use client";

import React, { useState, useRef, useEffect, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { sendAssistantMessage, getRecoveryBatchById, getAIExecutiveSummary } from "@/lib/api";
import { AIMessage, RecoveryBatch } from "@/lib/types";
import { ActionProposalCard } from "@/components/ai/ActionProposalCard";
import { ApprovalModal } from "@/components/recovery/ApprovalModal";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Bot,
  User,
  Send,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  RotateCcw,
  Clock,
  FileText,
  CheckCircle2,
  AlertTriangle,
  Layers,
} from "lucide-react";
import { cn } from "@/lib/utils";

const defaultMessages: AIMessage[] = [
  {
    id: "msg-welcome",
    role: "assistant",
    timestamp: "12:00 PM",
    content:
      "Hello. I am RecoverAI Copilot. I analyze verified telemetry across your payment rails, diagnose anomaly root causes, and propose bounded recovery workflows requiring your authorization.\n\nAsk me any operational question regarding the active incident.",
  },
];

const suggestedPrompts = [
  "Why did UPI payments fail?",
  "Why is HDFC the most affected bank?",
  "How much revenue is at risk?",
  "What should we do next?",
  "Did we recover any money?",
];

function renderInlineMarkdown(text: string): React.ReactNode[] {
  const parts: React.ReactNode[] = [];
  const regex = /(\*\*.*?\*\*|`.*?`)/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }
    const token = match[0];
    if (token.startsWith("**") && token.endsWith("**")) {
      parts.push(
        <strong key={match.index} className="font-semibold text-foreground">
          {token.slice(2, -2)}
        </strong>
      );
    } else if (token.startsWith("`") && token.endsWith("`")) {
      parts.push(
        <code key={match.index} className="font-mono bg-muted/80 px-1 py-0.5 rounded text-[11px] text-foreground">
          {token.slice(1, -1)}
        </code>
      );
    }
    lastIndex = regex.lastIndex;
  }

  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }

  return parts;
}

function FormattedMarkdown({ content }: { content: string }) {
  if (!content) return null;

  const normalized = content.replace(/\r\n/g, "\n");
  const blocks = normalized.split(/\n\n+/);

  return (
    <div className="space-y-2 text-xs leading-relaxed">
      {blocks.map((block, bIdx) => {
        const lines = block.split("\n").filter((l) => l.trim().length > 0);
        if (lines.length === 0) return null;

        const isList = lines.every((line) => {
          const t = line.trim();
          return t.startsWith("•") || t.startsWith("-") || /^\d+\./.test(t);
        });

        if (isList) {
          return (
            <ul key={bIdx} className="space-y-1.5 pl-1 my-1.5">
              {lines.map((line, lIdx) => {
                const cleanLine = line.trim().replace(/^[•\-]\s*/, "").replace(/^\d+\.\s*/, "");
                return (
                  <li key={lIdx} className="flex items-start gap-2">
                    <span className="inline-block w-1.5 h-1.5 rounded-full bg-violet-500 shrink-0 mt-1.5" />
                    <span className="flex-1">{renderInlineMarkdown(cleanLine)}</span>
                  </li>
                );
              })}
            </ul>
          );
        }

        return (
          <p key={bIdx} className="leading-relaxed">
            {lines.map((line, lIdx) => (
              <React.Fragment key={lIdx}>
                {lIdx > 0 && <br />}
                {renderInlineMarkdown(line)}
              </React.Fragment>
            ))}
          </p>
        );
      })}
    </div>
  );
}

function AIAssistantContent() {
  const searchParams = useSearchParams();
  const initialInvId = searchParams.get("inv") || "INV-00000000";


  const [selectedInvestigation, setSelectedInvestigation] = useState(initialInvId);
  const [messages, setMessages] = useState<AIMessage[]>(defaultMessages);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [batchForApproval, setBatchForApproval] = useState<RecoveryBatch | null>(null);
  const [approvalModalOpen, setApprovalModalOpen] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (queryText?: string) => {
    const text = (queryText || input).trim();
    if (!text || loading) return;

    const userMsg: AIMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const response = await sendAssistantMessage(text, messages, selectedInvestigation);
      setMessages((prev) => [...prev, response]);
    } catch (err) {
      console.error("AI chat error:", err);
      const errorMsg: AIMessage = {
        id: `err-${Date.now()}`,
        role: "assistant",
        content: "I encountered an error retrieving verified incident telemetry. Please try again.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleExecutiveSummary = async () => {
    if (loading) return;
    setLoading(true);
    try {
      const summary = await getAIExecutiveSummary(selectedInvestigation);
      const summaryMsg: AIMessage = {
        id: `summary-${Date.now()}`,
        role: "assistant",
        content: `**Executive Briefing: ${summary.incident_title}**\n\n• **Business Impact:** ${summary.impact_summary}\n• **Root Cause:** ${summary.root_cause_summary} (${Math.round(summary.confidence_score * 100)}% Confidence)\n• **Recommended Action:** ${summary.recommended_action}`,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        confidence: Math.round(summary.confidence_score * 100),
        evidenceRefs: ["EVID-TX-001", "EVID-PM-UPI", "EVID-BANK-HDFC"],
        groundingStatus: "VERIFIED",
        responseType: "SUMMARY",
        structuredCard: {
          type: "METRIC_SUMMARY",
          title: summary.incident_title,
          metrics: [
            { label: "Confidence", value: `${Math.round(summary.confidence_score * 100)}%` },
            { label: "Rev at Risk", value: "₹12.20L", isPositive: false },
            { label: "Recoverable", value: "₹3.05L", isPositive: true },
          ],
          bullets: summary.evidence_summary,
          actionLabel: "Inspect Incident Risk Case",
          actionRoute: "/risk-cases/RC-001",
          riskCaseId: "RC-001",
        },
      };
      setMessages((prev) => [...prev, summaryMsg]);
    } catch (err) {
      console.error("Failed to generate executive summary:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerApproval = async (batchId: string) => {
    const b = await getRecoveryBatchById(batchId);
    if (b) {
      setBatchForApproval(b);
      setApprovalModalOpen(true);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-border/60">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Bot className="w-6 h-6 text-violet-600 dark:text-violet-400" />
            RecoverAI Copilot
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground mt-0.5">
            Evidence-grounded natural-language diagnostics and policy reasoning.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          {/* Investigation Scoper */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md border border-border bg-card text-xs font-mono">
            <Layers className="w-3.5 h-3.5 text-muted-foreground" />
            <select
              value={selectedInvestigation}
              onChange={(e) => setSelectedInvestigation(e.target.value)}
              className="bg-transparent text-foreground focus:outline-none cursor-pointer"
            >
              <option value="INV-00000000">INV-00000000 (UPI Degradation - RC-001)</option>
              <option value="RC-001">RC-001 (Active Incident)</option>
            </select>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={handleExecutiveSummary}
            disabled={loading}
            className="h-8 gap-1.5 text-xs font-medium border-violet-500/30 text-violet-600 dark:text-violet-400 hover:bg-violet-500/10"
          >
            <FileText className="w-3.5 h-3.5" />
            Exec Summary
          </Button>
        </div>
      </div>


      {/* Suggested Prompts Bar */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-semibold text-muted-foreground">Suggested prompts:</span>
        {suggestedPrompts.map((prompt, i) => (
          <button
            key={i}
            onClick={() => handleSend(prompt)}
            disabled={loading}
            className="px-2.5 py-1 rounded-full text-xs font-medium border border-border bg-card hover:bg-muted/70 hover:border-violet-500/40 text-foreground transition-all shadow-2xs"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Chat Area */}
      <Card className="border-border/80 shadow-xs flex flex-col h-[520px]">
        {/* Messages Container */}
        <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => {
            const isUser = msg.role === "user";
            return (
              <div
                key={msg.id}
                className={cn("flex gap-3 text-xs leading-relaxed", isUser ? "justify-end" : "justify-start")}
              >
                {!isUser && (
                  <div className="w-7 h-7 rounded-md bg-violet-600 text-white flex items-center justify-center shrink-0 shadow-xs mt-0.5">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div className={cn("max-w-xl space-y-2", isUser && "text-right")}>
                  <div
                    className={cn(
                      "p-3.5 rounded-xl shadow-xs text-xs",
                      isUser
                        ? "bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-950 text-left"
                        : "bg-muted/40 border border-border/70 text-foreground"
                    )}
                  >
                    <FormattedMarkdown content={msg.content} />

                    {/* Grounding & Evidence Chips */}
                    {msg.evidenceRefs && msg.evidenceRefs.length > 0 && (
                      <div className="mt-2.5 pt-2 border-t border-border/50 flex flex-wrap items-center gap-1.5">
                        <span className="text-[10px] uppercase font-semibold text-muted-foreground">Evidence:</span>
                        {msg.evidenceRefs.map((ref, idx) => (
                          <Link
                            key={idx}
                            href="/risk-cases/RC-001"
                            className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-violet-500/10 hover:bg-violet-500/20 text-violet-700 dark:text-violet-300 font-mono text-[10px] border border-violet-500/20 transition-colors"
                          >
                            <CheckCircle2 className="w-2.5 h-2.5" />
                            {ref}
                          </Link>
                        ))}
                        {msg.confidence && (
                          <span className="ml-auto text-[10px] font-mono text-muted-foreground">
                            {msg.confidence}% Conf
                          </span>
                        )}
                      </div>
                    )}

                    {/* Warnings if any */}
                    {msg.warnings && msg.warnings.length > 0 && (
                      <div className="mt-2 p-2 rounded bg-amber-500/10 border border-amber-500/20 text-amber-800 dark:text-amber-300 text-[11px] flex items-center gap-1.5">
                        <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                        <span>{msg.warnings.join(". ")}</span>
                      </div>
                    )}
                  </div>

                  {msg.structuredCard && (
                    <ActionProposalCard
                      card={msg.structuredCard}
                      onTriggerApproval={handleTriggerApproval}
                    />
                  )}

                  <span className="text-[10px] text-muted-foreground px-1 font-mono">{msg.timestamp}</span>
                </div>


                {isUser && (
                  <div className="w-7 h-7 rounded-md bg-neutral-800 text-white dark:bg-neutral-200 dark:text-neutral-900 flex items-center justify-center shrink-0 shadow-xs mt-0.5 font-bold text-[10px]">
                    ME
                  </div>
                )}
              </div>
            );
          })}

          {loading && (
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              <div className="w-7 h-7 rounded-md bg-violet-600/10 text-violet-600 flex items-center justify-center shrink-0">
                <Sparkles className="w-4 h-4 animate-spin" />
              </div>
              <div className="p-3 rounded-xl bg-muted/40 border border-border/70 text-xs">
                Analyzing payment telemetry and policy constraints...
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </CardContent>

        {/* Input Bar */}
        <div className="p-3 border-t border-border/70 bg-card rounded-b-xl">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              placeholder="Ask about revenue drops, payment errors, or recovery authorizations..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
              className="flex-1 h-10 px-3.5 text-xs bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-violet-500/40 text-foreground placeholder:text-muted-foreground"
            />
            <Button
              type="submit"
              disabled={!input.trim() || loading}
              variant="fintech"
              size="default"
              className="h-10 px-4 gap-1.5 font-semibold text-xs shrink-0"
            >
              <Send className="w-3.5 h-3.5" />
              Send
            </Button>
          </form>
        </div>
      </Card>

      {/* Approval Modal if triggered via chat */}
      {batchForApproval && (
        <ApprovalModal
          batch={batchForApproval}
          open={approvalModalOpen}
          onOpenChange={setApprovalModalOpen}
        />
      )}
    </div>
  );
}

export default function AIAssistantPage() {
  return (
    <Suspense
      fallback={
        <div className="space-y-6 max-w-4xl mx-auto">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-[520px] rounded-xl" />
        </div>
      }
    >
      <AIAssistantContent />
    </Suspense>
  );
}

