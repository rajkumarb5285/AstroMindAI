# AstroMind AI — Antigravity Production Build Pack

**Purpose:** A practical, security-first, phase-gated implementation guide for building AstroMind AI, a production-ready Vedic astrology web application.

## Important security reality

No application, server, database, or AI system can honestly be guaranteed “unhackable,” including against the most capable attackers. The goal is to reduce attack surface, prevent common and advanced attack paths, limit blast radius, detect compromise quickly, and recover safely. This pack requires defense-in-depth, independent review, and ongoing patching; it does not replace a professional penetration test or security/legal review.

## How to use this pack

1. Open your AstroMind AI repository in **Google Antigravity**.
2. Give Antigravity `ANTIGRAVITY_MASTER_INSTRUCTIONS.md` first.
3. Tell it to execute **Phase 0 only**, then stop and report.
4. Review the report and the changed files before authorizing Phase 1.
5. Continue one phase at a time. Never allow an agent to deploy to production, run destructive database operations, rotate secrets, or change cloud access policies without your explicit approval.
6. Use `SECURITY_ACCEPTANCE_CHECKLIST.md` as a release gate.
7. Keep this pack in version control only if it contains no secrets or sensitive operational details.

## Contents

- `ANTIGRAVITY_MASTER_INSTRUCTIONS.md` — primary instructions and non-negotiable rules.
- `PHASED_IMPLEMENTATION_PLAN.md` — phased build sequence and stop points.
- `ARCHITECTURE.md` — recommended application architecture and trust boundaries.
- `THREAT_MODEL.md` — assets, threat actors, attack paths, and mitigations.
- `SECURITY_CONTROLS.md` — server, API, database, identity, infrastructure and operational controls.
- `RAG_AND_AI_SECURITY.md` — prompt injection, retrieval poisoning, tool abuse, privacy, and output validation.
- `ASTROLOGY_ENGINE_SPEC.md` — deterministic Vedic calculations, configuration, licensing, and validation.
- `DATABASE_AND_RLS_GUIDE.md` — data model and access-control requirements.
- `API_CONTRACTS.md` — endpoint and API behavior requirements.
- `DEPLOYMENT_RUNBOOK.md` — staging/production rollout, rollback, backup and recovery.
- `TESTING_AND_SECURITY_QA.md` — automated tests and security testing.
- `INCIDENT_RESPONSE.md` — response procedures for suspected compromise.
- `ENVIRONMENT_VARIABLES.example` — names and descriptions only; no credentials.
- `CI_SECURITY_EXAMPLE.yml` — illustrative CI security workflow to adapt and test.
- `RELEASE_CHECKLIST.md` — final go/no-go criteria.

## Default stack

- Frontend: Next.js App Router, React, TypeScript, Tailwind CSS.
- Backend: Python, FastAPI, Pydantic, SQLAlchemy 2.x, Alembic.
- Database/auth: PostgreSQL/Supabase, Supabase Auth where suitable, RLS.
- Retrieval: pgvector plus keyword search; approved/licensed source material only.
- AI: provider adapter, controlled LangGraph workflow if needed, strict tool contracts.
- Astrology: replaceable ephemeris adapter; select a legally compatible engine and license.
- Async jobs: managed Redis/worker only where needed.
- Deployment: Vercel frontend and managed Python backend, with private object storage.
- Monitoring: structured logs, error monitoring, metrics, alerts, backups and recovery tests.

## Security decision rule

If Antigravity cannot verify that a control is implemented and tested, it must mark it **NOT VERIFIED**, not “complete.” It must never claim the product is unhackable or production-secure merely because the code compiles.
