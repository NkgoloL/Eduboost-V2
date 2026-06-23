# Phase 02R Gate 2R.6 Implementation Note

**Gate:** 2R.6 — Grounded lesson and assessment generation
**Status:** Implementation assets only; evidence and approval remain separate.

## Implemented scope

This package adds deterministic, service-layer controls for grounded lesson and
assessment generation:

- active approved corpus retrieval is required before generation;
- generated lessons and assessments carry source references, source snapshot
  hashes, corpus version, binding epoch, and mapping provenance;
- curriculum and assessment claims are validated before an artifact can be
  marked `grounded_verified`;
- Grade 4 Mathematics assessment answers are checked by a deterministic-first
  verifier;
- generation fails closed when objective/source grounding is missing;
- explicit safe fallback is allowed only as a non-grounded fallback artifact;
- generation packet exports are stable and hashable for evidence.

## Explicit non-scope

This package does not:

- create a Gate 2R.6 approval manifest;
- authorise Gate 2R.7;
- wire learner-facing endpoints;
- change tutor runtime behavior;
- execute a live database migration;
- mark Phase 02R complete.

## Evidence commands

After the implementation commit is clean, collect evidence with:

```bash
bash scripts/collect_phase02r_evidence.sh --gate 2R.6
```

The evidence commit, approval commit, and 2R.6 to 2R.7 transition commit must
remain separate.
