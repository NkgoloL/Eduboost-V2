#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

EVIDENCE_DIR="docs/release-evidence/technical-audit/hosted-ci-merge-readiness"
RAW_DIR="$EVIDENCE_DIR/raw"
PYTHON_BIN="${PYTHON_BIN:-python3}"
REMOTE_CI_STATUS_JSON="${REMOTE_CI_STATUS_JSON:-}"

rm -rf "$EVIDENCE_DIR"
mkdir -p "$RAW_DIR"

run_json() {
  local name="$1"
  shift
  set +e
  "$@" > "$RAW_DIR/${name}.json" 2> "$RAW_DIR/${name}.stderr.txt"
  local rc=$?
  set -e
  "$PYTHON_BIN" - "$RAW_DIR/${name}.result.json" "$rc" "$*" <<'PY'
from __future__ import annotations
import json, sys
out, rc, cmd = sys.argv[1], int(sys.argv[2]), " ".join(sys.argv[3:])
with open(out, "w", encoding="utf-8") as fh:
    json.dump({"command": cmd, "returncode": rc}, fh, indent=2, sort_keys=True)
    fh.write("\n")
PY
  return 0
}

HEAD_SHA="$(git rev-parse HEAD)"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
STATUS_BEFORE="$(git status --short --untracked-files=all)"
FILTERED_STATUS="$(printf '%s\n' "$STATUS_BEFORE" | grep -v '^?? docs/release-evidence/technical-audit/hosted-ci-merge-readiness/' || true)"
if [[ -z "$FILTERED_STATUS" ]]; then
  CLEAN_BEFORE=true
else
  CLEAN_BEFORE=false
fi

"$PYTHON_BIN" - "$RAW_DIR/branch_state.json" <<PY
from __future__ import annotations
import json
from pathlib import Path
Path("$RAW_DIR/branch_status_before.txt").write_text("""$STATUS_BEFORE""", encoding="utf-8")
with open("$RAW_DIR/branch_state.json", "w", encoding="utf-8") as fh:
    json.dump({
        "branch": "$BRANCH",
        "head_sha": "$HEAD_SHA",
        "clean_worktree_before_collection": $CLEAN_BEFORE,
        "status_excluding_phase09_evidence": """$FILTERED_STATUS""",
    }, fh, indent=2, sort_keys=True)
    fh.write("\n")
PY

# Prior static/evidence gates. Each verifier writes pure JSON plus a small command result.
run_json backend_fast_evidence_check "$PYTHON_BIN" scripts/audit_remediation/verify_backend_fast_evidence.py --evidence-dir docs/release-evidence/technical-audit/backend-fast-gate --json
run_json frontend_tooling_evidence_check "$PYTHON_BIN" scripts/audit_remediation/verify_frontend_tooling_evidence.py --evidence-dir docs/release-evidence/technical-audit/frontend-tooling-authority --json
run_json ci_authority_workflow_evidence_check "$PYTHON_BIN" scripts/audit_remediation/verify_ci_authority_workflow_evidence.py --evidence-dir docs/release-evidence/technical-audit/ci-authority-workflow --json
run_json dependency_scan_evidence_check "$PYTHON_BIN" scripts/audit_remediation/verify_dependency_scan_evidence.py --evidence-dir docs/release-evidence/technical-audit/dependency-scan-enforcement --json
run_json e2e_playwright_evidence_check "$PYTHON_BIN" scripts/audit_remediation/verify_e2e_playwright_evidence.py --evidence-dir docs/release-evidence/technical-audit/e2e-playwright-authority --json
run_json openapi_frontend_contract_evidence_check "$PYTHON_BIN" scripts/audit_remediation/verify_openapi_frontend_contract_evidence.py --evidence-dir docs/release-evidence/technical-audit/openapi-frontend-contract --json
run_json remote_ci_branch_integration_evidence_check "$PYTHON_BIN" scripts/audit_remediation/verify_remote_ci_branch_integration_evidence.py --evidence-dir docs/release-evidence/technical-audit/remote-ci-branch-integration --json

if [[ -n "$REMOTE_CI_STATUS_JSON" ]]; then
  cp "$REMOTE_CI_STATUS_JSON" "$RAW_DIR/hosted_ci_status.json"
else
  "$PYTHON_BIN" - "$RAW_DIR/hosted_ci_status.json" <<'PY'
from __future__ import annotations
import json, os
with open(os.environ.get("OUT", "docs/release-evidence/technical-audit/hosted-ci-merge-readiness/raw/hosted_ci_status.json"), "w", encoding="utf-8") as fh:
    json.dump({
        "remote_ci_run_claimed": False,
        "conclusion": "not_claimed",
        "head_sha": None,
        "workflow": None,
        "reason": "REMOTE_CI_STATUS_JSON was not supplied; Phase 09 cannot close without real hosted CI success evidence.",
    }, fh, indent=2, sort_keys=True)
    fh.write("\n")
PY
fi

