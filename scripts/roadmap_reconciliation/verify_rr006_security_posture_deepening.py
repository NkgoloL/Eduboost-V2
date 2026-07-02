#!/usr/bin/env python3
"""Verify RR-006 security posture deepening authority."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RR_ID = "RR-006"
RECORD = Path("docs/roadmap/reconciliation/rr_006_security_posture_deepening_record.json")
REGISTER = Path("docs/roadmap/reconciliation/outstanding_work_register.md")
THREAT_MODEL = Path("docs/security/threat_model_v2.md")
THREAT_REVIEW = Path("docs/security/rr006_threat_model_review.md")
PENTEST = Path("docs/security/v2_pen_test_checklist.md")
CONTROL_MAP = Path("docs/security/rr006_security_posture_control_map.md")
PY_AUDIT_POLICY = Path("docs/security/python_dependency_audit_policy.md")
SECRETS_POLICY = Path("docs/security/secrets_scanning_enforcement.md")
PRECOMMIT = Path(".pre-commit-config.yaml")
SECRETS_CI = Path(".github/workflows/secrets-scan.yml")
RR006_CI = Path(".github/workflows/rr006-security-posture.yml")

BOUNDARY_FALSE_KEYS = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "runtime_kg_implementation_claimed",
)

REQUIRED_TRUE_KEYS = (
    "security_posture_deepening_recorded",
    "v2_threat_model_reviewed",
    "v2_pen_test_checklist_recorded",
    "dependency_vulnerability_scan_enforced",
    "python_dependency_audit_enforced",
    "secrets_scanning_precommit_enforced",
    "secrets_scanning_ci_enforced",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _contains(text: str, *needles: str) -> bool:
    lower = text.lower()
    return all(needle.lower() in lower for needle in needles)


def evaluate(root: Path | str = Path(".")) -> dict[str, Any]:
    root = Path(root)
    errors: list[str] = []
    warnings: list[str] = []

    def p(path: Path) -> Path:
        return root / path

    register = _read(p(REGISTER))
    record = _json(p(RECORD))
    threat_model = _read(p(THREAT_MODEL))
    threat_review = _read(p(THREAT_REVIEW))
    pentest = _read(p(PENTEST))
    control_map = _read(p(CONTROL_MAP))
    py_audit_policy = _read(p(PY_AUDIT_POLICY))
    secrets_policy = _read(p(SECRETS_POLICY))
    precommit = _read(p(PRECOMMIT))
    secrets_ci = _read(p(SECRETS_CI))
    rr006_ci = _read(p(RR006_CI))

    checks = {
        "rr006_in_outstanding_register": RR_ID in register and "Security posture" in register,
        "record_exists": p(RECORD).exists(),
        "threat_model_exists": p(THREAT_MODEL).exists(),
        "threat_model_review_exists": p(THREAT_REVIEW).exists(),
        "threat_model_mentions_stride": "STRIDE" in threat_model or "stride" in threat_model,
        "threat_review_complete_marker": _contains(threat_review, "Threat model review complete: true"),
        "pentest_checklist_exists": p(PENTEST).exists(),
        "pentest_covers_required_surfaces": all(
            token in pentest.lower()
            for token in ("authentication", "authorization", "popia", "llm", "infrastructure")
        ),
        "control_map_exists": p(CONTROL_MAP).exists(),
        "control_map_mentions_boundary": _contains(control_map, "production release", "runtime KG"),
        "python_dependency_audit_policy_exists": p(PY_AUDIT_POLICY).exists(),
        "python_dependency_audit_policy_mentions_pip_audit": "pip-audit" in py_audit_policy,
        "secrets_policy_exists": p(SECRETS_POLICY).exists(),
        "secrets_policy_mentions_detect_secrets": "detect-secrets" in secrets_policy,
        "precommit_detect_secrets": "detect-secrets" in precommit,
        "ci_secrets_scan_exists": p(SECRETS_CI).exists() and "detect-secrets" in secrets_ci,
        "rr006_ci_exists": p(RR006_CI).exists(),
        "rr006_ci_runs_pip_audit": "pip-audit" in rr006_ci,
        "rr006_ci_runs_detect_secrets": "detect-secrets" in rr006_ci,
    }

    if record.get("rr_id") != RR_ID:
        errors.append(f"record rr_id must be {RR_ID}")

    for key, passed in checks.items():
        if not passed:
            errors.append(f"missing or failed check: {key}")

    if record.get("security_posture_deepening_recorded") is True:
        for key in REQUIRED_TRUE_KEYS:
            if record.get(key) is not True:
                errors.append(f"record flag must be true after evidence capture: {key}")
    else:
        warnings.append("record is still pending evidence capture")

    for key in BOUNDARY_FALSE_KEYS:
        if record.get(key) is not False:
            errors.append(f"boundary flag must remain false: {key}")

    valid = not errors and record.get("security_posture_deepening_recorded") is True
    authority_valid = not [e for e in errors if not e.startswith("record flag must be true")]

    return {
        "valid": valid,
        "authority_valid": authority_valid,
        "rr_id": RR_ID,
        "record_path": str(RECORD),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "security_posture_deepening_recorded": record.get("security_posture_deepening_recorded") is True,
        "v2_threat_model_reviewed": record.get("v2_threat_model_reviewed") is True,
        "v2_pen_test_checklist_recorded": record.get("v2_pen_test_checklist_recorded") is True,
        "dependency_vulnerability_scan_enforced": record.get("dependency_vulnerability_scan_enforced") is True,
        "python_dependency_audit_enforced": record.get("python_dependency_audit_enforced") is True,
        "secrets_scanning_precommit_enforced": record.get("secrets_scanning_precommit_enforced") is True,
        "secrets_scanning_ci_enforced": record.get("secrets_scanning_ci_enforced") is True,
        **{key: record.get(key) is True for key in BOUNDARY_FALSE_KEYS},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    result = evaluate(Path(args.root))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("RR-006 security posture deepening verification")
        print(f"valid: {result['valid']}")
        print(f"authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
