---
title: "RR-013 Mastery Model Research Agenda"
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

# RR-013 Mastery Model Research Agenda

Research question 1: Which mastery-model family best improves learner-state estimation while preserving interpretability for parents and educators?

Research question 2: Which evaluation design can compare the current mastery formula against advanced knowledge-tracing candidates without exposing learner PII?

Research question 3: What CAPS-alignment checks are required before any advanced model can influence recommendations or reporting?

Research question 4: What human review, privacy, and safety gates are required before any learner-facing deployment decision?

Do not implement runtime KG in RR-013. The knowledge-graph north-star remains an architectural direction only and needs separate authorisation before runtime work starts.
