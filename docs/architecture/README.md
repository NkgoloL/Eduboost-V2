---
title: Architecture Documentation Index
status: active
owner: architecture
reviewers: [backend, frontend, security, operations]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-06-22
review_interval_days: 60
evidence_command: make runtime-check && make openapi-check
code_anchors: [app/api_v2.py, app/frontend/package.json, alembic]
---

# Architecture Documentation

Architecture documents must describe the real EduBoost V2 implementation and must not import stale concepts from unrelated systems.

Canonical architectural claims should be anchored to code paths, OpenAPI generation, migration checks, or ADRs.
