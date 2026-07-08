#!/usr/bin/env python3
"""Apply PRD-1.5-1.9 CI convergence, release-readiness, final reconciliation, and PRD-2 handoff."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

PRD_ID = "PRD-1.5-1.9"
STREAM_ID = "PRD-1-CI-RELEASE-GATE-CONVERGENCE"
MERGED_PRD_SLICES = ["PRD-1.5", "PRD-1.6", "PRD-1.7", "PRD-1.8", "PRD-1.9"]
ROOT = Path("docs/roadmap/production_readiness")
RECORD = ROOT / "prd_105_109_ci_convergence_release_readiness_handoff_record.json"
CONFIG = ROOT / "prd1_ci_convergence_release_readiness_handoff.json"
DOC = ROOT / "prd_105_109_ci_convergence_release_readiness_handoff.md"
ENGINEERING_DOC = Path("docs/engineering/prd1_ci_convergence_release_readiness_handoff.md")

TRUE_BOUNDARIES = [
    "runtime_kg_implementation_claimed",
    "runtime_kg_authority_switch_authorised",
    "authority_switch_executed",
]
FALSE_BOUNDARIES = [
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "public_beta_live_traffic_authorised",
    "live_learner_traffic_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
    "new_kg_slice_authorised",
    "prd2_implementation_authorised",
]
IMPLEMENTATION_TRUE = [
    "ci_convergence_evidence_defined",
    "release_readiness_register_defined",
    "authority_reconciliation_defined",
    "final_evidence_capture_defined",
    "prd2_handoff_defined",
]
IMPLEMENTATION_FALSE = [
    "required_checks_enforced",
    "release_gate_enforced",
    "branch_protection_modified",
    "production_release_deployed",
    "release_tag_created",
    "prd2_runtime_kg_implementation_performed",
]

REQUIRED_CHECKS = [
    "python-package-and-unit-tests",
    "openapi-contract-and-drift",
    "security-and-dependency-scan",
    "migration-and-runtime-contracts",
    "release-readiness-cluster",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def sha256(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def workflow_summary(root: Path) -> dict[str, Any]:
    workflow_root = root / ".github" / "workflows"
    workflows = sorted(p for p in workflow_root.iterdir() if p.is_file() and p.suffix in {".yml", ".yaml"}) if workflow_root.exists() else []
    python_m: list[str] = []
    python3_m: list[str] = []
    release_refs: list[str] = []
    deployment_refs: list[str] = []
    required_signal_refs: dict[str, list[str]] = {key: [] for key in REQUIRED_CHECKS}
    for path in workflows:
        text = read_text(path).lower()
        rel = path.relative_to(root).as_posix()
        if "python -m pytest" in text:
            python_m.append(rel)
        if "python3 -m pytest" in text:
            python3_m.append(rel)
        if "release/" in text or "release/**" in text or re.search(r"on:\s*release|release:", text):
            release_refs.append(rel)
        if any(term in text for term in ["deploy", "deployment", "promotion", "production", "environment"]):
            deployment_refs.append(rel)
        if any(term in text for term in ["pytest", "unit", "python"]):
            required_signal_refs["python-package-and-unit-tests"].append(rel)
        if "openapi" in text:
            required_signal_refs["openapi-contract-and-drift"].append(rel)
        if any(term in text for term in ["security", "dependency", "bandit", "pip-audit", "trivy", "secret"]):
            required_signal_refs["security-and-dependency-scan"].append(rel)
        if any(term in text for term in ["migration", "alembic", "runtime-contract", "contract"]):
            required_signal_refs["migration-and-runtime-contracts"].append(rel)
        if any(term in text for term in ["release-readiness", "release readiness", "cluster-h"]):
            required_signal_refs["release-readiness-cluster"].append(rel)
    return {
        "workflow_count": len(workflows),
        "python_m_pytest_workflow_count": len(python_m),
        "python3_m_pytest_workflow_count": len(python3_m),
        "release_reference_workflow_count": len(release_refs),
        "deployment_reference_workflow_count": len(deployment_refs),
        "python_m_pytest_workflows": python_m,
        "required_signal_refs": {key: sorted(set(value)) for key, value in required_signal_refs.items()},
        "required_signal_coverage": {key: bool(value) for key, value in required_signal_refs.items()},
    }


def openapi_summary(root: Path) -> dict[str, Any]:
    root_openapi = root / "openapi.json"
    docs_openapi = root / "docs" / "openapi.json"
    return {
        "root_openapi_present": root_openapi.exists(),
        "docs_openapi_present": docs_openapi.exists(),
        "root_openapi_sha256": sha256(root_openapi),
        "docs_openapi_sha256": sha256(docs_openapi),
        "root_and_docs_openapi_match": root_openapi.exists() and docs_openapi.exists() and sha256(root_openapi) == sha256(docs_openapi),
    }


def build_config(root: Path) -> dict[str, Any]:
    workflows = workflow_summary(root)
    openapi = openapi_summary(root)
    return {
        "schema_version": "prd1-ci-convergence-release-readiness-handoff/v1",
        "prd_id": PRD_ID,
        "merged_prd_slices": MERGED_PRD_SLICES,
        "stream_id": STREAM_ID,
        "purpose": "Close PRD-1 in one consolidated slice: CI convergence evidence, release-readiness register, authority reconciliation, final evidence capture, and handoff to PRD-2.",
        "predecessor_required": "PRD-1.2-1.4",
        "ci_convergence_evidence": {
            "local_verifier_chain_required": ["PRD-1.0", "PRD-1.1", "PRD-1.2-1.4", PRD_ID],
            "required_signal_coverage": workflows["required_signal_coverage"],
            "python_m_pytest_workflow_count": workflows["python_m_pytest_workflow_count"],
            "python3_m_pytest_workflow_count": workflows["python3_m_pytest_workflow_count"],
            "openapi_root_and_docs_match": openapi["root_and_docs_openapi_match"],
            "ci_convergence_evidence_recorded": False,
            "remote_ci_provider_state_recorded_by_github_prs": True,
            "branch_protection_evidence_recorded": False,
        },
        "release_readiness_register": {
            "release_gate_mechanics_ready": True,
            "release_gate_defined_by_prd1_4": True,
            "required_checks_defined": REQUIRED_CHECKS,
            "required_checks_enforced": False,
            "release_gate_enforced": False,
            "branch_protection_modified": False,
            "production_release_authorised": False,
            "release_tag_authorised": False,
            "deployment_authorised": False,
            "release_readiness_register_recorded": False,
            "release_execution_authority_remains": "PRD-11",
        },
        "authority_reconciliation": {
            "prd1_sequence_complete": False,
            "prd1_final_reconciliation_recorded": False,
            "next_authorised_item_after_capture": "PRD-2",
            "prd2_handoff_authority_only": True,
            "prd2_runtime_kg_implementation_authorised": False,
        },
        "final_evidence_capture": {
            "final_evidence_recorded": False,
            "evidence_directory": "docs/release-evidence/production-readiness/prd-105-109-ci-convergence-release-readiness-handoff",
        },
        "handoff_to_prd2": {
            "prd2_title": "Runtime KG Integration and Persistence",
            "prd2_handoff_authorised_after_capture": False,
            "prd2_implementation_authorised": False,
            "no_runtime_kg_changes_performed_by_prd1": True,
        },
        "workflow_summary": workflows,
        "openapi_summary": openapi,
        "authority_boundaries": {**{key: True for key in TRUE_BOUNDARIES}, **{key: False for key in FALSE_BOUNDARIES}},
        "implementation_boundaries": {**{key: True for key in IMPLEMENTATION_TRUE}, **{key: False for key in IMPLEMENTATION_FALSE}},
    }


def build_record(root: Path) -> dict[str, Any]:
    config = build_config(root)
    return {
        "schema_version": "prd1-ci-convergence-release-readiness-handoff-record/v1",
        "prd_id": PRD_ID,
        "merged_prd_slices": MERGED_PRD_SLICES,
        "stream_id": STREAM_ID,
        "status": "authority_defined_pending_evidence_capture",
        "next_authorised_item": "PRD-1.5",
        "prd2_handoff_authorised": False,
        "prd2_implementation_authorised": False,
        "ci_convergence_evidence_recorded": False,
        "release_readiness_register_recorded": False,
        "prd1_final_reconciliation_recorded": False,
        "prd1_final_evidence_recorded": False,
        "prd1_sequence_complete": False,
        "no_prd2_implementation_performed": True,
        "no_production_release_performed": True,
        "no_deployment_performed": True,
        "no_release_tag_created": True,
        "no_public_beta_authorised": True,
        "no_live_learner_traffic_authorised": True,
        "required_checks_enforced": False,
        "release_gate_enforced": False,
        "branch_protection_modified": False,
        "production_release_deployed": False,
        "release_tag_created": False,
        "prd2_runtime_kg_implementation_performed": False,
        **{key: True for key in TRUE_BOUNDARIES},
        **{key: False for key in FALSE_BOUNDARIES},
        "config_summary": {
            "workflow_count": config["workflow_summary"]["workflow_count"],
            "python_m_pytest_workflow_count": config["workflow_summary"]["python_m_pytest_workflow_count"],
            "python3_m_pytest_workflow_count": config["workflow_summary"]["python3_m_pytest_workflow_count"],
            "required_signal_coverage": config["ci_convergence_evidence"]["required_signal_coverage"],
            "openapi_root_and_docs_match": config["openapi_summary"]["root_and_docs_openapi_match"],
        },
    }


def docs() -> dict[Path, str]:
    return {
        DOC: """# PRD-1.5-1.9 — CI Convergence, Release Readiness, Final Evidence, and PRD-2 Handoff\n\n**Merged slices:** PRD-1.5, PRD-1.6, PRD-1.7, PRD-1.8, and PRD-1.9.\n\nThis consolidated slice closes PRD-1 without creating five more micro-slices. It records CI convergence evidence, the release-readiness register, the final PRD-1 authority reconciliation, the final PRD-1 evidence capture, and the controlled handoff to **PRD-2 — Runtime KG Integration and Persistence**.\n\n## Scope\n\n- Confirm PRD-1.0, PRD-1.1, and PRD-1.2-1.4 remain valid.\n- Confirm workflow pytest commands remain canonicalised to `python3 -m pytest`.\n- Confirm the root and docs OpenAPI artifacts remain reconciled.\n- Record release-gate mechanics as ready for later enforcement evidence.\n- Mark the PRD-1 sequence complete and authorise PRD-2 as the next workstream.\n\n## Boundary\n\nThis slice does **not** modify branch protection, enforce required checks in GitHub settings, create a release tag, deploy production, authorise public beta, authorise live learner traffic, authorise billing, or implement Runtime KG.\n\nPRD-11 remains the production release/deployment authority. PRD-2 remains the runtime KG implementation authority.\n""",
        ENGINEERING_DOC: """# PRD-1 CI/Release Gate Closure Handoff\n\nPRD-1.5-1.9 intentionally closes the CI/release-gate convergence stream in one bundle to reduce governance overhead. The implementation focus is evidence and register reconciliation, not more workflow sprawl.\n\n## CI convergence standard\n\nThe PRD-1 closure standard is:\n\n1. PRD-1.0 stream authority is valid.\n2. PRD-1.1 CI inventory authority is valid.\n3. PRD-1.2-1.4 required checks, workflow canonicalisation, and release-gate definition are valid.\n4. Workflow pytest command form remains `python3 -m pytest`.\n5. `docs/openapi.json` remains the canonical OpenAPI artifact with root `openapi.json` as a compatibility mirror.\n\n## Handoff\n\nAfter evidence capture, `next_authorised_item` becomes `PRD-2`. This authorises the next controlled stream only. Runtime KG implementation remains reserved for PRD-2 and is not performed here. Production deployment remains reserved for PRD-11.\n""",
    }


