# Security Controls Checklist

## Edge, network and server
- [ ] TLS enforced; HTTP redirected to HTTPS.
- [ ] Only required public ports exposed.
- [ ] Database, Redis, worker, adminer and metrics endpoints private.
- [ ] WAF/edge rate limiting and bot controls configured where available.
- [ ] Exact CORS allowlist; no wildcard with credentials.
- [ ] Trusted proxy headers configured only for known proxies.
- [ ] Security headers configured and tested: CSP, HSTS, frame restrictions, content-type nosniff, referrer policy, permissions policy.
- [ ] Debug mode disabled; stack traces hidden.
- [ ] Request, body, upload and response size limits.
- [ ] Timeouts and concurrency limits.
- [ ] Outbound egress minimized.
- [ ] Non-root containers, read-only filesystem where feasible, dropped capabilities, resource limits.
- [ ] Health endpoints disclose no secrets or internal topology.
- [ ] Admin access restricted and MFA enabled where supported.

## Application/API
- [ ] Authentication on private routes.
- [ ] Object-level authorization on every resource access.
- [ ] Server derives owner ID and plan from trusted auth/database context.
- [ ] Pydantic schemas reject unexpected/invalid values where appropriate.
- [ ] Parameterized queries; no untrusted SQL concatenation.
- [ ] CSRF defense for cookie-authenticated state-changing requests.
- [ ] Safe HTML rendering; sanitize untrusted Markdown/HTML.
- [ ] Rate limits per IP and user.
- [ ] AI quotas and maximum tokens/turns.
- [ ] Idempotency for retryable side effects.
- [ ] Safe errors with request ID; no stack traces.
- [ ] File upload validation and private storage.
- [ ] Billing webhooks verify signatures and idempotency.
- [ ] Password reset and verification flows resist enumeration and abuse.

## Secrets and supply chain
- [ ] Secret manager/environment settings used.
- [ ] `.env` ignored; `.env.example` contains placeholders only.
- [ ] Secret scanning in CI and before release.
- [ ] No production secrets in developer laptops/PR jobs unless required.
- [ ] Dependencies pinned and regularly updated.
- [ ] SCA/dependency audit runs in CI.
- [ ] Container image scan.
- [ ] CI actions pinned to immutable commit hashes where practical.
- [ ] Minimal CI permissions; protected production environment.
- [ ] SBOM/provenance added if supported by deployment pipeline.

## Database
- [ ] RLS enabled for browser-accessible tables.
- [ ] Policies tested for select/insert/update/delete.
- [ ] API queries include owner scope.
- [ ] Service role only on server and only where needed.
- [ ] Database roles least privilege.
- [ ] TLS/network allowlists configured.
- [ ] Migrations reviewed and tested in staging.
- [ ] Backups enabled and restore tested.
- [ ] Retention/deletion/export workflows tested.
- [ ] No PII in logs or analytics by default.
- [ ] Cross-user access tests run on every release.

## Monitoring and resilience
- [ ] Structured logs redact birth details, prompts, tokens, signed URLs and secrets.
- [ ] Error monitoring configured.
- [ ] Alerts for auth abuse, 5xx, latency, queue buildup, AI spend, rate-limit events and unusual database access.
- [ ] Uptime/readiness checks.
- [ ] Backup restoration and disaster recovery runbook.
- [ ] Incident response owner and contact path defined.
- [ ] Patch cadence and vulnerability triage process.
- [ ] Periodic external penetration test before broad public launch.
