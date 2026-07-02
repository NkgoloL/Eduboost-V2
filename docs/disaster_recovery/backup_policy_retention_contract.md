---
title: "Backup Policy and Retention Contract"
status: active
owner: operations
reviewers: [operations, security, privacy]
audience: operator
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-24
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: [docs/disaster_recovery, scripts]
---

# Backup Policy and Retention Contract

## Purpose

This contract defines backup frequency, retention, encryption, and ownership expectations.

## Required Backup Policy Fields

- backup scope
- backup frequency
- retention days
- recovery tier
- point-in-time recovery flag
- encryption flag
- integrity check requirement
- owner

## Required Retention Rules

- database backups require point-in-time recovery
- critical backups must be hourly or daily
- audit log backups require long retention
- backups must be encrypted
- backups must have integrity checks
- backup owners must be named
- retention expiry must be after backup creation
- retention policy must respect privacy and legal-hold boundaries

## Boundary

This contract records backup policy readiness. It does not configure retention in a live storage provider.
