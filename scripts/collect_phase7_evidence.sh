#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }

REPORT_DIR="docs/roadmap/execution/atlas"
EVIDENCE_DIR="docs/release-evidence/atlas/phase-07"
RAW="$EVIDENCE_DIR/raw"
mkdir -p "$REPORT_DIR" "$RAW"

capture() {
  local output="$1"; shift
  set +e
  "$@" >"$output" 2>&1
  local status=$?
  set -e
  cat "$output"
  printf '\nexit_code=%s\n' "$status" >>"$output"
  return "$status"
}

{
  echo "captured_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "branch=$(git branch --show-current)"
  echo "commit_sha=$(git rev-parse HEAD)"
  echo "worktree_status_begin"
  git status --short
  echo "worktree_status_end"
  echo "python_bin=$PYTHON_BIN"
  "$PYTHON_BIN" --version
  "$PYTHON_BIN" -m pip --version
  docker --version 2>/dev/null || true
  docker compose version 2>/dev/null || true
} >"$RAW/environment.txt"

capture "$RAW/verify_phase7.txt" bash scripts/verify_phase7.sh
capture "$RAW/verify_phase7_postgres.txt" bash scripts/verify_phase7_postgres.sh
capture "$RAW/migration_graph.txt" "$PYTHON_BIN" scripts/verify_migration_graph.py
capture "$RAW/schema_integrity.txt" "$PYTHON_BIN" scripts/validate_schema_integrity.py
capture "$RAW/registry_preflight.txt" env PYTHONPATH=. "$PYTHON_BIN" scripts/check_phase7_registry.py --json

capture "$RAW/router_inventory.txt" env PYTHONPATH=. "$PYTHON_BIN" - <<'PY'
from app.api_v2 import ROUTER_REGISTRY
router = dict(ROUTER_REGISTRY)["curriculum_expansion"]
for route in sorted(router.routes, key=lambda value: value.path):
    print(f"{','.join(sorted(route.methods or []))} {route.path}")
PY

capture "$RAW/job_inventory.txt" env PYTHONPATH=. "$PYTHON_BIN" - <<'PY'
from app.jobs.curriculum_expansion_job import capture_weekly_curriculum_coverage
from app.modules.jobs import WorkerSettings
print(f"function_registered={capture_weekly_curriculum_coverage in WorkerSettings.functions}")
for job in WorkerSettings.cron_jobs:
    if (
        getattr(job, "coroutine", None) is capture_weekly_curriculum_coverage
        or getattr(job, "name", "") == "capture_weekly_curriculum_coverage"
    ):
        print(f"cron={job!r}")
PY

if [[ -f scripts/generate_openapi.py ]]; then
  capture "$RAW/openapi_check.txt" "$PYTHON_BIN" scripts/generate_openapi.py --check
fi

cat >"$REPORT_DIR/phase_07_implementation_report.md" <<EOF
# Phase 7 Implementation Report — Curriculum Coverage Expansion, Multilingual Quality, and Training Dataset Governance

