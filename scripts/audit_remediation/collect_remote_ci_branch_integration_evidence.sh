#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EVIDENCE_DIR="$ROOT/docs/release-evidence/technical-audit/remote-ci-branch-integration"
RAW_DIR="$EVIDENCE_DIR/raw"
PYTHON_BIN="${PYTHON_BIN:-python3}"
REMOTE_CI_STATUS_JSON="${REMOTE_CI_STATUS_JSON:-}"

rm -rf "$RAW_DIR"
mkdir -p "$RAW_DIR"
cat > "$EVIDENCE_DIR/evidence_index.md" <<'MD'
# TA Phase 08 — Remote CI / Branch Integration Authority Evidence

- Status: collection in progress
MD

run_json() {
  local output="$1"
  shift
  "$@" > "$RAW_DIR/$output"
}

run_json remote_ci_branch_integration_verification.json \
  "$PYTHON_BIN" "$ROOT/scripts/audit_remediation/verify_remote_ci_branch_integration_authority.py" --json

run_json backend_fast_gate_evidence_check.json \
  "$PYTHON_BIN" "$ROOT/scripts/audit_remediation/verify_backend_fast_evidence.py" \
    --evidence-dir "$ROOT/docs/release-evidence/technical-audit/backend-fast-gate" --json

run_json frontend_tooling_authority_evidence_check.json \
  "$PYTHON_BIN" "$ROOT/scripts/audit_remediation/verify_frontend_tooling_evidence.py" \
    --evidence-dir "$ROOT/docs/release-evidence/technical-audit/frontend-tooling-authority" --json

run_json ci_authority_workflow_evidence_check.json \
  "$PYTHON_BIN" "$ROOT/scripts/audit_remediation/verify_ci_authority_workflow_evidence.py" \
    --evidence-dir "$ROOT/docs/release-evidence/technical-audit/ci-authority-workflow" --json

run_json dependency_scan_enforcement_evidence_check.json \
  "$PYTHON_BIN" "$ROOT/scripts/audit_remediation/verify_dependency_scan_evidence.py" \
    --evidence-dir "$ROOT/docs/release-evidence/technical-audit/dependency-scan-enforcement" --json

run_json e2e_playwright_authority_evidence_check.json \
  "$PYTHON_BIN" "$ROOT/scripts/audit_remediation/verify_e2e_playwright_evidence.py" \
    --evidence-dir "$ROOT/docs/release-evidence/technical-audit/e2e-playwright-authority" --json

run_json openapi_frontend_contract_evidence_check.json \
  "$PYTHON_BIN" "$ROOT/scripts/audit_remediation/verify_openapi_frontend_contract_evidence.py" \
    --evidence-dir "$ROOT/docs/release-evidence/technical-audit/openapi-frontend-contract" --json

"$PYTHON_BIN" - <<'PY' > "$RAW_DIR/git_state.json"
import json
import subprocess
from pathlib import Path
root = Path.cwd()

