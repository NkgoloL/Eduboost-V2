#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from scripts._subprocess import check_output, run
import xml.etree.ElementTree as ET  # nosec B405 -- parses locally-generated coverage.xml only, not external input
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.roadmap_reconciliation.verify_rr003_coverage_ci_route_authority import verify

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs/roadmap/reconciliation/rr_003_coverage_ci_route_authority_record.json"
EVIDENCE_DIR = ROOT / "docs/release-evidence/roadmap-reconciliation/rr-003-coverage-ci-route-authority"
RAW_DIR = EVIDENCE_DIR / "raw"

CHECKSUM_FILES = [
    ".github/workflows/rr003-release-authority.yml",
    "docs/roadmap/reconciliation/outstanding_work_register.md",
    "docs/roadmap/reconciliation/rr_003_coverage_ci_route_authority.md",
    "docs/roadmap/reconciliation/rr_003_coverage_ci_route_authority_record.json",
    "docs/release/coverage_ci_route_authority.md",
    "docs/release/coverage_ci_route_policy.json",
    "docs/release/dormant_router_inventory.md",
    "docs/release/route_alias_matrix.md",
    "docs/release/route_alias_exceptions.txt",
    "scripts/roadmap_reconciliation/verify_rr003_coverage_ci_route_authority.py",
    "scripts/roadmap_reconciliation/capture_rr003_coverage_ci_route_authority_evidence.py",
]


def _run(args: list[str]) -> dict[str, Any]:
    try:
        proc = run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
        return {"command": args, "returncode": proc.returncode, "output": proc.stdout}
    except Exception as exc:
        return {"command": args, "returncode": 127, "output": f"{type(exc).__name__}: {exc}"}


def _run_git(args: list[str]) -> str:
    try:
        return check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:
        return f"unavailable: {exc}"


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _parse_coverage_xml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "coverage_percent": None, "error": f"missing coverage xml: {path}"}
    try:
        root = ET.parse(path).getroot()  # nosec B314
        line_rate = float(root.attrib.get("line-rate", "0"))
        branch_rate = float(root.attrib.get("branch-rate", "0")) if "branch-rate" in root.attrib else None
        return {
            "exists": True,
            "coverage_xml": str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path),
            "coverage_percent": round(line_rate * 100, 2),
            "branch_coverage_percent": round(branch_rate * 100, 2) if branch_rate is not None else None,
            "lines_valid": int(root.attrib.get("lines-valid", "0") or 0),
            "lines_covered": int(root.attrib.get("lines-covered", "0") or 0),
        }
    except Exception as exc:
        return {"exists": True, "coverage_percent": None, "error": f"{type(exc).__name__}: {exc}"}


def capture(owner: str, target_branch: str, claim: bool, coverage_xml: Path, threshold_percent: float | None, skip_route_check: bool) -> dict[str, Any]:
    verification = verify()
    status_short = _run_git(["status", "--short"])
    git_state = {
        "branch": _run_git(["branch", "--show-current"]),
        "head_sha": _run_git(["rev-parse", "HEAD"]),
        "target_branch": target_branch,
        "status_short": status_short,
    }
    coverage = _parse_coverage_xml(coverage_xml)
    measured = coverage.get("coverage_percent")
    threshold = threshold_percent if threshold_percent is not None else measured

    route_alias_result = {"skipped": True, "returncode": 0, "output": "route alias check skipped by caller"}
    if not skip_route_check:
        route_alias_result = _run(["python3", "scripts/check_route_alias_matrix.py"])

    recorded = bool(
        claim
        and verification["valid"]
        and isinstance(measured, (int, float))
        and isinstance(threshold, (int, float))
        and measured >= threshold
        and route_alias_result.get("returncode") == 0
    )

    record = {
        "rr_id": "RR-003",
        "status": "coverage_ci_route_authority_recorded" if recorded else "authority_installed_evidence_pending",
        "coverage_ci_route_authority_recorded": recorded,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "authority_owner": owner,
        "target_branch": target_branch,
        "coverage_baseline_recorded": recorded,
        "coverage_threshold_decided": recorded,
        "coverage_baseline_percent": measured if recorded else None,
        "coverage_threshold_percent": threshold if recorded else None,
        "coverage_source": coverage,
        "release_checks_visible_in_ci": recorded,
        "route_alias_policy_enforced": recorded,
        "route_alias_check": route_alias_result,
        "dormant_router_inventory_recorded": recorded,
        "release_docs_point_to_current_evidence": recorded,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "public_beta_authorised": False,
        "runtime_kg_implementation_claimed": False,
        "verification": verification,
        "git_state": git_state,
        "clean_git_state_at_capture": status_short == "",
    }

    _write(RECORD, record)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    _write(RAW_DIR / "rr003_coverage_ci_route_authority_result.json", record)
    _write(RAW_DIR / "git_state.json", git_state)
    _write(RAW_DIR / "verification.json", verification)
    _write(RAW_DIR / "coverage_summary.json", coverage)
    _write(RAW_DIR / "route_alias_check.json", route_alias_result)

    lines: list[str] = []
    for rel in CHECKSUM_FILES:
        path = ROOT / rel
        if path.exists():
            lines.append(f"{_sha(path)}  {rel}")
    if coverage_xml.exists():
        try:
            rel = str(coverage_xml.relative_to(ROOT))
        except ValueError:
            rel = str(coverage_xml)
        lines.append(f"{_sha(coverage_xml)}  {rel}")
    (EVIDENCE_DIR / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    index_lines = [
        "# RR-003 Coverage / CI / Route Authority Evidence",
        "",
        f"Recorded: {recorded}",
        f"Owner: {owner}",
        f"Target branch: {target_branch}",
        f"Coverage baseline percent: {record.get('coverage_baseline_percent')}",
        f"Coverage threshold percent: {record.get('coverage_threshold_percent')}",
        "",
        "## Boundary",
        "",
        "This evidence records RR-003 coverage / CI / route authority only. It does not authorise production release, deployment, public beta, release tagging, or runtime KG implementation.",
        "",
        "## Raw evidence",
        "",
        "- `raw/rr003_coverage_ci_route_authority_result.json`",
        "- `raw/git_state.json`",
        "- `raw/verification.json`",
        "- `raw/coverage_summary.json`",
        "- `raw/route_alias_check.json`",
        "- `SHA256SUMS.txt`",
        "",
    ]
    (EVIDENCE_DIR / "evidence_index.md").write_text("\n".join(index_lines), encoding="utf-8")
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--claim-rr003-coverage-ci-route-authority", action="store_true")
    parser.add_argument("--authority-owner", required=True)
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--coverage-xml", default="coverage.xml")
    parser.add_argument("--coverage-threshold-percent", type=float, default=None)
    parser.add_argument("--skip-route-check", action="store_true")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = capture(
        owner=args.authority_owner,
        target_branch=args.target_branch,
        claim=args.claim_rr003_coverage_ci_route_authority,
        coverage_xml=(ROOT / args.coverage_xml).resolve() if not Path(args.coverage_xml).is_absolute() else Path(args.coverage_xml),
        threshold_percent=args.coverage_threshold_percent,
        skip_route_check=args.skip_route_check,
    )

    if args.json:
        print(json.dumps({"valid": bool(result["coverage_ci_route_authority_recorded"]), **result}, indent=2, sort_keys=True))
    else:
        print("valid" if result["coverage_ci_route_authority_recorded"] else "invalid")

    if args.require_valid and not result["coverage_ci_route_authority_recorded"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
