#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
EVIDENCE_DIR="docs/release-evidence/technical-audit/backend-fast-phase02i/${STAMP}"
RAW_DIR="${EVIDENCE_DIR}/raw"
mkdir -p "$RAW_DIR"

SOURCE_COMMIT="$(git rev-parse HEAD 2>/dev/null || printf 'unknown')"
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || printf 'unknown')"

python3 scripts/audit_remediation/verify_backend_fast_phase02i.py --json > "$RAW_DIR/phase02i_verification.json"
python3 scripts/audit_remediation/verify_backend_fast_phase02i.py --json --static-only > "$RAW_DIR/phase02i_static_verification.json"
python3 -m pytest -q tests/unit/test_topic_map_worklist.py tests/unit/audit_remediation/test_backend_fast_phase02i.py --no-cov > "$RAW_DIR/focused_tests.txt"
python3 -m compileall -q scripts/curriculum/build_topic_map_worklist.py scripts/audit_remediation > "$RAW_DIR/compileall.txt" 2>&1

VERIFIER_SHA="$(sha256sum "$RAW_DIR/phase02i_verification.json" | awk '{print $1}')"
FOCUSED_SHA="$(sha256sum "$RAW_DIR/focused_tests.txt" | awk '{print $1}')"

cat > "$EVIDENCE_DIR/evidence_index.md" <<EOF
# Backend Fast Phase 02I Evidence

Branch: \\`${BRANCH}\\`  
Source commit: \\`${SOURCE_COMMIT}\\`  
Collected at: \\`${STAMP}\\`  
Status: Phase 02I topic-map provenance verification passed — backend-fast retry pending

This evidence proves the focused Phase 02I remediation contract only. It does **not** create passing backend-fast gate evidence. Passing backend-fast evidence still requires \\`make test-fast\\` to exit 0 via \\`scripts/audit_remediation/collect_backend_fast_evidence.sh\\`.

## Raw evidence

- \\`raw/phase02i_verification.json\\` — SHA256 \\`${VERIFIER_SHA}\\`
- \\`raw/focused_tests.txt\\` — SHA256 \\`${FOCUSED_SHA}\\`
- \\`raw/phase02i_static_verification.json\\`
- \\`raw/compileall.txt\\`

## Boundary

- No backend-fast passing evidence is created here.
- No Phase 02R governance is changed.
- No product release-readiness claim is made.
- No live DB migration is executed.
- No runtime KG implementation is added.
EOF

(
  cd "$EVIDENCE_DIR"
  find raw -type f -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS.txt
)

printf 'Phase 02I evidence collected at %s\n' "$EVIDENCE_DIR"
