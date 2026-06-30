# Item Bank Launch Coverage Contract

## Purpose

This contract defines production-readiness expectations for the minimum viable diagnostic item bank and review workflow.

## Required Item Bank Capabilities

- minimum viable item bank for each supported launch grade
- minimum viable item bank for each supported launch subject
- item review status `draft`
- item review status `AI-generated`
- item review status `human-reviewed`
- item review status `approved`
- item review status `retired`
- item calibration workflow
- item exposure limits
- item reuse policy
- item retirement workflow
- item import/export tooling
- distractor quality review
- explanation quality review
- misconception tagging

## Current Launch Evidence

As of 2026-05-25T08:35:24Z, the Grade 4 Mathematics launch slice has runtime coverage evidence:

| CAPS Ref | Approved Items | Expected Items | Coverage Ratio |
|---|---:|---:|---:|
| 4.M.1.1 | 40 | 40 | 1.0 |
| 4.M.1.2 | 40 | 40 | 1.0 |
| 4.M.1.3 | 40 | 40 | 1.0 |

Evidence artifact: docs/release/runtime_launch_content_evidence_status.md.

## Repository Evidence

- app/domain/item_schema.py
- app/models/diagnostic_item.py
- app/modules/diagnostics/item_bank_service.py
- app/modules/diagnostics/item_validator.py
- app/repositories/item_bank_repository.py
- scripts/seed_item_bank.py
- data/generated/items/grade4_maths_launch_item_bank.json
- tests/unit/modules/diagnostics/test_item_validator.py
- tests/unit/test_launch_content_factory.py

## Launch Boundary

The launch boundary is green for 4.M.1.1, 4.M.1.2, 4.M.1.3. Expansion beyond that scope still requires generated artifacts, validation, seeding, and coverage evidence.
