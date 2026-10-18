# Incident Response Playbook

## Preparation
- Assign incident commander, engineering owner and communications owner.
- Maintain provider support and escalation contacts privately.
- Ensure audit logs, backups and deployment history are available.
- Store emergency credentials in an approved secret manager.
- Practice the process without using real customer data.

## If compromise is suspected
1. Triage severity and preserve relevant logs/evidence.
2. Stop the affected feature or isolate the affected service if necessary.
3. Revoke/rotate suspected credentials using approved provider procedures.
4. Disable compromised sessions/tokens and suspicious accounts where appropriate.
5. Restrict network access and outbound calls if exfiltration is possible.
6. Preserve forensic evidence; do not casually delete logs or affected resources.
7. Determine affected data, time window, entry point and scope.
8. Notify internal owners and provider support.
9. Follow applicable legal/regulatory notification requirements with qualified counsel.
10. Restore only from verified clean artifacts/backups.
11. Patch root cause, add regression tests and independently verify remediation.
12. Document timeline, impact, decisions and follow-up actions.

## Scenarios
- Leaked LLM/database key: revoke/rotate, inspect usage, investigate exfiltration, add secret scanning.
- Cross-user data leak: disable affected endpoint, preserve evidence, assess scope, notify according to obligations, fix authorization and add regression tests.
- RAG poisoning: disable affected source/version, restore last known-good index, inspect retrieval logs and review ingestion pipeline.
- Cost/DoS attack: enforce quotas, reduce concurrency, block abusive traffic, alert provider, protect essential functions.
- Dependency compromise: pin/rollback to verified version, inspect build artifacts, rotate any exposed secrets, rebuild from trusted pipeline.

Do not make public statements claiming there was no impact until investigation supports that conclusion.
