---
title: "Boundary Enforcement Policy"
status: active
owner: architecture
reviewers: [architecture, engineering]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/architecture/README.md]
---

# Boundary Enforcement Policy

**Status:** active for repaired P0 routers

## Rule

FastAPI routers must orchestrate request/response concerns. They must not construct repositories directly in repaired P0 domains.

## Current strict targets

- `app/api_v2_routers/popia.py`
- `app/api_v2_routers/lessons.py`

## Transitional allowance

`app/api_v2_routers/auth.py` may retain limited learner repository access until the auth service extraction batch fully centralizes register/login/refresh behavior.

## Next expansion

After auth service extraction, this policy should be extended to every v2 router and enforced by import-linter in CI.
