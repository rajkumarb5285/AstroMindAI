# Production Release Go/No-Go Checklist

Mark each item VERIFIED with evidence, NOT VERIFIED, or NOT APPLICABLE with justification.

## Product
- [ ] Real chart calculations, no mock calculations in production.
- [ ] Chart settings and engine version displayed/stored.
- [ ] AI answers grounded in actual calculation output.
- [ ] Sources/citations validated.
- [ ] Missing/uncertain birth time handled honestly.
- [ ] Privacy and account deletion controls work.

## Security
- [ ] Authentication and recovery tested.
- [ ] Object-level authorization tests pass for every private resource.
- [ ] RLS and grants tested with non-service roles.
- [ ] No secrets in repo, history review, client bundle or logs.
- [ ] CORS, CSP, TLS and security headers verified.
- [ ] Rate limits and cost quotas tested.
- [ ] RAG prompt-injection and cross-user leakage tests pass.
- [ ] Upload/SSRF protections tested if those features exist.
- [ ] Dependencies, source, containers and deployment config scanned.
- [ ] No unresolved critical findings.
- [ ] High findings remediated or formally risk-accepted with expiry.
- [ ] External penetration test completed before broad public launch.

## Reliability
- [ ] Migrations tested in staging.
- [ ] Backup restore test passed.
- [ ] Monitoring and alerts verified.
- [ ] Queue failure/retry and provider outage behavior tested.
- [ ] Rollback/forward-fix plan documented.
- [ ] Load/performance test completed against expected traffic.

## Legal and governance
- [ ] Ephemeris licensing approved.
- [ ] Knowledge source rights/attribution approved.
- [ ] Privacy notice and terms reviewed.
- [ ] Data retention/deletion policy implemented.
- [ ] Third-party AI data handling reviewed.
- [ ] User-facing astrology limitations are clear.

## Operations
- [ ] Production secrets set via approved secret manager.
- [ ] Staging and production isolated.
- [ ] No debug/admin/database/Redis ports publicly exposed.
- [ ] On-call/incident contact defined.
- [ ] Release owner approved rollout.
- [ ] Post-deploy smoke tests prepared.

A release is NO-GO if any critical security control is unverified, core ownership tests fail, production secrets are exposed, or legal licensing is unresolved.
