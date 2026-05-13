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

## Repository Evidence

- `app/domain/item_schema.py`
- `app/modules/diagnostics/production_readiness_contracts.py`
- `app/modules/diagnostics/calibration_service.py`
- `app/modules/diagnostics/item_bank_pipeline.py`
- `app/modules/diagnostics/item_bank_service.py`
- `app/modules/diagnostics/item_validator.py`
- `tests/unit/modules/diagnostics/test_item_bank_models.py`
- `tests/unit/modules/diagnostics/test_item_bank_service.py`
- `tests/unit/modules/diagnostics/test_item_validator.py`

## Launch Boundary

Repository evidence verifies schema, workflow, and guardrail readiness. Actual launch coverage must still be reviewed against the approved seed item bank and curriculum-owner signoff.
