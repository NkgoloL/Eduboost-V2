---
title: "Coverage Quality Threshold Contract"
status: active
owner: quality
reviewers: [quality, engineering, release-management]
audience: quality-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-24
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: [tests, pytest.ini, Makefile]
---

# Coverage Quality Threshold Contract

## Purpose

This contract defines coverage thresholds and quality ratchet rules.

## Required Coverage Controls

- minimum line coverage
- minimum branch coverage
- measured path
- coverage ratchet
- waiver policy
- branch coverage reporting
- coverage artifact retention
- coverage regression detection

## Required Threshold Rules

- production line coverage threshold must be at least 70 percent
- unit coverage waiver is not allowed by default
- integration coverage waiver requires release owner approval
- coverage ratchet is required
- coverage report must be retained as release evidence

## Boundary

This contract records coverage quality readiness. It does not claim a current coverage percentage.
