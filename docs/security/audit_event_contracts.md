---
title: "Audit Event Contracts"
status: archived
owner: security
reviewers: [security, engineering, privacy]
audience: security-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: '2026-09-23'
review_interval_days: null
evidence_command: null
code_anchors: [docs/security/README.md, app/security]
archived_at: '2026-09-23'
---
# Audit Event Contracts
> [!NOTE]
> **Status: ARCHIVED — 2026-09-23**
> Historical milestone evidence, review audit, or point-in-time record; retained for audit lineage.



## Purpose

`scripts/check_audit_event_contracts.py` verifies that the POPIA and security
audit baseline still exposes the required audit markers.

## Required Coverage

- `FourthEstateService.record`
- consent grant/revoke audit events
- consent renewal audit event
- consent erasure-request audit event
- consent access-rejected audit event
- V2 consent router delegation to `ConsentService`

## Verification

```bash
make audit-contract-check
pytest -c pytest.ini tests/unit/test_audit_event_contracts.py -q --no-cov
```
