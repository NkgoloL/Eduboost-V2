# ADR 0006: Next.js Frontend

## Status
Accepted

## Context
EduBoost needs a learner/guardian/teacher-facing web UI with protected flows, diagnostic and lesson experiences, accessibility requirements, and API-driven state.

## Decision
The frontend application lives under `app/frontend` and uses Next.js as the canonical web framework.

- Frontend scripts, dependency locks, and build gates are managed in `app/frontend`.
- User-facing flows must account for accessibility, mobile usability, session expiry, and consent state.
- API access should be typed or centrally wrapped to avoid route drift.

## Consequences

- **Pros**: Mature routing/build ecosystem, strong React integration, straightforward deployment options.
- **Cons**: Requires careful dependency/version management and explicit API-contract tests to prevent backend/frontend drift.