def patch_makefile(root: Path) -> None:
    makefile = root / "Makefile"
    marker = "# PRD-1.5-1.9 CI convergence/release-readiness/handoff"
    block = f"""
{marker}
.PHONY: prd105-109-ci-convergence-release-readiness-handoff-check prd105-109-ci-convergence-release-readiness-handoff-capture
prd105-109-ci-convergence-release-readiness-handoff-check:
\tPYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_prd105_109_ci_convergence_release_readiness_handoff.py --authority-only --json

prd105-109-ci-convergence-release-readiness-handoff-capture:
\tPYTHONPATH=. python3 scripts/roadmap_reconciliation/capture_prd105_109_ci_convergence_release_readiness_handoff_evidence.py --claim-prd105-109-ci-convergence-release-readiness-handoff --prd-owner "$${{PRD_OWNER:-Nkgolo Lebelo}}" --target-branch master --require-valid --json
# End PRD-1.5-1.9 CI convergence/release-readiness/handoff
"""
    if makefile.exists():
        text = makefile.read_text(encoding="utf-8", errors="replace")
        if marker not in text:
            makefile.write_text(text.rstrip() + "\n" + block, encoding="utf-8")


def apply(root: Path = Path("."), write_files: bool = True) -> dict[str, Any]:
    config = build_config(root)
    if write_files:
        for path, content in docs().items():
            full = root / path
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(content, encoding="utf-8")
        write_json(root / CONFIG, config)
        write_json(root / RECORD, build_record(root))
        patch_makefile(root)
    return config


def main() -> int:
    apply(Path("."), write_files=True)
    print(json.dumps({"applied": True, "prd_id": PRD_ID, "merged_prd_slices": MERGED_PRD_SLICES}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
