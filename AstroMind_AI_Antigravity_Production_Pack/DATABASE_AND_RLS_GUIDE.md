# Database and RLS Implementation Guide

## Suggested tables
- profiles
- birth_profiles
- chart_calculations
- conversations
- messages
- chat_tool_runs
- astrology_rules
- knowledge_sources
- knowledge_chunks
- reports
- subscriptions
- usage_events
- consent_records
- audit_events

## Required patterns
- UUID primary keys where useful; foreign keys and explicit deletion behavior.
- Every user-owned row has owner_id or derives ownership through a parent relation.
- Backend repositories accept authenticated owner context and scope every query.
- Never accept owner_id, role, plan, or price as authoritative from client input.
- RLS enabled for browser-accessible tables.
- Database grants and RLS policies both reviewed; RLS alone is not a substitute for least-privilege grants.
- Service-role key is server-only.
- Parameterized SQL and ORM expressions only.
- Index owner_id and common time/order columns.
- Keep embeddings dimension aligned to the selected embedding model.
- Use separate schema/table or explicit policy for public knowledge versus private data.
- Avoid storing unnecessary birth data in messages and telemetry.

## RLS testing matrix
For each table, test:
- Unauthenticated SELECT/INSERT/UPDATE/DELETE denied.
- User A can access permitted User A records.
- User A cannot read, modify or delete User B records.
- User A cannot attach a message to User B's conversation.
- User A cannot retrieve or download User B's report.
- Parent-child ownership mismatches are rejected.
- Admin access is explicit and audited.
- Service-role access is restricted and never exposed to browser.

## Migration policy
- All schema changes are versioned.
- Run migrations on a disposable test DB and staging first.
- Prefer additive migrations; separate risky data migrations.
- Backup before production migration.
- Have a rollback or forward-fix plan.
- Do not auto-run destructive migrations during application startup.
- Production migration requires human approval.
