---
title: "RR-005 Import-Linter Exception Register"
status: active
owner: architecture
audience: developer
source_of_truth: true
evidence_command: "PYTHONPATH=. python3 scripts/technical_debt/audit_rr005_technical_debt.py --json"
---

# RR-005 Import-Linter Exception Register

RR-005 records current `.importlinter` exceptions before further boundary hardening.

## Current exception source

The canonical source is `.importlinter`, especially `ignore_imports` entries under router-to-repository contracts.

## Required burn-down behaviour

- New `ignore_imports` entries require an explicit debt-register justification.
- Existing exceptions should be removed only after repository access moves behind canonical services.
- No exception may silently weaken POPIA, auth, learner-access, or lesson authorization boundaries.

## Evidence

The RR-005 audit script extracts `ignore_imports` entries and stores them in the evidence record.
