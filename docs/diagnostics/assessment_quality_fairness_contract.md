# Assessment Quality and Fairness Contract

## Purpose

This contract records quality, fairness, and bias-review expectations for diagnostic and assessment items.

## Required Fairness Dimensions

- item bias review across language
- item bias review across region
- item bias review across socioeconomic context
- distractor quality review
- explanation quality review
- misconception tagging
- educator sign-off process

## Required Quality Controls

- item schema validation
- item review workflow validation
- calibration workflow evidence
- item exposure limit evidence
- item reuse policy evidence
- item retirement workflow evidence
- minimum viable launch coverage evidence
- human review boundary for psychometric and curriculum fairness

## Repository Evidence

- `app/modules/diagnostics/bias_review_router.py`
- `app/modules/diagnostics/item_validator.py`
- `app/modules/diagnostics/quality_scorer.py`
- `app/modules/diagnostics/production_readiness_contracts.py`
- `tests/unit/modules/diagnostics/test_item_validator.py`

## Human Review Boundary

Automated checks can verify required metadata, states, and routing. They cannot replace educator review, psychometric review, or fairness signoff for live learner use.
