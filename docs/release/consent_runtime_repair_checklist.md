---
title: Consent Runtime Repair Checklist
status: release-record
owner: release-management
reviewers: [release-management, evidence-custodian, documentation-governance]
audience: release-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 180
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/release, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Consent Runtime Repair Checklist

**Status:** pending implementation

## Required implementation slices

| Slice | Description | Evidence |
|---|---|---|
| Consent inventory reviewed | Review `docs/release/consent_callsite_inventory.md` | TODO |
| Constructor compatibility checked | Verify `ConsentService` and `POPIADataRightsService` construction paths | TODO |
| Active consent path selected | Identify canonical `require_active_consent` owner | TODO |
| Audit normalization applied | Use consent audit normalizer where needed | TODO |
| Read/write authz preserved | Preserve explicit learner read/write authorization boundaries | TODO |
| Table semantics documented | Decide `consent_records` vs `parental_consents` roles | TODO |

## Minimum tests

- consent grant/revoke runtime paths do not crash
- active consent check has deterministic allow/deny behavior
- POPIA service construction is deterministic
- consent audit event maps learner/resource ID correctly
