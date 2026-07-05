---
title: "RR-013 Mastery Model Literature Review"
status: active
owner: research
reviewers: [research, learning-science, privacy]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-07-03
review_interval_days: 60
evidence_command: "PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_rr013_advanced_mastery_model_research.py --json"
code_anchors: [docs/research/mastery_model, scripts/mastery_research]
---

# RR-013 Mastery Model Literature Review

Advanced mastery-model literature reviewed: true
Research source limitations recorded: true
South African CAPS applicability reviewed: true

## Notes

The review covers the current mastery formula, Bayesian Knowledge Tracing, Performance Factors Analysis, Deep Knowledge Tracing, and knowledge-tracing transformers.

Source limitations:

- Most advanced mastery-model literature is published against datasets, curricula, and assessment regimes that differ from the EduBoost context.
- Interpretability and parent-facing explainability remain more important here than marginal offline accuracy gains.
- CAPS alignment must be verified against local curriculum structure rather than inferred from generic subject taxonomies.

CAPS applicability:

- Any candidate model must preserve the existing mastery model as the learner-facing baseline until separate authorisation exists.
- The literature supports structured comparison, but not deployment by itself.
- No runtime KG work is authorised by this research slice.
