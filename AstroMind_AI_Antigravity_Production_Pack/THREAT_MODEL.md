# Threat Model

## Assets
- Account credentials and sessions
- Birth details and profile data
- Chart calculations and personal readings
- Conversations and reports
- Knowledge corpus and licenses
- LLM/API credentials
- Database and storage credentials
- Billing/entitlement state
- Deployment pipeline and source repository
- Service availability, integrity and budget

## Threat actors
- Anonymous internet attacker
- Authenticated malicious user
- User attempting cross-account access
- Prompt-injection author or poisoned-document supplier
- Compromised dependency or build action
- Stolen API key or employee credential
- Botnet/spam user causing cost or availability abuse
- Misconfigured administrator or accidental operator error

## High-priority attack paths and mitigations

### Broken object-level authorization / IDOR
Attack: Change profile_id, chart_id, conversation_id or report_id.
Mitigation: Authorize ownership on every request; repository methods require owner scope; test cross-user access; do not rely on UUID secrecy.

### Credential/session theft
Attack: phishing, leaked tokens, insecure recovery, XSS.
Mitigation: managed auth, secure cookies, MFA for admins, session revocation, CSP, dependency patching, no tokens in localStorage when avoidable.

### SQL injection
Attack: crafted search or filter input.
Mitigation: parameterized SQL/ORM, typed input, no dynamic SQL concatenation, least-privilege database roles, testing.

### RLS bypass or service key leak
Attack: browser receives service-role key or API uses overprivileged role.
Mitigation: secret scanning, server-only keys, least privilege, RLS tests, separate roles, environment isolation.

### Prompt injection and indirect injection
Attack: user or retrieved content tells model to ignore policy, expose secrets, call tools.
Mitigation: treat content as data, isolate instructions, narrow tools, no secret context, tool authorization outside model, bounded steps, adversarial evaluation.

### Cross-user RAG leakage
Attack: retrieval returns another user's private content.
Mitigation: do not embed private user conversations into shared corpus by default; enforce tenant/ACL filters before retrieval; separate collections or row-level access; adversarial cross-user tests.

### RAG poisoning
Attack: manipulated documents introduce false rules or malicious instructions.
Mitigation: source allowlist, provenance, review queue, hashes, versioning, content scanning, source-level trust labels, retrieval monitoring, rollback of corpus versions.

### SSRF through URL ingestion
Attack: user submits URL to fetch cloud metadata, internal services, localhost.
Mitigation: disable arbitrary URL ingestion if not required; otherwise strict hostname allowlist, block private/reserved IPs, validate every redirect, defend DNS rebinding, outbound network restrictions, request timeout and size cap.

### Malicious uploads / parser abuse
Attack: oversized PDFs, zip bombs, malformed documents.
Mitigation: size/page/time limits, safe parser sandbox, no execution, MIME sniffing, malware scanning, temporary storage, restricted worker permissions.

### Denial of service and cost exhaustion
Attack: large requests, concurrent LLM calls, report floods.
Mitigation: edge protections, per-IP/user quotas, token limits, concurrency caps, timeouts, queue limits, circuit breakers, spending alerts, graceful degradation.

### Supply-chain compromise
Attack: compromised package/action/container.
Mitigation: lockfiles, pinned actions, minimal dependencies, provenance where available, dependency/container scanning, code review, restricted CI permissions, secretless PR builds, protected release branches.

### Storage leakage
Attack: public report bucket, long-lived URLs, predictable object keys.
Mitigation: private buckets, authorization checks, short-lived signed URLs, opaque keys, deletion policy, audit events.

### Admin and CI compromise
Attack: excessive roles or untrusted pull request executing with secrets.
Mitigation: least privilege, branch protection, approval gates, protected environments, no production secrets in untrusted PR jobs, MFA, audit logs.

## Risk management

Maintain a risk register with:
- ID and description
- Likelihood and impact
- Current controls
- Evidence/tests
- Owner
- Remediation deadline
- Explicit risk acceptance and expiry if not fixed

No critical/high issue should be waived silently. Any exception requires documented business justification, compensating controls, an owner, and an expiry date.
