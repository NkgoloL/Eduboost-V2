---
title: POPIA Orchestration Boundaries
status: active
owner: architecture
reviewers: [engineering, privacy, security]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-09-03
review_interval_days: 60
evidence_command: make docs-housekeeping-check
code_anchors: [docs/architecture/popia_orchestration_boundaries.md]
---

# POPIA Orchestration Boundaries (TSR-6.4)

## Architecture Overview
POPIA (Protection of Personal Information Act) compliance orchestration is separated into dedicated domain services and state machines:

1. **Consent Management Service:**
   - Handles parent/guardian consent verification, grant, deny, and expiry lifecycles.
   - Database table: `consent_records`.
2. **Data Subject Rights (DSR) Orchestration:**
   - **Export:** `data_export_requests` (JSON payload format, SLA tracking).
   - **Correction:** `correction_requests` (Field-level updates).
   - **Erasure:** `erasure_requests` (State machine tracking legal hold, soft deletion, and anonymization).
   - **Restriction:** `restriction_requests` (Processing restrictions).
3. **Audit Immutability Boundary:**
   - Every POPIA action dispatches to `audit_events` with SHA-256 HMAC chained signatures.
   - Enforced by PostgreSQL row-level triggers and rules (`trg_audit_events_immutable`).
