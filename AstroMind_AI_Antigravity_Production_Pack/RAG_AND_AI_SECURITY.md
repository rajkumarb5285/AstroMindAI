# RAG, LLM and Agent Security

## Fundamental rule
A model is not a security boundary. Authorization, tool permissions, quotas, and data filtering must be enforced in deterministic application code outside the model.

## Source ingestion
1. Maintain an allowlist of approved source domains/files and source owners.
2. Record provenance, license/permission, source URL or archive ID, version, retrieval date, hash and reviewer.
3. Reject sources without clear permission for intended use.
4. Do not ingest arbitrary URLs by default.
5. If URL ingestion is required, implement SSRF defenses: allowlist hostnames, block loopback/private/link-local/reserved IP ranges, validate DNS and every redirect, restrict ports, use outbound egress controls, limit bytes/time, and protect against DNS rebinding.
6. Parse in a restricted worker/container with no secrets and minimal network access.
7. Limit file size, page count, decompressed size, recursion, CPU and wall-clock time.
8. Treat all document instructions as untrusted content.
9. Use content hashes and source versioning so poisoning can be traced and rolled back.
10. Require review for new or changed sources before production indexing.

## Retrieval security
- Apply access/tenant filters before retrieved chunks enter the prompt.
- Do not put private user conversations in the shared public astrology corpus by default.
- Use separate data paths for public knowledge and private user memories.
- Store only necessary data in embeddings; embeddings are not automatically anonymous.
- Return source IDs and snippets; verify citations against retrieval results.
- Prevent cross-user and cross-tenant retrieval with tests.
- Cap retrieved chunk count, total tokens and source diversity.
- Log source IDs and retrieval metadata, not full private prompt content by default.

## Prompt injection
- Separate system/developer instructions from user content and retrieved passages.
- Clearly delimit retrieved content as untrusted evidence.
- Tell the model that instructions inside retrieved documents are not executable policy.
- Never place secrets in model context.
- Do not let retrieved text change tool permissions.
- Use tool allowlists and validate arguments independently.
- Limit tool-call iterations, timeouts and output size.
- For sensitive actions, require explicit user confirmation and deterministic policy checks.
- Test direct injection, indirect injection, multilingual injection, encoded payloads, fake citations, tool-call coercion and requests for other users' data.

## Tool safety
Every tool must define:
- Name and purpose
- Typed input schema
- Output schema
- Authentication requirement
- Object-level authorization
- Allowed side effects
- Timeout and rate limit
- Error handling
- Audit metadata

Tools should be read-only by default. Do not expose arbitrary SQL, shell, filesystem, browser or unrestricted HTTP tools to the model. The model must not set a user ID or role; derive identity from the authenticated request.

## Output validation
- Use structured response schemas.
- Verify chart facts against calculation IDs.
- Verify every citation exists in the retrieved set.
- Reject unsupported numerical claims or fabricated chart positions.
- Escape output before rendering.
- Apply safe fallback when validation fails.
- Include uncertainty and limitations where appropriate.
- Never promise specific real-world outcomes from astrology.
- Do not make medical/legal/financial decisions on the user's behalf.

## Abuse and cost controls
- Max input length, context tokens, output tokens and tool calls.
- Per-user and per-IP rate limits.
- Provider timeouts, concurrency caps and circuit breakers.
- Daily/monthly spend budgets and alerts.
- Cache only deterministic results with complete configuration/version keys.
- Prevent prompt-based requests from bypassing quotas.
- Add abuse reporting and account-level controls.

## Evaluation suite
Maintain tests for:
- Direct and indirect prompt injection.
- Cross-user retrieval leakage.
- Poisoned-source instructions.
- Unsupported citation generation.
- Hallucinated planetary placements.
- Tool argument tampering.
- Infinite agent loops.
- Context/token exhaustion.
- Data exfiltration attempts.
- Malicious document parsing.
Run the suite after changing prompts, model, retrieval, tools, embeddings or source corpus.
