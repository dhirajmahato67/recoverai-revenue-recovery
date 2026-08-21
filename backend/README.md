# RecoverAI — FastAPI Backend Foundation

Production-grade FastAPI backend service for the **RecoverAI** revenue recovery control center.

---

## 🏛️ Target Architecture

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application factory, lifespan, CORS, middleware, global error handlers
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py              # Root API router mounting versioned endpoints
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── health.py          # /api/v1/health/live and /api/v1/health/ready
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Pydantic Settings (APP_NAME, DATABASE_URL, CORS, POOL settings)
│   │   ├── logging.py             # Structured JSON/Console logging with request_id context
│   │   ├── exceptions.py          # AppException hierarchy (NotFound, Validation, Conflict, DB, etc.)
│   │   ├── middleware.py          # RequestID correlation & HTTP access log timing middleware
│   │   └── security.py            # Security headers & auth extension baseline
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py             # Async SQLAlchemy 2.0 engine, sessionmaker, get_db dependency
│   │   ├── base.py                # DeclarativeBase with timestamp/ID mixins
│   │   └── health.py              # check_db_health (lightweight SELECT 1 with sanitized error handling)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── common.py              # HealthResponse, ReadinessResponse, ErrorResponse, ErrorDetail schemas
│   └── services/
│       └── __init__.py            # Application service interface baseline
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Async pytest fixtures with ASGITransport & mock DB overrides
│   ├── test_health.py             # Liveness & readiness test suite
│   ├── test_config.py             # Configuration validation tests
│   └── test_middleware.py         # Request ID & error handling tests
├── alembic/
│   ├── env.py                     # Async migration runner connected to Settings
│   ├── script.py.mako
│   └── versions/
├── alembic.ini
├── pyproject.toml
├── Dockerfile                     # Multi-stage non-root Python 3.12+ image
├── .dockerignore
├── .env.example
└── README.md
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.12+**
- **PostgreSQL 16+** (optional locally, or via Docker Compose)

### 2. Environment Configuration
Copy the example environment file and adjust if necessary:
```bash
cp .env.example .env
```

### 3. Install Dependencies
Using standard `pip`:
```bash
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

pip install -e ".[dev]"
```

Or using `uv` (if available):
```bash
uv sync
```

---

## 🧪 Running Tests
Run the comprehensive test suite with `pytest`:
```bash
pytest
```
Or with `uv`:
```bash
uv run pytest
```

---

## 🗄️ Database Migrations with Alembic

### Run Migrations to Head:
```bash
alembic upgrade head
```

### Create a New Migration Revision (for future phases):
```bash
alembic revision --autogenerate -m "create_domain_models"
```

### Rollback Previous Migration:
```bash
alembic downgrade -1
```

---

## 🏃‍♂️ Running the Backend Locally

Start the development server with live reload:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Or with `uv`:
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Endpoints
- **Interactive Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **OpenAPI JSON Spec:** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)
- **Liveness Probe:** `GET http://localhost:8000/api/v1/health/live`
- **Readiness Probe:** `GET http://localhost:8000/api/v1/health/ready`

---

## 🐳 Docker & Docker Compose

### Start PostgreSQL with Docker Compose (from repository root):
```bash
docker compose up -d postgres
```

### Build & Run Full Stack (Frontend + Backend + Database):
```bash
docker compose up --build
```

### Build Backend Docker Image Manually:
```bash
docker build -t recover-ai-backend:latest -f backend/Dockerfile backend/
```

---

## 🛡️ Security & Observability

1. **Request Correlation:** Every incoming request receives an `X-Request-ID` header, propagated across logs, downstream tasks, and error responses.
2. **Sanitized Error Responses:** No database connection strings, credentials, or internal stack traces are ever leaked to API clients.
3. **Structured Logging:** Production logs output single-line JSON with timestamps, log levels, service names, and request IDs.
4. **Security Headers:** Automatic `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, and `Referrer-Policy` headers.
