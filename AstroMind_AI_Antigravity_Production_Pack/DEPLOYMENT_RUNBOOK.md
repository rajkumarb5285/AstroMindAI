# Deployment Runbook

## Environments
Use separate projects/accounts or strong isolated resources for development, staging and production:
- Separate databases and storage buckets.
- Separate auth configuration and redirect URLs.
- Separate LLM keys and quotas.
- Separate secrets.
- Separate monitoring environments.
Never copy production birth profiles or conversations into development.

## Pre-deployment
1. Review changes and migration SQL.
2. Run lint, type checks, unit/integration/security tests.
3. Run dependency, secret and container scans.
4. Confirm no critical/high unaccepted findings.
5. Confirm licensing/privacy approvals.
6. Confirm backup is current and restoration has been tested.
7. Confirm rollback or forward-fix plan.
8. Confirm feature flags and rate/spend limits.
9. Confirm environment variables are present without printing values.
10. Obtain explicit human approval.

## Deployment
- Deploy to staging first.
- Apply reviewed migrations using a controlled migration step.
- Run smoke tests for auth, profile, chart, chat, RAG, reports and authorization.
- Verify TLS, CORS, CSP, rate limits, private storage and log redaction.
- Observe latency, error rates, queue depth and model spend.
- Promote gradually/canary where supported.
- Do not expose databases, Redis, workers, adminers or debug endpoints publicly.

## Rollback
- Stop rollout if security checks fail, error rate spikes, data integrity is suspect, or costs exceed thresholds.
- Prefer rolling back application code while preserving compatible schema.
- Use forward fixes for irreversible schema changes when needed.
- Restore data only under an approved incident/change procedure.
- Record actions and notify the owner.

## Backups and recovery
Define recovery point objective (RPO) and recovery time objective (RTO).
- Enable provider backups/PITR if available and appropriate.
- Test restoring into an isolated environment on a schedule.
- Verify restored auth, data integrity, permissions and application connectivity.
- Encrypt backups and restrict access.
- Document retention and deletion behavior.
- A backup that has never been restored is not a proven recovery plan.

## Post-deployment
- Run smoke and authorization tests.
- Verify monitoring and alerts.
- Review logs for accidental PII/secrets.
- Check spend, latency and rate-limit signals.
- Record release version and migration version.
