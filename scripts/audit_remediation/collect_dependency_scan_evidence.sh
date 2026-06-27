#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
EVIDENCE_DIR="$ROOT/docs/release-evidence/technical-audit/dependency-scan-enforcement"
RAW_DIR="$EVIDENCE_DIR/raw"
rm -rf "$EVIDENCE_DIR"
mkdir -p "$RAW_DIR"
write_sha_manifest() {
  (
    cd "$RAW_DIR"
    find . -maxdepth 1 -type f \
      ! -name 'SHA256SUMS.txt' \
      ! -name 'dependency_scan_evidence_check.json' \
      -printf '%f\n' | sort | while read -r file; do
        sha256sum "$file"
      done > SHA256SUMS.txt
  )
}
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
SOURCE_COMMIT="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
set +e
python3 "$ROOT/scripts/audit_remediation/verify_dependency_scan_enforcement.py" --json > "$RAW_DIR/dependency_scan_enforcement_verification.json" 2> "$RAW_DIR/dependency_scan_enforcement_verification.stderr.txt"
VERIFY_RC=$?
set -e
cp "$ROOT/.github/workflows/dependency-scan.yml" "$RAW_DIR/dependency-scan.yml.snapshot"
if [[ "$VERIFY_RC" == "0" ]]; then
  STATUS="Dependency scan enforcement passed — remote hosted scan run not claimed"
else
  STATUS="Dependency scan enforcement failed — diagnostics preserved"
fi
cat > "$EVIDENCE_DIR/evidence_index.md" <<MD
# Technical Audit — Dependency Scan Enforcement Evidence

- Branch: \`$BRANCH\`
- Source commit: \`$SOURCE_COMMIT\`
- Status: $STATUS
- Authority command: \`python3 scripts/audit_remediation/verify_dependency_scan_enforcement.py --json\`
- Verifier exit code: \`$VERIFY_RC\`

## Raw artifacts

- \`raw/dependency_scan_enforcement_verification.json\`
- \`raw/dependency_scan_enforcement_verification.stderr.txt\`
- \`raw/dependency-scan.yml.snapshot\`
- \`raw/SHA256SUMS.txt\`

## Boundary

This evidence proves the dependency-scan workflow enforcement contract only. It does not claim that remote GitHub Actions dependency scans have run successfully.
MD
write_sha_manifest
set +e
python3 "$ROOT/scripts/audit_remediation/verify_dependency_scan_evidence.py" --evidence-dir "$EVIDENCE_DIR" --json > "$RAW_DIR/dependency_scan_evidence_check.json"
EVIDENCE_VERIFY_RC=$?
set -e
python3 "$ROOT/scripts/audit_remediation/verify_dependency_scan_evidence.py" --evidence-dir "$EVIDENCE_DIR" --json
exit "$EVIDENCE_VERIFY_RC"
