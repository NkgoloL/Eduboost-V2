#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
EVIDENCE_DIR="$ROOT/docs/release-evidence/technical-audit/ci-authority-workflow"
RAW_DIR="$EVIDENCE_DIR/raw"

rm -rf "$EVIDENCE_DIR"
mkdir -p "$RAW_DIR"

write_sha_manifest() {
  (
    cd "$RAW_DIR"
    find . -maxdepth 1 -type f \
      ! -name 'SHA256SUMS.txt' \
      ! -name 'ci_authority_workflow_evidence_check.json' \
      -printf '%f\n' | sort | while read -r file; do
        sha256sum "$file"
      done > SHA256SUMS.txt
  )
}

BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
SOURCE_COMMIT="$(git rev-parse HEAD 2>/dev/null || echo unknown)"

set +e
python3 "$ROOT/scripts/audit_remediation/verify_ci_authority_workflow.py" --json > "$RAW_DIR/ci_authority_workflow_verification.json" 2> "$RAW_DIR/ci_authority_workflow_verification.stderr.txt"
VERIFY_RC=$?
set -e

cp "$ROOT/.github/workflows/ci-cd.yml" "$RAW_DIR/ci-cd.yml.snapshot"

if [[ "$VERIFY_RC" == "0" ]]; then
  STATUS="CI authority workflow cleanup passed — remote CI run not claimed"
else
  STATUS="CI authority workflow cleanup failed — diagnostics preserved"
fi

cat > "$EVIDENCE_DIR/evidence_index.md" <<MD
# Technical Audit — CI Authority Workflow Cleanup Evidence

- Branch: 0$BRANCH0
- Source commit: 0$SOURCE_COMMIT0
- Status: $STATUS
- Authority command: 0python3 scripts/audit_remediation/verify_ci_authority_workflow.py --json0
- Verifier exit code: 0$VERIFY_RC0

## Raw artifacts

- 0raw/ci_authority_workflow_verification.json0
- 0raw/ci_authority_workflow_verification.stderr.txt0
- 0raw/ci-cd.yml.snapshot0
- 0raw/SHA256SUMS.txt0

## Boundary

This evidence proves the workflow configuration contract only. It does not claim that remote GitHub Actions has run successfully.
MD
# Replace unicode placeholder with backticks safely.
python3 - <<'PY' "$EVIDENCE_DIR/evidence_index.md"
from pathlib import Path
import sys
p=Path(sys.argv[1])
p.write_text(p.read_text(encoding='utf-8').replace('\u00030','`'), encoding='utf-8')
PY

write_sha_manifest

set +e
python3 "$ROOT/scripts/audit_remediation/verify_ci_authority_workflow_evidence.py" \
  --evidence-dir "$EVIDENCE_DIR" \
  --json > "$RAW_DIR/ci_authority_workflow_evidence_check.json"
EVIDENCE_VERIFY_RC=$?
set -e

python3 "$ROOT/scripts/audit_remediation/verify_ci_authority_workflow_evidence.py" \
  --evidence-dir "$EVIDENCE_DIR" \
  --json

exit "$EVIDENCE_VERIFY_RC"
