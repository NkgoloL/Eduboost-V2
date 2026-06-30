---
title: "Metaphor → Domain Name Glossary"
status: active
owner: architecture
reviewers: [architecture, engineering]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/architecture/README.md]
---

# Metaphor → Domain Name Glossary

Early design documents for EduBoost used a political/civic metaphor to name
architectural layers. This glossary maps those legacy metaphor names to the
canonical domain names used in all V2 engineering code.

**Metaphor language must not appear in engineering code, ADRs, API contracts,
service names, or onboarding docs for new engineers. It may be retained in
product/storytelling documents under `docs/product/` only.**

---

## Name Mapping

| Legacy metaphor name | Canonical domain name | Notes |
|---|---|---|
| `executive` | `auth` | JWT issuance, refresh, revocation, RBAC |
| `judiciary` | `popia` | Data subject rights, erasure, access requests |
| `fourth_estate` | `observability` | Prometheus metrics, structured logging, alerting |
| `ether` | `core` | Shared kernel — config, middleware, DB pool, exceptions |

---

## Detection & Rename

Run the following to find remaining metaphor references in active code:

```bash
python scripts/rename_metaphor_layers.py
```

To apply the rename automatically:

```bash
python scripts/rename_metaphor_layers.py --apply
```

After running, review the diff and confirm no product-facing copy was
inadvertently changed.
