# Architecture and Trust Boundaries

## High-level topology

Browser
  -> CDN/WAF/platform edge
  -> Next.js frontend
  -> FastAPI public API
       -> Auth/session validation
       -> Domain services
          -> Astrology engine adapter (deterministic)
          -> Versioned interpretation rules
          -> AI orchestration (bounded tools)
          -> RAG retrieval (ACL-filtered)
       -> PostgreSQL/Supabase (TLS, least privilege, RLS)
       -> private object storage
       -> optional Redis and private worker queue
       -> LLM provider via server-side adapter

## Trust boundaries

1. Browser is untrusted. It may change any field, ID, plan, role, price or request.
2. API validates authentication, authorization, schemas, quotas and ownership.
3. Database credentials are privileged secrets. They never enter browser code.
4. RAG documents are untrusted data even if they came from a nominally trusted source.
5. LLM output is untrusted. Validate before rendering or persisting.
6. Background workers process jobs from queues as untrusted input; validate job payloads and authorize referenced records.
7. Third-party providers are external trust boundaries. Minimize data shared and configure retention/privacy controls.
8. Admin functions require separate authorization and stronger audit/monitoring.

## Recommended deployment boundaries

- Only HTTPS public ingress to frontend/API.
- Database, Redis, worker and admin interfaces are not publicly reachable.
- Restrict backend egress to required services where supported.
- Separate staging and production projects, credentials, databases, storage buckets and LLM keys.
- Use separate service identities and minimum privileges.
- Use a private bucket for reports; signed URLs expire quickly.
- Never expose debug mode or public admin dashboards in production.

## Core design rules

- Modular monolith first; split services only when operationally justified.
- Calculation engine independent from API and LLM.
- Rules are versioned and testable.
- RAG retrieval is permission-filtered before content enters the model.
- LLM tools are allowlisted, typed and bounded.
- User data is minimized, encrypted in transit, protected at rest by provider controls, and deleted according to policy.
- Observability must redact sensitive content.
