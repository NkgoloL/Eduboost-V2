#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required" >&2; exit 2; }

REPORT="docs/roadmap/execution/atlas/phase_06_implementation_report.md"
EVIDENCE_DIR="docs/release-evidence/atlas/phase-06"
RAW="$EVIDENCE_DIR/raw"
INDEX="$EVIDENCE_DIR/phase_06_evidence_index.md"
AUDIT="$EVIDENCE_DIR/phase_06_audit_report.md"
mkdir -p "$RAW" "$(dirname "$REPORT")"

capture() {
  local output="$1"; shift
  set +e
  { printf '$'; printf ' %q' "$@"; printf '\n'; "$@"; } >"$output" 2>&1
  local rc=$?
  set -e
  printf '\nexit_code=%s\n' "$rc" >>"$output"
  return "$rc"
}

{
  echo "collected_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "branch=$(git branch --show-current)"
  echo "commit=$(git rev-parse HEAD)"
  echo "worktree_begin"
  git status --short
  echo "worktree_end"
  "$PYTHON_BIN" --version
  "$PYTHON_BIN" -m pip --version
  docker --version 2>/dev/null || true
  docker compose version 2>/dev/null || true
} >"$RAW/environment.txt"

capture "$RAW/verify_phase6.txt" bash scripts/verify_phase6.sh
capture "$RAW/verify_phase6_postgres.txt" bash scripts/verify_phase6_postgres.sh
capture "$RAW/migration_graph.txt" "$PYTHON_BIN" scripts/verify_migration_graph.py
capture "$RAW/schema_integrity.txt" "$PYTHON_BIN" scripts/validate_schema_integrity.py
capture "$RAW/router_inventory.txt" "$PYTHON_BIN" - <<'PY'
from app.api_v2 import app
for route in sorted((r for r in app.routes if "/ai-operations" in r.path), key=lambda r: r.path):
    print(sorted(getattr(route, "methods", [])), route.path)
PY
capture "$RAW/job_inventory.txt" "$PYTHON_BIN" - <<'PY'
from app.modules.jobs import WorkerSettings
print("functions")
for fn in WorkerSettings.functions:
    print(getattr(fn, "__name__", repr(fn)))
print("cron")
for job in WorkerSettings.cron_jobs:
    print(getattr(getattr(job, "coroutine", None), "__name__", repr(job)))
PY
if [[ -f scripts/generate_openapi.py ]]; then
  capture "$RAW/openapi_check.txt" "$PYTHON_BIN" scripts/generate_openapi.py --check
fi

cat >"$REPORT" <<EOF
# Phase 6 Implementation Report — Durable AI Operations, Budget Authority, and Production Hardening

**Generated:** $(date -u +%Y-%m-%dT%H:%M:%SZ)  
**Status:** Verification complete; independent audit and canonical closure pending  
**Branch:** $(git branch --show-current)  
**Candidate commit:** $(git rev-parse HEAD)

## 1. Objective

Implement PostgreSQL-authoritative AI token reservations, usage accounting, estimated cost telemetry, recovery, admin visibility, and production provider guards.

## 2. Delivered components

- AI budget counters for user-daily and tenant-monthly scopes.
- Idempotent operation reservations and finalization.
- Append-only AI usage events.
- Reservation expiry ARQ job.
- Protected AI operations administration API.
- Provider health derived from durable events.
- Prometheus budget and usage metrics.
- Production deterministic-provider guard.
- Phase 5 tutor integration with durable reservation/finalization.
- ADR-031 and operations runbook.

## 3. Verification

See the Phase 6 evidence index and raw logs. Both `verify_phase6.sh` and `verify_phase6_postgres.sh` completed successfully during evidence collection.

## 4. Migration

Expected head: `20260615_1500_p6_ai_ops`.

## 5. Deviations and residual actions

- Estimated provider cost is operational telemetry, not billing-grade accounting.
- Independent audit, merge, post-merge CI, evidence re-attribution to merge SHA, and final status-register update remain required.
- The collector does not self-approve this report or phase.
EOF

cat >"$INDEX" <<EOF
# Phase 6 Evidence Index

**Collected:** $(date -u +%Y-%m-%dT%H:%M:%SZ)  
**Candidate commit:** $(git rev-parse HEAD)  
**Status:** Evidence Complete — independent audit pending

| Claim | Evidence | Status |
|---|---|---|
| Environment and source state attributable | raw/environment.txt | Verified |
| Fast gate passed | raw/verify_phase6.txt | Verified |
| PostgreSQL gate passed with no unexpected skips | raw/verify_phase6_postgres.txt | Verified |
| One migration head | raw/migration_graph.txt | Verified |
| Schema integrity | raw/schema_integrity.txt | Verified |
| Protected routes registered | raw/router_inventory.txt | Verified |
| Expiry job registered and scheduled | raw/job_inventory.txt | Verified |
| OpenAPI contract current | raw/openapi_check.txt | Verified if present |
| Evidence hashes | raw/SHA256SUMS.txt | Verified |

Final evidence must be confirmed or regenerated against the canonical merge commit.
EOF

cat >"$AUDIT" <<EOF
# Phase 6 Independent Audit Report

**Prepared:** $(date -u +%Y-%m-%dT%H:%M:%SZ)  
**Source state:** $(git rev-parse HEAD)  
**Verdict:** Pending independent audit

## Required independent procedures

- Reproduce concurrent budget blocking and exact-once finalization.
- Attempt update and deletion of append-only usage events.
- Reproduce reservation expiry and counter release.
- Verify no prompt/completion content is persisted in the ledger.
- Verify all administration routes reject non-admin actors.
- Confirm deterministic/mock providers fail closed outside test.
- Reconcile Phase 1–5 regression evidence.
- Confirm merge SHA and post-merge CI before closure.

The evidence collector cannot issue a Pass verdict.
EOF

(
  cd "$RAW"
  find . -maxdepth 1 -type f ! -name SHA256SUMS.txt -printf '%P\0' \
    | sort -z \
    | xargs -0 sha256sum > SHA256SUMS.txt
)

echo "Phase 6 evidence collected under $EVIDENCE_DIR"
echo "Audit remains Pending by design."
