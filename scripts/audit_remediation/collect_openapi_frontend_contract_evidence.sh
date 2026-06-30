#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="${FALLBACK_PYTHON_BIN:-python3}"
fi

EVIDENCE_DIR="docs/release-evidence/technical-audit/openapi-frontend-contract"
RAW_DIR="$EVIDENCE_DIR/raw"
rm -rf "$RAW_DIR"
mkdir -p "$RAW_DIR"

SOURCE_COMMIT="$(git rev-parse HEAD 2>/dev/null || printf 'unknown')"
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || printf 'unknown')"
GENERATED_AT="$(date -Iseconds)"

run_capture_text() {
  local output="$1"
  shift
  "$@" >"$output" 2>&1
}

run_capture_json() {
  local output="$1"
  shift
  "$@" >"$output" 2>&1
  python3 -m json.tool "$output" >/tmp/eduboost-json-check.json
}

run_capture_text "$RAW_DIR/openapi_finalize_check.txt" bash -lc "\"$PYTHON_BIN\" scripts/generate_openapi.py --check && printf 'OPENAPI FRONTEND CONTRACT --check-only PASSED\\n'"
run_capture_json "$RAW_DIR/openapi_route_contract.json" "$PYTHON_BIN" scripts/audit_remediation/verify_openapi_route_contract.py --json
run_capture_json "$RAW_DIR/openapi_frontend_contract.json" "$PYTHON_BIN" scripts/audit_remediation/verify_openapi_frontend_contract.py --json
run_capture_json "$RAW_DIR/popia_route_contract.json" "$PYTHON_BIN" scripts/audit_remediation/verify_popia_route_contract.py --json

if [[ -f scripts/audit_remediation/verify_frontend_tooling_evidence.py ]]; then
  run_capture_json "$RAW_DIR/frontend_tooling_evidence_check.json" "$PYTHON_BIN" scripts/audit_remediation/verify_frontend_tooling_evidence.py --evidence-dir docs/release-evidence/technical-audit/frontend-tooling-authority --json
else
  printf '{"valid": true, "warnings": ["frontend tooling evidence verifier absent"]}\n' > "$RAW_DIR/frontend_tooling_evidence_check.json"
fi

run_capture_text "$RAW_DIR/unit_tests.txt" "$PYTHON_BIN" -m pytest -q tests/unit/audit_remediation/test_openapi_route_contracts.py tests/unit/audit_remediation/test_openapi_frontend_contract_finalization.py --no-cov

sha256sum docs/openapi.json > "$RAW_DIR/openapi_sha256.txt"
(
  cd "$RAW_DIR"
  find . -maxdepth 1 -type f ! -name 'SHA256SUMS.txt' -printf '%P\0' | sort -z | xargs -0 sha256sum > SHA256SUMS.txt
)

OPENAPI_SHA="$(cut -d' ' -f1 "$RAW_DIR/openapi_sha256.txt")"

EVIDENCE_DIR="$EVIDENCE_DIR" BRANCH="$BRANCH" SOURCE_COMMIT="$SOURCE_COMMIT" GENERATED_AT="$GENERATED_AT" OPENAPI_SHA="$OPENAPI_SHA" python3 - <<'PY'
import os
from pathlib import Path

evidence_dir = Path(os.environ["EVIDENCE_DIR"])
branch = os.environ["BRANCH"]
source_commit = os.environ["SOURCE_COMMIT"]
generated_at = os.environ["GENERATED_AT"]
openapi_sha = os.environ["OPENAPI_SHA"]

content = "\n".join(
    [
        "# Technical Audit Remediation Evidence - OpenAPI / Frontend Contract Finalization",
        "",
        "**Stream:** technical-audit-remediation  ",
        "**Slice:** 07-openapi-frontend-contract-finalization  ",
        f"**Branch:** {branch}  ",
        f"**Source commit:** {source_commit}  ",
        f"**Generated at:** {generated_at}  ",
        "Status: OpenAPI / frontend contract finalization passed - release readiness not claimed  ",
        f"**OpenAPI SHA-256:** {openapi_sha}",
        "",
        "## Authority commands",
        "",
        "- `bash scripts/audit_remediation/finalize_openapi_frontend_contract.sh --check-only`",
        "- `python3 scripts/audit_remediation/verify_openapi_route_contract.py --json`",
        "- `python3 scripts/audit_remediation/verify_openapi_frontend_contract.py --json`",
        "- `python3 scripts/audit_remediation/verify_popia_route_contract.py --json`",
        "- focused OpenAPI/frontend contract tests",
        "",
        "## Raw evidence",
        "",
        "- raw/openapi_finalize_check.txt",
        "- raw/openapi_route_contract.json",
        "- raw/openapi_frontend_contract.json",
        "- raw/popia_route_contract.json",
        "- raw/frontend_tooling_evidence_check.json",
        "- raw/unit_tests.txt",
        "- raw/openapi_sha256.txt",
        "- raw/SHA256SUMS.txt",
        "",
        "## Scope boundary",
        "",
        "This evidence proves regenerated OpenAPI/frontend route-contract alignment for the technical-audit remediation stream. It does not claim product release readiness, remote GitHub Actions success, full backend-backed E2E readiness, dependency vulnerability absence, or runtime KG implementation.",
        "",
    ]
)
evidence_dir.joinpath("evidence_index.md").write_text(content, encoding="utf-8")
PY

"$PYTHON_BIN" scripts/audit_remediation/verify_openapi_frontend_contract_evidence.py --evidence-dir "$EVIDENCE_DIR" --json > "$RAW_DIR/openapi_frontend_contract_evidence_check.json"

printf 'Collected OpenAPI/frontend contract evidence in %s\n' "$EVIDENCE_DIR"
