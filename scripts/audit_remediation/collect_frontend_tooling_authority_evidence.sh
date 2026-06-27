#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
EVIDENCE_DIR="$ROOT/docs/release-evidence/technical-audit/frontend-tooling-authority"
RAW_DIR="$EVIDENCE_DIR/raw"

rm -rf "$EVIDENCE_DIR"
mkdir -p "$RAW_DIR"

set +e
python3 "$ROOT/scripts/audit_remediation/run_frontend_tooling_authority.py" \
  --output-dir "$RAW_DIR" \
  --json > "$RAW_DIR/frontend_tooling_runner_stdout.json" 2> "$RAW_DIR/frontend_tooling_runner_stderr.txt"
RUNNER_RC=$?
set -e

(
  cd "$RAW_DIR"
  find . -maxdepth 1 -type f ! -name 'SHA256SUMS.txt' -printf '%f\n' | sort | while read -r file; do
    sha256sum "$file"
  done > SHA256SUMS.txt
)

RESULT_JSON="$RAW_DIR/frontend_tooling_authority_result.json"
VALID="false"
SOURCE_COMMIT="unknown"
BRANCH="unknown"
if [[ -f "$RESULT_JSON" ]]; then
  VALID="$(python3 - <<PY
import json
from pathlib import Path
p = Path('$RESULT_JSON')
try:
    data = json.loads(p.read_text())
    print('true' if data.get('valid') is True else 'false')
except Exception:
    print('false')
PY
)"
  SOURCE_COMMIT="$(python3 - <<PY
import json
from pathlib import Path
try:
    print(json.loads(Path('$RESULT_JSON').read_text()).get('source_commit') or 'unknown')
except Exception:
    print('unknown')
PY
)"
  BRANCH="$(python3 - <<PY
import json
from pathlib import Path
try:
    print(json.loads(Path('$RESULT_JSON').read_text()).get('branch') or 'unknown')
except Exception:
    print('unknown')
PY
)"
fi

if [[ "$VALID" == "true" ]]; then
  STATUS="Frontend tooling authority passed"
else
  STATUS="Frontend tooling authority failed — diagnostics preserved"
fi

cat > "$EVIDENCE_DIR/evidence_index.md" <<MD
# Technical Audit — Frontend Tooling Authority Evidence

- Branch: \\`$BRANCH\\`
- Source commit: \\`$SOURCE_COMMIT\\`
- Status: $STATUS
- Authority command: \\`python3 scripts/audit_remediation/run_frontend_tooling_authority.py --output-dir docs/release-evidence/technical-audit/frontend-tooling-authority/raw --json\\`
- Runner exit code: \\`$RUNNER_RC\\`

## Raw artifacts

- \\`raw/frontend_tooling_authority_result.json\\`
- \\`raw/frontend_tooling_runner_stdout.json\\`
- \\`raw/frontend_tooling_runner_stderr.txt\\`
- \\`raw/SHA256SUMS.txt\\`

Passing evidence is accepted only when \\`verify_frontend_tooling_evidence.py\\` returns \\`valid: true\\`.
MD

set +e
python3 "$ROOT/scripts/audit_remediation/verify_frontend_tooling_evidence.py" \
  --evidence-dir "$EVIDENCE_DIR" \
  --json > "$RAW_DIR/frontend_tooling_evidence_check.json"
VERIFY_RC=$?
set -e

# Recompute hashes after writing the verifier result.
(
  cd "$RAW_DIR"
  find . -maxdepth 1 -type f ! -name 'SHA256SUMS.txt' -printf '%f\n' | sort | while read -r file; do
    sha256sum "$file"
  done > SHA256SUMS.txt
)

# Run verifier one final time against the stabilized bundle.
python3 "$ROOT/scripts/audit_remediation/verify_frontend_tooling_evidence.py" \
  --evidence-dir "$EVIDENCE_DIR" \
  --json > "$RAW_DIR/frontend_tooling_evidence_check.json"

(
  cd "$RAW_DIR"
  find . -maxdepth 1 -type f ! -name 'SHA256SUMS.txt' -printf '%f\n' | sort | while read -r file; do
    sha256sum "$file"
  done > SHA256SUMS.txt
)

python3 "$ROOT/scripts/audit_remediation/verify_frontend_tooling_evidence.py" \
  --evidence-dir "$EVIDENCE_DIR" \
  --json
