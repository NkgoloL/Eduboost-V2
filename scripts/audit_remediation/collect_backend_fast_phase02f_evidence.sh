#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-python3}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="docs/release-evidence/technical-audit/backend-fast-phase02f/${STAMP}"
RAW="${OUT}/raw"
mkdir -p "$RAW"

SOURCE_COMMIT="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"

set +e
"$PYTHON_BIN" scripts/audit_remediation/verify_backend_fast_phase02f.py --json > "$RAW/phase02f_verification.json" 2> "$RAW/phase02f_verification.stderr"
VERIFY_STATUS=$?
"$PYTHON_BIN" -m compileall -q \
  app/services/content_staging_seed_executor.py \
  app/models/diagnostic_item.py \
  app/modules/diagnostics/item_bank_service.py \
  app/api_v2_routers/study_plans.py \
  scripts/audit_remediation > "$RAW/compileall.txt" 2>&1
COMPILE_STATUS=$?
"$PYTHON_BIN" -m pytest -q \
  tests/unit/audit_remediation/test_backend_fast_phase02f.py \
  tests/unit/test_content_staging_seed_executor.py \
  tests/unit/test_seed_staging_review_scopes.py \
  tests/unit/modules/diagnostics/test_item_bank_models.py \
  tests/unit/modules/diagnostics/test_item_bank_service.py \
  tests/unit/test_study_plan_consent_gate_wiring.py \
  tests/unit/test_api_v2_router_contract.py \
  --no-cov > "$RAW/focused_tests.txt" 2>&1
TEST_STATUS=$?
set -e

STATUS="Phase 02F verification passed — backend-fast retry pending"
VALID="true"
if [[ "$VERIFY_STATUS" -ne 0 || "$COMPILE_STATUS" -ne 0 || "$TEST_STATUS" -ne 0 ]]; then
  STATUS="Phase 02F verification failed — remediation pending"
  VALID="false"
fi

cat > "$OUT/evidence_index.md" <<EOF
# Technical Audit Phase 02F — Backend Fast Item/Seed/Router Evidence

- Branch: ${BRANCH}
- Source commit: ${SOURCE_COMMIT}
- Status: ${STATUS}
- Valid: ${VALID}
- Authority boundary: this is Phase 02F remediation evidence only; it is not passing backend-fast candidate evidence.
- Backend-fast authority command remains: \`make test-fast\`
- KG boundary: No runtime knowledge-graph implementation added.

## Raw artifacts

- raw/phase02f_verification.json
- raw/phase02f_verification.stderr
- raw/compileall.txt
- raw/focused_tests.txt
EOF

(
  cd "$OUT"
  find raw -type f -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS.txt
  sha256sum evidence_index.md >> SHA256SUMS.txt
)

cat > docs/roadmap/execution/technical_audit_remediation/02f_backend_fast_item_seed_router_status.md <<EOF
# Phase 02F Backend Fast Item/Seed/Router Status

- Evidence path: ${OUT}
- Source commit: ${SOURCE_COMMIT}
- Status: ${STATUS}
- Valid: ${VALID}

This evidence does not close the backend-fast authority gate. Retry \`make test-fast\` through
\`scripts/audit_remediation/collect_backend_fast_evidence.sh\` after this slice is committed.
EOF

if [[ "$VALID" != "true" ]]; then
  echo "Phase 02F evidence failed; inspect ${OUT}" >&2
  exit 1
fi

echo "${OUT}"
