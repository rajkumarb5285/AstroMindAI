# Testing and Security QA

## Required automated checks
- Formatter, linter and static typing.
- Unit tests for domain logic.
- API integration tests.
- Migration tests against disposable PostgreSQL.
- Auth and object-level authorization tests.
- RLS tests through browser-like roles.
- Secret scanning.
- Dependency/SCA scanning.
- Container scanning.
- SAST where practical.
- DAST against staging where authorized.
- Performance/load tests with safe test data.

## Security test cases
- Change every resource ID to another test user's ID.
- Attempt unauthenticated access to all private endpoints.
- Attempt role/plan/price tampering.
- Send oversized JSON, long text, malformed Unicode, invalid coordinates and unexpected enum values.
- Test SQL injection strings in every search/filter field.
- Test XSS strings in chat and retrieved content.
- Test CSRF where cookie-based sessions are used.
- Test CORS from an untrusted origin.
- Test rate limits and LLM budget limits.
- Test prompt injection and cross-user RAG access.
- Test SSRF only if URL fetch functionality exists.
- Test malicious/oversized files if uploads exist.
- Test expired/replayed signed URLs and billing webhooks.
- Verify logs do not contain secrets or full private prompts.

## Astrology regression tests
- Golden reference charts and documented tolerances.
- Longitude normalization.
- Sign/Nakshatra/pada boundaries.
- Ascendant and D9 boundaries.
- Dasha sequence and period edges.
- Timezone, leap day, midnight and missing-time behavior.
- Repeated calculation determinism.
- Engine/configuration upgrade diffs.

## Release thresholds
- No unresolved critical issues.
- No unresolved high issues without documented, time-limited risk acceptance and compensating controls.
- All core authorization tests pass.
- All production migrations tested.
- Restore test completed.
- Monitoring/alerts validated.
- No secrets in repository or client bundle.
- All skipped tests documented and risk-reviewed.
- External penetration test completed before broad public launch, with remediation verified.

Do not treat a vulnerability scanner's clean report as proof that the system is secure.
