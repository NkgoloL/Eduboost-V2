#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="$ROOT/docs/release-evidence/technical-audit/backend-fast-runtime-dependencies/$STAMP"
RAW_DIR="$OUT_DIR/raw"
mkdir -p "$RAW_DIR"

cd "$ROOT"
SOURCE_COMMIT="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"

AUTHORITY_PYTHON="${BACKEND_FAST_PYTHON:-}"
if [[ -z "$AUTHORITY_PYTHON" ]]; then
  AUTHORITY_PYTHON="$(python3 - <<'PY'
from pathlib import Path
root = Path.cwd()
makefile = root / 'Makefile'
value = '.venv/bin/python'
if makefile.exists():
    for line in makefile.read_text(encoding='utf-8').splitlines():
        if line.startswith('PYTEST ?='):
            rhs = line.split('?=', 1)[1].strip()
            if rhs:
                value = rhs.split()[0]
            break
path = Path(value)
print(str((root / path).resolve() if not path.is_absolute() else path))
PY
)"
fi

set +e
"$AUTHORITY_PYTHON" scripts/audit_remediation/verify_backend_fast_runtime_dependencies.py --json --output "$RAW_DIR/runtime_dependency_verification.json" > "$RAW_DIR/runtime_dependency_verification.stdout" 2>&1
VERIFY_RC=$?
python3 scripts/audit_remediation/verify_backend_fast_environment.py --json --python-bin "$AUTHORITY_PYTHON" > "$RAW_DIR/backend_fast_environment.json" 2>&1
ENV_RC=$?
python3 -m compileall -q scripts/audit_remediation > "$RAW_DIR/compileall.txt" 2>&1
COMPILE_RC=$?
set -e

python3 - <<PY
import json
from pathlib import Path
payload = {
  "source_commit": "${SOURCE_COMMIT}",
  "branch": "${BRANCH}",
  "authority_python": "${AUTHORITY_PYTHON}",
  "runtime_dependency_verification_rc": ${VERIFY_RC},
  "backend_fast_environment_rc": ${ENV_RC},
  "compileall_rc": ${COMPILE_RC},
  "valid": ${VERIFY_RC} == 0 and ${ENV_RC} == 0 and ${COMPILE_RC} == 0,
}
Path("$RAW_DIR/result.json").write_text(json.dumps(payload, indent=2) + "\n")
PY

(
  cd "$RAW_DIR"
  find . -maxdepth 1 -type f -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS.txt
)

VALID="$(python3 - <<PY
import json
from pathlib import Path
print(str(json.loads(Path('$RAW_DIR/result.json').read_text())['valid']).lower())
PY
)"
STATUS="Runtime dependency verification passed — backend-fast retry pending"
if [[ "$VALID" != "true" ]]; then
  STATUS="Runtime dependency verification failed — remediation pending"
fi
GENERATED_AT="$(date -Iseconds)"

cat > "$OUT_DIR/evidence_index.md" <<EOF2
# Technical Audit Remediation Evidence — Backend Fast Runtime Dependencies

**Stream:** technical-audit-remediation  
**Slice:** 02b-backend-fast-runtime-dependencies  
**Branch:** ${BRANCH}  
**Source commit:** ${SOURCE_COMMIT}  
**Generated at:** ${GENERATED_AT}  
**Status:** ${STATUS}  
**Authority command remains:** make test-fast  
**Authority Python:** ${AUTHORITY_PYTHON}

## Raw evidence

- raw/runtime_dependency_verification.json
- raw/runtime_dependency_verification.stdout
- raw/backend_fast_environment.json
- raw/compileall.txt
- raw/result.json
- raw/SHA256SUMS.txt

## Boundary

This evidence only proves that the backend-fast authority Python runtime dependencies are present. It is not backend-fast candidate evidence. Passing backend-fast evidence remains blocked until \`make test-fast\` exits 0 from a clean implementation commit.

No runtime knowledge-graph work is included in this slice.
EOF2

sha256sum "$OUT_DIR/evidence_index.md" > "$OUT_DIR/evidence_index.sha256"

cat > "$ROOT/docs/roadmap/execution/technical_audit_remediation/02b_backend_fast_runtime_dependencies.md.tmp" <<EOF2
# Technical Audit Remediation Phase 02B — Backend Fast Runtime Dependencies

**Status:** evidence collected  
**Evidence directory:** docs/release-evidence/technical-audit/backend-fast-runtime-dependencies/${STAMP}  
**Evidence status:** ${STATUS}  
**Source commit:** ${SOURCE_COMMIT}  
**Authority Python:** ${AUTHORITY_PYTHON}

This slice does not create passing backend-fast evidence. It only creates runtime-dependency evidence.

Backend-fast candidate evidence is still blocked until the full authority command exits 0:

\`\`\`bash
make test-fast
\`\`\`

No runtime knowledge-graph work is included. KG remains a future architectural north star, and this slice only preserves audit-remediation discipline.
EOF2
mv "$ROOT/docs/roadmap/execution/technical_audit_remediation/02b_backend_fast_runtime_dependencies.md.tmp" "$ROOT/docs/roadmap/execution/technical_audit_remediation/02b_backend_fast_runtime_dependencies.md"

if [[ "$VALID" != "true" ]]; then
  echo "Runtime dependency evidence is non-passing; see $OUT_DIR" >&2
  exit 2
fi

echo "Runtime dependency evidence collected at $OUT_DIR"
