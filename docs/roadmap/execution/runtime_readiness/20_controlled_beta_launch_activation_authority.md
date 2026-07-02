# Phase 20 — Controlled Beta Launch Activation Authority

Status: pending

Phase 20 is the first gate that may authorise a controlled beta launch for a
bounded cohort. It does not authorise production release, public beta, release
tagging, production deployment, or runtime knowledge-graph implementation.

## Required Inputs

- Phase 19 activation preflight verifier is valid.
- `controlled_beta_go_no_go_decision.md` records `Decision: go`.
- `controlled_beta_candidate_cohort_manifest.json` defines a bounded Grade 4
  Mathematics cohort and named operational owners.
- `controlled_beta_consent_pack_attestation.md` confirms guardian consent,
  POPIA notice, data export, and erasure route review.
- `controlled_beta_live_traffic_window.json` defines the activation window,
  owners, rollback owner, monitoring channel, and cohort traffic percentage.

## Boundary

This phase may authorise controlled beta launch, live learner traffic, and
learner data migration only when explicitly claimed by the capture command.
It must keep the following false:

- production release;
- production deployment;
- release tagging;
- public beta; and
- runtime KG implementation.
