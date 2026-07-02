---
title: "Frontend Accessibility Static Scan"
status: "active"
owner: "frontend"
reviewers: "[frontend, product, privacy]"
audience: "developer"
source_of_truth: "false"
supersedes: "[]"
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: "60"
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[app/frontend, docs/frontend/README.md]"
---

# Frontend Accessibility Static Scan

## Purpose

The static scan provides a dependency-free accessibility guard for frontend
source files before browser-level accessibility tests are introduced.

## Static Checks

- image tags include alt attributes
- empty buttons do not appear without accessible names
- interactive files include accessible-name evidence
- scan avoids generated build output and dependencies

## Current Boundary

This is a source-level guard. It does not replace browser-level axe checks,
keyboard traversal checks, or screen-reader validation.

## Command

```bash
make frontend-accessibility-static-check
```
