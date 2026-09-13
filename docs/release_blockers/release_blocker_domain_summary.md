---
title: "Release Blockers — Release Blocker Domain Summary"
status: "active"
owner: "release"
reviewers: ['release', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Release Blocker Domain Summary

## Required Domains

- repository
- backend API
- architecture
- authorization
- POPIA consent
- database
- AI safety
- frontend UX
- billing
- notifications
- observability
- deployment
- backup DR
- testing quality
- security
- operations support
- documentation
- beta launch
- roadmap
- external manual

## Required Rules

- domain checklist path must live under docs/
- domain check command is required
- domain summary owner is required
- required release evidence must be complete
- external/manual domain requires manual dependency

## Boundary

This summary records domain coverage. It does not execute checks automatically.
