---
title: "ADR-004: POPIA Data Rights Service Authority"
status: active
owner: architecture
reviewers: [engineering, architecture]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 180
evidence_command: make docs-housekeeping-stage3-check
code_anchors: []
---
# ADR-004: POPIA Data Rights Service Authority

**Status**: Accepted
**Date**: 2026-05-28
**Context**: T111C erasure workflow implementation identified duplicate erasure execution paths

## Context

During T111C (POPIA erasure workflow implementation), two erasure execution paths were identified:

1. `app/services/popia_service.py::POPIADataRightsService.execute_erasure` - FastAPI v2 integrated service
2. `app/services/data_subject_rights_service.py::DataSubjectRightsService.execute_erasure` - Legacy/alternative service

This duplication presents a maintainability risk where future developers could inadvertently call the wrong service, leading to inconsistent behavior, missing audit trails, or bypassing safety checks.

## Decision

**POPIADataRightsService is the authoritative service for FastAPI v2 POPIA lifecycle operations.**

All new POPIA-related endpoints and services must route through `POPIADataRightsService` in `app/services/popia_service.py`.

### Authoritative Service

- **Location**: `app/services/popia_service.py::POPIADataRightsService`
- **Purpose**: Canonical POPIA data rights implementation for FastAPI v2
- **Features**:
  - State machine-based erasure workflow (requested, verified, scheduled, cancelled, executed, failed)
  - Preflight safety checks (authorization, legal hold, grace period, export offered)
  - Postflight verification (PII not retrievable, audit preserved)
  - Support for soft, physical, and purge execution methods
  - Full audit trail integration
  - Consent versioning integration

### Legacy Service

- **Location**: `app/services/data_subject_rights_service.py::DataSubjectRightsService`
- **Status**: Legacy/alternative implementation
- **Characteristics**:
  - Uses asyncpg directly (not SQLAlchemy models)
  - Different domain models
  - Not integrated with FastAPI v2 routers
  - Not integrated with the new ErasureRequest state machine
  - Must not be used for new v2 flows

## Consequences

### Positive

- Single source of truth for POPIA operations
- Consistent audit trail across all POPIA operations
- Safety checks enforced uniformly
- Easier to maintain and test

### Negative

- Legacy service remains in codebase until deprecation
- Potential confusion if developers encounter both services

### Follow-up Actions

**T111D: Deprecate or reconcile legacy DataSubjectRightsService erasure path**

Priority: P1

Acceptance Criteria:
- Only one authoritative erasure service is available to v2 routes
- Legacy service has explicit deprecation guard/docs/tests
- Or legacy service is removed entirely

Options for resolution:
1. Add deprecation warnings to `DataSubjectRightsService.execute_erasure`
2. Add unit tests that verify no v2 routes call the legacy service
3. Remove `DataSubjectRightsService` entirely if not used
4. Wrap legacy service to delegate to authoritative service

## References

- T111C: POPIA erasure workflow implementation
- T110C: POPIA export payload completeness
- T112B: POPIA consent versioning
- T113: Guardian consent withdrawal
- `docs/popia_erasure_cascade_matrix.md` - Erasure cascade specification
