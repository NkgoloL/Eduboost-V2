---
title: "JWT Rotation Repair Report"
status: "active"
owner: "engineering"
reviewers: ["engineering"]
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-08-26"
review_interval_days: 60
evidence_command: "make docs-housekeeping-check"
code_anchors: ["docs/security/jwt_rotation_repair_report.md"]
---

# JWT Rotation Repair Report

Generated at: `2026-08-03T14:19:38Z`

**Status:** implemented

- Encode call patches: `0`
- Decode call patches: `0`
- Key-ring helper: `app/services/jwt_keyring.py`
- Current JWTs should include `kid` headers where patched.
