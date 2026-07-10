#!/usr/bin/env bash
set -euo pipefail

TARGET_ROOT="${1:-.}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PAYLOAD_DIR="${SCRIPT_DIR}/payload"

if [[ ! -d "${TARGET_ROOT}" ]]; then
  echo "Target root does not exist: ${TARGET_ROOT}" >&2
  exit 1
fi

copy_file() {
  local rel="$1"
  mkdir -p "${TARGET_ROOT}/$(dirname "${rel}")"
  cp "${PAYLOAD_DIR}/${rel}" "${TARGET_ROOT}/${rel}"
}

copy_file "Makefile"
copy_file "app/modules/controlled_beta/authorisation.py"
copy_file "app/modules/controlled_beta/__init__.py"
copy_file "app/api_v2_routers/controlled_beta.py"
copy_file "docs/engineering/prd10_controlled_beta_final_live_traffic_handoff.md"
copy_file "docs/roadmap/production_readiness/prd_1005_1009_controlled_beta_final_live_traffic_handoff_record.json"
copy_file "scripts/production_readiness/audit_prd900_904_billing_commercial_launch_readiness_foundation.py"
copy_file "scripts/production_readiness/audit_prd905_909_commercial_runtime_audit_remediation_handoff.py"
copy_file "scripts/production_readiness/audit_prd1000_1004_controlled_beta_live_traffic_preflight_foundation.py"
copy_file "scripts/production_readiness/audit_prd1005_1009_controlled_beta_final_live_traffic_handoff.py"
copy_file "scripts/roadmap_reconciliation/verify_prd1005_1009_controlled_beta_final_live_traffic_handoff.py"
copy_file "scripts/roadmap_reconciliation/capture_prd1005_1009_controlled_beta_final_live_traffic_handoff_evidence.py"
copy_file "tests/unit/modules/controlled_beta/test_controlled_beta_final_authorisation.py"
copy_file "tests/unit/roadmap_reconciliation/test_prd1005_1009_controlled_beta_final_live_traffic_handoff.py"

echo "Applied PRD-10.5-10.9 controlled beta final live-traffic handoff bundle to ${TARGET_ROOT}"
