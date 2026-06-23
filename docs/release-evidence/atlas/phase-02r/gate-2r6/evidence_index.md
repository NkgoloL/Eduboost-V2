# Phase 2R Gate 2R.6 Evidence Index

**Generated:** 2026-06-23T07:08:20Z
**Status:** Candidate verification passed — human approval pending
**Branch:** `feature/atlas-phase-02r-gate-2r1-remediation`
**Source commit:** `b55576dbc06c9cce5a461a481212284ecce75822`
**Gate 2R.7:** blocked
**Environment:** see `raw/environment.txt`

| Evidence ID / claim | Artifact |
|---|---|
| Gate 2R.6 preflight authorised from Gate 2R.5 | `raw/preflight.txt` |
| Gate 2R.6 integrated verifier | `raw/verify_phase02r.txt`, `raw/verify_phase02r_gate2r6.json` |
| Grounded lesson and assessment generation is deterministic and hashable | `raw/grounded_generation_artifact.json`, `raw/generation_packet.json` |
| Claim validation rejects unsupported curriculum claims | `raw/generation_validation.json` |
| Deterministic Grade 4 answer verification is enforced | `raw/generation_validation.json` |
| Generation fails closed without objective/source grounding | `raw/generation_validation.json` |
| Gate boundary excludes Gate 2R.7 tutor runtime wiring | `raw/generation_packet.json` |
| PostgreSQL/Alembic static-readiness disclosed | `raw/verify_phase02r_gate2r6_postgres.txt` |
| Focused Gate 2R.6 tests | `raw/focused_tests.txt` |
| Raw evidence checksums | `raw/SHA256SUMS.txt` |
