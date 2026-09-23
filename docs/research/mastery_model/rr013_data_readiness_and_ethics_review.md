---
title: "RR-013 Data Readiness and Ethics Review"
status: active
owner: research
reviewers: [research, learning-science, privacy]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: '2026-09-23'
review_interval_days: 90
evidence_command: 'PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_rr013_advanced_mastery_model_research.py --json'
code_anchors: [scripts/mastery_research/audit_rr013_advanced_mastery_model_research.py, scripts/roadmap_reconciliation/verify_rr013_advanced_mastery_model_research.py]
---
# RR-013 Data Readiness and Ethics Review

Data readiness and ethics reviewed: true
No learner PII exported for research: true
POPIA lawful basis review required before learner-data research: true
Synthetic or anonymised data preferred: true
Model retraining on production learner data authorised: false

## Notes

The research slice may use synthetic or anonymised data only.

Any future use of learner data requires a fresh POPIA lawful-basis review, privacy sign-off, and a separate authorisation path.

No production learner data is to be exported, copied, or repurposed as part of RR-013.
