# Grade 4 Mathematics - CAPS Item Bank Coverage Matrix

Last updated: 2026-05-25T08:35:24Z
Evidence: docs/release/runtime_launch_content_evidence_status.md

## Summary

| Metric | Value |
|---|---:|
| Launch grade | 4 |
| Launch subject | Mathematics |
| Launch scope | 4.M.1.1, 4.M.1.2, 4.M.1.3 |
| Target items per launch ref | 40 approved |
| Current approved items per launch ref | 40 approved |
| Total approved launch items | 120 |
| Outstanding launch items | 0 |
| Current status | Green for launch slice |

## Coverage By CAPS Reference

| CAPS Ref | Topic | Term | Approved | Draft | AI-Generated Pending Review | Retired | Status |
|---|---|---:|---:|---:|---:|---:|---|
| 4.M.1.1 | Whole Numbers | 1 | 40 | 0 | 0 | 0 | Ready |
| 4.M.1.2 | Common Fractions | 1 | 40 | 0 | 0 | 0 | Ready |
| 4.M.1.3 | 2D Shapes | 1 | 40 | 0 | 0 | 0 | Ready |

## Difficulty Distribution

| CAPS Ref | Easy | Moderate | On-level | Challenging | Total |
|---|---:|---:|---:|---:|---:|
| 4.M.1.1 | 10 | 10 | 10 | 10 | 40 |
| 4.M.1.2 | 10 | 10 | 10 | 10 | 40 |
| 4.M.1.3 | 10 | 10 | 10 | 10 | 40 |

## Definition Of Done Checklist

- [x] validate_launch_content.py --strict reports launch content status ok.
- [x] 40 approved diagnostic items for 4.M.1.1.
- [x] 40 approved diagnostic items for 4.M.1.2.
- [x] 40 approved diagnostic items for 4.M.1.3.
- [x] Runtime diagnostics coverage API returns coverage_ratio = 1.0 for all three launch refs.
- [x] Runtime release evidence records deployed SHA and Render deploy IDs.
- [ ] Add CI guardrail that fails if generated item artifacts contain fields the ORM cannot persist.
- [ ] Add browser journey evidence proving learners can consume the seeded diagnostic flow end to end.

## Boundary

This matrix is green for the Grade 4 Mathematics launch slice only. It is not a claim of full Grade 4 Mathematics or Grades R-7 CAPS coverage.
