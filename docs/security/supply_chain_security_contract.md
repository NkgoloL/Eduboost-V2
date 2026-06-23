---
title: "Supply Chain Security Contract"
status: active
owner: security
reviewers: [security, engineering, privacy]
audience: security-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/security/README.md, app/security]
---

# Supply Chain Security Contract

## Purpose

This contract defines supply-chain security controls.

## Required Supply-Chain Controls

- dependency lockfile is required
- SBOM is required
- artifact provenance is required
- dependency review is required
- license review is required
- signed artifact or digest pinning is required
- container image vulnerability scan is required
- transitive dependency risk is reviewed
- release artifact checksum is retained

## Boundary

This contract records supply-chain readiness. It does not sign artifacts or run dependency scanners.
