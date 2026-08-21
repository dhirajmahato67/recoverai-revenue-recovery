"use client";

import React, { useState, useEffect } from "react";
import { getMerchantSettings, updateMerchantSettings } from "@/lib/api";
import { MerchantProfile } from "@/lib/types";
import { formatINR } from "@/lib/utils";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Building2,
  ShieldCheck,
  Zap,
  Lock,
  CheckCircle2,
  Save,
  AlertTriangle,
  RefreshCw,
} from "lucide-react";

export default function SettingsPage() {
  const [merchant, setMerchant] = useState<MerchantProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  // Form State
  const [maxRetries, setMaxRetries] = useState(1);
  const [maxBatchSize, setMaxBatchSize] = useState(500);
  const [maxExposure, setMaxExposure] = useState(250000);
  const [failureThreshold, setFailureThreshold] = useState(30.0);
  const [requireApproval, setRequireApproval] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const data = await getMerchantSettings();
        setMerchant(data);
        if (data) {
          setMaxRetries(data.policies.maxRetries);
          setMaxBatchSize(data.policies.maxBatchSize);
          setMaxExposure(data.policies.maxExposureLimitINR);
          setFailureThreshold(data.policies.failureThresholdPercent);
          setRequireApproval(data.policies.requireMerchantApproval);
        }
      } catch (err) {
        console.error("Failed to load settings:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setSavedSuccess(false);
    try {
      await updateMerchantSettings({
        policies: {
          maxRetries,
          maxBatchSize,
          maxExposureLimitINR: maxExposure,
          failureThresholdPercent: failureThreshold,
          requireMerchantApproval: requireApproval,
          duplicateProtection: true,
          idempotencyProtection: true,
        },
      });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      console.error("Failed to save settings:", err);
    } finally {
      setSaving(false);
    }
  };

  if (loading || !merchant) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-64 rounded-lg" />
        <Skeleton className="h-80 rounded-lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-border/60">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-foreground">
            Settings & Safety Policy Controls
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground mt-0.5">
            Configure merchant business context, automated recovery bounds, and payment gateway sandbox connections.
          </p>
        </div>

        <Button
          variant="fintech"
          size="sm"
          onClick={handleSave}
          disabled={saving}
          className="h-8 gap-1.5 font-semibold text-xs shrink-0"
        >
          {saving ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
          {savedSuccess ? "Saved Successfully!" : "Save Policy Changes"}
        </Button>
      </div>

      {/* Section 1: Merchant Profile */}
      <Card className="border-border/80 shadow-xs">
        <CardHeader className="pb-3 border-b border-border/60">
          <CardTitle className="text-sm font-semibold flex items-center gap-2">
            <Building2 className="w-4 h-4 text-muted-foreground" />
            Merchant Profile & Financial Context
          </CardTitle>
          <CardDescription className="text-xs text-muted-foreground">
            Registered corporate entity and reporting currency specifications.
          </CardDescription>
        </CardHeader>

        <CardContent className="p-5 grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="text-[11px] font-semibold text-muted-foreground block mb-1">
              Business Name
            </label>
            <input
              type="text"
              defaultValue={merchant.businessName}
              disabled
              className="w-full h-8 px-3 bg-muted border border-border rounded-md text-foreground cursor-not-allowed font-medium"
            />
          </div>

          <div>
            <label className="text-[11px] font-semibold text-muted-foreground block mb-1">
              Legal Entity Name
            </label>
            <input
              type="text"
              defaultValue={merchant.legalEntity}
              disabled
              className="w-full h-8 px-3 bg-muted border border-border rounded-md text-foreground cursor-not-allowed"
            />
          </div>

          <div>
            <label className="text-[11px] font-semibold text-muted-foreground block mb-1">
              Base Settlement Currency
            </label>
            <input
              type="text"
              defaultValue="INR (₹ Indian Rupee)"
              disabled
              className="w-full h-8 px-3 bg-muted border border-border rounded-md text-foreground cursor-not-allowed font-mono"
            />
          </div>

          <div>
            <label className="text-[11px] font-semibold text-muted-foreground block mb-1">
              Timezone
            </label>
            <input
              type="text"
              defaultValue={merchant.timezone}
              disabled
              className="w-full h-8 px-3 bg-muted border border-border rounded-md text-foreground cursor-not-allowed font-mono"
            />
          </div>
        </CardContent>
      </Card>

      {/* Section 2: Recovery Policy Rules */}
      <Card className="border-violet-500/30 shadow-xs">
        <CardHeader className="pb-3 border-b border-border/60">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-violet-600 dark:text-violet-400" />
              Automated Recovery Policy Bounds
            </CardTitle>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-violet-500/10 text-violet-700 dark:text-violet-300 font-mono">
              Policy Engine Active
            </span>
          </div>
          <CardDescription className="text-xs text-muted-foreground">
            Hard constraints enforced before any financial retry or customer outreach action can execute.
          </CardDescription>
        </CardHeader>

        <CardContent className="p-5 space-y-5 text-xs">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-[11px] font-semibold text-foreground block mb-1">
                Maximum Retries Per Transaction
              </label>
              <input
                type="number"
                min={1}
                max={3}
                value={maxRetries}
                onChange={(e) => setMaxRetries(Number(e.target.value))}
                className="w-full h-8 px-3 bg-background border border-input rounded-md text-foreground font-mono focus:ring-1 focus:ring-ring"
              />
              <span className="text-[10px] text-muted-foreground mt-0.5 block">
                Single retry (1) recommended to prevent card network fatigue.
              </span>
            </div>

            <div>
              <label className="text-[11px] font-semibold text-foreground block mb-1">
                Maximum Batch Size
              </label>
              <input
                type="number"
                min={50}
                max={2000}
                value={maxBatchSize}
                onChange={(e) => setMaxBatchSize(Number(e.target.value))}
                className="w-full h-8 px-3 bg-background border border-input rounded-md text-foreground font-mono focus:ring-1 focus:ring-ring"
              />
              <span className="text-[10px] text-muted-foreground mt-0.5 block">
                Upper bound on transaction records dispatched per batch.
              </span>
            </div>

            <div>
              <label className="text-[11px] font-semibold text-foreground block mb-1">
                Maximum Exposure Cap (INR ₹)
              </label>
              <input
                type="number"
                min={10000}
                max={1000000}
                value={maxExposure}
                onChange={(e) => setMaxExposure(Number(e.target.value))}
                className="w-full h-8 px-3 bg-background border border-input rounded-md text-foreground font-mono focus:ring-1 focus:ring-ring"
              />
              <span className="text-[10px] text-muted-foreground mt-0.5 block">
                Hard financial exposure cap ({formatINR(maxExposure)}).
              </span>
            </div>

            <div>
              <label className="text-[11px] font-semibold text-foreground block mb-1">
                Safety Circuit Breaker Threshold (%)
              </label>
              <input
                type="number"
                min={10}
                max={50}
                step={0.5}
                value={failureThreshold}
                onChange={(e) => setFailureThreshold(Number(e.target.value))}
                className="w-full h-8 px-3 bg-background border border-input rounded-md text-foreground font-mono focus:ring-1 focus:ring-ring"
              />
              <span className="text-[10px] text-rose-600 dark:text-rose-400 mt-0.5 block">
                Automatically halts workflow if failure rate crosses {failureThreshold}%.
              </span>
            </div>
          </div>

          <div className="space-y-3 pt-2 border-t border-border/60">
            <label className="flex items-center gap-2.5 cursor-pointer">
              <input
                type="checkbox"
                checked={requireApproval}
                onChange={(e) => setRequireApproval(e.target.checked)}
                className="h-4 w-4 rounded border-border text-neutral-900 focus:ring-neutral-950"
              />
              <div>
                <span className="font-semibold text-foreground text-xs block">
                  Mandatory Merchant Admin Approval
                </span>
                <span className="text-[11px] text-muted-foreground">
                  Require explicit admin signature before any financial recovery batch is dispatched.
                </span>
              </div>
            </label>
          </div>
        </CardContent>
      </Card>

      {/* Section 3: Integrations & Gateway (Razorpay Test Mode) */}
      <Card className="border-border/80 shadow-xs">
        <CardHeader className="pb-3 border-b border-border/60">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-500" />
              Payment Gateway Integration
            </CardTitle>
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full border border-amber-500/30 bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400 text-xs font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
              Connected (Test Mode)
            </div>
          </div>
          <CardDescription className="text-xs text-muted-foreground">
            Sandboxed payment processing gateway credentials and webhook health telemetry.
          </CardDescription>
        </CardHeader>

        <CardContent className="p-5 space-y-4 text-xs">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <span className="text-[11px] font-semibold text-muted-foreground block mb-1">
                Gateway Provider
              </span>
              <p className="font-semibold text-foreground">{merchant.gateway}</p>
            </div>

            <div>
              <span className="text-[11px] font-semibold text-muted-foreground block mb-1">
                Razorpay Key ID (Public Client Key)
              </span>
              <p className="font-mono font-semibold text-foreground">{merchant.maskedKeyId}</p>
            </div>
          </div>

          <div className="rounded-md border border-border/60 bg-muted/20 p-3 flex items-center justify-between">
            <div className="space-y-0.5">
              <span className="font-semibold text-foreground text-xs flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                Ingestion Webhook Synchronized
              </span>
              <p className="text-[11px] text-muted-foreground">
                Last webhook event received 2 minutes ago (telemetry latency: 142ms)
              </p>
            </div>
            <span className="text-[10px] font-mono px-2 py-1 rounded bg-muted text-muted-foreground">
              v1/webhooks/razorpay
            </span>
          </div>

          {/* Security Note */}
          <div className="rounded-md border border-border/60 bg-muted/10 p-3 text-[11px] text-muted-foreground flex items-center gap-2">
            <Lock className="w-3.5 h-3.5 text-muted-foreground shrink-0" />
            <span>
              Razorpay API secrets and private tokens are encrypted server-side in the backend vault and are never exposed to the frontend.
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
