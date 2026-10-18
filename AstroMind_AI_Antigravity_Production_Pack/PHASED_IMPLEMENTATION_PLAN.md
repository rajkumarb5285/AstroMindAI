# Phased Implementation Plan — Stop and Review After Every Phase

## Phase 0 — Repository audit and threat model
**Do:** Inspect existing files, package manifests, environment files without printing secret values, deployment configuration, auth, database and tests. Inventory routes and dependencies. Create an architecture diagram, asset inventory, data-flow map, threat model, and prioritized backlog.
**Do not:** Make destructive changes, deploy, or change production credentials.
**Exit gate:** User reviews findings and approves Phase 1.

## Phase 1 — Secure foundation
Create frontend/backend scaffolds only where missing, strict typing, linting, formatting, health endpoints, Docker local environment, CI baseline, environment validation, safe error handling, and dependency pinning.
**Exit gate:** Fresh local setup works from README; checks run; no secrets committed.

## Phase 2 — Identity, database and authorization
Create migrations, auth integration, owner-scoped repositories, RLS, test identities, cross-user denial tests, deletion flows and privacy data inventory.
**Exit gate:** Automated tests prove user A cannot access user B's records through API or direct browser-accessible database paths.

## Phase 3 — Deterministic Vedic engine
Resolve ephemeris licensing, implement adapter, timezone conversion, D1, signs, houses, Nakshatras/padas and versioned configuration. Add golden reference tests.
**Exit gate:** Documented tolerances and boundary tests pass. No AI-generated calculations.

## Phase 4 — Profile/chart product slice
Implement birth profile CRUD, chart API, chart UI, saved calculations, loading/error states and accessibility.
**Exit gate:** An authenticated user can create and view a real chart; authorization tests pass.

## Phase 5 — Rulebook and RAG
Create source registry and ingestion pipeline, licensing metadata, safe parsers, chunking, embeddings, hybrid retrieval, source filtering, prompt-injection tests and rule versions.
**Exit gate:** Retrieval is permission-aware, citations are verifiable, and poisoned documents cannot override system policies.

## Phase 6 — Chat and advanced modules
Implement typed tool calls, chat, streaming, grounded responses, Dasha explanations, transit dates, compatibility and asynchronous reports. Keep each module behind feature flags until validated.
**Exit gate:** Evaluation set passes defined thresholds; spend/latency limits are enforced.

## Phase 7 — Security and operations hardening
Threat-model review, dependency and container scans, secret scanning, authorization tests, abuse/rate-limit tests, SSRF and upload tests if applicable, backup restoration, incident drills, monitoring and load tests.
**Exit gate:** No unresolved critical/high issues without explicit documented risk acceptance by an authorized owner.

## Phase 8 — Staging release
Deploy to isolated staging, apply migrations, run smoke tests, verify CSP/CORS/TLS, verify logs redact PII, test rollback and restore.
**Exit gate:** Signed release checklist. Production deployment requires explicit user approval.

## Phase 9 — Production launch and maintenance
Canary/gradual rollout, monitor errors and costs, patch dependencies, review access and audit logs, restore-test backups, re-run regression tests after engine or prompt changes, and conduct periodic external security testing.
