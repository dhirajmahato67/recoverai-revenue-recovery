# RecoverAI — AI Revenue Recovery Platform

> **Tagline:** *Find lost revenue. Recover it safely. Prove the impact.*

RecoverAI is an AI-powered revenue recovery control center for merchants. It monitors payment gateway telemetry in real time, detects revenue at risk from payment failures and checkout leakage, investigates root causes through structured AI diagnostics, recommends bounded recovery actions, enforces mandatory merchant authorization, executes live recovery workflows with safety circuit-breakers, reconciles actual recovered revenue, and maintains an immutable cryptographic audit trail.

---

## 🏛️ Fintech Product & Design Philosophy

RecoverAI is designed as an enterprise-grade fintech operations platform with the visual and interaction quality of **Stripe Dashboard, Linear, Ramp, and Brex**.

- **Trust & Financial Precision:** Exact Indian Rupee formatting (`₹8.40L`, `₹2.10L`, `₹1.28L`, `₹4,800`), clean typography (`Inter` & `JetBrains Mono`), and high-contrast, calm data hierarchy.
- **AI Intelligence with Safety Bounds:** Root cause decision trees and structured reasoning panels showing findings, evidence, and conclusions without exposing raw internal model chains-of-thought.
- **Bounded Autonomous Execution:** Strict 5-point safety constraints: single retry limit, merchant approval gate, duplicate charge protection, idempotency token guarantees, and automated circuit-breaker auto-stop thresholds.
- **Immutable Ledger:** Every AI diagnosis, policy check, merchant signature, and batch dispatch is cryptographically signed with SHA-256 ledger proofs.
- **Clear Test Mode Indicators:** Prominent amber Test Mode badge and Razorpay Sandbox disclaimer to prevent confusion with production settlements.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Run the Development Server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser. The application automatically redirects `/` to `/dashboard`.

---

## 🧭 Application Routes

| Route | Description |
|---|---|
| `/dashboard` | **Overview Dashboard:** KPI metrics (Revenue at Risk, Recoverable, Recovered, Active Cases), 7D/30D/90D revenue trends, Payment Health degradation breakdown, AI Revenue Insight card, and Recovery Performance charts. |
| `/risk-cases` | **Revenue Risk Cases:** Filterable data directory sorted by severity (`HIGH`, `MEDIUM`, `LOW`), risk type, and status with confidence scores. |
| `/risk-cases/[caseId]` | **Risk Case Detail:** Diagnostic summary, multi-tier Root Cause Tree (`Overall → UPI → HDFC UPI → Peak Impact`), evidence deltas, and bounded recovery action card. |
| `/investigations/[investigationId]` | **AI Investigation Workspace:** Split-screen experience with progressive reasoning checklist on the left, structured AI analysis on the right, and collapsible tool execution traces (`get_root_cause`, etc.). |
| `/recovery` | **Recovery Operations:** Batch directory with status filters (`Pending Approval`, `Running`, `Completed`, `Stopped`), conversion stats, and approval modals. |
| `/recovery/[batchId]` | **Live Recovery Execution Monitor:** Real-time transaction progress bar, live activity stream log, simulation controls (`Play`, `Pause`, `Step`, `Fast-Forward`), auto-stop circuit breaker, and post-recovery reconciliation card. |
| `/transactions` | **Transaction Explorer:** Multi-filter explorer across payment methods (`UPI`, `Card`, `Net Banking`, `Wallet`) and banks (`HDFC`, `ICICI`, `SBI`, `Axis`) with slide-out Transaction Detail Drawer. |
| `/audit` | **Immutable Audit Trail:** Fintech ledger recording every financial decision, policy validation, AI recommendation, and circuit-breaker trip with SHA-256 verification hashes. |
| `/ai-assistant` | **RecoverAI Copilot:** Conversational operations assistant with suggested prompt chips and structured bounded recovery proposals. |
| `/settings` | **Merchant Settings & Policies:** Merchant entity info, recovery safety bounds (exposure caps, retry limits, failure thresholds), and Razorpay Test Mode integration. |

---

## 🧪 Interactive Demo Scenarios for Evaluators

RecoverAI includes an interactive **Scenario Selector** in the header to effortlessly evaluate different platform states:

1. **Payment Degradation (HDFC UPI) — Primary Happy Path:**
   - UPI success rate drops 12.5pp (81.7% vs 94.2% baseline) with ₹8.40L revenue at risk.
   - **Flow:** Dashboard → Investigate Anomaly (`RC-001`) → Inspect AI Root Cause Tree → View AI Investigation (`INV-001`) → Review Recovery Plan → Authorize Batch `RB-024` → Watch live simulation process transactions → See ₹2.86L actual recovered funds → Inspect recorded event in Audit Trail.

2. **Recovery Auto-Stop (Circuit Breaker Failure Path):**
   - Simulates a transient failure spike during live recovery execution.
   - **Flow:** In `/recovery/RB-024` or `/recovery/RB-025`, click **Trigger Auto-Stop Demo**. When failure rate crosses the 30% limit, the system instantly trips the circuit-breaker, transitions into the high-visibility **RECOVERY STOPPED** state, protects the remaining transaction queue, and logs the trip to the Audit Trail.

3. **Mobile Checkout Drop-off:**
   - Safari Mobile OTP autofill latency anomaly (₹3.20L at risk).

4. **Subscription Renewal Failures:**
   - Recurring e-mandate presentation failure batch (₹1.80L at risk).

5. **Normal Baseline (Optimal State):**
   - Healthy 98.4% payment success rate, zero critical alerts.

---

## ⚡ Global Power Features

- **Command Palette (`Cmd + K` / `Ctrl + K`):** Jump to any case (`RC-001`), transaction (`TX-103928`), batch (`RB-024`), or navigation route instantly.
- **Notification Center:** Real-time dropdown alerting merchants of high revenue risk, circuit-breaker trips, and completed recoveries.
- **Theme Switcher:** Seamless Light & Dark mode support designed with high-contrast fintech tokens.
- **Simulation Control Bar:** Full interactive playback controls (`Play`, `Pause`, `Step 1 Tx`, `Fast-Forward`, `Trigger Failure Spike`, `Reset`).

---

## 🔌 Connecting to the Python / FastAPI Backend

RecoverAI is architected with a decoupled service layer (`src/lib/api/*`). To transition from the built-in mock engine to a live FastAPI service:

1. Copy `.env.example` to `.env.local`:
   ```bash
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

2. The `apiClient` in `src/lib/api/client.ts` automatically switches from mock handlers to direct HTTP calls:
   - `GET /api/v1/dashboard/metrics`
   - `GET /api/v1/risk-cases`
   - `GET /api/v1/risk-cases/{caseId}`
   - `GET /api/v1/investigations/{investigationId}`
   - `GET /api/v1/recovery/batches`
   - `POST /api/v1/recovery/batches/{batchId}/approve`
   - `GET /api/v1/transactions`
   - `GET /api/v1/audit`
   - `POST /api/v1/assistant/chat`

Zero UI code modifications are required when attaching the backend!

---

## 🛡️ Security Guarantees

- **No Secrets in Frontend:** Razorpay private API keys, LLM credentials, and database connection strings belong strictly in the backend vault and are never stored or logged in client code.
- **Idempotency Protected:** Bounded recovery batches enforce unique idempotency tokens per transaction attempt to prevent duplicate debits.
- **Strict Authorization:** Autonomous financial actions cannot dispatch without explicit merchant admin signoff.
