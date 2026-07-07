# PRD-0.3 — Documentation Housekeeping Ratchet Refresh

**Stream:** PRD-PRODUCTION-READINESS  
**Status:** Authority added; evidence capture required before closure  
**Previous required item:** PRD-0.2 — Historical report and stale-source quarantine  
**Next authorised item after closure:** PRD-0.4 — Test/dependency bootstrap baseline

## Purpose

PRD-0.3 refreshes the documentation housekeeping ratchet after the RR closure, KG closure, KG activation, and PRD-0.0 through PRD-0.2 current-state cleanup work.

This slice makes the committed documentation inventory, findings CSV, and housekeeping ratchet baseline a fresh post-closure baseline before PRD-0 moves into test/dependency and workflow stabilisation.

## Scope

PRD-0.3 records and verifies:

- deterministic documentation inventory regeneration;
- documentation findings CSV regeneration;
- housekeeping ratchet baseline refresh from the regenerated inventory;
- documentation housekeeping ratchet check passing against the refreshed baseline;
- evidence snapshots for the refreshed inventory summary and baseline;
- continued PRD boundary protection.

## Out of scope

PRD-0.3 does **not** fix every documentation finding. It refreshes the ratchet so future slices can prevent regression from a current, reproducible baseline.

It does **not** authorise production release, deployment, public beta, live learner traffic, billing, new KG work, or PRD-1 implementation.

## Required evidence artifacts

Evidence capture must produce:

- `docs/generated/documentation_inventory.json`
- `docs/generated/documentation_inventory.csv`
- `docs/generated/documentation_findings.csv`
- `docs/documentation/housekeeping_ratchet_baseline.json`
- `docs/roadmap/production_readiness/prd_003_documentation_housekeeping_ratchet_refresh_record.json`
- `docs/release-evidence/production-readiness/prd-003-documentation-housekeeping-ratchet-refresh/`

## Boundary

The controlled runtime KG authority state remains true/executed:

```text
runtime_kg_implementation_claimed: true
runtime_kg_authority_switch_authorised: true
authority_switch_executed: true
```

The following remain false:

```text
production_release_authorised: false
deployment_authorised: false
release_tag_authorised: false
public_beta_authorised: false
public_beta_live_traffic_authorised: false
live_learner_traffic_authorised: false
billing_launch_authorised: false
live_payment_processing_authorised: false
new_kg_slice_authorised: false
prd1_implementation_authorised: false
```
