# RecoverAI — Deployment Guide

> **Production deployment guide for the RecoverAI AI-powered revenue recovery platform**

RecoverAI is deployed as a full-stack application with a separated frontend, backend API, and managed PostgreSQL database.

The production architecture is:

```text
                         INTERNET
                            │
                            ▼
                 ┌────────────────────┐
                 │      Netlify       │
                 │   Next.js Frontend │
                 └─────────┬──────────┘
                           │
                           │ HTTPS / REST API
                           ▼
                 ┌────────────────────┐
                 │      Render       │
                 │   FastAPI Backend  │
                 └─────────┬──────────┘
                           │
                           │ Async PostgreSQL
                           ▼
                 ┌────────────────────┐
                 │ Managed PostgreSQL │
                 │    PostgreSQL 16   │
                 └────────────────────┘
```

The browser never connects directly to PostgreSQL.

---

## Table of Contents

3. [Deployment Philosophy](#3-deployment-philosophy)
4. [Repository Structure](#4-repository-structure)
5. [Hosting Responsibilities](#5-hosting-responsibilities)
6. [Frontend Deployment](#6-frontend-deployment)
7. [Next.js Production Configuration](#7-nextjs-production-configuration)
8. [Netlify Configuration](#8-netlify-configuration)
9. [Frontend Environment Variable](#9-frontend-environment-variable)
10. [Why NEXT_PUBLIC_API_URL Is Important](#10-why-next_public_api_url-is-important)
11. [Frontend API Flow](#11-frontend-api-flow)
12. [Backend Deployment](#12-backend-deployment)
13. [Backend Startup](#13-backend-startup)
14. [Backend Environment Variables](#14-backend-environment-variables)
15. [Database Deployment](#15-database-deployment)
16. [DATABASE_URL](#16-database_url)
17. [Database Initialization](#17-database-initialization)
18. [Seed Safety](#18-seed-safety)
19. [Canonical Demonstration Dataset](#19-canonical-demonstration-dataset)
20. [Render Blueprint](#20-render-blueprint)
21. [Render Backend Service](#21-render-backend-service)
22. [Render Health Check](#22-render-health-check)
23. [Readiness Verification](#23-readiness-verification)
24. [CORS Configuration](#24-cors-configuration)
25. [Custom Domain Architecture](#25-custom-domain-architecture)
26. [DNS and Custom Domain](#26-dns-and-custom-domain)
27. [Production API Verification](#27-production-api-verification)
28. [Dashboard API Verification](#28-dashboard-api-verification)
29. [End-to-End Deployment Verification](#29-end-to-end-deployment-verification)
30. [Production Verification Checklist](#30-production-verification-checklist)
31. [Application Route Verification](#31-application-route-verification)
32. [Navigation Verification](#32-navigation-verification)
33. [Recovery Verification](#33-recovery-verification)
34. [Timeframe Verification](#34-timeframe-verification)
35. [Scenario Verification](#35-scenario-verification)
36. [Production Build Verification](#36-production-build-verification)
37. [Backend Test Verification](#37-backend-test-verification)
38. [Docker Verification](#38-docker-verification)
39. [Local Production Simulation](#39-local-production-simulation)
40. [GitHub Deployment Flow](#40-github-deployment-flow)
41. [Recommended Git Workflow](#41-recommended-git-workflow)
42. [Automatic Deployment](#42-automatic-deployment)
43. [Frontend Deployment Failure](#43-frontend-deployment-failure)
44. [Backend Deployment Failure](#44-backend-deployment-failure)
45. [Database Connection Failure](#45-database-connection-failure)
46. [Frontend Shows "Failed to Load Data"](#46-frontend-shows-failed-to-load-data)
47. [CORS Troubleshooting](#47-cors-troubleshooting)
48. [Environment Variable Troubleshooting](#48-environment-variable-troubleshooting)
49. [Secrets Management](#49-secrets-management)
50. [Environment Separation](#50-environment-separation)
51. [Production Security Rules](#51-production-security-rules)
52. [Payment Integration Safety](#52-payment-integration-safety)
53. [Recovery Safety in Production](#53-recovery-safety-in-production)
54. [Monitoring](#54-monitoring)
55. [Recommended Alerts](#55-recommended-alerts)
56. [Logging](#56-logging)
57. [Deployment Rollback](#57-deployment-rollback)
58. [Database Change Policy](#58-database-change-policy)
59. [Deployment Incident Checklist](#59-deployment-incident-checklist)
60. [Production Smoke Test](#60-production-smoke-test)
61. [Production Acceptance Criteria](#61-production-acceptance-criteria)
62. [Current Production Status](#62-current-production-status)
63. [Production Readiness Summary](#63-production-readiness-summary)
64. [Deployment Architecture at a Glance](#64-deployment-architecture-at-a-glance)
65. [Deployment Philosophy (Summary)](#65-deployment-philosophy-summary)
66. [Final Principle](#66-final-principle)

---

# 3. Deployment Philosophy

RecoverAI follows these production principles:

**Separation of concerns**
Frontend, backend, and database are independently deployed services.

**No database access from frontend**
The browser communicates only with the FastAPI API.

**No secrets in frontend**
Database credentials and backend secrets remain server-side.

**HTTPS in production**
All public application communication uses HTTPS.

**No production mock fallback**
If the backend is unavailable, the frontend should report the API failure rather than silently displaying fabricated financial data.

**Idempotent initialization**
Database initialization and seeding are designed to avoid duplicating the canonical dataset.

**Bounded recovery**
Financial recovery operations remain subject to authorization and safety constraints.

---

# 4. Repository Structure

The deployment-relevant repository structure is approximately:

```text
recoverai-revenue-recovery/
│
├── src/
│   ├── app/
│   ├── components/
│   └── lib/
│       └── api/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── main.py
│   │
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── public/
│
├── next.config.mjs
├── netlify.toml
├── render.yaml
├── docker-compose.yml
├── Dockerfile.frontend
├── package.json
└── README.md
```

---

# 5. Hosting Responsibilities

### Netlify

Netlify is responsible for:

- Hosting the Next.js frontend
- Serving static production assets
- HTTPS
- CDN delivery
- Production frontend deployments
- Environment variable configuration
- Connecting the public domain to the frontend

### Render

Render is responsible for:

- Running the FastAPI backend
- Building the backend Docker image
- Starting the FastAPI application
- Providing a public HTTPS API endpoint
- Health checks
- Automatic deployments from GitHub
- Backend environment variables

### Managed PostgreSQL

The managed PostgreSQL service is responsible for:

- Persistent application data
- Transactions
- Risk cases
- Investigations
- Recovery data
- Audit records
- Merchant data

---

# 6. Frontend Deployment

The frontend is a Next.js application.

The production build is generated using:

```bash
npm run build
```

The application uses a static export configuration compatible with Netlify.

The generated production output is:

```text
out/
```

---

# 7. Next.js Production Configuration

RecoverAI uses:

```text
output: "export"
```

in the Next.js configuration.

This allows the frontend to be deployed as static assets.

The deployment architecture therefore becomes:

```text
Next.js Source
      │
      ▼
npm run build
      │
      ▼
Static Production Output
      │
      ▼
out/
      │
      ▼
Netlify
```

---

# 8. Netlify Configuration

The repository contains:

```text
netlify.toml
```

which defines the frontend deployment configuration.

A typical deployment configuration uses:

```toml
[build]
  publish = "out"
```

The exact configuration in the repository should be treated as the source of truth.

---

# 9. Frontend Environment Variable

The most important frontend production environment variable is:

```text
NEXT_PUBLIC_API_URL
```

This tells the Next.js frontend where the production FastAPI backend is located.

Example:

```text
NEXT_PUBLIC_API_URL=https://<YOUR-RENDER-BACKEND-URL>
```

Do not use:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000
```

in production.

---

# 10. Why NEXT_PUBLIC_API_URL Is Important

Next.js embeds public environment variables into the client-side JavaScript during the build.

Therefore:

```text
Environment Variable
        │
        ▼
Next.js Build
        │
        ▼
Client JavaScript Bundle
        │
        ▼
Browser
        │
        ▼
Production FastAPI API
```

Changing the variable in Netlify does not automatically modify an already-generated JavaScript bundle.

After changing:

```text
NEXT_PUBLIC_API_URL
```

a new production build/deployment must be triggered.

---

# 11. Frontend API Flow

The frontend uses the centralized API client rather than scattering backend URLs throughout the application.

Conceptually:

```text
React Component
      │
      ▼
API Client
      │
      ▼
NEXT_PUBLIC_API_URL
      │
      ▼
FastAPI
```

For example:

```text
GET /api/v1/dashboard/metrics
```

becomes:

```text
https://<BACKEND_URL>/api/v1/dashboard/metrics
```

in production.

---

# 12. Backend Deployment

The backend is a FastAPI application.

The backend is containerized using:

```text
backend/Dockerfile
```

The production architecture is:

```text
GitHub
   │
   ▼
Render
   │
   ▼
Docker Build
   │
   ▼
FastAPI Container
   │
   ▼
Public HTTPS API
```

---

# 13. Backend Startup

The backend starts using Uvicorn.

The container is configured to bind to:

```text
0.0.0.0
```

and use the platform-provided:

```text
PORT
```

variable.

Conceptually:

```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

This is important because cloud platforms assign the runtime port dynamically.

---

# 14. Backend Environment Variables

Production backend configuration includes:

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

Example:

```text
APP_NAME=RecoverAI API
APP_ENV=production
DEBUG=false
PORT=<PLATFORM_PORT>
DATABASE_URL=<MANAGED_POSTGRES_CONNECTION_STRING>
CORS_ALLOWED_ORIGINS=<APPROVED_FRONTEND_ORIGINS>
LOG_LEVEL=INFO
DOCS_ENABLED=true
```

Actual secret values must be configured through the hosting platform and must not be committed to Git.

---

# 15. Database Deployment

RecoverAI requires PostgreSQL in production.

The production database is managed independently from the application container.

```text
FastAPI
   │
   │ DATABASE_URL
   ▼
Managed PostgreSQL
```

The database should not be exposed directly to the browser.

---

# 16. DATABASE_URL

The backend connects to PostgreSQL through:

```text
DATABASE_URL
```

The value is supplied through the Render environment.

The application supports PostgreSQL using the asynchronous SQLAlchemy/asyncpg stack.

Conceptually:

```text
DATABASE_URL
      │
      ▼
Pydantic Settings
      │
      ▼
SQLAlchemy Async Engine
      │
      ▼
asyncpg
      │
      ▼
PostgreSQL
```

---

# 17. Database Initialization

RecoverAI initializes missing database structures during backend startup.

The application performs database initialization through the FastAPI lifecycle.

Conceptually:

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
Check Existing Merchant
      │
      ▼
Seed Only When Required
      │
      ▼
Application Ready
```

---

# 18. Seed Safety

RecoverAI uses an idempotent seed mechanism.

The canonical merchant ID is:

```text
00000000-0000-0000-0000-000000000001
```

The seed process checks whether the merchant already exists before inserting the demonstration dataset.

Therefore:

```text
First Startup
     │
     ▼
Merchant Missing
     │
     ▼
Seed Dataset
```

while:

```text
Later Startup
     │
     ▼
Merchant Exists
     │
     ▼
Skip Duplicate Seeding
```

This prevents repeated deployments from duplicating the demonstration transactions.

---

# 19. Canonical Demonstration Dataset

The production demonstration environment is based on the controlled Acme Commerce dataset.

Key values include:

```text
Total Transactions:       1,251
Captured:                 1,024
Failed:                     227
Success Rate:             ~81.85%
```

Financial exposure:

```text
Revenue at Risk:          ₹12,19,544
Recoverable Revenue:      ₹3,04,886
Revenue Recovered:        ₹42,000
```

Primary incident:

```text
Risk Case:                RC-001
Investigation:            INV-00000000
```

These values are controlled demonstration data and should not be represented as real customer payment records.

---

# 20. Render Blueprint

The repository contains:

```text
render.yaml
```

This defines the infrastructure required to deploy the backend and managed PostgreSQL service.

The Blueprint describes:

```text
Web Service
    │
    ├── recoverai-backend
    │
    └── FastAPI Docker Container

Database
    │
    └── recoverai-postgres
```

---

# 21. Render Backend Service

The backend service uses:

```text
Environment: Docker
Dockerfile: backend/Dockerfile
Docker Context: backend
Health Check: /api/v1/health/live
```

The exact values in `render.yaml` are the source of truth for deployment configuration.

---

# 22. Render Health Check

Render checks:

```text
/api/v1/health/live
```

A successful response should be:

```json
{
  "status": "ok"
}
```

with:

```text
HTTP 200
```

If this endpoint fails, the backend should be treated as unhealthy.

---

# 23. Readiness Verification

After deployment, verify:

```text
/api/v1/health/ready
```

A healthy response should indicate:

```json
{
  "status": "healthy",
  "database": "ok"
}
```

This confirms that:

```text
FastAPI
   │
   ▼
PostgreSQL
```

communication is working.

---

# 24. CORS Configuration

The production backend must allow requests from the deployed frontend.

The backend uses:

```text
CORS_ALLOWED_ORIGINS
```

Example:

```text
https://recoverai.dhirajm.com.np
```

If the Netlify hostname is also used, it may be included as an approved origin.

Development origins such as:

```text
http://localhost:3000
```

should not be unnecessarily exposed in a strict production configuration.

---

# 25. Custom Domain Architecture

The public application is available through:

```text
https://recoverai.dhirajm.com.np
```

The domain points to the deployed frontend.

Conceptually:

```text
recoverai.dhirajm.com.np
              │
              ▼
           Netlify
              │
              ▼
          Next.js
              │
              ▼
          Render API
```

The backend remains a separate service.

---

# 26. DNS and Custom Domain

The custom domain configuration is managed through the domain/DNS provider and Netlify.

Typical setup:

```text
DNS
 │
 └── Custom Domain
          │
          ▼
       Netlify
```

After DNS propagation, HTTPS should be enabled for the production domain.

---

# 27. Production API Verification

After deploying the backend, verify the health endpoint:

```bash
curl https://<BACKEND_URL>/api/v1/health/live
```

Expected:

```json
{
  "status": "ok"
}
```

Then verify database readiness:

```bash
curl https://<BACKEND_URL>/api/v1/health/ready
```

Expected:

```json
{
  "status": "healthy",
  "database": "ok"
}
```

---

# 28. Dashboard API Verification

Test:

```text
GET /api/v1/dashboard/metrics?timeframe=24h
```

Then:

```text
GET /api/v1/dashboard/metrics?timeframe=7d
GET /api/v1/dashboard/metrics?timeframe=30d
GET /api/v1/dashboard/metrics?timeframe=90d
```

All supported requests should return:

```text
HTTP 200
```

when the backend and database are healthy.

---

# 29. End-to-End Deployment Verification

After both frontend and backend are deployed:

```text
Browser
   │
   ▼
https://recoverai.dhirajm.com.np
   │
   ▼
Netlify
   │
   ▼
Next.js
   │
   ▼
NEXT_PUBLIC_API_URL
   │
   ▼
Render FastAPI
   │
   ▼
Managed PostgreSQL
```

Verify that dashboard data is actually coming from the production API.

---

# 30. Production Verification Checklist

### Frontend

```text
[ ] Production URL loads
[ ] HTTPS works
[ ] Dashboard loads
[ ] Navigation works
[ ] Risk Cases loads
[ ] Investigations loads
[ ] Recovery loads
[ ] Transactions loads
[ ] Audit loads
[ ] AI Assistant loads
[ ] Settings loads
[ ] Responsive layout works
```

### Backend

```text
[ ] Backend deployed
[ ] Container running
[ ] /health/live returns 200
[ ] /health/ready returns 200
[ ] Database connection works
[ ] CORS works
[ ] API routes return expected responses
```

### Database

```text
[ ] PostgreSQL running
[ ] Tables initialized
[ ] Seed data available
[ ] No duplicate seed records
[ ] Transactions available
[ ] Risk cases available
[ ] Recovery records available
[ ] Audit records available
```

---

# 31. Application Route Verification

Verify the following production routes:

```text
/dashboard
/risk-cases
/risk-cases/RC-001
/investigations
/investigations/INV-00000000
/recovery
/recovery/RB-024
/transactions
/audit
/ai-assistant
/settings
```

Each route should load successfully without relying on a page refresh.

---

# 32. Navigation Verification

Special attention should be given to client-side navigation.

Test:

```text
Dashboard
    ↓
Risk Cases
    ↓
Risk Case Detail
    ↓
Investigation
    ↓
Recovery
    ↓
Transactions
    ↓
Audit
```

The application should work when navigating through the UI without manually refreshing the browser.

---

# 33. Recovery Verification

Recovery functionality should be tested carefully.

Verify:

```text
[ ] Recovery batches load
[ ] Active recovery loads
[ ] Batch details load
[ ] Approval state works
[ ] Safety controls are enforced
[ ] Duplicate processing is prevented
[ ] Circuit breaker works
[ ] Recovery reconciliation is displayed
[ ] Audit events are generated
```

Production deployment should never be considered successful solely because the recovery page renders.

---

# 34. Timeframe Verification

The dashboard supports:

```text
24H
7D
30D
90D
```

Verify that selecting each timeframe triggers the correct API request.

Example:

```text
24H
  ↓
?timeframe=24h

7D
  ↓
?timeframe=7d

30D
  ↓
?timeframe=30d

90D
  ↓
?timeframe=90d
```

If the underlying demonstration dataset covers only a limited period, the UI should transparently communicate the available data coverage rather than implying that historical data exists when it does not.

---

# 35. Scenario Verification

RecoverAI separates:

> Live Active Incident

from:

> Simulation Scenario

Production verification should ensure that selecting a simulation scenario does not falsely imply that the PostgreSQL dataset has changed.

The UI should clearly communicate when the user is viewing:

> Authoritative telemetry

versus:

> Synthetic simulation context

---

# 36. Production Build Verification

Before deployment, run:

```bash
npm run lint
```

Expected:

```text
0 errors
0 warnings
```

Run:

```bash
npx tsc --noEmit
```

Expected:

```text
0 errors
```

Run:

```bash
npm run build
```

Expected:

```text
Build completed successfully
```

---

# 37. Backend Test Verification

Run:

```bash
pytest backend/tests
```

The current project has previously achieved:

```text
84 passed
```

Before a new production deployment, the test suite should pass again.

---

# 38. Docker Verification

For local production-like validation:

```bash
docker compose build backend frontend
```

Then:

```bash
docker compose up -d
```

Check:

```bash
docker compose ps
```

Expected services include:

```text
PostgreSQL
Backend
Frontend
```

The PostgreSQL and backend containers should report healthy status where health checks are configured.

---

# 39. Local Production Simulation

Before pushing major production changes:

```bash
npm run lint
npx tsc --noEmit
npm run build
pytest backend/tests
docker compose build backend frontend
```

This provides a strong pre-deployment quality gate.

---

# 40. GitHub Deployment Flow

RecoverAI uses GitHub as the source repository.

The recommended flow is:

```text
Developer
    │
    ▼
Local Changes
    │
    ▼
Tests
    │
    ▼
Git Commit
    │
    ▼
Git Push
    │
    ▼
GitHub
    │
    ├──────────────► Netlify
    │
    └──────────────► Render
```

---

# 41. Recommended Git Workflow

Before pushing:

```bash
git status
```

Review changed files.

Then:

```bash
git add .
```

Commit:

```bash
git commit -m "Update RecoverAI production deployment"
```

Push:

```bash
git push origin main
```

The connected deployment platforms can then build and deploy the updated application.

---

# 42. Automatic Deployment

The production services can use Git-based automatic deployment.

Conceptually:

```text
GitHub Push
     │
     ├───────────────┐
     ▼               ▼
 Netlify           Render
     │               │
     ▼               ▼
Frontend Build    Backend Build
     │               │
     ▼               ▼
Frontend Deploy   API Deploy
```

Always verify the deployment logs after a production push.

---

# 43. Frontend Deployment Failure

If Netlify deployment fails:

Check:

```text
1. Build command
2. Publish directory
3. Node version
4. Environment variables
5. Next.js configuration
6. Static export compatibility
```

A common frontend build problem is an external font dependency.

RecoverAI previously encountered a production Docker build failure caused by:

```text
next/font/google
```

attempting to download Google Fonts during an isolated build.

The project was changed to use robust local/system font fallback stacks so production builds do not depend on external font downloads.

---

# 44. Backend Deployment Failure

If Render deployment fails:

Check:

```text
1. Docker build logs
2. Python dependencies
3. DATABASE_URL
4. PORT configuration
5. FastAPI startup command
6. Health check endpoint
7. Database connectivity
8. Environment variables
```

The most important initial test is:

```text
/api/v1/health/live
```

---

# 45. Database Connection Failure

If:

```text
/health/live
```

works but:

```text
/health/ready
```

fails, investigate the database.

Typical causes:

```text
Incorrect DATABASE_URL
Database unavailable
Network configuration
Invalid credentials
Database not initialized
Connection pool issue
```

The distinction is:

```text
Liveness
   =
Application process works

Readiness
   =
Application + required dependencies work
```

---

# 46. Frontend Shows "Failed to Load Data"

If the production dashboard displays an API error:

**Step 1**

Open browser Developer Tools.

**Step 2**

Open:

```text
Network
```

**Step 3**

Find:

```text
/api/v1/dashboard/metrics
```

**Step 4**

Check the request URL.

It should point to the production FastAPI backend.

It must not point to:

```text
localhost
127.0.0.1
```

or incorrectly resolve to the Netlify frontend unless an API proxy is intentionally configured.

---

# 47. CORS Troubleshooting

If the API works directly but browser requests fail:

Check:

```text
CORS_ALLOWED_ORIGINS
```

The frontend origin must be included.

For the custom production application:

```text
https://recoverai.dhirajm.com.np
```

The backend must allow this origin.

---

# 48. Environment Variable Troubleshooting

When changing:

```text
NEXT_PUBLIC_API_URL
```

remember:

```text
Changing Netlify variable
        ≠
Changing existing JavaScript bundle
```

You must trigger:

```text
New Build
    │
    ▼
New Deployment
```

before the browser receives the updated API URL.

---

# 49. Secrets Management

Never commit:

```text
.env
.env.local
production secrets
database passwords
private API keys
LLM credentials
```

to GitHub.

Use:

```text
Netlify Environment Variables
```

for frontend configuration and:

```text
Render Environment Variables
```

for backend secrets.

---

# 50. Environment Separation

RecoverAI should maintain separate environments conceptually:

```text
Development
     │
     ▼
Local Docker
     │
     ▼
Testing
     │
     ▼
Production
```

Development may use:

```text
localhost
```

while production uses:

```text
HTTPS
Managed PostgreSQL
Cloud-hosted FastAPI
```

---

# 51. Production Security Rules

The following rules should always be followed.

**Never expose DATABASE_URL**

`DATABASE_URL` must remain backend-only.

**Never expose private payment credentials**

Razorpay private credentials, if introduced, must remain server-side.

**Never expose database ports unnecessarily**

PostgreSQL should not be publicly accessible to the browser.

**Never trust frontend authorization**

The backend must enforce financial authorization.

**Never rely only on UI safety**

A hidden/disabled button is not a security mechanism.

**Never log secrets**

Logs should not contain credentials or sensitive tokens.

---

# 52. Payment Integration Safety

RecoverAI currently operates as a controlled demonstration platform.

If real payment provider integrations are introduced later, production deployment must additionally consider:

- Webhook verification
- Signature validation
- Idempotency
- Provider API authentication
- PCI considerations
- Sensitive data handling
- Retry policies
- Settlement reconciliation

Real financial execution should not be enabled merely because the UI contains a recovery button.

---

# 53. Recovery Safety in Production

Before enabling real recovery workflows, verify:

```text
[ ] Merchant authorization
[ ] Transaction eligibility
[ ] Duplicate-charge protection
[ ] Idempotency keys
[ ] Retry limit
[ ] Exposure limits
[ ] Circuit breaker
[ ] Failure threshold
[ ] Reconciliation
[ ] Audit trail
```

The principle is:

> Automation must remain bounded.

---

# 54. Monitoring

Production monitoring should observe:

### Application

- API uptime
- Response latency
- HTTP errors
- Container health

### Database

- Connection availability
- Query latency
- Storage
- Connection pool

### Business

- Payment failures
- Revenue at risk
- Recoverable revenue
- Recovery success
- Recovery failure
- Circuit-breaker events

---

# 55. Recommended Alerts

Important operational alerts include:

- Backend unavailable
- Database unavailable
- High API error rate
- Recovery failure spike
- Circuit breaker triggered
- Unexpected transaction failure spike
- Large increase in revenue at risk

---

# 56. Logging

Backend logs should help diagnose:

- API failures
- Database failures
- Recovery execution
- Authorization failures
- Circuit breaker events
- Unexpected exceptions

Logs should never contain:

- Passwords
- Private API keys
- Database credentials
- Authentication tokens
- Sensitive payment credentials

---

# 57. Deployment Rollback

If a production deployment introduces a critical regression:

```text
Identify bad deployment
        │
        ▼
Stop further rollout
        │
        ▼
Rollback frontend/backend
        │
        ▼
Verify health endpoints
        │
        ▼
Verify dashboard
        │
        ▼
Verify critical workflows
```

The database should not be rolled back blindly.

Database changes require separate migration and rollback planning.

---

# 58. Database Change Policy

Do not modify production schema manually unless required.

Before database changes:

```text
1. Backup / recovery strategy
2. Migration plan
3. Compatibility review
4. Test migration locally
5. Deploy migration
6. Verify application
```

Application deployments should avoid destructive database operations.

---

# 59. Deployment Incident Checklist

If production breaks:

```text
[ ] Check Netlify deployment status
[ ] Check Render deployment status
[ ] Check backend health endpoint
[ ] Check backend readiness endpoint
[ ] Check browser Network tab
[ ] Check NEXT_PUBLIC_API_URL
[ ] Check CORS
[ ] Check DATABASE_URL
[ ] Check PostgreSQL status
[ ] Check Render logs
[ ] Check Netlify build logs
[ ] Verify API response
[ ] Verify frontend response
```

---

# 60. Production Smoke Test

After every significant deployment:

**1. Open application**

```text
https://recoverai.dhirajm.com.np/dashboard
```

**2. Dashboard**

Verify:

```text
Revenue at Risk
Recoverable Revenue
Revenue Recovered
Payment Success Rate
```

**3. Risk Cases**

Verify:

```text
Risk cases load
Active cases count is correct
```

**4. Investigation**

Verify:

```text
Investigation page opens
Root cause information loads
```

**5. Recovery**

Verify:

```text
Recovery batches load
Active recovery page loads
```

**6. Transactions**

Verify:

```text
Transactions load
Filters work
```

**7. Audit**

Verify:

```text
Audit records load
```

**8. Assistant**

Verify:

```text
Assistant responds correctly
```

---

# 61. Production Acceptance Criteria

A deployment is considered successful when:

```text
Frontend
   ✓

Backend
   ✓

Database
   ✓

API
   ✓

HTTPS
   ✓

CORS
   ✓

Environment Variables
   ✓

Dashboard Data
   ✓

Risk Cases
   ✓

Investigations
   ✓

Recovery
   ✓

Transactions
   ✓

Audit
   ✓
```

---

# 62. Current Production Status

RecoverAI has been deployed as a full-stack internet-accessible application.

Production frontend:

```text
https://recoverai.dhirajm.com.np/dashboard
```

The production architecture uses:

```text
Netlify
   │
   ▼
Next.js Frontend
   │
   ▼
Render
   │
   ▼
FastAPI Backend
   │
   ▼
Managed PostgreSQL
```

The application is designed to serve the controlled Acme Commerce demonstration dataset through the production API.

---

# 63. Production Readiness Summary

The RecoverAI deployment provides:

```text
✓ Public HTTPS frontend
✓ Cloud-hosted FastAPI backend
✓ Managed PostgreSQL
✓ Environment-based configuration
✓ CORS configuration
✓ Health checks
✓ Database readiness checks
✓ Automated database initialization
✓ Idempotent seed mechanism
✓ REST API architecture
✓ Dockerized backend
✓ Static Next.js frontend deployment
✓ Git-based deployment workflow
✓ Recovery safety controls
✓ Auditability
```

---

# 64. Deployment Architecture at a Glance

```text
                       ┌─────────────────────┐
                       │       USER          │
                       │      BROWSER        │
                       └──────────┬──────────┘
                                  │
                                  │ HTTPS
                                  ▼
                       ┌─────────────────────┐
                       │      NETLIFY       │
                       │                     │
                       │  Next.js Frontend  │
                       └──────────┬──────────┘
                                  │
                                  │ REST API
                                  │ HTTPS
                                  ▼
                       ┌─────────────────────┐
                       │       RENDER       │
                       │                     │
                       │   FastAPI Backend  │
                       └──────────┬──────────┘
                                  │
                                  │ asyncpg
                                  ▼
                       ┌─────────────────────┐
                       │ MANAGED POSTGRESQL │
                       │                     │
                       │   RecoverAI Data   │
                       └─────────────────────┘
```

---

# 65. Deployment Philosophy (Summary)

RecoverAI is intentionally designed so that deployment infrastructure mirrors the application's financial-control philosophy:

```text
Frontend
   │
   │ Requests
   ▼
Backend
   │
   │ Validated Operations
   ▼
Database
```

The frontend presents intelligence.

The backend enforces business rules.

The database provides persistent authoritative state.

This separation prevents the client application from becoming the source of truth for financial operations.

---

# 66. Final Principle

> Deploy the interface globally, keep financial logic server-side, keep data authoritative, and make every production operation observable and recoverable.

RecoverAI's production deployment is therefore not simply:

> "Put the website online."

It is:

```text
Frontend
    +
API
    +
Database
    +
Security
    +
Health Monitoring
    +
Data Integrity
    +
Recovery Safety
    +
Auditability
```

Together, these components form the production deployment architecture of RecoverAI.

---

