---
title: "ADR-029: Supabase Auth Strategy"
status: active
owner: architecture
reviewers: [engineering, architecture]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 180
evidence_command: make docs-housekeeping-stage3-check
code_anchors: []
---
# ADR-029: Supabase Auth Strategy

**Date**: 2026-06-12  
**Status**: Accepted  
**Deciders**: Platform Team

## Context

The EduBoost V2 codebase contains references to both:
1. **Raw PostgreSQL** with custom JWT authentication (primary implementation)
2. **Supabase** (optional, commented out in `.env.example`)

There is ambiguity about which auth strategy is authoritative and how they interact. This ADR clarifies the approach.

## Decision

**Primary Auth**: Raw PostgreSQL with JWT tokens (FastAPI-native)

- All production auth flows use `app/core/auth.py` (JWT signing/verification)
- Session management via Redis (`app/core/session.py`)
- Password hashing with bcrypt via `app/security/password.py`

**Supabase**: Optional, for specific use cases only

- Supabase references in `.env.example` are for **legacy migration** and **edge cases**
- Supabase client is NOT initialized in the V2 app by default
- If Supabase URL/keys are provided, the app does NOT automatically use Supabase auth
- Supabase storage may be used for asset uploads (R2 is preferred)

## Consequences

### Positive
- Single authoritative auth path (JWT)
- No hidden Supabase auth state affecting sessions
- Clear env var requirements: `JWT_SECRET`, `DATABASE_URL` are required; Supabase vars are optional

### Negative
- Existing Supabase users require migration (documented separately)
- Teams using Supabase for other projects need explicit config

## Migration Path

For teams currently using Supabase Auth:
1. Export user data from Supabase
2. Import into V2's `users` table with bcrypt-hashed passwords
3. Issue JWTs via the V2 auth flow

## References

- `app/core/auth.py` — JWT handling
- `app/core/session.py` — Redis session
- `.env.example` — Environment configuration (lines 150-156)
- ADR-005 (auth architecture decision, if exists)