---
title: "RR-013 Evaluation Protocol Template"
status: active
owner: research
reviewers: [research, learning-science, privacy]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-03
review_interval_days: 60
evidence_command: "PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_rr013_advanced_mastery_model_research.py --json"
code_anchors: [docs/research/mastery_model, scripts/mastery_research]
---

# RR-013 Evaluation Protocol

Evaluation protocol recorded: false
Offline evaluation required: true
A/B test requires separate approval: true
CAPS alignment evaluation required: true
Fairness and bias evaluation required: true

## Required evaluation dimensions

- predictive calibration
- mastery-label stability
- CAPS topic alignment
- explainability for parent/educator reporting
- privacy and POPIA constraints
