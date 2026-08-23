# RecoverAI — Demo Guide

> **Find lost revenue. Recover it safely. Prove the impact.**

This guide provides a structured walkthrough for evaluating the RecoverAI platform.

RecoverAI is an AI-powered payment intelligence and revenue recovery control center designed to help merchants:

```text
Detect payment failures
        ↓
Identify the root cause
        ↓
Quantify revenue at risk
        ↓
Determine recoverable revenue
        ↓
Create a bounded recovery plan
        ↓
Obtain merchant authorization
        ↓
Execute recovery safely
        ↓
Reconcile recovered revenue
        ↓
Create an immutable audit trail
```

The recommended demonstration follows this same operational workflow.

---

## Table of Contents

1. [Live Demo](#1-live-demo)
2. [What This Demo Demonstrates](#2-what-this-demo-demonstrates)
3. [Recommended Demo Flow](#3-recommended-demo-flow)
4. [Demo Scenario — HDFC UPI Degradation](#4-demo-scenario--hdfc-upi-degradation)
5. [Step 1 — Open the Dashboard](#5-step-1--open-the-dashboard)
6. [Dashboard Overview](#6-dashboard-overview)
7. [Key Demonstration Metrics](#7-key-demonstration-metrics)
8. [How to Explain "Revenue at Risk"](#8-how-to-explain-revenue-at-risk)
9. [How to Explain "Recoverable Revenue"](#9-how-to-explain-recoverable-revenue)
10. [Timeframe Selector](#10-timeframe-selector)
11. [Important Demo Note About Historical Data](#11-important-demo-note-about-historical-data)
12. [Active Incident Indicator](#12-active-incident-indicator)
13. [Step 2 — Open Risk Cases](#13-step-2--open-risk-cases)
14. [What Risk Cases Solve](#14-what-risk-cases-solve)
15. [Risk Case RC-001](#15-risk-case-rc-001)
16. [Step 3 — Risk Case Detail](#16-step-3--risk-case-detail)
17. [Root Cause Tree](#17-root-cause-tree)
18. [Why Root Cause Analysis Matters](#18-why-root-cause-analysis-matters)
19. [Step 4 — Open Investigation](#19-step-4--open-investigation)
20. [Investigation Page](#20-investigation-page)
21. [AI Investigation Flow](#21-ai-investigation-flow)
22. [Investigation Confidence](#22-investigation-confidence)
23. [Step 5 — Move to Recovery](#23-step-5--move-to-recovery)
24. [Recovery Operations](#24-recovery-operations)
25. [Merchant Authorization](#25-merchant-authorization)
26. [Why Authorization Matters](#26-why-authorization-matters)
27. [Recovery Safety Controls](#27-recovery-safety-controls)
28. [Step 6 — Active Recovery](#28-step-6--active-recovery)
29. [Recovery Execution Monitor](#29-recovery-execution-monitor)
30. [Recovery Simulation Controls](#30-recovery-simulation-controls)
31. [What "Pending in Queue" Means](#31-what-pending-in-queue-means)
32. [Real-World Recovery Example](#32-real-world-recovery-example)
33. [When Recovery Is Not Possible](#33-when-recovery-is-not-possible)
34. [Circuit Breaker Demo](#34-circuit-breaker-demo)
35. [Circuit Breaker Behavior](#35-circuit-breaker-behavior)
36. [Why the Circuit Breaker Matters](#36-why-the-circuit-breaker-matters)
37. [Recovery Reconciliation](#37-recovery-reconciliation)
38. [Revenue Reconciliation](#38-revenue-reconciliation)
39. [Step 7 — Transactions](#39-step-7--transactions)
40. [Transaction Explorer](#40-transaction-explorer)
41. [Why Transaction-Level Visibility Matters](#41-why-transaction-level-visibility-matters)
42. [Step 8 — Audit Trail](#42-step-8--audit-trail)
43. [What the Audit Trail Records](#43-what-the-audit-trail-records)
44. [Cryptographic Audit Proof](#44-cryptographic-audit-proof)
45. [Why Auditability Matters](#45-why-auditability-matters)
46. [Step 9 — AI Assistant](#46-step-9--ai-assistant)
47. [AI Assistant Safety](#47-ai-assistant-safety)
48. [Step 10 — Settings](#48-step-10--settings)
49. [Test Mode](#49-test-mode)
50. [Scenario Selector](#50-scenario-selector)
51. [Live Active Incident](#51-live-active-incident)
52. [Simulation Scenarios](#52-simulation-scenarios)
53. [Normal Baseline Scenario](#53-normal-baseline-scenario)
54. [Checkout Drop-off Scenario](#54-checkout-drop-off-scenario)
55. [Subscription Failure Scenario](#55-subscription-failure-scenario)
56. [Recovery Auto-Stop Scenario](#56-recovery-auto-stop-scenario)
57. [Suggested 5-Minute Demo](#57-suggested-5-minute-demo)
58. [Suggested 10-Minute Demo](#58-suggested-10-minute-demo)
59. [Recommended Demo Narrative](#59-recommended-demo-narrative)
60. [The Business Problem](#60-the-business-problem)
61. [Real-World Example for Judges](#61-real-world-example-for-judges)
62. [What Makes RecoverAI Different](#62-what-makes-recoverai-different)
63. [What the Demo Data Represents](#63-what-the-demo-data-represents)
64. [Important Data Integrity Principle](#64-important-data-integrity-principle)
65. [Demo Safety Notes](#65-demo-safety-notes)
66. [Common Questions During Demo](#66-common-questions-during-demo)
67. [Judge Evaluation Checklist](#67-judge-evaluation-checklist)
68. [Technical Stack](#68-technical-stack)
69. [Production Architecture](#69-production-architecture)
70. [Final Demo Story](#70-final-demo-story)
71. [Final Takeaway](#71-final-takeaway)

---

# 1. Live Demo

## Production Application

The live RecoverAI application is available at:

```text
https://recoverai.dhirajm.com.np/dashboard
```

Open the URL in a modern browser.

The production application is connected to the deployed FastAPI backend and managed PostgreSQL database.

---

# 2. What This Demo Demonstrates

The primary demonstration shows how RecoverAI handles a payment degradation incident affecting UPI transactions.

The core scenario is:

```text
Merchant
   ↓
Payment failures increase
   ↓
UPI payment success rate deteriorates
   ↓
Revenue becomes exposed
   ↓
RecoverAI detects the problem
   ↓
AI investigation identifies the likely cause
   ↓
RecoverAI calculates recoverable revenue
   ↓
Merchant reviews recovery plan
   ↓
Merchant authorizes recovery
   ↓
Recovery engine processes eligible transactions
   ↓
Safety controls monitor execution
   ↓
Recovered revenue is reconciled
   ↓
Actions are recorded in the audit trail
```

---

# 3. Recommended Demo Flow

For the strongest presentation, follow this order:

```text
1. Dashboard
2. Risk Cases
3. Risk Case Detail
4. Investigation
5. Recovery
6. Active Recovery
7. Transactions
8. Audit Trail
9. AI Assistant
10. Settings
```

The primary story is:

```text
Dashboard
    ↓
Risk Case
    ↓
Investigation
    ↓
Recovery Decision
    ↓
Recovery Execution
    ↓
Reconciliation
    ↓
Audit
```

---

# 4. Demo Scenario — HDFC UPI Degradation

The primary RecoverAI scenario is:

```text
HDFC UPI Degradation
Risk Case: RC-001
```

The incident represents a payment-processing degradation where UPI transactions are experiencing an elevated failure rate.

The objective is not simply to show that payments failed.

The objective is to demonstrate how RecoverAI converts payment failures into an actionable revenue recovery workflow.

---

# 5. Step 1 — Open the Dashboard

Open:

```text
https://recoverai.dhirajm.com.np/dashboard
```

The dashboard provides the high-level operational view.

It answers:

> "What is happening to the merchant's payment business right now?"

---

# 6. Dashboard Overview

The dashboard presents key metrics such as:

- Revenue at Risk
- Recoverable Revenue
- Revenue Recovered
- Payment Success Rate
- Active Risk Cases

These metrics allow an operations team to understand the financial impact before investigating individual transactions.

---

# 7. Key Demonstration Metrics

The controlled demonstration dataset contains:

```text
Total Transactions:      1,251
Captured:                1,024
Failed:                    227
Overall Success Rate:    ~81.9%
```

Financial exposure:

```text
Revenue at Risk:         ₹12.20L
Recoverable Revenue:      ₹3.05L
Revenue Recovered:        ₹42K
```

These values represent the controlled Acme Commerce demonstration environment.

They are not real customer payment records.

---

# 8. How to Explain "Revenue at Risk"

When presenting the dashboard, explain:

> Revenue at Risk represents the estimated transaction value exposed to payment failures or payment degradation.

For example:

```text
100 failed transactions
        ×
Average transaction value
        =
Potential revenue exposure
```

This does not mean that every failed transaction can be recovered.

That distinction is important.

---

# 9. How to Explain "Recoverable Revenue"

Recoverable Revenue represents the subset of exposed revenue that the system considers potentially eligible for a controlled recovery action.

Conceptually:

```text
Revenue at Risk
       │
       ├── Permanently lost / ineligible
       │
       └── Potentially recoverable
                 │
                 ▼
          Recoverable Revenue
```

RecoverAI therefore separates:

> Potential exposure

from:

> Actionable recovery opportunity

---

# 10. Timeframe Selector

The dashboard provides:

```text
24H
7D
30D
90D
```

Selecting a timeframe changes the requested telemetry window.

The frontend sends the selected timeframe to the backend.

For example:

```text
24H
 ↓
GET /api/v1/dashboard/metrics?timeframe=24h
```

and:

```text
7D
 ↓
GET /api/v1/dashboard/metrics?timeframe=7d
```

---

# 11. Important Demo Note About Historical Data

The current demonstration environment contains a limited telemetry history.

Therefore, when selecting:

```text
7D
30D
90D
```

RecoverAI should transparently communicate when sufficient historical telemetry is unavailable.

This is intentional.

The platform should never fabricate historical payment data merely to make a chart appear populated.

The correct behavior is:

```text
Limited historical data
        ↓
Show available telemetry
        ↓
Explain the limitation
```

rather than:

```text
Limited historical data
        ↓
Invent historical values
```

This demonstrates data integrity.

---

# 12. Active Incident Indicator

The navigation/header identifies the live incident:

```text
Active Incident:
UPI Degradation
RC-001
```

This is the authoritative demonstration incident.

Simulation profiles are separate from the live PostgreSQL telemetry.

---

# 13. Step 2 — Open Risk Cases

From the navigation bar, select:

```text
Risk Cases
```

or open:

```text
/risk-cases
```

This page represents the merchant's revenue risk case directory.

---

# 14. What Risk Cases Solve

A merchant may have thousands or millions of payment transactions.

It is not practical for an operations team to manually inspect every failed transaction.

RecoverAI groups meaningful payment problems into structured risk cases.

For example:

```text
Payment degradation
       ↓
Risk detection
       ↓
Risk case created
       ↓
Operations team investigates
```

---

# 15. Risk Case RC-001

Open:

```text
RC-001
```

This is the primary demonstration case.

The case represents:

```text
HDFC UPI Degradation
```

The detail page provides a deeper view of the incident.

---

# 16. Step 3 — Risk Case Detail

The Risk Case Detail page answers:

> "What exactly is going wrong?"

The page provides structured information such as:

- Incident severity
- Payment method
- Bank
- Failure type
- Revenue exposure
- Affected transactions
- Evidence
- Root cause indicators
- Recovery recommendation

---

# 17. Root Cause Tree

The root cause analysis is structured hierarchically.

Conceptually:

```text
Overall Payment Degradation
            │
            ▼
           UPI
            │
            ▼
         HDFC UPI
            │
            ▼
      Gateway Timeout
            │
            ▼
       Peak Impact
```

This helps the operator move from a broad symptom toward the most specific observable contributor.

---

# 18. Why Root Cause Analysis Matters

Without root cause analysis:

```text
Payment failed
      ↓
Retry everything
```

This is dangerous.

RecoverAI instead attempts to determine:

```text
Which payments failed?
        ↓
Why did they fail?
        ↓
Which failures are likely transient?
        ↓
Which transactions are eligible?
        ↓
What recovery action is safe?
```

This reduces unnecessary retries and financial risk.

---

# 19. Step 4 — Open Investigation

From the risk case, open the investigation.

The investigation represents the analytical stage of the workflow.

The primary investigation is:

```text
INV-00000000
```

---

# 20. Investigation Page

The investigation workspace presents structured AI-assisted analysis.

It is designed to answer:

> "Why did the incident happen?"

The investigation considers evidence such as:

- Payment method performance
- Bank performance
- Failure codes
- Transaction patterns
- Baseline comparisons
- Failure concentration
- Revenue impact

---

# 21. AI Investigation Flow

The investigation can be explained as:

```text
Detect anomaly
      ↓
Collect evidence
      ↓
Compare against baseline
      ↓
Identify strongest contributor
      ↓
Estimate confidence
      ↓
Produce structured conclusion
```

The system intentionally presents structured findings rather than exposing private internal model chain-of-thought.

---

# 22. Investigation Confidence

The demonstration investigation has a confidence score of approximately:

```text
83%
```

Explain this as:

> The system has high confidence that the identified payment degradation pattern is associated with the observed evidence.

Confidence is not a guarantee.

It is an indicator of how strongly the available evidence supports the investigation conclusion.

---

# 23. Step 5 — Move to Recovery

Once the problem has been investigated, move to:

```text
Recovery
```

or:

```text
/recovery
```

This page represents the operational recovery queue.

---

# 24. Recovery Operations

The Recovery page shows recovery batches and their lifecycle.

Typical states include:

```text
Pending Approval
Running
Completed
Stopped
```

The recovery workflow is intentionally controlled.

RecoverAI does not treat:

> Payment Failed

as an automatic instruction to:

> Charge Again

---

# 25. Merchant Authorization

Before financial recovery actions are dispatched, merchant authorization is required.

The intended workflow is:

```text
AI Recommendation
       ↓
Safety Policy Check
       ↓
Merchant Review
       ↓
Merchant Authorization
       ↓
Recovery Execution
```

This creates a human control point before financial actions.

---

# 26. Why Authorization Matters

Imagine a failed payment worth:

```text
₹5,000
```

If the first payment actually succeeded but the client incorrectly received a failure response, blindly retrying could result in:

```text
Original charge: ₹5,000
Retry charge:    ₹5,000
-----------------------
Potential duplicate debit: ₹10,000
```

Therefore, recovery must be bounded.

---

# 27. Recovery Safety Controls

RecoverAI applies safety constraints such as:

- Single retry limit
- Merchant approval
- Duplicate charge protection
- Idempotency protection
- Circuit breaker
- Failure thresholds
- Exposure limits

The goal is:

> Recover eligible revenue without turning recovery into another source of financial loss.

---

# 28. Step 6 — Active Recovery

Open an active recovery batch.

For example:

```text
RB-024
```

The Active Recovery page represents the execution monitor.

---

# 29. Recovery Execution Monitor

The execution monitor provides:

- Transaction progress
- Processing status
- Recovery activity
- Success/failure results
- Queue state
- Circuit breaker status
- Reconciliation

The operator can observe recovery execution rather than receiving only a final number.

---

# 30. Recovery Simulation Controls

The demonstration environment may provide controls such as:

```text
Play
Pause
Step
Fast-Forward
Reset
Trigger Failure Spike
```

These controls allow evaluators to understand how the recovery engine behaves during different execution conditions.

---

# 31. What "Pending in Queue" Means

A transaction in:

```text
Pending
```

or:

```text
Queued
```

means it has been identified for processing but has not yet completed the recovery attempt.

For example:

```text
438 transactions pending
```

means:

```text
438 eligible transactions
        ↓
Waiting for recovery processing
```

It does not mean:

```text
438 transactions definitely lost
```

and it does not mean:

```text
438 transactions successfully recovered
```

They are waiting to be processed.

---

# 32. Real-World Recovery Example

Consider:

```text
Customer attempts payment
Amount = ₹5,000
```

The payment gateway times out.

The customer sees:

```text
Payment Failed
```

but the merchant's system identifies that the failure may be transient.

RecoverAI can evaluate the transaction.

If the transaction satisfies recovery policies:

```text
Eligible
   ↓
Authorized
   ↓
Idempotency protection
   ↓
Recovery attempt
```

If successful:

```text
₹5,000
   ↓
Recovered Revenue
```

If the payment cannot safely be retried:

```text
Do not retry
   ↓
Protect customer
   ↓
Protect merchant
```

---

# 33. When Recovery Is Not Possible

Not every failed payment should be recovered.

Examples include:

- Insufficient funds
- Invalid payment credentials
- Expired card
- Explicit customer cancellation
- Permanent bank rejection
- Fraud-related decline
- Transaction already successfully captured
- Duplicate transaction risk
- Provider restrictions

In these cases, attempting recovery could create additional risk.

RecoverAI therefore focuses on:

> Recoverability, not blind retries.

---

# 34. Circuit Breaker Demo

One of the most important demonstrations is the recovery circuit breaker.

Navigate to an active recovery batch such as:

```text
RB-024
```

Use:

```text
Trigger Failure Spike
```

if the demonstration control is available.

---

# 35. Circuit Breaker Behavior

The recovery engine monitors execution health.

If failures cross the configured threshold:

```text
Failure rate increases
        ↓
Threshold exceeded
        ↓
Circuit breaker trips
        ↓
Recovery stops
        ↓
Remaining queue protected
        ↓
Audit event recorded
```

The recovery should transition into a clearly visible:

```text
RECOVERY STOPPED
```

state.

---

# 36. Why the Circuit Breaker Matters

Suppose recovery starts processing:

```text
1,000 transactions
```

and the payment provider suddenly begins failing most recovery attempts.

Continuing blindly could create:

- More failures
- More retries
- More customer friction
- More operational risk

The circuit breaker prevents uncontrolled execution.

It converts:

> Unexpected failure spike

into:

> Automatic stop

---

# 37. Recovery Reconciliation

After recovery execution, the system compares:

```text
Eligible transactions
        ↓
Attempted transactions
        ↓
Successful recoveries
        ↓
Recovered revenue
        ↓
Failed recovery attempts
```

This produces the actual recovery outcome.

---

# 38. Revenue Reconciliation

The important distinction is:

> Revenue at Risk

versus:

> Recoverable Revenue

versus:

> Revenue Recovered

For example:

```text
Revenue at Risk
₹12.20L
       ↓
Recoverable
₹3.05L
       ↓
Actually Recovered
₹42K
```

These values represent different stages of the recovery funnel.

---

# 39. Step 7 — Transactions

Open:

```text
Transactions
```

or:

```text
/transactions
```

This page provides transaction-level visibility.

---

# 40. Transaction Explorer

The Transaction Explorer allows the evaluator to inspect transaction data across payment methods and banks.

Examples include:

```text
UPI
Card
Net Banking
Wallet
```

and:

```text
HDFC
ICICI
SBI
Axis
```

---

# 41. Why Transaction-Level Visibility Matters

Aggregated metrics tell you:

> Something is wrong.

Transaction data helps answer:

> Which transactions are affected?

This is important for:

- Investigation
- Recovery eligibility
- Customer support
- Financial reconciliation
- Auditability

---

# 42. Step 8 — Audit Trail

Open:

```text
Audit
```

or:

```text
/audit
```

This page represents the accountability layer of RecoverAI.

---

# 43. What the Audit Trail Records

The audit trail can record events such as:

- AI investigation
- Risk detection
- Policy validation
- Merchant authorization
- Recovery batch creation
- Recovery execution
- Circuit breaker activation
- Recovery reconciliation

---

# 44. Cryptographic Audit Proof

RecoverAI uses SHA-256 based event verification.

Conceptually:

```text
Event Data
    ↓
SHA-256
    ↓
Cryptographic Hash
    ↓
Audit Record
```

This provides evidence that important operational events were recorded in a tamper-evident manner.

---

# 45. Why Auditability Matters

Financial automation requires accountability.

A merchant should be able to answer:

- Why was this transaction recovered?
- Who authorized it?
- What policy allowed it?
- When did it happen?
- What was the result?
- Did a circuit breaker stop anything?
- How much revenue was actually recovered?

The audit trail is designed to support those questions.

---

# 46. Step 9 — AI Assistant

Open:

```text
AI Assistant
```

or:

```text
/ai-assistant
```

The RecoverAI Copilot provides a conversational interface for operational questions.

Examples:

```text
What is causing the current payment degradation?

Which payment method has the highest failure rate?

How much revenue is recoverable?

What recovery action is recommended?

What happened during the latest recovery?
```

---

# 47. AI Assistant Safety

The AI assistant should be understood as an operational intelligence interface.

It does not replace:

- Merchant authorization
- Backend validation
- Recovery policies
- Safety controls

The assistant can recommend actions, but financial execution remains bounded by the platform's recovery controls.

---

# 48. Step 10 — Settings

Open:

```text
Settings
```

or:

```text
/settings
```

This section represents merchant configuration.

Relevant controls include:

- Merchant information
- Recovery limits
- Retry limits
- Failure thresholds
- Exposure controls
- Test Mode configuration

---

# 49. Test Mode

RecoverAI's demonstration environment should be treated as a controlled test/simulation environment.

The application may display indicators such as:

```text
TEST MODE
```

or:

```text
Razorpay Sandbox
```

These indicators are intentionally visible.

They prevent evaluators from confusing the demonstration environment with live production settlement infrastructure.

---

# 50. Scenario Selector

The application provides a scenario selector.

It separates:

> Live Active Incident

from:

> Simulation Scenarios

This distinction is important.

---

# 51. Live Active Incident

The primary live incident is:

```text
HDFC UPI Degradation
RC-001
```

This view is backed by the authoritative PostgreSQL demonstration telemetry.

---

# 52. Simulation Scenarios

The application may provide scenarios such as:

```text
Normal Baseline
Checkout Drop-off
Subscription Failures
Recovery Auto-stop
```

These are designed for demonstration and stress-testing.

They should not be interpreted as separate production databases or separate real merchants.

---

# 53. Normal Baseline Scenario

The Normal Baseline scenario represents a healthy payment environment.

Use it to demonstrate the contrast between:

> Healthy payment processing

and:

> Payment degradation

---

# 54. Checkout Drop-off Scenario

This scenario demonstrates a checkout-related revenue leakage pattern.

The purpose is to show that revenue loss does not always originate from the payment gateway itself.

Potential sources can include:

- Authentication friction
- OTP delays
- Checkout latency
- Mobile browser behavior
- Payment UI failures

---

# 55. Subscription Failure Scenario

This scenario represents recurring payment or subscription-related failure patterns.

The purpose is to demonstrate how RecoverAI can conceptually apply the same:

```text
Detect
Investigate
Quantify
Recover
Audit
```

workflow to recurring payment failures.

---

# 56. Recovery Auto-Stop Scenario

This is the circuit-breaker demonstration.

The evaluator can intentionally introduce a recovery failure spike and observe:

```text
Failure rate increases
        ↓
Threshold exceeded
        ↓
Circuit breaker
        ↓
Recovery stopped
        ↓
Remaining transactions protected
        ↓
Audit event generated
```

---

# 57. Suggested 5-Minute Demo

If you only have five minutes, use this flow:

### 00:00 — Dashboard

Show:

```text
Revenue at Risk
Recoverable Revenue
Revenue Recovered
Payment Success Rate
```

Say:

> "RecoverAI turns payment failures into measurable revenue recovery opportunities."

### 01:00 — Risk Case

Open:

```text
RC-001
```

Show:

```text
UPI
HDFC
Gateway Timeout
Revenue Impact
```

Say:

> "Instead of treating all failed payments equally, RecoverAI identifies where the degradation is concentrated."

### 02:00 — Investigation

Open:

```text
INV-00000000
```

Show:

```text
Evidence
Root Cause
Confidence
```

Say:

> "The investigation connects the payment degradation to the strongest observable contributor."

### 03:00 — Recovery

Open:

```text
RB-024
```

Show:

```text
Eligibility
Approval
Queue
Recovery Progress
```

Say:

> "Recovery is bounded by merchant authorization and safety controls rather than blindly retrying every failed payment."

### 04:00 — Circuit Breaker

Trigger:

```text
Failure Spike
```

Show:

```text
RECOVERY STOPPED
```

Say:

> "If recovery behavior becomes unsafe, the circuit breaker automatically stops further processing."

### 04:30 — Audit

Open:

```text
Audit
```

Show:

```text
Recovery Event
Authorization
Circuit Breaker
Reconciliation
```

Say:

> "Every important financial decision and execution event is recorded for accountability."

### 05:00 — Close

End with:

> "RecoverAI does not simply detect failed payments. It connects payment intelligence, financial exposure, investigation, controlled recovery, reconciliation, and auditability into one operational workflow."

---

# 58. Suggested 10-Minute Demo

For a longer presentation:

```text
1. Dashboard                         1 min
2. Risk Cases                        1 min
3. Risk Case Detail                 1 min
4. AI Investigation                 1.5 min
5. Recovery Operations              1 min
6. Active Recovery                  1.5 min
7. Circuit Breaker                  1 min
8. Transactions                     0.5 min
9. Audit Trail                      0.5 min
10. AI Assistant                    0.5 min
```

---

# 59. Recommended Demo Narrative

Do not present RecoverAI as:

> "This is a dashboard with payment data."

Instead, present it as:

> "RecoverAI is an operational control center for payment failures. It detects where revenue is leaking, investigates why it is happening, determines which failed transactions may be recoverable, requires authorization before financial action, executes recovery within strict safety bounds, reconciles the actual outcome, and records the complete operational history."

This framing communicates the business value much more clearly.

---

# 60. The Business Problem

The core problem is:

```text
Payment failure
      ↓
Customer sees failure
      ↓
Merchant potentially loses revenue
      ↓
Operations team lacks visibility
      ↓
Recoverable transactions remain unresolved
```

RecoverAI changes this into:

```text
Payment failure
      ↓
Detection
      ↓
Investigation
      ↓
Revenue quantification
      ↓
Recovery eligibility
      ↓
Merchant authorization
      ↓
Controlled recovery
      ↓
Reconciliation
      ↓
Audit
```

---

# 61. Real-World Example for Judges

Use this example if someone asks:

> "How does revenue recovery actually work?"

Explain:

Imagine a customer attempts to purchase something worth:

```text
₹5,000
```

The customer has sufficient funds.

The payment request reaches the payment infrastructure, but the gateway times out.

The customer sees:

```text
Payment Failed
```

The merchant may lose the sale.

RecoverAI can investigate whether the failure appears transient and whether the transaction is eligible for recovery.

If eligible:

```text
Failed Transaction
       ↓
Eligibility Check
       ↓
Merchant Authorization
       ↓
Idempotency Protection
       ↓
Controlled Retry
       ↓
Successful Payment
       ↓
₹5,000 Recovered
```

But if the payment already succeeded behind the scenes, RecoverAI must avoid retrying it.

That is why:

> Recovery ≠ Blind Retry

The platform is designed around:

> Safe Recovery

---

# 62. What Makes RecoverAI Different

The platform combines multiple operational layers:

```text
Payment Monitoring
        +
Risk Detection
        +
Root Cause Investigation
        +
Financial Impact Analysis
        +
Recovery Policy
        +
Merchant Authorization
        +
Bounded Automation
        +
Circuit Breaker
        +
Reconciliation
        +
Auditability
```

The goal is to move from:

> "Payment failed."

to:

> "Why did it fail? How much revenue is affected? Which transactions are recoverable? Is recovery safe? Who authorized it? What was recovered? What happened during execution?"

---

# 63. What the Demo Data Represents

The current RecoverAI application uses a controlled demonstration dataset.

It represents:

```text
Merchant:
Acme Commerce
```

The dataset includes:

```text
1,251 transactions
1,024 captured
227 failed
```

and the demonstrated financial metrics include:

```text
₹12.20L Revenue at Risk
₹3.05L Recoverable Revenue
₹42K Revenue Recovered
```

This data is intentionally controlled for demonstration purposes.

It should not be represented as actual production merchant financial data.

---

# 64. Important Data Integrity Principle

RecoverAI intentionally avoids fabricating historical telemetry.

If the available dataset does not contain enough historical information for:

```text
7D
30D
90D
```

the application should communicate that limitation.

This is preferable to generating artificial historical payment behavior.

The demo therefore prioritizes:

> Data integrity

over:

> Artificially impressive charts

---

# 65. Demo Safety Notes

During the demonstration:

- Do not enter real customer payment information.
- Do not enter real card numbers.
- Do not enter real banking credentials.
- Do not expose production secrets.
- Treat recovery execution as demonstration/simulation behavior unless explicitly configured otherwise.
- Do not interpret demonstration revenue as actual recovered merchant funds.
- Use the provided scenario controls for testing recovery behavior.

---

# 66. Common Questions During Demo

**"Is this real payment data?"**

Answer:

> No. The current environment uses a controlled Acme Commerce demonstration dataset connected to the production application infrastructure.

**"Is this actually connected to a payment gateway?"**

Answer:

> The platform is architected around payment-provider telemetry and recovery workflows, but the current demonstration environment is controlled and uses test/simulation behavior rather than real customer settlement activity.

**"Can RecoverAI recover every failed payment?"**

Answer:

> No. That would be unsafe. RecoverAI focuses on identifying potentially recoverable transactions and applying eligibility and safety rules before attempting recovery.

**"Why can't every failed payment be retried?"**

Answer:

> Some failures are permanent, some transactions may already have succeeded despite a timeout, and some retries can create duplicate charges. Recovery therefore requires eligibility checks, idempotency protection, authorization, and bounded execution.

**"What happens if recovery starts failing?"**

Answer:

> The circuit breaker monitors recovery performance and can automatically stop execution when configured failure thresholds are exceeded.

**"Why is there a merchant approval step?"**

Answer:

> Because financial recovery is a high-impact action. AI can recommend a recovery strategy, but the merchant retains control over financial execution.

**"What does Recoverable Revenue mean?"**

Answer:

> It is the portion of revenue at risk that the recovery logic considers potentially eligible for a safe recovery action. It is not the same as revenue actually recovered.

**"Why is Revenue Recovered smaller than Recoverable Revenue?"**

Answer:

> Recoverable revenue represents opportunity. Revenue recovered represents the amount actually recovered successfully during execution.

**"Why do 7D, 30D, and 90D sometimes show limited data?"**

Answer:

> The demonstration telemetry has limited historical coverage. RecoverAI intentionally communicates that limitation instead of fabricating historical payment data.

---

# 67. Judge Evaluation Checklist

A judge can evaluate RecoverAI using the following checklist:

### Product Understanding

```text
[ ] Clear problem statement
[ ] Clear revenue recovery use case
[ ] Clear target users
[ ] Clear business impact
```

### Detection

```text
[ ] Payment degradation visible
[ ] Revenue exposure visible
[ ] Risk cases available
```

### Investigation

```text
[ ] Root cause analysis
[ ] Evidence
[ ] Confidence
[ ] Structured AI output
```

### Recovery

```text
[ ] Recoverable revenue
[ ] Recovery eligibility
[ ] Merchant authorization
[ ] Execution monitoring
[ ] Safety controls
```

### Reliability

```text
[ ] Circuit breaker
[ ] Idempotency
[ ] Duplicate protection
[ ] Failure threshold
```

### Financial

```text
[ ] Revenue at risk
[ ] Recoverable revenue
[ ] Revenue recovered
[ ] Reconciliation
```

### Auditability

```text
[ ] Audit events
[ ] Authorization records
[ ] Recovery events
[ ] Circuit breaker events
[ ] Cryptographic verification
```

### Engineering

```text
[ ] Next.js frontend
[ ] FastAPI backend
[ ] PostgreSQL
[ ] REST API
[ ] Docker
[ ] Cloud deployment
[ ] Production HTTPS
```

---

# 68. Technical Stack

The production system uses:

```text
Frontend
────────
Next.js
React
TypeScript
Tailwind CSS

Backend
───────
FastAPI
Python
Pydantic
SQLAlchemy
asyncpg

Database
────────
PostgreSQL

Infrastructure
──────────────
Docker
Netlify
Render
Managed PostgreSQL

Development
───────────
Git
GitHub
ESLint
TypeScript
Pytest
```

---

# 69. Production Architecture

The live application follows:

```text
Browser
   │
   ▼
Netlify
   │
   │ HTTPS REST API
   ▼
Render
   │
   ▼
FastAPI
   │
   │ Async SQL
   ▼
Managed PostgreSQL
```

The frontend never directly accesses PostgreSQL.

---

# 70. Final Demo Story

The entire RecoverAI demonstration can be summarized in one sentence:

> RecoverAI helps merchants turn payment failures into measurable, explainable, and safely recoverable revenue opportunities.

The complete operational story is:

```text
              PAYMENT FAILURE
                     │
                     ▼
              DETECT PROBLEM
                     │
                     ▼
             IDENTIFY RISK CASE
                     │
                     ▼
              INVESTIGATE CAUSE
                     │
                     ▼
             QUANTIFY EXPOSURE
                     │
                     ▼
           IDENTIFY RECOVERABILITY
                     │
                     ▼
            CREATE RECOVERY PLAN
                     │
                     ▼
            MERCHANT AUTHORIZATION
                     │
                     ▼
            BOUNDED RECOVERY
                     │
             ┌───────┴───────┐
             │               │
             ▼               ▼
          SUCCESS         FAILURE SPIKE
             │               │
             ▼               ▼
        RECONCILIATION   CIRCUIT BREAKER
             │               │
             └───────┬───────┘
                     ▼
                AUDIT TRAIL
                     │
                     ▼
              PROVEN IMPACT
```

---

# 71. Final Takeaway

RecoverAI is not simply a payment analytics dashboard.

It is designed as an operational workflow connecting:

```text
Payment Intelligence
        +
AI-Assisted Investigation
        +
Revenue Risk Quantification
        +
Recovery Decisioning
        +
Merchant Authorization
        +
Bounded Financial Automation
        +
Circuit-Breaker Protection
        +
Revenue Reconciliation
        +
Cryptographic Auditability
```

The central principle is:

> Do not blindly retry failed payments. Understand the failure, identify what is safely recoverable, authorize the action, execute within strict limits, and prove the outcome.

---

## Live Demo

```text
https://recoverai.dhirajm.com.np/dashboard
```
