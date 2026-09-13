---
title: "Release — Auth Lifecycle HTTP Route Proof Status"
status: "active"
owner: "release"
reviewers: ['release', 'engineering']
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Auth Lifecycle HTTP Route Proof Status

Generated at: `2026-09-02T21:18:25Z`
Commit: `689420a46ef961b11a3f1c8dcd6182ae8c478824`

**Status:** `auth-lifecycle-http-route-proof-passing`
**Router import OK:** `True`
**Synthetic app registration OK:** `True`

| Function | Service method | Source route | Registered | Service method | Dependency | Delegates | Methods | Paths | Passed |
|---|---|---:|---:|---:|---:|---:|---|---|---:|
| `register` | `register` | True | True | True | True | True | `POST` | `/auth/register` | True |
| `login` | `login` | True | True | True | True | True | `POST` | `/auth/login` | True |
| `refresh` | `refresh` | True | True | True | True | True | `POST` | `/auth/refresh` | True |
| `logout` | `logout` | True | True | True | True | True | `POST` | `/auth/logout` | True |
| `revoke_all_tokens` | `revoke_all_tokens` | True | True | True | True | True | `POST` | `/auth/revoke-all` | True |

## Blockers

- None

## No false-closure rules

- Route registration/source proof does not prove database-backed auth semantics.
- Cookie persistence and refresh-token revocation semantics remain separate runtime concerns.
- This proof does not approve beta release.
