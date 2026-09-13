---
title: "POPIA And Data Rights (Readme)"
status: "active"
owner: "compliance"
reviewers: ['compliance', 'legal', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# POPIA And Data Rights

POPIA work covers guardian consent, data export, correction, restriction, erasure, audit preservation, and privacy-safe telemetry.

## Runtime map

- Routes: `app/api_v2_routers/popia.py`, `consent.py`, `consent_renewal.py`
- Services: `app/services/popia_service.py`, `app/services/consent*.py`, `app/services/popia_transactional_lifecycle.py`
- Audit persistence: `app/repositories/audit_repository.py`
- Security evidence: `docs/security/`

## Current implementation notes

- Data-rights routes are implemented, but legal-hold/export prerequisite checks remain an open deep-audit finding.
- Consent lifecycle changes must write audit events in the same transaction boundary where supported.
- No production readiness claim is valid without runtime evidence for export, erasure, correction, and restriction paths.

## Verification

- `make popia-consent-gate-check`
- `make popia-consent-audit-check`
- POPIA tests under `tests/unit/test_popia_*` and `tests/popia/`

Back to the main index: [docs/README.md](../README.md). Root overview: [README.md](../../README.md).
