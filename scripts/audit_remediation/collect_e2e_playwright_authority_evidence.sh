#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
EVIDENCE_DIR="$ROOT/docs/release-evidence/technical-audit/e2e-playwright-authority"
RAW_DIR="$EVIDENCE_DIR/raw"
rm -rf "$EVIDENCE_DIR"
mkdir -p "$RAW_DIR"

write_sha_manifest() {
  (
    cd "$RAW_DIR"
    find . -maxdepth 1 -type f \
      ! -name 'SHA256SUMS.txt' \
      ! -name 'e2e_playwright_evidence_check.json' \
      -printf '%f\n' | sort | while read -r file; do
        sha256sum "$file"
      done > SHA256SUMS.txt
  )
}

BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
SOURCE_COMMIT="$(git rev-parse HEAD 2>/dev/null || echo unknown)"

set +e
python3 "$ROOT/scripts/audit_remediation/verify_e2e_playwright_authority.py" --json > "$RAW_DIR/e2e_playwright_authority_verification.json" 2> "$RAW_DIR/e2e_playwright_authority_verification.stderr.txt"
VERIFY_RC=$?
python3 "$ROOT/scripts/audit_remediation/run_e2e_playwright_authority.py" --output-dir "$RAW_DIR" --json > "$RAW_DIR/e2e_playwright_authority_runner_stdout.json" 2> "$RAW_DIR/e2e_playwright_authority_runner_stderr.txt"
RUN_RC=$?
set -e

cp "$ROOT/.github/workflows/ci-cd.yml" "$RAW_DIR/ci-cd.yml.snapshot"
cp "$ROOT/.github/workflows/e2e.yml" "$RAW_DIR/e2e.yml.snapshot"
cp "$ROOT/.github/workflows/frontend-e2e.yml" "$RAW_DIR/frontend-e2e.yml.snapshot"
cp "$ROOT/playwright.config.ts" "$RAW_DIR/playwright.config.ts.snapshot"

if [[ "$VERIFY_RC" == "0" && "$RUN_RC" == "0" ]]; then
  STATUS="E2E Playwright execution authority passed — remote hosted CI run not claimed"
else
  STATUS="E2E Playwright execution authority failed — diagnostics preserved"
fi

cat > "$EVIDENCE_DIR/evidence_index.md" <<MD
# Technical Audit — E2E / Playwright Execution Authority Evidence

- Branch: \`$BRANCH\`
- Source commit: \`$SOURCE_COMMIT\`
- Status: $STATUS
- Static authority command: \`python3 scripts/audit_remediation/verify_e2e_playwright_authority.py --json\`
- Execution authority command: \`python3 scripts/audit_remediation/run_e2e_playwright_authority.py --output-dir docs/release-evidence/technical-audit/e2e-playwright-authority/raw --json\`
- Static verifier exit code: \`$VERIFY_RC\`
- Execution runner exit code: \`$RUN_RC\`

## Raw artifacts

- \`raw/e2e_playwright_authority_verification.json\`
- \`raw/e2e_playwright_authority_verification.stderr.txt\`
- \`raw/e2e_playwright_authority_result.json\`
- \`raw/e2e_playwright_authority_runner_stdout.json\`
- \`raw/e2e_playwright_authority_runner_stderr.txt\`
- \`raw/ci-cd.yml.snapshot\`
- \`raw/e2e.yml.snapshot\`
- \`raw/frontend-e2e.yml.snapshot\`
- \`raw/playwright.config.ts.snapshot\`
- \`raw/SHA256SUMS.txt\`

## Boundary

This evidence proves local mocked Playwright/E2E execution authority and workflow ownership. It does not claim remote GitHub Actions success or full backend-backed production E2E readiness.
MD

write_sha_manifest
set +e
python3 "$ROOT/scripts/audit_remediation/verify_e2e_playwright_evidence.py" --evidence-dir "$EVIDENCE_DIR" --json > "$RAW_DIR/e2e_playwright_evidence_check.json"
EVIDENCE_VERIFY_RC=$?
set -e
python3 "$ROOT/scripts/audit_remediation/verify_e2e_playwright_evidence.py" --evidence-dir "$EVIDENCE_DIR" --json
exit "$EVIDENCE_VERIFY_RC"
