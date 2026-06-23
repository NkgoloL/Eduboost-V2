# Phase 2R Gate 2R.7 Evidence Index

**Generated:** 2026-06-23T14:40:30Z
**Status:** Candidate verification passed — human approval pending
**Source commit:** `e67c32e20f9ef24c6b74d7b38ba815cca8d7da00`
**Environment:** see `raw/environment.txt`

| Evidence ID / claim | Artifact |
|---|---|
| Gate 2R.7 preflight authorised from Gate 2R.6 | `raw/preflight.txt` |
| Gate 2R.7 integrated verifier | `raw/verify_phase02r.txt`, `raw/verify_phase02r_gate2r7.json` |
| Grounded learner tutor response is deterministic and hashable | `raw/grounded_tutor_response.json`, `raw/tutor_packet.json` |
| Tutor retrieves from active approved corpus hierarchy | `raw/grounded_tutor_response.json`, `raw/tutor_validation.json` |
| Safe fallback emits no authoritative CAPS claim | `raw/tutor_validation.json` |
| Tutor provenance is persisted append-only | `raw/tutor_packet.json`, `raw/tutor_validation.json` |
| Audience-specific provenance views are access-shaped | `raw/tutor_packet.json`, `raw/tutor_validation.json` |
| Ownership, consent, safety, rate, budget controls are enforced at service contract level | `raw/tutor_validation.json` |
| Gate boundary excludes Gate 2R.8 migration/evaluation closure | `raw/tutor_packet.json` |
| PostgreSQL/Alembic static-readiness disclosed | `raw/verify_phase02r_gate2r7_postgres.txt` |
| Focused Gate 2R.7 tests | `raw/focused_tests.txt` |
| Raw evidence checksums | `raw/SHA256SUMS.txt` |