**Generated:** $(date -u +%Y-%m-%dT%H:%M:%SZ)  
**Status:** Verification complete — independent audit and canonical merge closure pending  
**Branch:** $(git branch --show-current)  
**Candidate commit:** $(git rev-parse HEAD)  
**Execution plan:** \`docs/roadmap/execution/atlas/phase_07_execution_plan.md\`

## 1. Objective

Implement deterministic curriculum coverage snapshots and gap planning, plus a governed, reproducible training dataset pipeline that exports only eligible published content.

## 2. Delivered implementation

- Durable curriculum coverage snapshots.
- Dry-run-only curriculum expansion plans.
- Protected curriculum expansion and training-manifest API.
- Published-content training eligibility gates.
- Source licence, provenance, safety, quality, CAPS alignment, answer-key, PII, and language checks.
- Immutable training dataset entries and approved manifests.
- Deterministic per-record and dataset SHA-256 identities.
- Safe artifact-root-constrained JSONL export.
- Approved-manifest training-readiness dry run.
- Weekly ARQ snapshot job.
- Prometheus metrics, ADR-032, and operations runbook.
- Source-controlled Content Factory registry files required by clean checkouts.
- Migration \`20260615_1800_p7_curriculum\`.

## 3. Verification

See the raw evidence directory:

\`docs/release-evidence/atlas/phase-07/raw/\`

Required evidence includes the fast verifier, PostgreSQL verifier, migration graph, schema integrity, registry preflight, route inventory, job inventory, and OpenAPI check.

## 4. Deviations and boundaries

- Expansion plans do not execute generation or publication.
- Machine language checks do not constitute human language sign-off.
- CI performs training-readiness dry runs only.
- Actual adapter training, evaluation, and deployment require separate controlled decisions.
- This report does not mark the phase complete or issue an audit verdict.

## 5. Remaining closure actions

1. Review all raw evidence and investigate any warning, retry, skip, or non-zero exit.
2. Complete qualified curriculum and language review.
3. Conduct the independent Phase 7 audit.
4. Merge through the canonical pull-request process.
5. Repeat or confirm required gates against the merge commit.
6. Freeze evidence against the merge SHA.
7. Update the phase status register last.
EOF

cat >"$EVIDENCE_DIR/phase_07_evidence_index.md" <<EOF
# Phase 7 Evidence Index

**Generated:** $(date -u +%Y-%m-%dT%H:%M:%SZ)  
**Candidate commit:** $(git rev-parse HEAD)  
**Status:** Collected — audit review pending

| Evidence | Path | Claim |
|---|---|---|
| Environment | \`raw/environment.txt\` | Exact branch, commit, Python, worktree, and tool identity |
| Fast verification | \`raw/verify_phase7.txt\` | Focused implementation, registration, registry, OpenAPI, and prior-phase fast gates |
| PostgreSQL verification | \`raw/verify_phase7_postgres.txt\` | Migration, triggers, eligibility, immutability, and prior-phase DB gates |
| Migration graph | \`raw/migration_graph.txt\` | Single Phase 7 migration head |
| Schema integrity | \`raw/schema_integrity.txt\` | ORM/schema integrity |
| Registry preflight | \`raw/registry_preflight.txt\` | Clean-checkout scope and target registry availability |
| Router inventory | \`raw/router_inventory.txt\` | Protected Phase 7 API surface |
| Job inventory | \`raw/job_inventory.txt\` | Weekly coverage job registration |
| OpenAPI | \`raw/openapi_check.txt\` | Contract drift gate |
| Hash manifest | \`raw/SHA256SUMS.txt\` | Evidence-file integrity |

## Completion declaration

This evidence collection is not an audit verdict. Final evidence must be re-attributed to the canonical merge commit before Phase 7 can be marked complete.
EOF

cat >"$EVIDENCE_DIR/phase_07_audit_report.md" <<EOF
# Phase 7 Independent Audit Report

**Generated:** $(date -u +%Y-%m-%dT%H:%M:%SZ)  
**Source state:** $(git rev-parse HEAD)  
**Verdict:** Pending independent audit

## Required audit procedures

- Confirm the approved execution plan predates substantive implementation.
- Reproduce registry preflight from a clean checkout.
- Reproduce published-only eligibility and all exclusion reasons.
- Attempt to export quarantined, pending-review, unsafe, low-quality, ungrounded, and disallowed-licence artifacts.
- Reproduce dataset hashes.
- Attempt to mutate approved manifests and entries.
- Review multilingual evidence and human sign-offs.
- Confirm training readiness rejects non-approved manifests.
- Confirm Phase 1–6 regressions.
- Confirm merge SHA and post-merge CI.

Any unresolved Critical or High finding requires a Fail verdict.
EOF

(
  cd "$RAW"
  find . -maxdepth 1 -type f ! -name SHA256SUMS.txt -print0 \
    | sort -z \
    | xargs -0 sha256sum > SHA256SUMS.txt
)

echo "PHASE 7 EVIDENCE COLLECTED"
echo "report=$REPORT_DIR/phase_07_implementation_report.md"
echo "evidence=$EVIDENCE_DIR/phase_07_evidence_index.md"
echo "audit=$EVIDENCE_DIR/phase_07_audit_report.md"
