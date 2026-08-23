# RecoverAI — API Documentation

> **REST API reference for the RecoverAI payment intelligence and revenue recovery platform**

RecoverAI exposes a versioned REST API through a FastAPI backend.

The API acts as the authoritative application layer between the frontend and PostgreSQL database. It provides access to payment telemetry, dashboard intelligence, revenue risk cases, investigations, recovery operations, transactions, audit records, and the RecoverAI operations assistant.

---

## Table of Contents

1. [API Overview](#1-api-overview)
2. [Production API Base URL](#2-production-api-base-url)
3. [Local Development API](#3-local-development-api)
4. [API Format](#4-api-format)
5. [HTTP Methods](#5-http-methods)
6. [Content Type](#6-content-type)
7. [Merchant Context](#7-merchant-context)
8. [API Endpoint Summary](#8-api-endpoint-summary)
9. [Health API](#9-health-api)
10. [Readiness Check](#10-readiness-check)
11. [Dashboard Metrics API](#11-dashboard-metrics-api)
12. [Dashboard Metric Definitions](#12-dashboard-metric-definitions)
13. [Timeframe Behavior](#13-timeframe-behavior)
14. [Risk Cases API](#14-risk-cases-api)
15. [Risk Case Detail API](#15-risk-case-detail-api)
16. [Risk Case Lifecycle](#16-risk-case-lifecycle)
17. [Investigations API](#17-investigations-api)
18. [Investigation Root Cause Model](#18-investigation-root-cause-model)
19. [Investigation Confidence](#19-investigation-confidence)
20. [Recovery Batch API](#20-recovery-batch-api)
21. [Recovery Batch Lifecycle](#21-recovery-batch-lifecycle)
22. [Recovery Approval API](#22-recovery-approval-api)
23. [Recovery Approval Safety](#23-recovery-approval-safety)
24. [Recovery Idempotency](#24-recovery-idempotency)
25. [Circuit Breaker](#25-circuit-breaker)
26. [Recovery Reconciliation](#26-recovery-reconciliation)
27. [Transaction API](#27-transaction-api)
28. [Transaction Filtering](#28-transaction-filtering)
29. [Transaction Data Model](#29-transaction-data-model)
30. [Audit API](#30-audit-api)
31. [Audit Events](#31-audit-events)
32. [Audit Integrity](#32-audit-integrity)
33. [AI Assistant API](#33-ai-assistant-api)
34. [Assistant Request](#34-assistant-request)
35. [Assistant Response](#35-assistant-response)
36. [AI Safety Boundary](#36-ai-safety-boundary)
37. [Error Handling](#37-error-handling)
38. [Validation Errors](#38-validation-errors)
39. [Resource Not Found](#39-resource-not-found)
40. [Recovery Conflicts](#40-recovery-conflicts)
41. [Backend Unavailability](#41-backend-unavailability)
42. [No Mock Fallback Principle](#42-no-mock-fallback-principle)
43. [API Security](#43-api-security)
44. [API and Database Separation](#44-api-and-database-separation)
45. [API Request Lifecycle](#45-api-request-lifecycle)
46. [API Performance Considerations](#46-api-performance-considerations)
47. [Async Backend Architecture](#47-async-backend-architecture)
48. [API Versioning](#48-api-versioning)
49. [API Documentation and FastAPI](#49-api-documentation-and-fastapi)
50. [Example End-to-End API Workflow](#50-example-end-to-end-api-workflow)
51. [Example: Payment Failure to Recovery](#51-example-payment-failure-to-recovery)
52. [Canonical Demonstration Data](#52-canonical-demonstration-data)
53. [Scenario and Simulation Context](#53-scenario-and-simulation-context)
54. [Production API Architecture](#54-production-api-architecture)
55. [Local API Architecture](#55-local-api-architecture)
56. [Deployment Environment Variables](#56-deployment-environment-variables)
57. [Production Deployment Checklist](#57-production-deployment-checklist)
58. [API Testing Checklist](#58-api-testing-checklist)
59. [API Reliability Principles](#59-api-reliability-principles)
60. [API Architecture Summary](#60-api-architecture-summary)
61. [Design Philosophy](#61-design-philosophy)
62. [Related Documentation](#62-related-documentation)
63. [API Status](#63-api-status)
64. [Final API Principle](#64-final-api-principle)

---

# 1. API Overview

RecoverAI follows a REST-based architecture:

```text
Frontend
   │
   │ HTTPS / JSON
   ▼
FastAPI REST API
   │
   ├── Validation
   ├── Merchant Context
   ├── Business Logic
   ├── Recovery Safety Controls
   └── Data Access
          │
          ▼
      PostgreSQL
```

The API is versioned under:

```text
/api/v1
```

The primary production application is:

```text
https://recoverai.dhirajm.com.np/dashboard
```

The frontend communicates with the backend through the configured:

```text
NEXT_PUBLIC_API_URL
```

environment variable.

---

# 2. Production API Base URL

The production frontend uses a publicly accessible FastAPI backend.

The exact backend service URL is environment-specific and should be configured through:

```text
NEXT_PUBLIC_API_URL
```

The frontend should therefore make requests using:

```text
${NEXT_PUBLIC_API_URL}/api/v1/...
```

rather than hardcoding a backend hostname into individual components.

For example:

```text
GET ${NEXT_PUBLIC_API_URL}/api/v1/dashboard/metrics
```

---

# 3. Local Development API

For local development, the FastAPI backend normally runs on:

```text
http://localhost:8000
```

Therefore:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Example:

```text
GET http://localhost:8000/api/v1/health/live
```

---

# 4. API Format

RecoverAI uses JSON for API request and response bodies.

Typical request:

```text
GET /api/v1/dashboard/metrics?timeframe=24h
```

Typical response:

```json
{
  "revenueAtRisk": 1219544,
  "recoverableRevenue": 304886,
  "revenueRecovered": 42000
}
```

---

# 5. HTTP Methods

The API uses standard HTTP methods.

| Method | Purpose |
|---|---|
| GET | Retrieve data |
| POST | Create or execute an operation |
| PUT | Replace/update a resource |
| PATCH | Partially update a resource |
| DELETE | Remove a resource |

The current RecoverAI operational API primarily uses:

```text
GET
POST
```

---

# 6. Content Type

JSON requests should use:

```text
Content-Type: application/json
```

Example:

```text
Content-Type: application/json
Accept: application/json
```

---

# 7. Merchant Context

RecoverAI is designed around merchant-scoped operations.

Requests may include:

```text
X-Merchant-ID: 00000000-0000-0000-0000-000000000001
```

This identifies the merchant whose data should be queried.

Conceptually:

```text
Request
   │
   ▼
X-Merchant-ID
   │
   ▼
Merchant Context
   │
   ▼
Merchant-Scoped Query
   │
   ▼
PostgreSQL
```

The frontend should not arbitrarily switch merchant IDs without an authorized merchant context.

---

# 8. API Endpoint Summary

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/v1/health/live` | GET | Liveness check |
| `/api/v1/health/ready` | GET | Readiness/database check |
| `/api/v1/dashboard/metrics` | GET | Dashboard intelligence and financial metrics |
| `/api/v1/risk-cases` | GET | Retrieve revenue risk cases |
| `/api/v1/risk-cases/{caseId}` | GET | Retrieve an individual risk case |
| `/api/v1/investigations/{investigationId}` | GET | Retrieve investigation details |
| `/api/v1/recovery/batches` | GET | Retrieve recovery batches |
| `/api/v1/recovery/batches/{batchId}/approve` | POST | Authorize a recovery batch |
| `/api/v1/transactions` | GET | Explore transactions |
| `/api/v1/audit` | GET | Retrieve audit records |
| `/api/v1/assistant/chat` | POST | Interact with RecoverAI Assistant |

Endpoint behavior should always be treated as the contract implemented by the current FastAPI backend. If additional routes are introduced, this document should be updated together with the API implementation.

---

# 9. Health API

Health endpoints are used by developers, deployment platforms, monitoring systems, and operators.

## 9.1 Liveness Check

### Endpoint

```text
GET /api/v1/health/live
```

### Purpose

Determines whether the FastAPI application process is alive.

This endpoint is intentionally lightweight and should not require a full application workflow.

### Example

```bash
curl https://<BACKEND_URL>/api/v1/health/live
```

### Successful Response

```json
{
  "status": "ok"
}
```

### HTTP Status

```text
200 OK
```

### Interpretation

```text
200 → Application process is alive
```

---

# 10. Readiness Check

### Endpoint

```text
GET /api/v1/health/ready
```

### Purpose

Determines whether the backend is ready to serve application requests, including database connectivity.

### Example

```bash
curl https://<BACKEND_URL>/api/v1/health/ready
```

### Successful Response

```json
{
  "status": "healthy",
  "database": "ok"
}
```

### HTTP Status

```text
200 OK
```

### Architecture

```text
Readiness Request
       │
       ▼
FastAPI
       │
       ▼
Database Connection
       │
       ├── Available → Healthy
       │
       └── Unavailable → Not Ready
```

---

# 11. Dashboard Metrics API

### Endpoint

```text
GET /api/v1/dashboard/metrics
```

This is one of the most important RecoverAI endpoints.

It supplies the dashboard with financial, payment, risk, and trend intelligence.

## 11.1 Query Parameters

### `timeframe`

Supported values:

```text
24h
7d
30d
90d
```

Example:

```text
GET /api/v1/dashboard/metrics?timeframe=24h
```

### `scenario`

The dashboard can optionally provide the active incident/scenario context.

Example:

```text
GET /api/v1/dashboard/metrics?timeframe=24h&scenario=UPI_DEGRADATION
```

## 11.2 Example Request

```bash
curl "https://<BACKEND_URL>/api/v1/dashboard/metrics?timeframe=24h&scenario=UPI_DEGRADATION" \
  -H "X-Merchant-ID: 00000000-0000-0000-0000-000000000001"
```

## 11.3 Example Response

A representative response contains financial and payment health metrics such as:

```json
{
  "revenueAtRisk": 1219544.0,
  "recoverableRevenue": 304886.0,
  "revenueRecovered": 42000.0,
  "paymentSuccessRate": 81.9,
  "baselineSuccessRate": 81.9,
  "successRateDeltaPercentagePoints": 0.0,
  "paymentMethods": [
    {
      "method": "UPI",
      "successRate": 72.1,
      "deltaPercent": -22.1,
      "volume": 738,
      "status": "critical"
    },
    {
      "method": "Card",
      "successRate": 95.4,
      "deltaPercent": -0.1,
      "volume": 241,
      "status": "normal"
    },
    {
      "method": "Net Banking",
      "successRate": 94.5,
      "deltaPercent": -1.0,
      "volume": 164,
      "status": "normal"
    },
    {
      "method": "Wallet",
      "successRate": 99.1,
      "deltaPercent": 3.6,
      "volume": 108,
      "status": "normal"
    }
  ]
}
```

Additional fields may be returned for trend data, recovery performance, risk information, and other dashboard visualizations.

---

# 12. Dashboard Metric Definitions

### Revenue at Risk

Estimated merchant revenue exposed because of payment failures or degradation.

Example:

```text
₹12,19,544
```

### Recoverable Revenue

Subset of revenue at risk that the recovery logic determines may be eligible for controlled recovery.

Example:

```text
₹3,04,886
```

### Revenue Recovered

Revenue actually recovered through completed recovery operations.

Example:

```text
₹42,000
```

### Payment Success Rate

Percentage of payment transactions successfully captured.

Conceptually:

```text
Captured Transactions
--------------------- × 100
Total Transactions
```

For the canonical demonstration dataset:

```text
1,024 / 1,251 × 100 ≈ 81.85%
```

### Payment Method Success Rate

Success rate calculated independently for each payment method.

Example:

```text
UPI
Card
Net Banking
Wallet
```

### Success Rate Delta

Difference between current payment performance and the applicable baseline.

A negative value indicates degradation.

---

# 13. Timeframe Behavior

The dashboard supports:

```text
24H
7D
30D
90D
```

The selected timeframe is passed to the backend.

Example:

```text
GET /api/v1/dashboard/metrics?timeframe=7d
```

The backend determines the appropriate aggregation.

The system should not fabricate historical payment events when the available dataset does not contain telemetry for the entire requested period.

If the available data covers only a limited period, the frontend should communicate this limitation through an appropriate notice.

---

# 14. Risk Cases API

### Endpoint

```text
GET /api/v1/risk-cases
```

### Purpose

Returns merchant revenue risk cases detected by RecoverAI.

Risk cases represent business-level payment incidents rather than individual transactions.

## 14.1 Example

```bash
curl "https://<BACKEND_URL>/api/v1/risk-cases" \
  -H "X-Merchant-ID: 00000000-0000-0000-0000-000000000001"
```

## 14.2 Conceptual Response

```json
{
  "items": [
    {
      "caseId": "RC-001",
      "status": "OPEN",
      "severity": "HIGH",
      "riskType": "Payment Degradation",
      "revenueAtRisk": 1219544,
      "recoverableRevenue": 304886
    }
  ]
}
```

The exact response fields should follow the current FastAPI schema.

---

# 15. Risk Case Detail API

### Endpoint

```text
GET /api/v1/risk-cases/{caseId}
```

Example:

```text
GET /api/v1/risk-cases/RC-001
```

### Purpose

Returns detailed information about a specific revenue risk case.

The detail response can support:

- Risk metadata
- Severity
- Status
- Financial exposure
- Payment method
- Root-cause information
- Evidence
- Investigation reference
- Recovery recommendation

### Example

```bash
curl "https://<BACKEND_URL>/api/v1/risk-cases/RC-001" \
  -H "X-Merchant-ID: 00000000-0000-0000-0000-000000000001"
```

---

# 16. Risk Case Lifecycle

A risk case can conceptually move through:

```text
DETECTED
   │
   ▼
OPEN
   │
   ▼
INVESTIGATING
   │
   ▼
RECOVERY ELIGIBLE
   │
   ▼
RECOVERY / MONITORING
   │
   ▼
RESOLVED
```

The exact statuses available are determined by the backend domain model.

---

# 17. Investigations API

### Endpoint

```text
GET /api/v1/investigations/{investigationId}
```

Example:

```text
GET /api/v1/investigations/INV-00000000
```

### Purpose

Returns structured investigation information for a revenue risk case.

The investigation is responsible for explaining:

> Why is this payment degradation happening?

## 17.1 Investigation Information

A typical investigation can include:

- Investigation ID
- Risk Case ID
- Status
- Confidence
- Root Cause
- Evidence
- Findings
- Timeline
- Recommended Action

## 17.2 Example

```bash
curl "https://<BACKEND_URL>/api/v1/investigations/INV-00000000" \
  -H "X-Merchant-ID: 00000000-0000-0000-0000-000000000001"
```

---

# 18. Investigation Root Cause Model

RecoverAI can represent root cause hierarchically.

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
```

This allows the frontend to show both high-level and detailed diagnostic findings.

---

# 19. Investigation Confidence

Investigations can include a confidence score.

For example:

```text
Confidence: 83%
```

The confidence value indicates how strongly the available evidence supports the investigation conclusion.

It should not be interpreted as a guarantee of correctness.

---

# 20. Recovery Batch API

### Endpoint

```text
GET /api/v1/recovery/batches
```

### Purpose

Returns recovery batches available to the merchant.

### Example

```bash
curl "https://<BACKEND_URL>/api/v1/recovery/batches" \
  -H "X-Merchant-ID: 00000000-0000-0000-0000-000000000001"
```

### Conceptual Response

```json
{
  "items": [
    {
      "batchId": "RB-024",
      "status": "PENDING_APPROVAL",
      "transactionCount": 120,
      "recoverableAmount": 304886
    }
  ]
}
```

The exact fields depend on the backend response schema.

---

# 21. Recovery Batch Lifecycle

A recovery batch can move through states such as:

```text
PENDING_APPROVAL
       │
       ▼
APPROVED
       │
       ▼
RUNNING
       │
       ├───────────────┐
       │               │
       ▼               ▼
 COMPLETED          STOPPED
       │               │
       └───────┬───────┘
               ▼
          RECONCILIATION
```

A batch must not be considered financially recovered simply because it has been approved or started.

Actual recovery is determined during reconciliation.

---

# 22. Recovery Approval API

### Endpoint

```text
POST /api/v1/recovery/batches/{batchId}/approve
```

Example:

```text
POST /api/v1/recovery/batches/RB-024/approve
```

### Purpose

Authorizes a recovery batch after the merchant/operator explicitly approves the proposed recovery action.

### Example

```bash
curl -X POST \
  "https://<BACKEND_URL>/api/v1/recovery/batches/RB-024/approve" \
  -H "X-Merchant-ID: 00000000-0000-0000-0000-000000000001" \
  -H "Content-Type: application/json"
```

---

# 23. Recovery Approval Safety

Approval is not intended to bypass safety controls.

A valid recovery operation should conceptually pass through:

```text
Approval Request
      │
      ▼
Merchant Validation
      │
      ▼
Batch Validation
      │
      ▼
Policy Validation
      │
      ▼
Idempotency Check
      │
      ▼
Exposure Check
      │
      ▼
Retry Constraints
      │
      ▼
Approved
```

If a safety requirement fails, execution should be rejected or stopped.

---

# 24. Recovery Idempotency

Recovery operations must protect against duplicate processing.

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
    ├── Existing → Do Not Duplicate
    │
    └── New → Process
```

This protects against duplicate recovery attempts caused by:

- Double submission
- Network retries
- Backend retries
- Worker retries
- Application restarts

---

# 25. Circuit Breaker

Recovery execution includes a circuit-breaker safety concept.

The circuit breaker monitors execution quality.

Example:

```text
Recovery Running
      │
      ▼
Failure Rate Monitoring
      │
      ▼
Threshold Check
      │
      ├── Below Threshold → Continue
      │
      └── Above Threshold
              │
              ▼
        RECOVERY STOPPED
              │
              ▼
        Remaining Queue Protected
              │
              ▼
          Audit Event
```

This prevents a degraded recovery mechanism from continuing to process transactions uncontrollably.

---

# 26. Recovery Reconciliation

The recovery workflow separates:

> Proposed Recovery

from:

> Actual Recovery

Conceptually:

```text
Recoverable Revenue
        │
        ▼
Recovery Batch
        │
        ▼
Execution
        │
        ▼
Successful Transactions
        │
        ▼
Reconciliation
        │
        ▼
Revenue Recovered
```

This distinction is essential for financial accuracy.

---

# 27. Transaction API

### Endpoint

```text
GET /api/v1/transactions
```

### Purpose

Provides transaction-level visibility into payment activity.

The transaction explorer can be used to investigate:

- Payment method
- Bank
- Status
- Failure reason
- Amount
- Transaction ID
- Transaction timing

### Example

```bash
curl "https://<BACKEND_URL>/api/v1/transactions" \
  -H "X-Merchant-ID: 00000000-0000-0000-0000-000000000001"
```

---

# 28. Transaction Filtering

The transaction endpoint can support query filtering according to the implemented API schema.

Typical business filters include:

- Payment Method
- Bank
- Transaction Status
- Failure Reason
- Time Range

Examples of payment methods:

```text
UPI
Card
Net Banking
Wallet
```

Examples of banks:

```text
HDFC
ICICI
SBI
Axis
```

The exact supported query parameter names should be treated as defined by the current FastAPI endpoint implementation.

---

# 29. Transaction Data Model

A transaction can conceptually contain:

```json
{
  "transactionId": "TX-103928",
  "amount": 5000,
  "paymentMethod": "UPI",
  "bank": "HDFC",
  "status": "FAILED",
  "failureReason": "GATEWAY_TIMEOUT",
  "timestamp": "2026-08-21T12:30:00"
}
```

The actual API schema may contain additional fields.

---

# 30. Audit API

### Endpoint

```text
GET /api/v1/audit
```

### Purpose

Returns operational and financial audit events.

### Example

```bash
curl "https://<BACKEND_URL>/api/v1/audit" \
  -H "X-Merchant-ID: 00000000-0000-0000-0000-000000000001"
```

---

# 31. Audit Events

Audit records can represent events such as:

- Risk Detected
- Investigation Created
- Root Cause Determined
- Recovery Recommended
- Policy Validated
- Merchant Approved
- Recovery Started
- Recovery Completed
- Circuit Breaker Triggered
- Recovery Stopped
- Reconciliation Completed

---

# 32. Audit Integrity

RecoverAI's design includes cryptographic audit concepts.

Audit events can contain verification information such as SHA-256 hashes.

Conceptually:

```text
Event Data
    │
    ▼
Canonical Representation
    │
    ▼
SHA-256
    │
    ▼
Audit Proof
```

The purpose is to make important operational events tamper-evident and traceable.

---

# 33. AI Assistant API

### Endpoint

```text
POST /api/v1/assistant/chat
```

### Purpose

Provides the RecoverAI operational assistant with an API interface.

The assistant can help users understand:

- Payment degradation
- Risk cases
- Revenue exposure
- Investigations
- Recovery opportunities
- Recovery status
- Operational questions

---

# 34. Assistant Request

A conceptual request can look like:

```json
{
  "message": "Why is UPI performing poorly?"
}
```

Example:

```bash
curl -X POST \
  "https://<BACKEND_URL>/api/v1/assistant/chat" \
  -H "X-Merchant-ID: 00000000-0000-0000-0000-000000000001" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Why is UPI performing poorly?"
  }'
```

---

# 35. Assistant Response

A conceptual response can contain:

```json
{
  "message": "UPI is showing degraded performance primarily due to concentrated HDFC UPI gateway timeout failures."
}
```

The exact response schema depends on the current assistant implementation.

---

# 36. AI Safety Boundary

The AI assistant does not replace backend financial controls.

The following distinction is important:

```text
AI Recommendation
       ≠
Financial Authorization
```

For example:

```text
AI:
"This batch may be suitable for recovery."

        ↓

Backend:
"Is the merchant authorized?"

        ↓

Backend:
"Does the policy permit this action?"

        ↓

Backend:
"Has this transaction already been processed?"

        ↓

Backend:
"Is the exposure within limits?"

        ↓

Execute only if allowed
```

This prevents an AI-generated response from becoming an uncontrolled financial transaction.

---

# 37. Error Handling

RecoverAI uses standard HTTP status codes.

| Status | Meaning |
|---|---|
| 200 | Request successful |
| 201 | Resource created |
| 400 | Invalid request |
| 401 | Authentication/authorization required |
| 403 | Operation forbidden |
| 404 | Resource not found |
| 409 | Conflict, such as duplicate operation |
| 422 | Validation error |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
| 503 | Service/database unavailable |

The exact status returned depends on the API endpoint and backend implementation.

---

# 38. Validation Errors

FastAPI/Pydantic validation errors can return structured information.

A conceptual response is:

```json
{
  "detail": [
    {
      "loc": ["query", "timeframe"],
      "msg": "Invalid timeframe",
      "type": "value_error"
    }
  ]
}
```

Clients should not assume every error response has exactly the same structure.

---

# 39. Resource Not Found

If a requested resource does not exist:

```text
GET /api/v1/risk-cases/RC-999
```

the backend can return:

```text
404 Not Found
```

The frontend should display an appropriate not-found state.

---

# 40. Recovery Conflicts

A recovery request may encounter a conflict.

Examples:

- Batch already approved
- Transaction already recovered
- Duplicate operation
- Recovery already running

A conflict can be represented using:

```text
409 Conflict
```

This is particularly important for idempotent recovery operations.

---

# 41. Backend Unavailability

If the API is unavailable:

```text
Frontend
   │
   ▼
API Request
   │
   X
Backend unavailable
```

The frontend should display a transparent error state.

It should not silently replace production API results with fabricated financial data.

---

# 42. No Mock Fallback Principle

Production financial metrics should not silently fall back to mock data when the backend fails.

The preferred architecture is:

```text
API Available
     │
     ▼
Render Real Backend Data
```

If the API fails:

```text
API Failure
     │
     ▼
Display Error / Unavailable State
```

rather than:

```text
API Failure
     │
     ▼
Invent / Substitute Financial Data
```

This is especially important for:

- Revenue
- Recovery amounts
- Payment success rates
- Risk cases
- Transactions
- Recovery status

---

# 43. API Security

The API should follow these security principles:

**Backend-only secrets**
Database and private credentials remain server-side.

**HTTPS**
Production API communication should use HTTPS.

**CORS**
Only approved frontend origins should be allowed.

**Merchant scoping**
Requests should operate within the correct merchant context.

**Validation**
Input should be validated before business logic executes.

**Recovery authorization**
Financial actions should require appropriate authorization.

**Idempotency**
Duplicate recovery actions must be prevented.

---

# 44. API and Database Separation

The frontend never directly connects to PostgreSQL.

Incorrect:

```text
Browser ─────────► PostgreSQL
```

Correct:

```text
Browser
   │
   ▼
FastAPI
   │
   ▼
PostgreSQL
```

This protects:

- Database credentials
- Schema
- Query logic
- Tenant isolation
- Financial business rules

---

# 45. API Request Lifecycle

A typical request follows:

```text
1. Browser sends request
        │
        ▼
2. FastAPI receives request
        │
        ▼
3. Request validation
        │
        ▼
4. Merchant context resolved
        │
        ▼
5. Business logic executed
        │
        ▼
6. Repository queries PostgreSQL
        │
        ▼
7. Result transformed into API schema
        │
        ▼
8. JSON response returned
        │
        ▼
9. Frontend renders response
```

---

# 46. API Performance Considerations

The API should avoid unnecessary database operations.

Recommended principles include:

- Use database-side aggregation for dashboard metrics
- Query only required columns
- Avoid N+1 queries
- Use appropriate database indexes
- Use async database access
- Keep recovery operations bounded
- Paginate large transaction/audit collections where supported
- Avoid returning unnecessary transaction payloads

---

# 47. Async Backend Architecture

RecoverAI uses asynchronous backend/database infrastructure.

Conceptually:

```text
FastAPI
   │
   ▼
Async SQLAlchemy
   │
   ▼
asyncpg
   │
   ▼
PostgreSQL
```

This allows the backend to handle concurrent I/O operations more efficiently than blocking database access.

---

# 48. API Versioning

All current application endpoints are grouped under:

```text
/api/v1
```

This creates a stable version boundary.

Future breaking API changes can be introduced through:

```text
/api/v2
```

without immediately breaking clients using:

```text
/api/v1
```

---

# 49. API Documentation and FastAPI

FastAPI automatically provides interactive API documentation when enabled.

Typical endpoints are:

```text
/docs
```

and:

```text
/redoc
```

depending on the production configuration.

These can be used by developers to inspect:

- Available routes
- Request schemas
- Response schemas
- Query parameters
- HTTP methods
- Validation requirements

---

# 50. Example End-to-End API Workflow

The following demonstrates the intended operational flow.

**Step 1 — Check service**

```text
GET /api/v1/health/live
```

**Step 2 — Check readiness**

```text
GET /api/v1/health/ready
```

**Step 3 — Load dashboard**

```text
GET /api/v1/dashboard/metrics?timeframe=24h
```

**Step 4 — Inspect risk**

```text
GET /api/v1/risk-cases/RC-001
```

**Step 5 — Investigate**

```text
GET /api/v1/investigations/INV-00000000
```

**Step 6 — Inspect recovery batches**

```text
GET /api/v1/recovery/batches
```

**Step 7 — Approve eligible batch**

```text
POST /api/v1/recovery/batches/RB-024/approve
```

**Step 8 — Monitor transactions**

```text
GET /api/v1/transactions
```

**Step 9 — Inspect audit trail**

```text
GET /api/v1/audit
```

---

# 51. Example: Payment Failure to Recovery

Consider a failed ₹5,000 payment.

The API workflow is conceptually:

```text
Transaction
    │
    ▼
GET /transactions
    │
    ▼
Risk Case
    │
    ▼
GET /risk-cases/RC-001
    │
    ▼
Investigation
    │
    ▼
GET /investigations/INV-00000000
    │
    ▼
Recovery Batch
    │
    ▼
GET /recovery/batches
    │
    ▼
Merchant Approval
    │
    ▼
POST /recovery/batches/RB-024/approve
    │
    ▼
Recovery Execution
    │
    ▼
Reconciliation
    │
    ▼
GET /audit
```

The API therefore supports the complete operational lifecycle rather than treating payment failure as an isolated transaction status.

---

# 52. Canonical Demonstration Data

The current RecoverAI demonstration environment contains:

```text
Total Transactions:       1,251
Captured:                 1,024
Failed:                     227
Overall Success Rate:     81.85%
```

Financial metrics include:

```text
Revenue at Risk:          ₹12,19,544
Recoverable Revenue:      ₹3,04,886
Revenue Recovered:        ₹42,000
```

Primary active incident:

```text
Risk Case:                RC-001
Investigation:            INV-00000000
```

These values represent the controlled demonstration dataset used by RecoverAI.

They should not be interpreted as real customer payment records.

---

# 53. Scenario and Simulation Context

RecoverAI supports controlled demonstration scenarios.

The API architecture distinguishes between:

> Authoritative Live Incident

and:

> Synthetic Simulation Scenario

The scenario selector must not imply that selecting a simulation profile automatically replaces the authoritative PostgreSQL dataset.

This distinction prevents misleading financial reporting.

---

# 54. Production API Architecture

The current production architecture is:

```text
                         INTERNET
                            │
                            ▼
                 ┌────────────────────┐
                 │       Netlify      │
                 │   Next.js Frontend │
                 └─────────┬──────────┘
                           │
                           │ HTTPS
                           ▼
                 ┌────────────────────┐
                 │       Render       │
                 │    FastAPI API     │
                 └─────────┬──────────┘
                           │
                           │ Async SQL
                           ▼
                 ┌────────────────────┐
                 │ Managed PostgreSQL │
                 └────────────────────┘
```

The database is not exposed directly to the public internet.

---

# 55. Local API Architecture

Local development uses:

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

This mirrors the production service boundaries.

---

# 56. Deployment Environment Variables

### Frontend

```text
NEXT_PUBLIC_API_URL
```

Example:

```text
NEXT_PUBLIC_API_URL=https://<BACKEND_URL>
```

The variable is compiled into the Next.js client bundle during the production build.

Therefore, changing it requires a new frontend build/deployment.

### Backend

Typical backend configuration includes:

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

Sensitive values must remain backend-only.

---

# 57. Production Deployment Checklist

Before considering the API production-ready:

```text
[ ] Backend deployed
[ ] PostgreSQL provisioned
[ ] DATABASE_URL configured
[ ] Backend health endpoint returns 200
[ ] Backend readiness endpoint returns 200
[ ] Database connection verified
[ ] CORS configured
[ ] Frontend NEXT_PUBLIC_API_URL configured
[ ] Frontend rebuilt after API URL configuration
[ ] Dashboard API returns data
[ ] Risk Cases API returns data
[ ] Investigation API returns data
[ ] Recovery API returns data
[ ] Transactions API returns data
[ ] Audit API returns data
[ ] No production mock fallback
[ ] Secrets excluded from Git
```

---

# 58. API Testing Checklist

For each deployment, verify:

**Health**

```text
GET /api/v1/health/live
GET /api/v1/health/ready
```

**Dashboard**

```text
GET /api/v1/dashboard/metrics?timeframe=24h
GET /api/v1/dashboard/metrics?timeframe=7d
GET /api/v1/dashboard/metrics?timeframe=30d
GET /api/v1/dashboard/metrics?timeframe=90d
```

**Risk**

```text
GET /api/v1/risk-cases
GET /api/v1/risk-cases/RC-001
```

**Investigation**

```text
GET /api/v1/investigations/INV-00000000
```

**Recovery**

```text
GET /api/v1/recovery/batches
POST /api/v1/recovery/batches/RB-024/approve
```

**Transactions**

```text
GET /api/v1/transactions
```

**Audit**

```text
GET /api/v1/audit
```

**Assistant**

```text
POST /api/v1/assistant/chat
```

---

# 59. API Reliability Principles

RecoverAI follows these reliability principles:

**Never silently fabricate financial data**
If the API fails, report the failure.

**Never bypass recovery safety controls**
A UI action is not sufficient authorization.

**Never expose database credentials**
Database access belongs to the backend.

**Never treat recoverable revenue as recovered revenue**
Recovery must be reconciled.

**Never retry financial operations indefinitely**
Recovery must remain bounded.

**Never allow duplicate recovery operations**
Idempotency must be enforced.

**Never continue unsafe recovery execution**
The circuit breaker should stop the batch when configured thresholds are exceeded.

---

# 60. API Architecture Summary

The API can be summarized as:

```text
                    RECOVERAI API
                         │
          ┌──────────────┼───────────────┐
          │              │               │
          ▼              ▼               ▼
      Intelligence    Operations       Controls
          │              │               │
          │              │               │
     Dashboard       Recovery          Audit
     Risk Cases      Transactions      Health
     Investigations  Assistant         Validation
          │              │               │
          └──────────────┼───────────────┘
                         │
                         ▼
                    PostgreSQL
```

The API therefore acts as the central control plane connecting payment intelligence, risk analysis, recovery operations, and financial auditability.

---

# 61. Design Philosophy

RecoverAI's API architecture follows a simple principle:

> The API should make it easy to understand what happened, why it happened, how much is at risk, what can be recovered, and whether recovery is safe.

The API is not designed merely to expose database tables.

It represents the operational lifecycle of payment revenue:

```text
Detect
  ↓
Investigate
  ↓
Quantify
  ↓
Decide
  ↓
Authorize
  ↓
Recover
  ↓
Reconcile
  ↓
Audit
```

---

# 62. Related Documentation

For additional technical and product context, see:

- `README.md` — Project overview and quick start
- `project_documentation.md` — Complete project and product documentation
- `ARCHITECTURE.md` — System architecture and infrastructure design

---

# 63. API Status

| Area | Status |
|---|---|
| FastAPI Backend | Production Deployed |
| API Version | `/api/v1` |
| Health Endpoint | Operational |
| Readiness Endpoint | Operational |
| Dashboard API | Operational |
| Risk Cases API | Operational |
| Investigation API | Operational |
| Recovery API | Operational |
| Transactions API | Operational |
| Audit API | Operational |
| Assistant API | Operational |
| PostgreSQL | Connected |
| HTTPS | Enabled |
| CORS | Configured |
| Merchant Context | Supported |
| Recovery Safety Controls | Implemented |
| Idempotency Protection | Implemented |
| Circuit Breaker | Implemented |

---

# 64. Final API Principle

RecoverAI's API is designed around a strict separation between:

> INTELLIGENCE

and:

> EXECUTION

The system may detect a payment problem, investigate its cause, quantify financial exposure, and recommend a recovery strategy.

However:

```text
Recommendation
      ≠
Authorization
      ≠
Execution
      ≠
Recovered Revenue
```

Each stage has its own controls and verification.

This separation is what allows RecoverAI to combine AI-assisted payment intelligence with controlled financial operations.

---

**RecoverAI API Principle:**

> Expose the truth. Enforce the rules. Execute within bounds. Reconcile the result. Audit the decision.

---



That separation makes the repository look like a real software/fintech product repository rather than a Buildathon-only submission.
