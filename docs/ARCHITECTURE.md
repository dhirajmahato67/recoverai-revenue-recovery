# RecoverAI — System Architecture

> **Technical architecture, data flow, service boundaries, security model, and production deployment architecture**

RecoverAI is a full-stack payment intelligence and revenue recovery platform designed to help merchants detect payment degradation, identify revenue at risk, investigate root causes, determine recoverability, authorize controlled recovery actions, monitor recovery execution, reconcile financial outcomes, and maintain an auditable record of every important decision.

The architecture separates the user interface, API/business logic, persistence layer, and deployment infrastructure so that payment intelligence and recovery operations are not dependent on frontend-only state.

---

## Table of Contents

1. [Architecture Goals](#1-architecture-goals)
2. [High-Level System Architecture](#2-high-level-system-architecture)
3. [Architectural Layers](#3-architectural-layers)
4. [Presentation Layer](#4-presentation-layer)
5. [Frontend Application Structure](#5-frontend-application-structure)
6. [Frontend API Client](#6-frontend-api-client)
7. [Backend Architecture](#7-backend-architecture)
8. [Backend Responsibility](#8-backend-responsibility)
9. [Backend Logical Structure](#9-backend-logical-structure)
10. [Database Architecture](#10-database-architecture)
11. [Core Data Domains](#11-core-data-domains)
12. [Data Flow](#12-data-flow)
13. [Dashboard Data Flow](#13-dashboard-data-flow)
14. [Timeframe Architecture](#14-timeframe-architecture)
15. [Payment Health Architecture](#15-payment-health-architecture)
16. [Risk Detection Architecture](#16-risk-detection-architecture)
17. [Investigation Architecture](#17-investigation-architecture)
18. [Root Cause Architecture](#18-root-cause-architecture)
19. [Financial Impact Architecture](#19-financial-impact-architecture)
20. [Recovery Architecture](#20-recovery-architecture)
21. [Recovery Authorization](#21-recovery-authorization)
22. [Recovery Safety Architecture](#22-recovery-safety-architecture)
23. [Idempotency Protection](#23-idempotency-protection)
24. [Retry Bounds](#24-retry-bounds)
25. [Circuit Breaker Architecture](#25-circuit-breaker-architecture)
26. [Recovery Reconciliation](#26-recovery-reconciliation)
27. [Audit Architecture](#27-audit-architecture)
28. [Multi-Tenant Architecture](#28-multi-tenant-architecture)
29. [API Architecture](#29-api-architecture)
30. [Health Architecture](#30-health-architecture)
31. [Frontend Route Architecture](#31-frontend-route-architecture)
32. [Dashboard Architecture](#32-dashboard-architecture)
33. [Risk Case Architecture](#33-risk-case-architecture)
34. [Investigation Architecture (UI)](#34-investigation-architecture-ui)
35. [Recovery UI Architecture](#35-recovery-ui-architecture)
36. [Transactions Architecture](#36-transactions-architecture)
37. [Audit Architecture (UI)](#37-audit-architecture-ui)
38. [AI Assistant Architecture](#38-ai-assistant-architecture)
39. [Scenario Architecture](#39-scenario-architecture)
40. [Live Incident vs Simulation](#40-live-incident-vs-simulation)
41. [Time-Series Data Architecture](#41-time-series-data-architecture)
42. [Production Deployment Architecture](#42-production-deployment-architecture)
43. [Production Request Flow](#43-production-request-flow)
44. [Production Environment Variables](#44-production-environment-variables)
45. [CORS Architecture](#45-cors-architecture)
46. [Docker Architecture](#46-docker-architecture)
47. [Local Development Architecture](#47-local-development-architecture)
48. [Database Initialization](#48-database-initialization)
49. [Canonical Demonstration Dataset](#49-canonical-demonstration-dataset)
50. [Security Architecture](#50-security-architecture)
51. [Secret Management](#51-secret-management)
52. [Recovery Security Boundary](#52-recovery-security-boundary)
53. [Failure Handling Architecture](#53-failure-handling-architecture)
54. [Observability](#54-observability)
55. [Testing Architecture](#55-testing-architecture)
56. [Architecture Quality Gates](#56-architecture-quality-gates)
57. [End-to-End Architecture Example](#57-end-to-end-architecture-example)
58. [Why the Architecture Uses a Backend](#58-why-the-architecture-uses-a-backend)
59. [Why PostgreSQL Is the Source of Truth](#59-why-postgresql-is-the-source-of-truth)
60. [Production vs Local Architecture](#60-production-vs-local-architecture)
61. [Deployment Pipeline](#61-deployment-pipeline)
62. [Domain Architecture](#62-domain-architecture)
63. [Architecture Principles](#63-architecture-principles)
64. [Current Architecture Summary](#64-current-architecture-summary)
65. [Final Architecture Perspective](#65-final-architecture-perspective)

---

# 1. Architecture Goals

RecoverAI is designed around the following architectural goals:

## 1.1 Real Data

The production application should consume data through the FastAPI backend and PostgreSQL database rather than relying on frontend-only mock values.

## 1.2 Financial Safety

Recovery operations must be bounded by explicit safety policies.

The architecture therefore supports:

- Merchant authorization
- Idempotency protection
- Retry limits
- Exposure limits
- Failure-rate thresholds
- Circuit-breaker auto-stop
- Sandbox/test-mode execution

## 1.3 Separation of Concerns

The system separates:

```text
Presentation
     ↓
API
     ↓
Business Logic
     ↓
Data Access
     ↓
PostgreSQL
```

The frontend does not directly access PostgreSQL.

## 1.4 Auditability

Important actions should be traceable from:

```text
Payment Failure
      ↓
Risk Detection
      ↓
Investigation
      ↓
Recovery Recommendation
      ↓
Merchant Authorization
      ↓
Recovery Execution
      ↓
Reconciliation
      ↓
Audit Record
```

## 1.5 Production Deployability

The architecture supports both:

- Local development using Docker/local services
- Public production deployment using Netlify + Render + managed PostgreSQL

---

# 2. High-Level System Architecture

The complete production architecture is:

```text
                         ┌──────────────────────┐
                         │       End User       │
                         │ Merchant / Operator  │
                         └──────────┬───────────┘
                                    │
                                    │ HTTPS
                                    ▼
                    ┌──────────────────────────────┐
                    │           Netlify            │
                    │      Frontend Hosting        │
                    │                              │
                    │ Next.js + React + TypeScript │
                    └──────────────┬───────────────┘
                                   │
                                   │ HTTPS REST API
                                   │ X-Merchant-ID
                                   ▼
                    ┌──────────────────────────────┐
                    │           Render             │
                    │                              │
                    │       FastAPI Backend        │
                    │                              │
                    │  API Routes                  │
                    │  Business Logic              │
                    │  Validation                  │
                    │  Recovery Controls           │
                    │  Investigation Logic          │
                    │  Data Access                 │
                    └──────────────┬───────────────┘
                                   │
                                   │ Async SQL
                                   ▼
                    ┌──────────────────────────────┐
                    │      Managed PostgreSQL      │
                    │                              │
                    │ Transactions                 │
                    │ Risk Cases                   │
                    │ Investigations               │
                    │ Recovery Batches             │
                    │ Audit Logs                   │
                    │ Merchant Configuration       │
                    └──────────────────────────────┘
```

The public production application is available at:

```text
https://recoverai.dhirajm.com.np/dashboard
```

---

# 3. Architectural Layers

RecoverAI can be understood as five major layers:

```text
┌──────────────────────────────────────────┐
│  1. Presentation Layer                   │
│  Next.js / React / TypeScript            │
├──────────────────────────────────────────┤
│  2. API Layer                            │
│  FastAPI REST endpoints                  │
├──────────────────────────────────────────┤
│  3. Business Logic Layer                 │
│  Risk / Investigation / Recovery Logic   │
├──────────────────────────────────────────┤
│  4. Persistence Layer                    │
│  SQLAlchemy / Repository Layer           │
├──────────────────────────────────────────┤
│  5. Infrastructure Layer                 │
│  Docker / Render / Netlify / PostgreSQL  │
└──────────────────────────────────────────┘
```

Each layer has a specific responsibility.

---

# 4. Presentation Layer

The presentation layer is implemented using:

- Next.js
- React
- TypeScript
- Tailwind CSS
- Reusable React components

The frontend is responsible for:

- Rendering dashboards
- Displaying financial metrics
- Displaying risk cases
- Presenting investigation results
- Showing recovery operations
- Displaying transactions
- Displaying audit records
- Handling user navigation
- Collecting merchant authorization actions
- Presenting API errors and system states
- Providing responsive layouts for desktop, laptop, tablet, and mobile devices

The frontend does not directly communicate with PostgreSQL.

Instead:

```text
React Component
      ↓
API Client
      ↓
FastAPI
      ↓
PostgreSQL
```

---

# 5. Frontend Application Structure

The major frontend areas are:

```text
src/
│
├── app/
│   ├── dashboard/
│   ├── risk-cases/
│   ├── investigations/
│   ├── recovery/
│   ├── transactions/
│   ├── audit/
│   ├── ai-assistant/
│   └── settings/
│
├── components/
│   ├── dashboard/
│   ├── navigation/
│   ├── layout/
│   ├── recovery/
│   ├── investigations/
│   └── shared/
│
└── lib/
    └── api/
        ├── client.ts
        ├── dashboard.ts
        ├── risk-cases.ts
        ├── investigations.ts
        ├── recovery.ts
        ├── transactions.ts
        └── audit.ts
```

The exact directory structure may evolve as the application grows, but the architectural principle remains the same:

> UI components should consume API services rather than directly implementing persistence logic.

---

# 6. Frontend API Client

RecoverAI centralizes backend communication through an API client layer.

Conceptually:

```text
Dashboard Component
        │
        ▼
dashboard.ts
        │
        ▼
apiClient
        │
        ▼
FastAPI REST API
```

This prevents individual components from creating independent networking implementations.

The API base URL is controlled through:

```text
NEXT_PUBLIC_API_URL
```

For production, the frontend points to the public FastAPI backend.

For local development, it can point to the local backend:

```text
http://localhost:8000
```

The production frontend should never depend on a user's local machine.

---

# 7. Backend Architecture

The backend is implemented using:

- Python
- FastAPI
- Pydantic
- SQLAlchemy 2.x
- Async database access
- PostgreSQL
- asyncpg

The backend provides the central application API and business rules.

Conceptually:

```text
HTTP Request
     │
     ▼
FastAPI Router
     │
     ▼
Validation
     │
     ▼
Business Logic
     │
     ▼
Repository / Data Access
     │
     ▼
PostgreSQL
```

---

# 8. Backend Responsibility

The backend is responsible for:

- Request validation
- Merchant/tenant identification
- Dashboard aggregation
- Risk case retrieval
- Investigation retrieval
- Recovery batch management
- Recovery authorization
- Recovery execution controls
- Transaction querying
- Audit trail retrieval
- AI assistant requests
- Database access
- Health checks
- Security controls

The backend is the authoritative source for application data exposed to the frontend.

---

# 9. Backend Logical Structure

The backend follows a layered organization:

```text
backend/
│
├── app/
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── health.py
│   │       ├── dashboard.py
│   │       ├── risk_cases.py
│   │       ├── investigations.py
│   │       ├── recovery.py
│   │       ├── transactions.py
│   │       ├── audit.py
│   │       └── assistant.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── db/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── seed.py
│   │   └── session.py
│   │
│   ├── services/
│   │   ├── risk/
│   │   ├── investigation/
│   │   └── recovery/
│   │
│   └── main.py
│
└── tests/
```

The implementation may contain additional modules, but the architectural responsibilities remain separated.

---

# 10. Database Architecture

PostgreSQL is the persistent data store for RecoverAI.

The database stores the authoritative application state.

Conceptually:

```text
                    PostgreSQL
                         │
        ┌────────────────┼─────────────────┐
        │                │                 │
        ▼                ▼                 ▼
 Transactions       Risk Cases       Investigations
        │                │                 │
        └────────────────┼─────────────────┘
                         │
                         ▼
                  Recovery Batches
                         │
                         ▼
                    Audit Logs
```

---

# 11. Core Data Domains

RecoverAI's data can be grouped into the following domains.

### Transaction Domain

Contains payment transaction information such as:

- Transaction identifier
- Merchant
- Amount
- Payment method
- Bank/rail
- Status
- Failure reason
- Timestamp

### Risk Domain

Contains detected revenue risk cases.

Examples:

```text
RC-001
RC-002
RC-003
RC-004
```

A risk case can contain:

- Severity
- Status
- Risk type
- Revenue exposure
- Recoverable amount
- Detection metadata
- Root-cause information

### Investigation Domain

Contains diagnostic investigations associated with risk cases.

Example:

```text
INV-00000000
```

Investigation information can include:

- Investigation status
- Confidence score
- Root-cause findings
- Evidence
- Diagnostic observations
- Investigation timeline

### Recovery Domain

Contains recovery batches and their execution state.

Examples:

```text
RB-022
RB-023
RB-024
RB-025
```

Recovery records can contain:

- Batch ID
- Recovery strategy
- Transaction count
- Approval status
- Execution status
- Failure rate
- Recovery amount
- Idempotency information
- Circuit-breaker state

### Audit Domain

Contains records describing important system actions.

Examples include:

- Risk detection
- Investigation
- Policy evaluation
- Merchant approval
- Recovery execution
- Recovery stop
- Reconciliation

---

# 12. Data Flow

A typical payment failure flows through the system as follows:

```text
Payment Transaction
       │
       ▼
Transaction Telemetry
       │
       ▼
Risk Detection
       │
       ▼
Risk Case Created
       │
       ▼
Investigation
       │
       ├──────────────► Root Cause
       │
       ├──────────────► Evidence
       │
       └──────────────► Confidence
                         │
                         ▼
                  Financial Analysis
                         │
                         ├── Revenue at Risk
                         ├── Recoverable Revenue
                         └── Recovery Eligibility
                                   │
                                   ▼
                            Recovery Proposal
                                   │
                                   ▼
                          Merchant Authorization
                                   │
                                   ▼
                            Recovery Batch
                                   │
                                   ▼
                         Bounded Execution
                                   │
                       ┌───────────┴───────────┐
                       │                       │
                       ▼                       ▼
                  Successful               Failure
                       │                       │
                       └───────────┬───────────┘
                                   ▼
                              Reconciliation
                                   │
                                   ▼
                              Audit Record
```

---

# 13. Dashboard Data Flow

When a merchant opens the dashboard:

```text
Browser
   │
   │ GET /api/v1/dashboard/metrics
   │
   ▼
FastAPI
   │
   ▼
Dashboard Service
   │
   ▼
Payment Repository
   │
   ▼
PostgreSQL
   │
   ▼
Aggregated Metrics
   │
   ▼
FastAPI JSON Response
   │
   ▼
Frontend Dashboard
```

The dashboard can display metrics including:

- Revenue at Risk
- Recoverable Revenue
- Revenue Recovered
- Active Risk Cases
- Payment Success Rate
- Payment Method Health
- Revenue Trends
- Recovery Performance

---

# 14. Timeframe Architecture

The dashboard supports:

- 24H
- 7D
- 30D
- 90D

The selected timeframe is sent to the backend:

```text
GET /api/v1/dashboard/metrics?timeframe=24h
```

or:

```text
GET /api/v1/dashboard/metrics?timeframe=7d
```

or:

```text
GET /api/v1/dashboard/metrics?timeframe=30d
```

or:

```text
GET /api/v1/dashboard/metrics?timeframe=90d
```

The backend is responsible for aggregating the appropriate time window.

The frontend does not fabricate historical data.

When the available telemetry does not cover the selected historical window, the system should communicate the limitation to the user instead of presenting fabricated historical payment events.

---

# 15. Payment Health Architecture

The Payment Health section analyzes payment performance across methods and rails.

Example structure:

```text
Payment Health
      │
      ├── UPI
      │     └── HDFC UPI
      │
      ├── Card
      │
      ├── Net Banking
      │
      └── Wallet
```

The system can identify concentrated degradation.

For example:

```text
Overall Payment Success Rate
            │
            ▼
           UPI
            │
            ▼
        HDFC UPI
            │
            ▼
    Gateway Timeout
```

This allows RecoverAI to move from:

> "Payments are failing"

to:

> "The majority of degradation is concentrated on the HDFC UPI payment rail and gateway timeout failures."

---

# 16. Risk Detection Architecture

Risk detection converts transaction-level failures into operational risk cases.

Conceptually:

```text
Transaction Telemetry
        │
        ▼
Failure / Degradation Signals
        │
        ▼
Aggregation
        │
        ▼
Severity Evaluation
        │
        ▼
Revenue Exposure Calculation
        │
        ▼
Risk Case
```

A risk case represents a business-level incident rather than an individual failed payment.

For example:

```text
RC-001
│
├── Status: OPEN
├── Risk Type: Payment Degradation
├── Payment Rail: HDFC UPI
├── Revenue at Risk
├── Recoverable Revenue
└── Root Cause Investigation
```

---

# 17. Investigation Architecture

The investigation system transforms an operational risk case into a structured diagnosis.

```text
Risk Case
    │
    ▼
Investigation
    │
    ├── Payment Method Analysis
    ├── Bank/Rail Analysis
    ├── Error Analysis
    ├── Volume Analysis
    ├── Temporal Analysis
    └── Baseline Comparison
             │
             ▼
       Root Cause Finding
             │
             ▼
       Confidence Score
```

The investigation interface exposes structured findings rather than exposing private model chain-of-thought.

The goal is to provide:

- Evidence
- Findings
- Confidence
- Root cause
- Recommended next action

---

# 18. Root Cause Architecture

RecoverAI uses a hierarchical root-cause representation.

Example:

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
      Revenue Impact
```

This structure allows an operator to move from a broad incident to the most significant contributing factor.

---

# 19. Financial Impact Architecture

RecoverAI separates three important financial concepts.

```text
Failed Transactions
        │
        ▼
Revenue at Risk
        │
        ▼
Recoverable Revenue
        │
        ▼
Revenue Recovered
```

**Revenue at Risk**
The estimated amount of revenue exposed because of payment failures or degradation.

**Recoverable Revenue**
The subset of revenue at risk that the system determines may be eligible for controlled recovery.

**Revenue Recovered**
The amount actually recovered through completed recovery actions.

Therefore:

```text
Revenue at Risk
      ≥
Recoverable Revenue
      ≥
Revenue Recovered
```

These values should not be treated as interchangeable.

---

# 20. Recovery Architecture

Recovery is deliberately separated from detection and investigation.

```text
Detection
   │
   ▼
Investigation
   │
   ▼
Recovery Eligibility
   │
   ▼
Recovery Proposal
   │
   ▼
Merchant Approval
   │
   ▼
Recovery Batch
   │
   ▼
Bounded Execution
```

This separation prevents a detected failure from automatically becoming an uncontrolled financial action.

---

# 21. Recovery Authorization

A recovery action should pass through an authorization boundary.

```text
Recovery Recommendation
          │
          ▼
     Safety Policy
          │
          ▼
     Merchant Approval
          │
          ▼
     Recovery Execution
```

The system is intentionally designed so that financial actions cannot simply be triggered by an arbitrary frontend click without backend policy validation.

---

# 22. Recovery Safety Architecture

RecoverAI uses multiple safety controls.

```text
                 Recovery Request
                        │
                        ▼
              ┌──────────────────┐
              │ Merchant Approval│
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │ Idempotency Check│
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │ Exposure Limits  │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │ Retry Limit      │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │ Execute Recovery │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │ Failure Monitor  │
              └────────┬─────────┘
                       │
                 Failure Threshold
                       │
                       ▼
              ┌──────────────────┐
              │ Circuit Breaker  │
              │     AUTO-STOP    │
              └──────────────────┘
```

---

# 23. Idempotency Protection

Payment recovery must avoid accidentally processing the same financial action multiple times.

RecoverAI therefore uses idempotency controls.

Conceptually:

```text
Transaction
     │
     ▼
Recovery Attempt
     │
     ▼
Idempotency Key
     │
     ├── Already processed → Stop
     │
     └── New attempt → Continue
```

This protects against duplicate recovery actions caused by:

- User double-clicks
- Network retries
- Request retries
- Worker retries
- Application restarts

---

# 24. Retry Bounds

Recovery operations are bounded.

The system does not continuously retry a failed transaction indefinitely.

Conceptually:

```text
Attempt 1
   │
   ├── Success → Complete
   │
   └── Failure
        │
        ▼
   Retry Allowed?
        │
        ├── No → Stop
        │
        └── Yes → Controlled Retry
```

The exact retry policy is determined by the configured recovery policy.

---

# 25. Circuit Breaker Architecture

The circuit breaker protects the remaining recovery queue when execution quality deteriorates.

Example:

```text
Recovery Batch
      │
      ▼
Transaction 1 ──► Success
Transaction 2 ──► Success
Transaction 3 ──► Failure
Transaction 4 ──► Failure
Transaction 5 ──► Failure
      │
      ▼
Failure Rate Increasing
      │
      ▼
Threshold Exceeded
      │
      ▼
┌──────────────────────┐
│   CIRCUIT BREAKER    │
│      TRIPPED         │
└──────────┬───────────┘
           │
           ▼
Recovery STOPPED
           │
           ▼
Remaining Queue Protected
           │
           ▼
Audit Event Recorded
```

The circuit breaker prevents a recovery operation from continuing when the failure rate exceeds the configured safety threshold.

---

# 26. Recovery Reconciliation

Recovery execution and recovery reconciliation are separate concepts.

Execution answers:

> What happened during the recovery attempt?

Reconciliation answers:

> What financial result was actually achieved?

Conceptually:

```text
Recovery Batch
      │
      ▼
Execution Results
      │
      ├── Successful Transactions
      ├── Failed Transactions
      ├── Stopped Transactions
      └── Remaining Transactions
                │
                ▼
         Reconciliation
                │
                ▼
        Actual Recovered
             Revenue
```

This prevents the system from treating a proposed recovery amount as automatically recovered revenue.

---

# 27. Audit Architecture

Auditability is a core architectural requirement.

Important operations generate audit records.

```text
Risk Detection
      │
      ▼
Audit Event
      │
Investigation
      │
      ▼
Audit Event
      │
Merchant Approval
      │
      ▼
Audit Event
      │
Recovery Execution
      │
      ▼
Audit Event
      │
Circuit Breaker
      │
      ▼
Audit Event
      │
Reconciliation
      │
      ▼
Audit Event
```

The audit trail provides a chronological record of important system activity.

---

# 28. Multi-Tenant Architecture

RecoverAI supports merchant-aware API access.

Requests can contain:

```text
X-Merchant-ID
```

The backend uses merchant context when retrieving tenant-specific information.

Conceptually:

```text
Frontend Request
      │
      │ X-Merchant-ID
      ▼
FastAPI
      │
      ▼
Tenant Validation
      │
      ▼
Merchant-Scoped Query
      │
      ▼
PostgreSQL
```

This architectural boundary helps prevent one merchant's data from being unintentionally returned to another merchant.

---

# 29. API Architecture

The primary API namespace is:

```text
/api/v1
```

Major API groups include:

```text
/api/v1/health
/api/v1/dashboard
/api/v1/risk-cases
/api/v1/investigations
/api/v1/recovery
/api/v1/transactions
/api/v1/audit
/api/v1/assistant
```

---

# 30. Health Architecture

RecoverAI provides separate health concepts.

**Liveness**

```text
GET /api/v1/health/live
```

Used to determine whether the application process is alive.

**Readiness**

```text
GET /api/v1/health/ready
```

Used to determine whether the application and database are ready to serve requests.

Conceptually:

```text
Load Balancer / Platform
        │
        ├── /health/live
        │       │
        │       ▼
        │    Process Alive
        │
        └── /health/ready
                │
                ▼
          Database Available
```

---

# 31. Frontend Route Architecture

The major frontend routes are:

| Route | Responsibility |
|---|---|
| `/dashboard` | Main payment intelligence dashboard |
| `/risk-cases` | Revenue risk case directory |
| `/risk-cases/[caseId]` | Individual risk case |
| `/investigations` | Investigation directory |
| `/investigations/[investigationId]` | Investigation workspace |
| `/recovery` | Recovery batch directory |
| `/recovery/[batchId]` | Recovery execution monitor |
| `/transactions` | Transaction explorer |
| `/audit` | Audit trail |
| `/ai-assistant` | Operations assistant |
| `/settings` | Merchant configuration and safety policies |

---

# 32. Dashboard Architecture

The dashboard is the primary operational view.

```text
                    Dashboard
                        │
       ┌────────────────┼─────────────────┐
       │                │                 │
       ▼                ▼                 ▼
 Financial KPIs    Payment Health    Risk Cases
       │                │                 │
       └────────────────┼─────────────────┘
                        │
                        ▼
                 Revenue Trends
                        │
                        ▼
                 AI Insights
                        │
                        ▼
                Recovery Performance
```

The dashboard combines data from multiple backend resources while maintaining a consistent merchant context.

---

# 33. Risk Case Architecture

The Risk Cases interface provides:

```text
Risk Case Directory
        │
        ├── Filter by Status
        ├── Filter by Severity
        ├── Filter by Risk Type
        └── Open Case
               │
               ▼
         Risk Case Detail
               │
               ├── Financial Impact
               ├── Root Cause
               ├── Evidence
               ├── Investigation
               └── Recovery Recommendation
```

---

# 34. Investigation Architecture (UI)

The investigation experience is connected to risk cases.

```text
Risk Case
   │
   ▼
Investigation
   │
   ├── Investigation Status
   ├── Diagnostic Findings
   ├── Evidence
   ├── Root Cause
   └── Confidence
```

This allows an operator to move from detection to explanation.

---

# 35. Recovery UI Architecture

Recovery is split into two major views.

**Recovery Batches** — `/recovery`

Shows the recovery operations directory.

**Active Recovery** — `/recovery/[batchId]`

Shows an individual recovery execution.

The navigation state distinguishes the two views so that:

> Recovery Batches

and:

> Active Recovery

do not appear simultaneously active when viewing a specific batch.

---

# 36. Transactions Architecture

The transaction explorer provides transaction-level visibility.

```text
Transactions
    │
    ├── Payment Method
    ├── Bank
    ├── Status
    ├── Failure Reason
    └── Transaction Detail
```

The transaction layer provides the granular evidence behind higher-level risk and financial metrics.

---

# 37. Audit Architecture (UI)

The Audit page provides a chronological operational record.

```text
Audit Trail
    │
    ├── Risk Detection
    ├── Investigation
    ├── Policy Decision
    ├── Approval
    ├── Recovery
    ├── Circuit Breaker
    └── Reconciliation
```

This creates traceability across the complete recovery lifecycle.

---

# 38. AI Assistant Architecture

The AI Assistant acts as an operational interface over RecoverAI capabilities.

Conceptually:

```text
User Question
      │
      ▼
AI Assistant API
      │
      ▼
Context / Application Data
      │
      ▼
Structured Response
      │
      ▼
Frontend Assistant
```

The assistant should not bypass financial safety controls.

An AI-generated recovery recommendation is not equivalent to an authorized financial action.

The authorization and policy boundaries remain enforced by the application.

---

# 39. Scenario Architecture

RecoverAI includes a scenario mechanism for demonstrations and controlled simulation.

The architecture distinguishes between:

> Live Active Incident

and:

> Simulation Scenario

This distinction is important because a simulation profile should not falsely imply that PostgreSQL contains a completely different live merchant dataset.

The production demonstration is anchored to the authoritative active incident and database telemetry.

---

# 40. Live Incident vs Simulation

Conceptually:

```text
                    Scenario Selector
                           │
                ┌──────────┴───────────┐
                │                      │
                ▼                      ▼
        Active Incident        Simulation Profile
                │                      │
                ▼                      ▼
        PostgreSQL Data        Synthetic Context
                │                      │
                └──────────┬───────────┘
                           │
                           ▼
                    User Experience
```

This prevents synthetic scenario labels from being confused with live database state.

---

# 41. Time-Series Data Architecture

RecoverAI supports multiple aggregation granularities.

```text
24 Hours
   │
   └── Hourly / short-window aggregation

7 Days
   │
   └── Daily aggregation

30 Days
   │
   └── Weekly aggregation

90 Days
   │
   └── Monthly aggregation
```

When insufficient historical telemetry exists, the frontend should clearly communicate the limitation.

The system should not silently manufacture historical transaction data.

---

# 42. Production Deployment Architecture

The current production deployment uses:

```text
                     Internet
                        │
                        ▼
              ┌──────────────────┐
              │      Netlify     │
              │                  │
              │ Next.js Frontend │
              └────────┬─────────┘
                       │
                       │ HTTPS
                       ▼
              ┌──────────────────┐
              │      Render      │
              │                  │
              │ FastAPI Backend  │
              └────────┬─────────┘
                       │
                       │ PostgreSQL
                       ▼
              ┌──────────────────┐
              │ Managed Postgres │
              │                  │
              │ RecoverAI Data   │
              └──────────────────┘
```

---

# 43. Production Request Flow

When a user accesses the live dashboard:

```text
User
 │
 │ https://recoverai.dhirajm.com.np/dashboard
 ▼
Netlify / Production Frontend
 │
 │ GET /api/v1/dashboard/metrics
 ▼
Render FastAPI Backend
 │
 │ SQL Query
 ▼
Managed PostgreSQL
 │
 │ Aggregated Result
 ▼
FastAPI JSON Response
 │
 ▼
Next.js / React
 │
 ▼
Dashboard UI
```

---

# 44. Production Environment Variables

The frontend uses:

```text
NEXT_PUBLIC_API_URL
```

This points the production frontend to the public backend.

The backend uses environment variables for configuration such as:

```text
APP_NAME
APP_ENV
DEBUG
PORT
DATABASE_URL
CORS_ALLOWED_ORIGINS
LOG_LEVEL
DOCS_ENABLED
```

Database credentials remain backend-side.

They must never be exposed through:

```text
NEXT_PUBLIC_*
```

environment variables.

---

# 45. CORS Architecture

Because the frontend and backend are hosted separately, browser requests require appropriate CORS configuration.

Conceptually:

```text
recoverai.dhirajm.com.np
          │
          │ HTTPS API Request
          ▼
     Render Backend
          │
          ▼
      CORS Check
          │
          ├── Allowed → Continue
          │
          └── Rejected → Block
```

Only trusted frontend origins should be allowed in production.

---

# 46. Docker Architecture

RecoverAI supports containerized development and deployment.

The local architecture can be represented as:

```text
┌──────────────────────────────────────────────┐
│                 Docker Compose               │
│                                              │
│  ┌──────────────┐                            │
│  │  Frontend    │                            │
│  │  Next.js     │                            │
│  │  :3000       │                            │
│  └──────┬───────┘                            │
│         │                                     │
│         ▼                                     │
│  ┌──────────────┐                            │
│  │   Backend    │                            │
│  │   FastAPI    │                            │
│  │   :8000      │                            │
│  └──────┬───────┘                            │
│         │                                     │
│         ▼                                     │
│  ┌──────────────┐                            │
│  │ PostgreSQL   │                            │
│  │ :5432        │                            │
│  └──────────────┘                            │
│                                              │
└──────────────────────────────────────────────┘
```

This allows local development to approximate the production service boundaries.

---

# 47. Local Development Architecture

The local environment typically consists of:

```text
Browser
   │
   ▼
localhost:3000
   │
   ▼
localhost:8000
   │
   ▼
localhost:5432
```

The production environment changes the hosting layer:

```text
Browser
   │
   ▼
Netlify
   │
   ▼
Render
   │
   ▼
Managed PostgreSQL
```

The application architecture remains conceptually the same.

---

# 48. Database Initialization

The backend supports automatic initialization of missing database structures during startup.

The initialization flow is:

```text
Backend Startup
      │
      ▼
Database Connection
      │
      ▼
Create Missing Tables
      │
      ▼
Check Seed State
      │
      ▼
Seed If Required
      │
      ▼
Application Ready
```

The seed process is designed to be idempotent so that an existing canonical merchant dataset is not blindly duplicated during every restart.

---

# 49. Canonical Demonstration Dataset

The current demonstration dataset represents a merchant environment containing:

```text
Total Transactions:       1,251
Captured:                 1,024
Failed:                     227
Overall Success Rate:     81.85%
```

The primary active incident includes:

```text
Risk Case:                RC-001
Investigation:            INV-00000000
```

Key financial demonstration values include:

```text
Revenue at Risk:          ₹12,19,544
Recoverable Revenue:      ₹3,04,886
Revenue Recovered:        ₹42,000
```

The dataset is intended for product demonstration and Buildathon evaluation.

It is not a representation of real customer payment credentials or live settlement accounts.

---

# 50. Security Architecture

Security is implemented at multiple levels.

```text
                    Security
                       │
        ┌──────────────┼───────────────┐
        │              │               │
        ▼              ▼               ▼
   API Security    Data Security   Recovery Safety
        │              │               │
        │              │               │
     CORS          DB Secrets      Approval
     Tenant        Isolation       Idempotency
     Validation                    Retry Limits
                                   Exposure Caps
                                   Circuit Breaker
```

---

# 51. Secret Management

Sensitive credentials should remain on the backend.

Examples:

- Database credentials
- Private API credentials
- Payment credentials
- AI provider credentials

These should never be embedded in:

- React components
- Next.js client bundles
- GitHub repository
- `NEXT_PUBLIC_*` variables

Only non-sensitive public configuration should be exposed to the browser.

---

# 52. Recovery Security Boundary

One of the most important architectural boundaries is:

```text
Frontend
   │
   │ "Approve Recovery"
   ▼
Backend
   │
   ├── Validate Merchant
   ├── Validate Batch
   ├── Validate Policy
   ├── Check Idempotency
   ├── Check Exposure
   ├── Check Retry Limit
   └── Execute Allowed Action
```

The frontend should never be treated as the security boundary.

The backend is responsible for enforcing financial rules.

---

# 53. Failure Handling Architecture

RecoverAI should distinguish between different types of failures.

**Frontend Failure**

Example: API unavailable

The UI should show a transparent error state rather than silently displaying misleading financial data.

**Backend Failure**

Example: HTTP 500

The frontend should surface the failure appropriately.

**Database Failure**

The readiness endpoint should indicate that the backend is not fully ready.

**Recovery Failure**

Recovery execution should be evaluated against safety thresholds.

If the failure threshold is crossed:

```text
Recovery → STOPPED
```

---

# 54. Observability

The architecture provides several verification points.

```text
Frontend
   │
   ├── Browser Network
   └── Browser Console
          │
          ▼
Backend
   │
   ├── Health Endpoint
   ├── Readiness Endpoint
   └── Application Logs
          │
          ▼
Database
   │
   └── PostgreSQL Queries
```

This allows problems to be isolated between:

- Frontend
- Backend
- Database
- Deployment

---

# 55. Testing Architecture

RecoverAI uses multiple quality gates.

```text
                Code Change
                     │
       ┌─────────────┼─────────────┐
       │             │             │
       ▼             ▼             ▼
   TypeScript      ESLint       Pytest
       │             │             │
       └─────────────┼─────────────┘
                     ▼
              Production Build
                     │
                     ▼
               Docker Build
                     │
                     ▼
              API Verification
                     │
                     ▼
              End-to-End Check
```

The backend test suite has been verified with:

```text
84 passed
```

The frontend has also been verified through:

- TypeScript
- ESLint
- Next.js Production Build

---

# 56. Architecture Quality Gates

Before production deployment, the following should pass:

```text
[✓] TypeScript
[✓] ESLint
[✓] Backend Tests
[✓] Next.js Production Build
[✓] Docker Build
[✓] Backend Health
[✓] Backend Readiness
[✓] Database Connectivity
[✓] Dashboard API
[✓] Risk Case API
[✓] Investigation API
[✓] Recovery API
[✓] Transaction API
[✓] Audit API
[✓] Production Frontend
```

---

# 57. End-to-End Architecture Example

Consider a customer attempting a ₹5,000 payment.

The conceptual flow is:

```text
Customer
   │
   ▼
Payment Attempt
   │
   ▼
Gateway Timeout
   │
   ▼
Transaction Recorded as Failed
   │
   ▼
Risk Detection
   │
   ▼
Revenue Exposure Identified
   │
   ▼
Risk Case
   │
   ▼
Investigation
   │
   ▼
Root Cause:
HDFC UPI Gateway Timeout
   │
   ▼
Recovery Eligibility
   │
   ▼
Recovery Recommendation
   │
   ▼
Merchant Authorization
   │
   ▼
Idempotency Check
   │
   ▼
Bounded Recovery Attempt
   │
   ├──────── Success ────────► Reconciliation
   │                              │
   │                              ▼
   │                         Revenue Recovered
   │
   └──────── Failure ─────────► Failure Monitoring
                                  │
                                  ▼
                            Circuit Breaker
                                  │
                                  ▼
                              Audit Event
```

The important architectural principle is that a failed transaction is not automatically retried.

The transaction passes through eligibility and safety controls first.

---

# 58. Why the Architecture Uses a Backend

A frontend-only implementation would make it difficult to safely enforce:

- Database access control
- Merchant isolation
- Recovery authorization
- Idempotency
- Financial policy enforcement
- Audit consistency
- Secret management

RecoverAI therefore keeps financial and operational rules on the backend.

```text
Frontend = Presentation + Interaction

Backend = Validation + Business Rules + Financial Controls

Database = Persistent Source of Truth
```

---

# 59. Why PostgreSQL Is the Source of Truth

The frontend can display data, but it should not be treated as the authoritative source.

The architectural hierarchy is:

```text
PostgreSQL
     ↑
FastAPI
     ↑
Frontend
```

The database stores the persistent state.

FastAPI retrieves and processes that state.

The frontend renders the resulting information.

This prevents UI state from becoming the source of financial truth.

---

# 60. Production vs Local Architecture

### Local

```text
Browser
  │
  ▼
Next.js
localhost:3000
  │
  ▼
FastAPI
localhost:8000
  │
  ▼
PostgreSQL
localhost:5432
```

### Production

```text
Browser
  │
  ▼
Netlify
  │
  ▼
Render FastAPI
  │
  ▼
Managed PostgreSQL
```

The production deployment replaces local infrastructure with managed services while preserving the application architecture.

---

# 61. Deployment Pipeline

The deployment pipeline is:

```text
Developer
    │
    ▼
GitHub Repository
    │
    ├─────────────────────┐
    │                     │
    ▼                     ▼
Netlify                 Render
Frontend                Backend
    │                     │
    │                     ▼
    │              Managed PostgreSQL
    │
    └──────────── HTTPS ────────────►
```

A source-code update can therefore flow through:

```text
GitHub
  ↓
Build
  ↓
Deploy
  ↓
Production
```

---

# 62. Domain Architecture

The public application is exposed through the custom domain:

```text
https://recoverai.dhirajm.com.np/dashboard
```

The browser-facing domain represents the frontend application.

The frontend communicates with the backend through HTTPS.

The database remains private to the backend infrastructure.

Conceptually:

```text
Public Internet
      │
      ▼
recoverai.dhirajm.com.np
      │
      ▼
Frontend
      │
      ▼
Public HTTPS API
      │
      ▼
FastAPI
      │
      ▼
Private Database
```

The database should never be exposed directly to the public browser.

---

# 63. Architecture Principles

RecoverAI follows these core principles:

**Principle 1 — Database as Source of Truth**
Financial metrics originate from persistent backend data.

**Principle 2 — Backend-Enforced Safety**
Financial rules are enforced server-side.

**Principle 3 — Explicit Authorization**
Recovery actions require an authorization boundary.

**Principle 4 — Idempotent Recovery**
Duplicate financial actions must be prevented.

**Principle 5 — Bounded Automation**
Automation must have limits.

**Principle 6 — Fail Safe**
When recovery becomes unsafe, stop rather than continue.

**Principle 7 — Transparent Data**
The application should not fabricate historical payment telemetry.

**Principle 8 — Auditable Operations**
Important decisions and actions should be traceable.

**Principle 9 — Separation of Concerns**
Frontend, backend, business logic, and database responsibilities remain separated.

**Principle 10 — Production Parity**
Local Docker architecture should approximate the service boundaries used in production.

---

# 64. Current Architecture Summary

```text
┌──────────────────────────────────────────────────────────────┐
│                         RECOVERAI                            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  USER                                                        │
│   │                                                          │
│   ▼                                                          │
│  Next.js / React / TypeScript                                │
│   │                                                          │
│   │ HTTPS                                                    │
│   ▼                                                          │
│  FastAPI                                                     │
│   │                                                          │
│   ├── Dashboard                                              │
│   ├── Risk Detection                                         │
│   ├── Investigations                                         │
│   ├── Recovery                                                │
│   ├── Transactions                                            │
│   ├── Audit                                                   │
│   └── AI Assistant                                            │
│   │                                                          │
│   ▼                                                          │
│  Business Logic                                               │
│   │                                                          │
│   ├── Financial Analysis                                      │
│   ├── Recovery Policies                                       │
│   ├── Authorization                                           │
│   ├── Idempotency                                             │
│   └── Circuit Breaker                                         │
│   │                                                          │
│   ▼                                                          │
│  SQLAlchemy / Repository Layer                                │
│   │                                                          │
│   ▼                                                          │
│  PostgreSQL                                                    │
│   │                                                          │
│   ├── Transactions                                             │
│   ├── Risk Cases                                               │
│   ├── Investigations                                           │
│   ├── Recovery Batches                                         │
│   └── Audit Logs                                               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

# 65. Final Architecture Perspective

RecoverAI is intentionally designed as more than a payment dashboard.

Its architecture represents a complete operational loop:

```text
OBSERVE
   ↓
DETECT
   ↓
INVESTIGATE
   ↓
QUANTIFY
   ↓
DECIDE
   ↓
AUTHORIZE
   ↓
RECOVER
   ↓
RECONCILE
   ↓
AUDIT
```

The most important architectural boundary is between intelligence and financial execution.

RecoverAI can identify a payment problem, investigate its cause, estimate financial exposure, and recommend a recovery action. However, recovery execution is deliberately constrained by authorization, idempotency, retry limits, exposure controls, and circuit-breaker protection.

This design allows the platform to demonstrate how AI-assisted payment operations can be combined with deterministic financial controls.

---

## Production Deployment

**Live Application:**

```text
https://recoverai.dhirajm.com.np/dashboard
```

- **Frontend:** Next.js / React / TypeScript
- **Backend:** FastAPI / Python
- **Database:** PostgreSQL
- **Frontend Hosting:** Netlify
- **Backend Hosting:** Render
- **Containerization:** Docker

---

## Related Documentation

- `README.md` — Project overview, features, setup, and live demo
- `project_documentation.md` — Detailed product and technical documentation

---

## Architecture Status

| Component | Status |
|---|---|
| Frontend | Production Deployed |
| Backend API | Production Deployed |
| PostgreSQL | Production Connected |
| REST API | Operational |
| Dashboard | Operational |
| Risk Cases | Operational |
| Investigations | Operational |
| Recovery | Operational |
| Transactions | Operational |
| Audit Trail | Operational |
| AI Assistant | Operational |
| Docker | Supported |
| Responsive UI | Supported |
| Production Domain | Active |
| Automated Backend Tests | 84 Passed |

---

**RecoverAI Architecture Principle:**

> Detect intelligently. Decide carefully. Recover safely. Reconcile accurately. Audit everything.
