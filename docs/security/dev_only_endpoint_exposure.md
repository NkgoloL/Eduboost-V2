---
title: "Dev-Only Endpoint Exposure Guard"
status: active
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

# Dev-Only Endpoint Exposure Guard

## Purpose

Development-only bootstrap endpoints must not expose operational details or
create sessions in production.

## Guarded Endpoint

```text
POST /api/v2/auth/dev-session
```

## Required Production Behavior

The route must check `settings.is_production()` and return `HTTP_404_NOT_FOUND`
with a generic `Not found` response in production.

## Command

```bash
make dev-only-endpoint-check
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_dev_only_endpoint_exposure.py -q --no-cov
```
