---
title: "Security Documentation"
status: active
owner: security
reviewers: [backend, operations, privacy]
audience: security
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-09-23
review_interval_days: 45
evidence_command: "PYTHONPATH=. .venv/bin/python -m pytest tests/test_popia_negative.py tests/smoke/test_v2_smoke.py -q --no-cov"
code_anchors: [docs/security/README.md, app/security, app/core/security.py]
---

# Security Documentation

Security documents must distinguish policy, architecture, controls, evidence, and historical review material.

Security readiness claims require evidence commands and must not be made as broad prose claims without a current verification boundary.
