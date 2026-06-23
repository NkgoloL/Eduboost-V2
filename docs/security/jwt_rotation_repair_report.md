---
title: "JWT Rotation Repair Report"
status: current-evidence
owner: security
reviewers: [security, engineering, privacy]
audience: security-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/security/README.md, app/security]
---

# JWT Rotation Repair Report

Generated at: `2026-06-13T13:48:49Z`

**Status:** implemented

- Encode call patches: `0`
- Decode call patches: `0`
- Key-ring helper: `app/services/jwt_keyring.py`
- Current JWTs should include `kid` headers where patched.
