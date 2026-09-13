---
title: "Release — No False-Closure Status After AUTH-REFRESH-DB-PROOF-001 / code_2671_2710"
status: "active"
owner: "release"
reviewers: ['release', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# No False-Closure Status After AUTH-REFRESH-DB-PROOF-001 / code_2671_2710

**Status:** auth refresh DB proof harness added.

## Proven

- A DB-backed proof path exists and requires explicit `AUTH_REFRESH_DB_PROOF_DSN`.
- Skipped DB tests are not accepted as proof.
- Pending evidence remains `external-blocked`.
- Release-mode check fails until accepted DB proof evidence exists.

## Not claimed

- Refresh-token persistence is proven yet.
- Logout/revoke-all DB revocation is proven yet.
- Token reuse detection is proven yet.
- Beta release is approved.
