---
title: "Compliance Documentation"
status: active
owner: privacy
reviewers: [security, legal, engineering]
audience: privacy
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-09-23
review_interval_days: 45
evidence_command: "PYTHONPATH=. .venv/bin/python -m pytest tests/test_popia_negative.py tests/smoke/test_v2_smoke.py -q --no-cov"
code_anchors: [docs/compliance/README.md, app/api_v2_routers/popia.py, app/api_v2_routers/consent.py]
---

# Compliance Documentation

Compliance documents cover POPIA, consent, data-subject rights, privacy boundaries, retention, subprocessor handling, and evidence requirements.

Current compliance claims must be verified against implementation and tests, especially where route contracts, actor identity, consent, and data-rights flows are involved.
