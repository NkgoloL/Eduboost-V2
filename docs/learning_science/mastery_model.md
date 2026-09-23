---
title: "Mastery Model"
status: "active"
owner: "learning-science"
reviewers: ["learning-science", "diagnostics", "curriculum"]
audience: "learning-science-reviewer"
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: '2026-09-23'
review_interval_days: 90
evidence_command: 'PYTHON=.venv/bin/python make diagnostics-assessment-check'
code_anchors: [app/modules/progress/mastery_model.py, tests/unit/modules/progress/test_mastery_model.py, tests/unit/test_mastery_semantics.py]
---
# Mastery Model

Topic mastery combines diagnostic and practice signals into a score from `0.0` to `1.0`.

Weights:

- IRT theta transformed through the normal CDF and confidence-weighted by SE: 40%
- Rolling practice accuracy: 25%
- Recency decay: 15%
- Consistency ratio: 10%
- Confidence interval width: 10%

Labels:

- `needs_practice`: 0.00-0.39
- `developing`: 0.40-0.59
- `on_track`: 0.60-0.74
- `proficient`: 0.75-0.89
- `mastered`: 0.90-1.00

Diagnostic completion upserts `topic_mastery` and appends `mastery_snapshots`. Progress services expose topic timelines, subject summaries, learning velocity, risk, and next-best-activity recommendations for study-plan and parent-report consumers.
