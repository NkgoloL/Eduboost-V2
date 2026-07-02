---
title: "RR-005 Dormant Router Review"
status: active
owner: engineering
audience: developer
source_of_truth: true
evidence_command: "PYTHONPATH=. python3 scripts/technical_debt/audit_rr005_technical_debt.py --json"
---

# RR-005 Dormant Router Review

RR-005 continues the RR-003 dormant-router inventory and records the retirement boundary.

## Retirement boundary

No dormant router is retired in this audit-only slice without call-site proof.

## Current review rule

- Confirm active use before keeping specialist routers.
- Archive only after imports, route registration, tests, and generated OpenAPI references are checked.
- Do not delete route files as part of debt inventory alone.

## Evidence

The audit reads `docs/release/dormant_router_inventory.md`, confirms listed router paths, and records review status.
