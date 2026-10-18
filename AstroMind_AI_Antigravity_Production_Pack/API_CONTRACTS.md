# API Contract Requirements

Base path: /api/v1

## Suggested endpoints
- GET /health/live
- GET /health/ready
- GET /api/v1/me
- CRUD /api/v1/birth-profiles
- POST /api/v1/birth-profiles/{profile_id}/charts
- GET /api/v1/charts/{chart_id}
- POST /api/v1/chat
- POST /api/v1/chat/stream
- GET /api/v1/conversations
- GET /api/v1/conversations/{id}/messages
- DELETE /api/v1/conversations/{id}
- POST /api/v1/compatibility
- GET /api/v1/horoscope/daily
- GET /api/v1/transits
- POST /api/v1/reports
- GET /api/v1/reports/{id}
- DELETE /api/v1/reports/{id}

## Contract rules
- Every private route requires authentication and object-level authorization.
- Birth dates, times, timezone identifiers and coordinates are validated.
- Return stable response schemas and safe error codes.
- Include request_id in errors and logs.
- Never return internal stack traces or secret values.
- Use pagination for list endpoints.
- Limit request bodies and text lengths.
- Rate-limit by user and IP; enforce LLM token and spending quotas.
- Use idempotency keys for operations that may be retried.
- Streaming uses documented SSE event types, heartbeat, timeout, cancellation and safe errors.
- Report generation returns 202 and a status resource when asynchronous.
- Signed download URLs expire and are issued only after authorization.
- Billing webhook signatures and replay/idempotency must be verified.
- Generate OpenAPI and use it to keep frontend client types aligned.
