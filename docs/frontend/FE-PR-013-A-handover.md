# FE-PR-013-A Handover

This PR seeds the AI tutor safety shell. It includes:

- Server-proxied `/api/tutor` route (server-only provider key)
- Input validation and conservative free-chat / PII filters
- Provider client that reads `TUTOR_PROVIDER_KEY` from environment
- Audit hook stub that logs safe events server-side
- Frontend hook `useTutorStream` as a thin client shell
- Basic tests proving conservative request rejection

Non-goals (explicit): voice, microphone, WhatsApp, parent review, transcripts.

Next steps: integrate rate-limiter, wire real audit persistence, implement streaming safety envelope.
# FE-PR-013-A AI Tutor Safety Shell Handover

## Purpose

Implement a minimal, safe AI tutor server shell for lesson-bound assistance. This PR creates the backend proxy, request and response filters, rate limiting, audit hooks, and a frontend client hook without exposing any provider credentials or allowing free-chat.

## Included work

- `app/frontend/src/app/api/tutor/route.ts`
  - New server-side tutor POST endpoint
  - Lesson-bounded request contract
  - Server-only provider key access via `TUTOR_PROVIDER_API_KEY`
  - Input filtering and free-chat refusal
  - Output filtering and safe refusal defaults
  - Rate-limit guard returning a safe educational retry message
  - Audit event stubs for request, sanitization, provider call, response filtering, refusal, and rate-limit events

- `app/frontend/src/lib/tutor/types.ts`
  - Shared tutor request and response shapes
  - Audit event shape

- `app/frontend/src/lib/tutor/safety.ts`
  - Input validation and sanitization helpers
  - Broad free-chat refusal detection
  - Output safety envelope

- `app/frontend/src/lib/tutor/rate-limit.ts`
  - In-memory lesson request rate limiter
  - Safe 429 refusal response

- `app/frontend/src/lib/tutor/audit.ts`
  - Audit hooks and in-memory event store for later persistence

- `app/frontend/src/lib/tutor/client.ts`
  - Frontend client wrapper for `/api/tutor`

- `app/frontend/src/hooks/useTutorStream.ts`
  - Client hook exposing request, loading, error, and response state

- `app/frontend/src/__tests__/tutor/*`
  - Route and safety tests for the new tutor shell

## Environment variables

- `TUTOR_PROVIDER_API_URL` — server-side tutor provider endpoint
- `TUTOR_PROVIDER_API_KEY` — server-only provider key

## Non-goals in this PR

- No voice input, microphone access, or Web Speech API
- No WhatsApp sharing or URL shortcuts
- No tutor transcript storage or schema persistence
- No parent-review history persistence
- No unrestricted chatbot UI
- No background streaming or audio recording

## Verification notes

This PR is intentionally scoped to the safety shell. It can be extended in later split PRs once the contract and audit boundaries are reviewed.
