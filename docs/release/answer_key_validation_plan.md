---
title: "Release — Answer-Key Validation Plan"
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
# Answer-Key Validation Plan

Status: workflow defined; pending educator/content approval

## Purpose

Reduce the risk of incorrect answers in CAPS-aligned diagnostic and lesson items before controlled beta.

## Validation Workflow

1. Export candidate items with item ID, grade, subject, CAPS reference, stem, options, answer key, explanation, and source.
2. Run automated schema and safety checks before educator review.
3. Assign each item to an educator/content reviewer.
4. Reviewer marks each answer key as approved, rejected, or needs correction.
5. Corrections require a second review before approval.
6. Approved item count is recorded in the beta product scope and release bundle.

## Required Reviewer Fields

- Reviewer name
- Review date
- Item ID
- Decision
- Correction notes, if any
- CAPS alignment note

## Completion Rule

This plan does not approve content by itself. NS-46 remains external until reviewer records exist.