#!/usr/bin/env python3
"""Capture branch-protection evidence and update hosted-CI merge readiness.

This script is deliberately conservative. It never marks merge readiness as true
unless the existing hosted-CI authority record already contains a completed,
successful GitHub Actions run and this capture finds branch protection for the
target branch through either classic branch protection or active branch rulesets.
"""

from __future__ import annotations
import subprocess  # nosec B404 — subprocess constants support the controlled wrapper

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
from scripts._subprocess import run
import sys
from typing import Any

RECORD_PATH = pathlib.Path(
    "docs/roadmap/execution/technical_audit_remediation/hosted_ci_authority_record.json"
)
REGISTER_PATH = pathlib.Path("docs/roadmap/execution/technical_audit_remediation/blocker_register.json")
EVIDENCE_DIR = pathlib.Path("docs/release-evidence/technical-audit/phase-09-hosted-ci")
RAW_DIR = EVIDENCE_DIR / "raw"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(cmd, check=check, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def git_value(args: list[str], default: str | None = None) -> str | None:
    try:
        return run(["git", *args]).stdout.strip()
    except Exception:
        return default


def gh_repo_from_origin() -> str | None:
    url = git_value(["remote", "get-url", "origin"])
    if not url:
        return None
    patterns = [
        r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$",
        r"https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return f"{match.group('owner')}/{match.group('repo')}"
    return None


def require_gh() -> None:
    try:
        run(["gh", "--version"])
    except Exception as exc:
        raise SystemExit(
            "GitHub CLI 'gh' is required to capture branch-protection evidence. "
            "Install gh, authenticate with `gh auth login`, then rerun this script."
        ) from exc


def write_json(path: pathlib.Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: pathlib.Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON file: {path}: {exc}") from exc


def gh_api_json(path: str) -> tuple[bool, Any, dict[str, Any]]:
    completed = run(["gh", "api", path], check=False)
    meta = {
        "command": f"gh api {path}",
        "returncode": completed.returncode,
        "stderr": completed.stderr.strip(),
    }
    if completed.returncode != 0:
        return False, {
            "available": False,
            "reason": "gh_api_failed",
            "returncode": completed.returncode,
            "stderr": completed.stderr.strip(),
        }, meta
    try:
        return True, json.loads(completed.stdout), meta
    except json.JSONDecodeError:
        return False, {
            "available": False,
            "reason": "invalid_json_from_gh_api",
            "stdout": completed.stdout,
            "stderr": completed.stderr.strip(),
        }, meta


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_sha256sums(raw_files: list[pathlib.Path], sums_path: pathlib.Path) -> None:
    unique = sorted({p for p in raw_files if p.exists()}, key=lambda p: p.as_posix())
    lines = [f"{sha256_file(path)}  {path.as_posix()}" for path in unique]
    sums_path.parent.mkdir(parents=True, exist_ok=True)
    sums_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def _ruleset_targets_branch(ruleset: dict[str, Any], target_branch: str, default_branch: str | None) -> bool:
    target = ruleset.get("target")
    if target and target != "branch":
        return False

    conditions = ruleset.get("conditions") or {}
    ref_name = conditions.get("ref_name") if isinstance(conditions, dict) else None
    if not isinstance(ref_name, dict):
        # Repository-level branch rulesets without explicit ref_name conditions are
        # treated as potentially applying to branch refs.
        return True

    includes = [str(item) for item in _as_list(ref_name.get("include"))]
    excludes = [str(item) for item in _as_list(ref_name.get("exclude"))]
    names = {
        target_branch,
        f"refs/heads/{target_branch}",
    }
    if default_branch and target_branch == default_branch:
        names.add("~DEFAULT_BRANCH")

    def matches(pattern: str) -> bool:
        if pattern in names:
            return True
        if pattern.startswith("refs/heads/") and pattern.removeprefix("refs/heads/") == target_branch:
            return True
        # GitHub ruleset patterns commonly use fnmatch-style wildcards.
        regex = re.escape(pattern).replace(r"\*", ".*")
        return any(re.fullmatch(regex, name) for name in names)

    if any(matches(pattern) for pattern in excludes):
        return False
    return not includes or any(matches(pattern) for pattern in includes)


def _ruleset_signals(ruleset: dict[str, Any]) -> dict[str, bool]:
    rules = _as_list(ruleset.get("rules"))
    rule_types = {str(rule.get("type")) for rule in rules if isinstance(rule, dict)}
    return {
        "requires_status_checks": "required_status_checks" in rule_types,
        "requires_pull_request": "pull_request" in rule_types,
        "blocks_deletion": "deletion" in rule_types,
        "blocks_force_push": "non_fast_forward" in rule_types,
    }


def evaluate_branch_protection(
    *,
    target_branch: str,
    branch_payload: dict[str, Any],
    classic_payload: dict[str, Any],
    rulesets_payload: Any,
) -> dict[str, Any]:
    default_branch = branch_payload.get("default_branch")
    # The branches endpoint does not reliably include default_branch, so infer only
    # when the branch payload carries it. The ~DEFAULT_BRANCH matcher is therefore
    # conservative unless the API payload confirms it.

    classic_available = bool(classic_payload) and classic_payload.get("available") is not False and "url" in classic_payload
    active_matching_rulesets: list[dict[str, Any]] = []
    for item in _as_list(rulesets_payload):
        if not isinstance(item, dict):
            continue
        enforcement = item.get("enforcement")
        if enforcement != "active":
            continue
        if _ruleset_targets_branch(item, target_branch, default_branch):
            active_matching_rulesets.append(
                {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "target": item.get("target"),
                    "enforcement": enforcement,
                    "signals": _ruleset_signals(item),
                }
            )

    mechanism = "none"
    if classic_available and active_matching_rulesets:
        mechanism = "classic_and_rulesets"
    elif classic_available:
        mechanism = "classic_branch_protection"
    elif active_matching_rulesets:
        mechanism = "active_branch_rulesets"

    branch_protection_claimed = mechanism != "none"
    return {
        "schema_version": 1,
        "captured_at_utc": utc_now(),
        "target_branch": target_branch,
        "branch_protection_claimed": branch_protection_claimed,
        "mechanism": mechanism,
        "classic_branch_protection_available": classic_available,
        "active_matching_rulesets": active_matching_rulesets,
        "release_readiness_claimed": False,
        "runtime_kg_implementation_claimed": False,
        "notes": [
            "Branch protection evidence may come from classic branch protection or active branch rulesets.",
            "This result does not claim production release readiness.",
        ],
    }


def update_register(register_path: pathlib.Path, record: dict[str, Any]) -> None:
    if not register_path.exists():
        return
    try:
        register = load_json(register_path)
    except SystemExit:
        return
    if not isinstance(register, dict):
        return

    merge_ready = record.get("merge_readiness_authorised") is True
    register["active_slice"] = "next-technical-audit-slice" if merge_ready else "ta-phase-10-branch-protection-merge-readiness"
    register["status"] = (
        "phase_10_branch_protection_merge_readiness_closed"
        if merge_ready
        else "phase_10_branch_protection_merge_readiness_blocked"
    )

    phase09 = register.setdefault("phase_09_hosted_ci_authority", {})
    if isinstance(phase09, dict):
        phase09.update(
            {
                "authority_record": str(RECORD_PATH),
                "hosted_ci_run_claimed": record.get("hosted_ci_run_claimed") is True,
                "branch_protection_claimed": record.get("branch_protection_claimed") is True,
                "merge_readiness_authorised": merge_ready,
                "status": "merge_readiness_authorised" if merge_ready else "branch_protection_evidence_missing",
                "workflow": ".github/workflows/technical-audit-hosted-ci.yml",
            }
        )

    blockers = register.get("remaining_release_blockers_after_reset")
    if isinstance(blockers, list):
        for item in blockers:
            if isinstance(item, dict) and item.get("id") == "TA-HOSTED-CI-001":
                item.update(
                    {
                        "hosted_ci_merge_readiness_result": "valid" if merge_ready else "blocked_branch_protection_missing",
                        "remote_ci_run_claimed": record.get("hosted_ci_run_claimed") is True,
                        "remote_ci_success_claimed": record.get("hosted_ci_run_claimed") is True,
                        "branch_protection_claimed": record.get("branch_protection_claimed") is True,
                        "merge_readiness_authorised": merge_ready,
                        "release_readiness_claimed": False,
                        "runtime_kg_implementation_claimed": False,
                        "status": "evidence_recorded" if merge_ready else "branch_protection_evidence_missing",
                    }
                )
                break

    write_json(register_path, register)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=os.environ.get("GH_REPO") or gh_repo_from_origin())
    parser.add_argument("--target-branch", default=os.environ.get("TARGET_BRANCH", "master"))
    parser.add_argument("--record", default=str(RECORD_PATH))
    parser.add_argument("--register", default=str(REGISTER_PATH))
    parser.add_argument("--evidence-dir", default=str(EVIDENCE_DIR))
    parser.add_argument("--require-branch-protection", action="store_true")
    parser.add_argument("--no-register-update", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.repo:
        raise SystemExit("Could not infer GitHub repo. Pass --repo OWNER/REPO or set GH_REPO.")
    require_gh()

    record_path = pathlib.Path(args.record)
    evidence_dir = pathlib.Path(args.evidence_dir)
    raw_dir = evidence_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    record = load_json(record_path)
    if not isinstance(record, dict):
        raise SystemExit("hosted CI authority record must contain a JSON object")
    if record.get("hosted_ci_run_claimed") is not True or record.get("hosted_ci_conclusion") != "success":
        raise SystemExit("Hosted CI success must be captured before branch-protection merge readiness can be claimed.")
    sha = record.get("head_sha")
    if not isinstance(sha, str) or not SHA_RE.match(sha):
        raise SystemExit("hosted CI authority record has an invalid head_sha")

    safe_branch = re.sub(r"[^A-Za-z0-9_.-]", "_", args.target_branch)

    repo_ok, repo_payload, repo_meta = gh_api_json(f"repos/{args.repo}")
    if isinstance(repo_payload, dict):
        repo_payload.setdefault("available", repo_ok)
        repo_payload.setdefault("api_meta", repo_meta)
    repo_path = raw_dir / "repository.json"
    write_json(repo_path, repo_payload)

    branch_ok, branch_payload, branch_meta = gh_api_json(f"repos/{args.repo}/branches/{args.target_branch}")
    if isinstance(branch_payload, dict):
        branch_payload.setdefault("available", branch_ok)
        branch_payload.setdefault("api_meta", branch_meta)
    branch_path = raw_dir / f"branch_{safe_branch}.json"
    write_json(branch_path, branch_payload)

    classic_ok, classic_payload, classic_meta = gh_api_json(f"repos/{args.repo}/branches/{args.target_branch}/protection")
    if isinstance(classic_payload, dict):
        classic_payload.setdefault("available", classic_ok)
        classic_payload.setdefault("api_meta", classic_meta)
    classic_path = raw_dir / f"branch_protection_{safe_branch}.json"
    write_json(classic_path, classic_payload)

    rulesets_ok, rulesets_payload, rulesets_meta = gh_api_json(f"repos/{args.repo}/rulesets")
    rulesets_wrapper = {
        "available": rulesets_ok,
        "api_meta": rulesets_meta,
        "rulesets": rulesets_payload if isinstance(rulesets_payload, list) else [],
        "raw": rulesets_payload,
    }
    rulesets_path = raw_dir / "branch_rulesets.json"
    write_json(rulesets_path, rulesets_wrapper)

    effective_branch_payload = branch_payload if isinstance(branch_payload, dict) else {}
    if isinstance(repo_payload, dict) and repo_payload.get("default_branch"):
        effective_branch_payload = dict(effective_branch_payload)
        effective_branch_payload["default_branch"] = repo_payload.get("default_branch")

    result = evaluate_branch_protection(
        target_branch=args.target_branch,
        branch_payload=effective_branch_payload,
        classic_payload=classic_payload if isinstance(classic_payload, dict) else {},
        rulesets_payload=rulesets_wrapper["rulesets"],
    )
    result.update({"repository": args.repo, "head_sha": sha})
    result_path = raw_dir / f"branch_protection_result_{safe_branch}.json"
    write_json(result_path, result)

    raw_files = [repo_path, branch_path, classic_path, rulesets_path, result_path]
    for raw in record.get("raw_evidence_files") or []:
        if isinstance(raw, str):
            raw_path = pathlib.Path(raw)
            if raw_path.exists():
                raw_files.append(raw_path)
    sums_path = evidence_dir / "SHA256SUMS.txt"
    write_sha256sums(raw_files, sums_path)

    branch_claimed = result.get("branch_protection_claimed") is True
    record["target_branch"] = args.target_branch
    record["branch_protection_claimed"] = branch_claimed
    record["branch_protection_evidence"] = result_path.as_posix()
    record["branch_protection_mechanism"] = result.get("mechanism")
    record["merge_readiness_authorised"] = bool(branch_claimed and record.get("hosted_ci_run_claimed") is True and record.get("hosted_ci_conclusion") == "success")
    record["status"] = "merge_readiness_authorised" if record["merge_readiness_authorised"] else "branch_protection_evidence_missing"
    record["updated_at_utc"] = utc_now()
    record["raw_evidence_files"] = sorted({p.as_posix() for p in raw_files})
    record["sha256sums"] = sums_path.as_posix()
    constraints = list(record.get("constraints") or [])
    constraints.append("Branch protection evidence is derived from GitHub API classic protection and ruleset payloads.")
    record["constraints"] = sorted(set(str(item) for item in constraints))
    write_json(record_path, record)

    if not args.no_register_update:
        update_register(pathlib.Path(args.register), record)

    output = {
        "valid": record["merge_readiness_authorised"],
        "record": record_path.as_posix(),
        "branch_protection_claimed": branch_claimed,
        "branch_protection_mechanism": result.get("mechanism"),
        "branch_protection_evidence": result_path.as_posix(),
        "merge_readiness_authorised": record["merge_readiness_authorised"],
        "release_readiness_claimed": False,
    }
    print(json.dumps(output, indent=2, sort_keys=True))

    if args.require_branch_protection and not branch_claimed:
        print("Branch protection was not found for the target branch; merge readiness remains blocked.", file=sys.stderr)
        return 3
    return 0 if record["merge_readiness_authorised"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
