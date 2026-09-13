---
title: "POPIA Legal Evidence (Popia Legal Evidence)"
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
# POPIA Legal Evidence

This index links POPIA data-rights, retention, subprocessor, audit, and legal
document evidence. Legal review remains required before public beta.

- POPIA overview: `docs/POPIA_COMPLIANCE.md`
- Data rights: `docs/compliance/popia_data_rights.md`
- Retention: `docs/compliance/data_retention_policy.md`
- Subprocessors: `docs/compliance/subprocessor_register.md`
- Legal index: `docs/legal/legal_documents_index.md`
- Policy versioning: `docs/legal/policy_versioning.md`
- Audit baseline: `docs/security/POPIA_CONSENT_AUDIT_BASELINE.md`

Run:

```bash
make popia-legal-check
```

Verification gaps: external legal review, signed policy approval, and staging
evidence are still required.
