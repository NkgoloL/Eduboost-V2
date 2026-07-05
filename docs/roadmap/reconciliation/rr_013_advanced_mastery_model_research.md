---
title: RR-013 Advanced Mastery-Model Research
status: active
owner: research
reviewers: [research, learning-science, privacy]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-05
review_interval_days: 60
evidence_command: make roadmap-reconciliation-check
code_anchors: [docs/roadmap/reconciliation, scripts/roadmap_reconciliation]
---

# RR-013 Advanced Mastery-Model Research

## Register citation

- RR item: `RR-013`
- Register title: `Advanced mastery-model research`
- Source: `post_baseline_roadmap_register.md` / `RM-003`
- Priority: `P2`

## Purpose

RR-013 records research authority and evidence for advanced mastery-model options after RR-012 telemetry dashboard work has landed.

This slice is deliberately research-only. It compares candidate mastery-model approaches, defines evaluation protocol, records data-readiness and privacy boundaries, and preserves the current mastery model until a later separately authorised implementation decision exists.

## Explicit boundary

- Runtime KG implementation claimed: false
- Learner-facing model deployment authorised: false
- Learner-facing model change authorised: false
- Model retraining on production learner data authorised: false
- Production release authorised: false
- Deployment authorised: false
- Release tag authorised: false
- Public beta authorised: false

## Required evidence outputs

- `docs/research/mastery_model/rr013_mastery_model_literature_review.md`
- `docs/research/mastery_model/rr013_candidate_model_comparison.md`
- `docs/research/mastery_model/rr013_evaluation_protocol.md`
- `docs/research/mastery_model/rr013_data_readiness_and_ethics_review.md`
- `docs/research/mastery_model/rr013_research_decision_memo.md`

## Verification

```bash
PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_rr013_advanced_mastery_model_research.py --json
```
