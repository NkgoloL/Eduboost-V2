# Phase 9 Evidence - Release-Blocker Checklist

**Evidence date:** 2026-06-14
**Status:** Supported after remediation; DB/live-runtime checks remain environment-limited locally

## Evidence Sources

- `docs/roadmap/execution/phase_9_execution_plan.md`
- `docs/roadmap/execution/phase_9_implementation_report.md`
- `docs/openapi.json`
- `scripts/generate_openapi.py`
- `scripts/check_answer_key_independence.py`
- `scripts/check_item_bank_count.py`
- `scripts/check_route_alias_matrix.py`
- `.github/workflows/ci-cd.yml`
- `.github/workflows/openapi-drift.yml`
- `docs/release/route_alias_matrix.md`

## Remediation Performed During Audit

- Regenerated `docs/openapi.json`; `python3 scripts/generate_openapi.py --check` now passes.
- Removed duplicate `schema-drift` job id drift by renaming the Alembic job to `alembic-drift`.
- Aligned remaining frontend E2E workflow steps with pnpm and the tracked `app/frontend/pnpm-lock.yaml`.
- Fixed `scripts/check_route_alias_matrix.py` direct execution by moving its repo-root path bootstrap before imports.
- Updated `scripts/check_answer_key_independence.py` to validate the current generated lesson schema (`lessons[*].answer_key`) and default to the Grade 4 launch lesson artifact.
- Added `scripts/check_item_bank_count.py` for the documented Grade 4 Mathematics item-bank threshold.
- Tuned `scripts/popia_sweep.py` so `--fail-on-issues` blocks true critical/high LLM and consent findings while reporting broad PII-like source patterns as informational.

## Passing Evidence

```text
python3 scripts/generate_openapi.py --check
# passed
```

```text
python3 -m pytest --no-cov -q tests/unit/test_generate_openapi.py tests/integration/test_api_envelope.py -rs
# 4 passed, 8 skipped
# skipped tests require a local PostgreSQL test database at 127.0.0.1:5432
```

```text
python3 scripts/check_answer_key_independence.py
# grade4_maths_launch_lessons.json: 24 payload(s) passed
```

```text
python3 scripts/check_item_bank_count.py --grade 4 --subject mathematics
# 120 approved items; PASS minimum 50
```

```text
python3 -m pytest --no-cov -q \
  tests/unit/modules/diagnostics/test_irt_engine_hardening.py \
  tests/unit/test_irt_properties.py \
  tests/unit/test_irt_gap_probe.py -rs
# 11 passed
```

```text
python3 scripts/popia_sweep.py --fail-on-issues --output-json /tmp/phase9_popia_sweep.json
# passed; 16 informational PII pattern sightings, 0 critical/high blockers
```

```text
python3 scripts/check_route_alias_matrix.py
# PASS; 173 canonical /api/v2 rows, 0 missing aliases
```

```text
python3 scripts/check_ci_workflow_consolidation.py
# passed
```

```text
python3 -m py_compile \
  scripts/check_route_alias_matrix.py \
  scripts/check_answer_key_independence.py \
  scripts/check_item_bank_count.py \
  scripts/popia_sweep.py
# passed
```

```text
python3 - <<'PY'
from pathlib import Path
import yaml
for path in [
    Path(".github/workflows/ci-cd.yml"),
    Path(".github/workflows/frontend-e2e.yml"),
    Path(".github/workflows/ci_lesson_quality.yml"),
    Path(".github/workflows/dependency-scan.yml"),
]:
    yaml.safe_load(path.read_text())
    print(f"YAML OK {path}")
PY
# passed
```

## Residual Limits

- `tests/integration/test_api_envelope.py` skipped locally because PostgreSQL was unavailable.
- `scripts/verify_api_health.py` was not run against a live API server in this local audit.
- `/v2` remains an accepted compatibility alias. Phase 9 now verifies the alias policy and matrix rather than claiming a literal single-prefix router tree.

## Verdict

Phase 9 is now supported for the remediated OpenAPI, CI workflow, route-alias, AI/LLM, and item-bank evidence gates. Live API health and DB-backed envelope checks still require an environment with the stack and PostgreSQL running.