"$PYTHON_BIN" - "$RAW_DIR/prior_gate_evidence_summary.json" "$RAW_DIR" <<'PY'
from __future__ import annotations
import json, sys
from pathlib import Path
raw = Path(sys.argv[2])
checks = {}
for path in sorted(raw.glob("*_evidence_check.json")):
    name = path.name.removesuffix("_evidence_check.json")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        data = {"valid": False, "errors": [f"invalid JSON: {exc}"]}
    result_file = raw / f"{name}_evidence_check.result.json"
    rc = None
    if result_file.exists():
        try:
            rc = json.loads(result_file.read_text(encoding="utf-8")).get("returncode")
        except Exception:
            rc = None
    checks[name] = {"valid": data.get("valid") is True and rc == 0, "returncode": rc, "errors": data.get("errors", [])}
with (raw / "prior_gate_evidence_summary.json").open("w", encoding="utf-8") as fh:
    json.dump({"checks": checks, "valid": all(v["valid"] for v in checks.values())}, fh, indent=2, sort_keys=True)
    fh.write("\n")
PY

"$PYTHON_BIN" - "$RAW_DIR/merge_readiness_result.json" "$RAW_DIR" <<'PY'
from __future__ import annotations
import json, sys
from pathlib import Path
raw = Path(sys.argv[2])
branch = json.loads((raw / "branch_state.json").read_text(encoding="utf-8"))
prior = json.loads((raw / "prior_gate_evidence_summary.json").read_text(encoding="utf-8"))
ci = json.loads((raw / "hosted_ci_status.json").read_text(encoding="utf-8"))
ci_ok = (
    ci.get("remote_ci_run_claimed") is True
    and ci.get("conclusion") == "success"
    and ci.get("head_sha") == branch.get("head_sha")
    and bool(ci.get("workflow"))
    and bool(ci.get("run_id") or ci.get("run_url") or ci.get("html_url"))
)
valid = bool(branch.get("clean_worktree_before_collection") is True and prior.get("valid") is True and ci_ok)
errors = []
if branch.get("clean_worktree_before_collection") is not True:
    errors.append("worktree was not clean before collection")
if prior.get("valid") is not True:
    errors.append("one or more prior authority evidence checks failed")
if not ci_ok:
    errors.append("hosted CI success was not supplied or does not match branch HEAD")
with (raw / "merge_readiness_result.json").open("w", encoding="utf-8") as fh:
    json.dump({
        "valid": valid,
        "errors": errors,
        "branch": branch.get("branch"),
        "head_sha": branch.get("head_sha"),
        "remote_ci_run_claimed": ci.get("remote_ci_run_claimed") is True,
        "remote_ci_conclusion": ci.get("conclusion"),
        "prior_gate_evidence_valid": prior.get("valid") is True,
        "release_readiness_claimed": False,
        "runtime_kg_implementation_claimed": False,
        "full_backend_backed_e2e_claimed": False,
    }, fh, indent=2, sort_keys=True)
    fh.write("\n")
PY

# Create hashes after all raw artifacts have stabilized. Exclude any verifier output that can be regenerated later.
(
  cd "$RAW_DIR"
  find . -maxdepth 1 -type f ! -name 'SHA256SUMS.txt' ! -name 'hosted_ci_merge_readiness_evidence_check.json' -printf '%f\n' | sort | xargs -r sha256sum > SHA256SUMS.txt
)

MERGE_VALID="$($PYTHON_BIN - <<PY
import json
print(str(json.load(open('$RAW_DIR/merge_readiness_result.json')).get('valid')).lower())
PY
)"
if [[ "$MERGE_VALID" == "true" ]]; then
  STATUS="Hosted CI merge-readiness passed"
else
  STATUS="Hosted CI merge-readiness blocked — hosted CI success not claimed or not matching HEAD"
fi

cat > "$EVIDENCE_DIR/evidence_index.md" <<EOF
# TA Phase 09 Hosted CI / Merge-Readiness Evidence

- Status: $STATUS
- Branch: $BRANCH
- Source commit: $HEAD_SHA
- Remote CI run claimed: $(python3 - <<PY
import json
print(str(json.load(open('$RAW_DIR/hosted_ci_status.json')).get('remote_ci_run_claimed') is True).lower())
PY
)
- Release readiness claimed: false
- Runtime KG implementation claimed: false

## Raw artifacts

- raw/branch_state.json
- raw/prior_gate_evidence_summary.json
- raw/hosted_ci_status.json
- raw/merge_readiness_result.json
- raw/SHA256SUMS.txt

This evidence bundle is valid only when a real hosted CI status artifact is supplied and matches the branch HEAD.
EOF
sha256sum "$EVIDENCE_DIR/evidence_index.md" > "$EVIDENCE_DIR/evidence_index.sha256"

set +e
"$PYTHON_BIN" scripts/audit_remediation/verify_hosted_ci_merge_readiness_evidence.py --evidence-dir "$EVIDENCE_DIR" --json > "$RAW_DIR/hosted_ci_merge_readiness_evidence_check.json"
VERIFY_RC=$?
set -e
exit "$VERIFY_RC"
