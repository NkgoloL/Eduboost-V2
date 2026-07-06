---
title: PR-006 AI/CAPS/diagnostics safety
status: active-control
owner: delivery-planning
reviewers: [delivery-planning, engineering, documentation-governance]
audience: delivery-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 30
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/backlog, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# PR-006 AI/CAPS/diagnostics safety

## Summary

Implemented a safety baseline for AI-generated lessons, CAPS topic validation, diagnostic item contracts, and curriculum coverage gap detection.

## Completed

- Centralized versioned CAPS topic map MVP.
- CAPS validator now returns canonical reference, phase, term, subtopic, prerequisites, assessment standards, and alignment confidence.
- Lesson output schema now includes CAPS/trust/safety/quality metadata.
- LLM prompt context redacts email, phone, and SA ID-number patterns before serialization.
- Deterministic `LLM_PROVIDER=mock` added for tests and contract stability.
- Lesson generation now enriches/stores CAPS reference, alignment confidence, quality score, and trust label metadata.
- Diagnostic item schema now includes skill, CAPS reference, explanation, review status, and misconception tag.
- Added migration `20260507_1500` for AI/CAPS/diagnostic safety metadata.
- Added curriculum gap analyzer to detect missing lessons, diagnostic items, and quality-reviewed content.

## Tests

Passed:

```bash
PYTHONPATH=. pytest \
  tests/unit/test_caps_topic_map.py \
  tests/unit/test_ai_safety_contracts.py \
  tests/unit/test_diagnostic_item_safety.py \
  tests/unit/test_curriculum_coverage.py \
  tests/unit/test_caps_alignment.py \
  --no-cov -q
```

Result: `19 passed`.

## Remaining partials

- Full CAPS coverage remains intentionally unclaimed.
- Human review queue UI/storage is still pending.
- Arithmetic-specific independent answer checking should be implemented in a later math-content PR.
- Curriculum dashboard/export UI remains pending.
- Adaptive remediation and teacher insight modes remain future product/learning-science work.
