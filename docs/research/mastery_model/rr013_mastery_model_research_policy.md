---
title: "RR-013 Mastery Model Research Policy"
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

# RR-013 Mastery Model Research Policy

Advanced mastery-model research authority recorded: true
Research-only boundary recorded: true
Existing mastery model preserved: true
Runtime KG implementation claimed: false
Learner-facing model deployment authorised: false
Model retraining on production learner data authorised: false
Human review required before deployment: true
CAPS alignment evaluation required: true

## Boundary and caveats carried forward

- RR-003 remains valid, but its fallback coverage baseline recorded 0.0 because full test collection had pre-existing blockers.
- RR-006 remains valid, but its evidence PR merged with only the required branch-protection check blocking; other non-required checks were red.
- RR-014 public beta expansion remains outstanding.
- RR-015 external approvals remain outstanding.
- RR-016 operational drills remain outstanding.

## Research-only scope

RR-013 may produce research findings, comparisons, and evaluation protocols. It may not deploy a new mastery model, alter learner-facing model behaviour, start runtime KG implementation, retrain on production learner data, or authorise public beta/production release.
