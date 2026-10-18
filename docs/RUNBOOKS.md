# AstroMind AI — Production Operations Runbooks

This document provides actionable standard operating procedures (SOPs) and runbooks for Site Reliability Engineers (SRE), Security Operations, and On-Call Engineers managing AstroMind AI.

---

## 1. Incident Response Runbook

### 1.1 Incident Severity Levels

| Severity | Definition | Response Target | Example Scenarios |
| :--- | :--- | :--- | :--- |
| **SEV-1 (Critical)** | Core service outage, catastrophic calculation failure, data breach, or security incident affecting all users. | < 15 min | Swiss Ephemeris crash, authentication bypass, data leak, 5xx error rate > 5%. |
| **SEV-2 (Major)** | Degraded functionality affecting a subset of users, elevated latency, or partial engine outage. | < 1 hour | PDF report generation worker stalled, transit calculations timing out, p95 latency > 100ms. |
| **SEV-3 (Minor)** | Non-critical bug, cosmetic frontend issue, or isolated telemetry failure. | < 24 hours | UI styling anomaly on chart wheel, non-blocking log format warning. |

### 1.2 Incident Handling Workflow

```text
[DETECT] -> [ACKNOWLEDGE] -> [TRIAGE & ISOLATE] -> [REMEDIATE] -> [VERIFY] -> [POST-MORTEM]
```

1. **Detection & Triage:**
   - Inspect `/api/v1/metrics` for server health, process uptime, and error counters.
   - Query structured JSON logs filtered by `level="ERROR"` and `audit_event="AUTH_ACCESS_DENIED"`.
2. **Containment:**
   - If an ongoing attack (credential stuffing or scraping) is detected, adjust sliding window rate limits in `.env`:
     ```bash
     RATE_LIMIT_AUTH_PER_MINUTE=5
     RATE_LIMIT_CALCULATION_PER_MINUTE=20
     ```
   - For malicious IPs, block at cloud ingress / reverse proxy layer.
3. **Escalation & Communication:**
   - Designate Incident Commander (IC).
   - Post hourly status updates to status page until resolved.

---

## 2. Emergency Rollback Procedures

### 2.1 Backend Rollback

If a bad backend release introduces calculation regressions or instability:

1. **Identify Previous Stable Commit / Container Tag:**
   ```bash
   git log --oneline -n 5
   ```
2. **Revert Deployment:**
   - For containerized deployments:
     ```bash
     docker compose pull backend:<previous-tag>
     docker compose up -d --no-deps backend
     ```
   - For Git-based staging/production:
     ```bash
     git revert --no-edit <bad-commit-hash>
     git push origin main
     ```
3. **Database Migration Downgrade (if migration was run):**
   ```bash
   cd backend
   alembic downgrade -1
   ```

### 2.2 Frontend Rollback

1. **Vercel / Next.js Instant Rollback:**
   - Navigate to Vercel Dashboard -> Project -> Deployments.
   - Locate the previous successful deployment and click **"Promote to Production"**.
   - Rollback executes within 5 seconds without container rebuilds.

---

## 3. Database Backup & Disaster Recovery Runbook

### 3.1 Automated Scheduled Backups

Backups are executed automatically via cron/task scheduler calling `scripts/backup_db.py`:

```powershell
python scripts/backup_db.py --output-dir backend/backups --keep 14
```

**Artifacts Generated:**
- `backend/backups/astromind_sqlite_YYYYMMDD_HHMMSS.db` (or `.dump` for PostgreSQL)
- `backend/backups/astromind_sqlite_YYYYMMDD_HHMMSS.db.sha256` (Cryptographic hash)
- `backend/backups/astromind_sqlite_YYYYMMDD_HHMMSS.db.meta.json` (Metadata, record counts, execution latency)

### 3.2 Backup Integrity Verification

To verify backup validity without touching live databases:
```powershell
python scripts/restore_db.py backend/backups/astromind_sqlite_YYYYMMDD_HHMMSS.db --verify-only
```

### 3.3 Full Disaster Recovery (Restoration)

In the event of database corruption or hardware disaster:

1. **Stop Application Instances:**
   ```powershell
   # Prevent concurrent write operations during restore
   docker compose stop backend
   ```
2. **Execute Verified Restore:**
   ```powershell
   python scripts/restore_db.py backend/backups/<backup-file> --target-db <destination>
   ```
   *Note: `restore_db.py` automatically validates the SHA-256 hash before applying any changes. If the checksum is invalid, restoration aborts immediately.*
3. **Validate Tables & Row Counts:**
   - The script outputs a verified table dictionary with row counts for: `profiles`, `birth_profiles`, `chart_calculations`, `conversations`, `messages`, and `audit_events`.
4. **Restart Backend:**
   ```powershell
   docker compose start backend
   curl http://localhost:8000/health/ready
   ```

---

## 4. Key Rotation & Secret Hygiene Runbook

### 4.1 Secrets Inventory

| Secret Name | Location | Usage | Rotation Frequency |
| :--- | :--- | :--- | :--- |
| `SUPABASE_SERVICE_ROLE_KEY` | Environment / Secrets Vault | Server-to-DB privileged auth | 90 days |
| `LLM_API_KEY` | Environment / Secrets Vault | OpenAI / Anthropic provider | 90 days |
| `JWT_SECRET` | Environment / Secrets Vault | Auth token signing | 180 days |

### 4.2 Safe Rotation Procedure

1. **Staged Key Overlap:** Configure the service to accept both the previous key and new key during a 15-minute transition window.
2. **Update Environment:** Deploy updated environment configuration via secret manager.
3. **Rolling Restart:** Perform zero-downtime rolling restart of backend worker nodes.
4. **Revoke Old Key:** Revoke previous key in the third-party provider dashboard.

---

## 5. Observability & Monitoring Guide

- **Live Server Telemetry:**
  ```http
  GET /api/v1/metrics
  Authorization: Bearer <admin-token>
  ```
  Returns:
  - Process uptime & system platform
  - Swiss Ephemeris engine configuration
  - Rate limiting active thresholds
  - Audit event counters
- **Health Probes:**
  - `GET /health/live` — Returns 200 if process is running.
  - `GET /health/ready` — Returns 200 if database connection and ephemeris library respond within SLA.
