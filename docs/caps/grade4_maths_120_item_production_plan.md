# Grade 4 Mathematics 120-Item Production Plan

This document records the current launch-slice item-bank state after the runtime launch content deployment on 2026-05-25T08:35:24Z.

## Current State

The Grade 4 Mathematics launch slice is seeded and green in the live runtime.

| CAPS Ref | Topic | Approved Items | Production Target | Status |
|---|---|---:|---:|---|
| 4.M.1.1 | Whole Numbers | 40 | 40 | Complete |
| 4.M.1.2 | Common Fractions | 40 | 40 | Complete |
| 4.M.1.3 | 2D Shapes | 40 | 40 | Complete |
| Total |  | 120 | 120 | Complete |

## Difficulty Distribution

Each launch CAPS ref has the required final distribution.

| CAPS Ref | Easy | Moderate | On-level | Challenging | Total |
|---|---:|---:|---:|---:|---:|
| 4.M.1.1 | 10 | 10 | 10 | 10 | 40 |
| 4.M.1.2 | 10 | 10 | 10 | 10 | 40 |
| 4.M.1.3 | 10 | 10 | 10 | 10 | 40 |

## Runtime Evidence

| Evidence | Value |
|---|---|
| Deployed SHA | 6b68736 |
| Backend deploy | dep-d89vt47r43ps73e3cd20 |
| Frontend deploy | dep-d8a00ur7uimc739v13p0 |
| Diagnostic coverage | 40/40 approved for each launch ref |
| Runtime content evidence | docs/release/runtime_launch_content_evidence_status.md |

## Validation Commands

- python3 scripts/validate_launch_content.py --strict
- python3 scripts/seed_item_bank.py --input data/generated/items/grade4_maths_launch_item_bank.json --status approved --dry-run --abort-on-failure

## Remaining Work

This launch slice is complete. Remaining curriculum work is expansion: full Grade 4 Mathematics, then Grades R-7, plus CI guardrails and a canonical lesson-bank model as tracked in docs/release/runtime_launch_content_evidence_status.md.