def git(*args):
    proc = subprocess.run(["git", *args], cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return {"returncode": proc.returncode, "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()}

status = git("status", "--short")
evidence_prefix = "docs/release-evidence/technical-audit/remote-ci-branch-integration/"
status_lines = [line for line in status["stdout"].splitlines() if line.strip()] if status["returncode"] == 0 else []
non_evidence_status_lines = [
    line for line in status_lines
    if evidence_prefix not in line and not line.endswith("docs/release-evidence/technical-audit/remote-ci-branch-integration")
]
branch = git("rev-parse", "--abbrev-ref", "HEAD")
head = git("rev-parse", "HEAD")
head_short = git("rev-parse", "--short=10", "HEAD")
upstream = git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
merge_base_main = git("merge-base", "HEAD", "origin/main")
merge_base_master = git("merge-base", "HEAD", "origin/master")
print(json.dumps({
    "branch": branch["stdout"] if branch["returncode"] == 0 else None,
    "head": head["stdout"] if head["returncode"] == 0 else None,
    "head_short": head_short["stdout"] if head_short["returncode"] == 0 else None,
    "upstream": upstream["stdout"] if upstream["returncode"] == 0 else None,
    "working_tree_clean": status["returncode"] == 0 and not non_evidence_status_lines,
    "status_short": status["stdout"],
    "non_evidence_status_short": "\n".join(non_evidence_status_lines),
    "evidence_path_ignored_for_cleanliness": evidence_prefix,
    "merge_base_origin_main": merge_base_main["stdout"] if merge_base_main["returncode"] == 0 else None,
    "merge_base_origin_master": merge_base_master["stdout"] if merge_base_master["returncode"] == 0 else None,
}, indent=2, sort_keys=True))
PY

if [[ -n "$REMOTE_CI_STATUS_JSON" ]]; then
  cp "$REMOTE_CI_STATUS_JSON" "$RAW_DIR/remote_ci_status.json"
else
  cat > "$RAW_DIR/remote_ci_status.json" <<'JSON'
{
  "remote_ci_run_claimed": false,
  "conclusion": null,
  "head_sha": null,
  "workflow": null,
  "note": "No hosted GitHub Actions run is claimed by this Phase 08 static branch-integration evidence bundle."
}
JSON
fi

"$PYTHON_BIN" - <<'PY' > "$RAW_DIR/workflow_inventory.json"
import json
from pathlib import Path
root = Path.cwd()
items = []
for path in sorted((root / ".github/workflows").glob("*.yml")) + sorted((root / ".github/workflows").glob("*.yaml")):
    text = path.read_text(encoding="utf-8")
    items.append({
        "path": str(path.relative_to(root)),
        "uses_upload_artifact_v4": "actions/upload-artifact@v4" in text,
        "uses_unsupported_upload_artifact": "actions/upload-artifact@v7" in text,
        "uses_npm_ci": "npm ci" in text,
        "uses_pnpm": "pnpm" in text,
    })
print(json.dumps({"workflow_count": len(items), "workflows": items}, indent=2, sort_keys=True))
PY

"$PYTHON_BIN" - <<'PY' > "$RAW_DIR/branch_integration_summary.json"
import json
from pathlib import Path
raw = Path("docs/release-evidence/technical-audit/remote-ci-branch-integration/raw")
checks = {}
for name in [
    "remote_ci_branch_integration_verification",
    "backend_fast_gate_evidence_check",
    "frontend_tooling_authority_evidence_check",
    "ci_authority_workflow_evidence_check",
    "dependency_scan_enforcement_evidence_check",
    "e2e_playwright_authority_evidence_check",
    "openapi_frontend_contract_evidence_check",
]:
    data = json.loads((raw / f"{name}.json").read_text(encoding="utf-8"))
    checks[name] = bool(data.get("valid"))
remote = json.loads((raw / "remote_ci_status.json").read_text(encoding="utf-8"))
git_state = json.loads((raw / "git_state.json").read_text(encoding="utf-8"))
valid = all(checks.values()) and git_state.get("working_tree_clean") is True
print(json.dumps({
    "branch_integration_authority_result": "valid" if valid else "invalid",
    "valid": valid,
    "checks": checks,
    "remote_ci_run_claimed": remote.get("remote_ci_run_claimed"),
    "remote_ci_conclusion": remote.get("conclusion"),
    "source_commit": git_state.get("head_short"),
    "release_readiness_claimed": False,
    "runtime_kg_implementation_claimed": False,
}, indent=2, sort_keys=True))
PY

(
  cd "$RAW_DIR"
  find . -type f \
    ! -name 'SHA256SUMS.txt' \
    ! -name 'remote_ci_branch_integration_evidence_check.json' \
    -printf '%P\0' | sort -z | xargs -0 sha256sum > SHA256SUMS.txt
)

"$PYTHON_BIN" "$ROOT/scripts/audit_remediation/verify_remote_ci_branch_integration_evidence.py" \
  --evidence-dir "$EVIDENCE_DIR" --json > "$RAW_DIR/remote_ci_branch_integration_evidence_check.json"

STATUS=$("$PYTHON_BIN" - <<'PY'
import json
from pathlib import Path
check = json.loads(Path("docs/release-evidence/technical-audit/remote-ci-branch-integration/raw/remote_ci_branch_integration_evidence_check.json").read_text(encoding="utf-8"))
summary = json.loads(Path("docs/release-evidence/technical-audit/remote-ci-branch-integration/raw/branch_integration_summary.json").read_text(encoding="utf-8"))
remote = json.loads(Path("docs/release-evidence/technical-audit/remote-ci-branch-integration/raw/remote_ci_status.json").read_text(encoding="utf-8"))
if check.get("valid"):
    if remote.get("remote_ci_run_claimed"):
        print("Remote CI branch integration authority passed — hosted CI success claimed from supplied status artifact")
    else:
        print("Remote CI branch integration authority passed — hosted CI success not claimed")
else:
    print("Remote CI branch integration authority failed — inspect raw evidence")
PY
)
SOURCE_COMMIT=$("$PYTHON_BIN" - <<'PY'
import json
from pathlib import Path
print(json.loads(Path("docs/release-evidence/technical-audit/remote-ci-branch-integration/raw/git_state.json").read_text()).get("head_short"))
PY
)
EVIDENCE_CHECK_VALID=$("$PYTHON_BIN" - <<'PY'
import json
from pathlib import Path
print(json.loads(Path("docs/release-evidence/technical-audit/remote-ci-branch-integration/raw/remote_ci_branch_integration_evidence_check.json").read_text()).get("valid"))
PY
)

cat > "$EVIDENCE_DIR/evidence_index.md" <<MD
# TA Phase 08 — Remote CI / Branch Integration Authority Evidence

- Status: ${STATUS}
- Source commit: ${SOURCE_COMMIT}
- Evidence verifier valid: ${EVIDENCE_CHECK_VALID}
- Remote hosted CI run claimed: $("$PYTHON_BIN" - <<'PY'
import json
from pathlib import Path
print(json.loads(Path("docs/release-evidence/technical-audit/remote-ci-branch-integration/raw/remote_ci_status.json").read_text()).get("remote_ci_run_claimed"))
PY
)
- Release readiness claimed: false
- Runtime KG implementation claimed: false

## Raw evidence

- raw/remote_ci_branch_integration_verification.json
- raw/backend_fast_gate_evidence_check.json
- raw/frontend_tooling_authority_evidence_check.json
- raw/ci_authority_workflow_evidence_check.json
- raw/dependency_scan_enforcement_evidence_check.json
- raw/e2e_playwright_authority_evidence_check.json
- raw/openapi_frontend_contract_evidence_check.json
- raw/git_state.json
- raw/workflow_inventory.json
- raw/remote_ci_status.json
- raw/branch_integration_summary.json
- raw/SHA256SUMS.txt
- raw/remote_ci_branch_integration_evidence_check.json
MD

if [[ "$EVIDENCE_CHECK_VALID" != "True" && "$EVIDENCE_CHECK_VALID" != "true" ]]; then
  echo "Phase 08 evidence verifier failed; see $RAW_DIR/remote_ci_branch_integration_evidence_check.json" >&2
  exit 1
fi

echo "Collected Phase 08 evidence at $EVIDENCE_DIR"
