---
title: "Defect Triage and Release Blocker Contract"
status: "active"
owner: "quality"
reviewers: "[quality, engineering, release-management]"
audience: "quality-reviewer"
source_of_truth: "false"
supersedes: "[]"
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: "60"
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[tests, pytest.ini, Makefile]"
---

# Defect Triage and Release Blocker Contract

## Purpose

This contract defines defect severity and release-blocker rules.

## Severity Rules

- low defects require owner
- medium defects require owner
- high defects block release unless waived
- critical defects block release
- release blockers block production
- release blockers allowed for production must be zero
- defects require fix or waiver
- defect SLA is required
- known issues register must be reviewed before beta and production

## Boundary

This contract records defect triage readiness. It does not close defects or approve waivers.
