---
title: "RR-007 Playwright CI Gate"
status: active
owner: engineering
audience: developer
source_of_truth: false
last_reviewed: 2026-07-02
review_interval_days: 60
---


# RR-007 Playwright CI Gate

Playwright CI gate recorded: true

## Required expectation

Backend-backed and seeded E2E evidence must remain connected to CI-visible checks. The canonical Playwright workflow is `.github/workflows/e2e.yml`; RR-007 adds a quality-gate workflow that verifies the product quality gate anchors stay present.

## Boundary

This document records CI visibility and policy. It does not claim that every browser/device journey is complete.
