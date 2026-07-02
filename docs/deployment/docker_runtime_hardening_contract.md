---
title: "Docker Runtime Hardening Contract"
status: active
owner: release-management
reviewers: [release-management, operations, security]
audience: operator
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-24
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: [Dockerfile, docker-compose.yml, docker-compose.prod.yml, .github/workflows]
---

# Docker Runtime Hardening Contract

## Purpose

This contract defines Docker image and runtime hardening expectations.

## Required Docker Controls

- pinned base image
- multi-stage build
- non-root user
- container healthcheck
- dependency lockfile
- vulnerability scan
- SBOM generation
- minimal runtime image
- no development secrets in image
- no test credentials in image
- explicit runtime command
- runtime role separation

## Required Image Roles

- API image
- worker image
- frontend image
- migration image
- scheduler image where applicable

## Boundary

This contract records Docker hardening readiness. It does not build, scan, publish, or deploy images.
