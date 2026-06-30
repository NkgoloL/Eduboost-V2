#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
EVIDENCE_DIR="$ROOT/docs/release-evidence/technical-audit/frontend-tooling-phase03a"
RAW_DIR="$EVIDENCE_DIR/raw"
rm -rf "$EVIDENCE_DIR"
mkdir -p "$RAW_DIR"

python3 "$ROOT/scripts/audit_remediation/verify_frontend_tooling_phase03a.py" --json > "$RAW_DIR/phase03a_verification.json"
python3 -m compileall -q "$ROOT/scripts/audit_remediation" > "$RAW_DIR/compileall_stdout.txt" 2> "$RAW_DIR/compileall_stderr.txt"
python3 -m pytest -q "$ROOT/tests/unit/audit_remediation/test_frontend_tooling_phase03a.py" --no-cov > "$RAW_DIR/focused_tests_stdout.txt" 2> "$RAW_DIR/focused_tests_stderr.txt"

(
  cd "$RAW_DIR"
  find . -maxdepth 1 -type f ! -name 'SHA256SUMS.txt' -printf '%f\n' | sort | while read -r file; do
    sha256sum "$file"
  done > SHA256SUMS.txt
)

BRANCH="$(git -C "$ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
SOURCE_COMMIT="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo unknown)"
cat > "$EVIDENCE_DIR/evidence_index.md" <<MD
# Technical Audit — Frontend Tooling Phase 03A Evidence

- Branch: \`$BRANCH\`
- Source commit: \`$SOURCE_COMMIT\`
- Status: Phase 03A verification passed — frontend tooling authority retry pending

## Raw artifacts

- \`raw/phase03a_verification.json\`
- \`raw/compileall_stdout.txt\`
- \`raw/compileall_stderr.txt\`
- \`raw/focused_tests_stdout.txt\`
- \`raw/focused_tests_stderr.txt\`
- \`raw/SHA256SUMS.txt\`

This evidence proves only the Phase 03A repair assets. The frontend/tooling authority gate remains open until \`collect_frontend_tooling_authority_evidence.sh\` verifies valid evidence.
MD

python3 "$ROOT/scripts/audit_remediation/verify_frontend_tooling_phase03a.py" --json
