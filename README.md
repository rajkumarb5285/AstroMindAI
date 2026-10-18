# AstroMind AI — Production Vedic Astrology & Grounded AI Platform

[![Live App](https://img.shields.io/badge/Live_App-frontend--steel--nu--90.vercel.app-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://frontend-steel-nu-90.vercel.app)
[![Backend API](https://img.shields.io/badge/Backend_API-Live_on_Render-46E3B7?style=for-the-badge&logo=render&logoColor=black)](https://astromind-backend.onrender.com/health/live)

- **Live Production Web Application**: [https://frontend-steel-nu-90.vercel.app](https://frontend-steel-nu-90.vercel.app)
- **Live Production Backend API**: [https://astromind-backend.onrender.com](https://astromind-backend.onrender.com)
- **Interactive API Documentation (Swagger)**: [https://astromind-backend.onrender.com/docs](https://astromind-backend.onrender.com/docs)

AstroMind AI is a production-ready web application for Vedic astrology (Jyotish) featuring deterministic ephemeris chart calculations, source-grounded AI analysis, tenant isolation with PostgreSQL Row-Level Security (RLS), and defense-in-depth architecture.

---

## 1. Architecture Highlights

- **Deterministic Ephemeris Engine:** Mathematical calculation of planetary longitudes, Ascendant, Whole-Sign houses, Nakshatras/padas, and Vimshottari Dasha intervals.
- **Isolated AI Layer:** The LLM does not calculate astronomical charts, execute raw SQL, or receive direct database access. Narrow, typed, read-only tools bound all interactions.
- **Security & Tenant Isolation:** Server-side object-level ownership checks on every private endpoint, augmented with PostgreSQL RLS policies.
- **Zero Secrets in Prompts & Logs:** Automatic PII (birth dates, tokens, keys) redaction on all structured logs.
- **Strict Network & Response Security:** No wildcard CORS with credentials, 1MB body size limiter, and defense-in-depth response headers (CSP, HSTS, X-Content-Type-Options: nosniff, X-Frame-Options: DENY).

---

## 2. Directory Structure

```text
├── AstroMind_AI_Antigravity_Production_Pack/  # Canonical architecture, specs & threat model
├── backend/                                   # FastAPI (Python 3.11) API service
│   ├── app/
│   │   ├── api/v1/                            # API routes (Health, Birth Profiles, Charts, Chat)
│   │   ├── core/                              # Config, structured logging, middleware, security
│   │   └── main.py                            # FastAPI entry point
│   ├── tests/                                 # Pytest test suite (health, security, config)
│   └── pyproject.toml                         # Dependency specifications & tool configs
├── frontend/                                  # Next.js 14 App Router, TypeScript strict, Tailwind CSS
│   ├── src/
│   │   ├── app/                               # App router pages and layouts
│   │   └── components/                        # UI components (Navbar, Footer, Telemetry)
│   ├── next.config.mjs                        # Production security headers
│   └── package.json
├── docker-compose.yml                         # Local PostgreSQL 16 (pgvector) & Redis 7
├── .env.example                               # Safe template with configuration placeholders
└── .github/workflows/ci.yml                   # CI lint, typecheck, and test pipeline
```

---

## 3. Local Development Quickstart

### Prerequisites
- Python 3.11+ (or `uv`)
- Node.js 18+ (Node 20+ recommended)
- Docker Desktop (for PostgreSQL + pgvector and Redis)

### Step 1: Start Databases
```bash
docker compose up -d
```
PostgreSQL (with `pgvector`) will be available at `127.0.0.1:5432` and Redis at `127.0.0.1:6379`.

### Step 2: Set Up Backend
```bash
# Using uv (fastest):
uv venv backend/.venv --python 3.11
backend\.venv\Scripts\activate
uv pip install -e "backend[dev]"

# Run backend test suite:
backend\.venv\Scripts\pytest backend\tests -v

# Run linter and typechecker:
backend\.venv\Scripts\ruff check backend
backend\.venv\Scripts\mypy backend\app --ignore-missing-imports

# Start FastAPI server:
backend\.venv\Scripts\uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
API probes available at:
- Liveness: `http://localhost:8000/health/live`
- Readiness: `http://localhost:8000/health/ready`

### Step 3: Set Up Frontend
```bash
cd frontend
npm install
npm run typecheck
npm run dev
```
Frontend application accessible at `http://localhost:3000`.

---

## 4. Ethical & Non-Predictive Disclaimer

Vedic Astrology (Jyotish) is a traditional interpretive symbolic practice, not an empirical scientifically validated method for predicting future events. AstroMind AI does not make guaranteed claims, predictions of absolute certainty, or replace licensed medical, mental health, legal, investment, or financial advice.
