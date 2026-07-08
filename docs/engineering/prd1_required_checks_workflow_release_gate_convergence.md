# PRD-1 CI Release-Gate Convergence — Required Checks and Gate Baseline

This document is the compact engineering reference for the consolidated PRD-1.2-1.4 slice.

## Canonical command rule

Use `python3 -m pytest` for repository-owned workflow and Makefile pytest calls. The older `python -m pytest` form is treated as stale unless a third-party action or historical archive explicitly requires it.

## Required-check baseline

The required-check baseline is recorded in `docs/roadmap/production_readiness/prd1_required_checks_workflow_release_gate_convergence.json`.

Checks are classified as required for `master`, release-candidate blocking, advisory / not yet master-required, or historical evidence-only.

## Release-gate boundary

PRD-1 defines the release gate mechanics. PRD-11 remains the production release/deployment authority. PRD-10 remains the live learner traffic authority. PRD-2 remains the runtime KG implementation authority.
