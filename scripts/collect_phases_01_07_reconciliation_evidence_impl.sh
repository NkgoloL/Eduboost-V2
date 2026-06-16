#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
ROOT="$(cd "$ROOT" && pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-$ROOT/.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }

REPORT="docs/roadmap/execution/atlas/phases_01_07_reconciliation_report.md"
EVIDENCE_ROOT="docs/release-evidence/atlas/programme-reconciliation-01-07"
RAW="$EVIDENCE_ROOT/raw"
mkdir -p "$RAW" "$(dirname "$REPORT")"

run_capture() {
  local output="$1"
  shift
  echo "+ $*" | tee "$output"
  set +e
  "$@" 2>&1 | tee -a "$output"
  local rc=${PIPESTATUS[0]}
  set -e
  echo "exit_code=$rc" | tee -a "$output"
  return "$rc"
}

{
  date -u +'%Y-%m-%dT%H:%M:%SZ'
  "$PYTHON_BIN" --version
  "$PYTHON_BIN" -m pip --version || true
  docker --version || true
  docker compose version || true
  if [[ -d .git ]]; then
    git status --short
    git branch --show-current
    git rev-parse HEAD
    git log -n 5 --oneline
  fi
} > "$RAW/environment.txt" 2>&1

run_capture "$RAW/verify_reconciliation_fast.txt" \
  bash scripts/verify_phases_01_07_reconciliation.sh

if [[ "${SKIP_POSTGRES:-0}" == "1" ]]; then
  printf 'SKIPPED_BY_OPERATOR=true\n' > "$RAW/verify_reconciliation_postgres.txt"
  POSTGRES_STATUS="Skipped — not eligible for closure"
else
  run_capture "$RAW/verify_reconciliation_postgres.txt" \
    bash scripts/verify_phases_01_07_reconciliation_postgres.sh
  POSTGRES_STATUS="Passed"
fi

run_capture "$RAW/migration_graph.txt" "$PYTHON_BIN" scripts/verify_migration_graph.py
run_capture "$RAW/schema_integrity.txt" "$PYTHON_BIN" scripts/validate_schema_integrity.py
run_capture "$RAW/control_sets.txt" "$PYTHON_BIN" scripts/validate_phase_control_sets.py

if [[ -f data/retrieval/phase2_closure_evaluation_v2.json ]]; then
  set +e
  "$PYTHON_BIN" scripts/validate_phase2_evaluation_dataset.py \
    data/retrieval/phase2_closure_evaluation_v2.json \
    > "$RAW/phase2_closure_dataset.txt" 2>&1
  DATASET_RC=$?
  set -e
  echo "exit_code=$DATASET_RC" >> "$RAW/phase2_closure_dataset.txt"
else
  printf 'missing=true\n' > "$RAW/phase2_closure_dataset.txt"
  DATASET_RC=1
fi

cat > "$REPORT" <<EOF
# Phases 1–7 Reconciliation Implementation Report

**Generated:** $(date -u +'%Y-%m-%dT%H:%M:%SZ')  
**Status:** Verification and independent closure review required

## Changes applied

- Canonical Atlas paths for all active Phase 1–7 control documents.
- Accurate phase statuses; Phase 8 remains blocked.
- Phase 0 execution plan created as a prerequisite.
- Independent answer-key verification records, API and publication/training gates.
- Phase 2 fail-closed generated-content metadata and vector-error handling.
- Phase 2 two-case dataset demoted to smoke-only; closure dataset diversity gate added.
- Phase 4 expired override exclusion.
- Phase 6 actual-token overage accounting and blocking signal.
- Phase 7 published-only beta coverage and isolated PostgreSQL ports.
- Repository backup directories moved outside the source tree.
- Evidence manifests regenerated and Atlas control-set validator installed.

## Verification

- Fast reconciliation gate: Passed
- PostgreSQL reconciliation gate: $POSTGRES_STATUS
- Migration head: `20260615_2100_p17_reconcile`
- Phase 2 closure dataset validator exit code: $DATASET_RC

## Remaining human-controlled closure work

- Complete and audit Phase 0.
- Populate, approve and pass the Phase 2 closure evaluation dataset.
- Complete Phase 3 compensating governance review.
- Re-run and independently audit each affected phase against the canonical merge commit.
- Record post-merge CI URLs and final evidence hashes.
- Update phase statuses only after passing independent audits.
EOF

cat > "$EVIDENCE_ROOT/evidence_index.md" <<EOF
# Phases 1–7 Reconciliation Evidence Index

**Generated:** $(date -u +'%Y-%m-%dT%H:%M:%SZ')  
**Status:** Evidence collected; independent audit pending

| Evidence | Path | Status |
|---|---|---|
| Environment/source state | `raw/environment.txt` | Collected |
| Fast verification | `raw/verify_reconciliation_fast.txt` | Passed |
| PostgreSQL verification | `raw/verify_reconciliation_postgres.txt` | $POSTGRES_STATUS |
| Migration graph | `raw/migration_graph.txt` | Collected |
| Schema integrity | `raw/schema_integrity.txt` | Collected |
| Atlas control sets | `raw/control_sets.txt` | Collected |
| Phase 2 closure dataset | `raw/phase2_closure_dataset.txt` | $( [[ $DATASET_RC -eq 0 ]] && echo Passed || echo Pending ) |
| File hashes | `raw/SHA256SUMS.txt` | Generated |
EOF

cat > "$EVIDENCE_ROOT/audit_report.md" <<EOF
# Phases 1–7 Reconciliation Independent Audit

**Verdict:** Pending independent audit

The evidence collector cannot self-approve the programme. The auditor must reproduce the critical code, database, evidence-integrity and governance gates against the canonical merge commit. Any Phase 1–7 status change requires phase-specific closure approval after this programme-level review.
EOF

(
  cd "$RAW"
  find . -maxdepth 1 -type f ! -name 'SHA256SUMS.txt' -printf '%f\n' \
    | sort \
    | while read -r name; do sha256sum "$name"; done \
    > SHA256SUMS.txt
)

echo "Reconciliation evidence collected under $EVIDENCE_ROOT"
