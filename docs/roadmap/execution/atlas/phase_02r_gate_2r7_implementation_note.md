# Phase 02R Gate 2R.7 Implementation Note — Grounded Learner Tutor

**Gate:** 2R.7  
**Scope:** Grounded learner tutor service-layer controls  
**Status:** Implementation package asset; not an approval record

## Implemented controls

- Deterministic grounded learner tutor service facade.
- Active-corpus retrieval through the Gate 2R.5 projection contract.
- Tutor request controls for ownership, consent, PII minimisation, safety, rate, and budget preconditions.
- Typed safe non-authoritative fallback when approved grounding is unavailable.
- Fail-closed behavior when fallback is disabled.
- Append-only tutor provenance persistence contract.
- Tutor provenance trace fields required by the Phase 02R plan.
- Audience-specific provenance views for learner, guardian, educator, reviewer, operator, and auditor.
- Gate-specific build, export, validation, verification, PostgreSQL-readiness, evidence collection, and focused tests.

## Explicit non-scope

- No Gate 2R.7 approval manifest is created.
- No Gate 2R.8 transition is created.
- No legacy migration/evaluation closure is wired.
- No learner-facing API route or frontend runtime is wired by this package.
- No live database migration is executed.

## Evidence commands

```bash
bash scripts/preflight_phase02r.sh --gate 2R.7
bash scripts/verify_phase02r.sh --gate 2R.7 --mode implementation
bash scripts/verify_phase02r_gate2r7_postgres.sh
python scripts/curriculum/build_phase02r_gate2r7_grounded_tutor.py --json
python scripts/curriculum/export_phase02r_gate2r7_tutor_packet.py --json
python scripts/curriculum/validate_phase02r_gate2r7_tutor.py --json
python -m pytest -q tests/unit/phase02r/test_gate2r7_grounded_tutor.py --no-cov
```
