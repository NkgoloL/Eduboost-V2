#!/usr/bin/env python3
"""Capture Phase 14 live-stack readiness evidence.

This phase proves a controlled runtime stack with Postgres and Redis available.
It intentionally does not authorise production release, deployment, release
 tagging, live learner traffic, or runtime knowledge-graph implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from scripts._subprocess import run
import sys
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

RECORD_PATH = pathlib.Path("docs/roadmap/execution/runtime_readiness/phase_14_live_stack_readiness_record.json")
EVIDENCE_DIR = pathlib.Path("docs/release-evidence/runtime-readiness/phase-14-live-stack-readiness")
POST_MERGE_VERIFIER = "scripts/technical_audit/verify_post_merge_baseline.py"
CRITICAL_COMPONENTS = ("secrets", "postgres", "redis", "migrations", "audit_repository")
BOUNDARY_FALSE_FIELDS = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "live_learner_traffic_authorised",
    "runtime_kg_implementation_claimed",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run(cmd: list[str]) -> dict[str, Any]:
    proc = run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {"cmd": cmd, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def git_value(args: list[str]) -> str | None:
    proc = run(["git", *args])
    if proc["returncode"] != 0:
        return None
    return str(proc["stdout"]).strip()


def write_json(path: pathlib.Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_sha256sums(evidence_dir: pathlib.Path) -> pathlib.Path:
    sums_path = evidence_dir / "SHA256SUMS.txt"
    entries: list[tuple[str, str]] = []
    for path in sorted(evidence_dir.rglob("*")):
        if path.is_file() and path.name != sums_path.name:
            entries.append((sha256_file(path), path.as_posix()))
    sums_path.write_text("".join(f"{digest}  {rel}\n" for digest, rel in entries), encoding="utf-8")
    return sums_path


def collect_verifier(script: str) -> dict[str, Any]:
    proc = run([sys.executable, script, "--json"])
    try:
        parsed = json.loads(proc["stdout"] or "{}")
    except json.JSONDecodeError:
        parsed = {"raw_stdout": proc["stdout"]}
    return {
        "script": script,
        "returncode": proc["returncode"],
        "valid": bool(isinstance(parsed, dict) and parsed.get("valid") is True and proc["returncode"] == 0),
        "payload": parsed,
        "stderr": proc["stderr"],
    }


def http_probe(base_url: str, path: str, timeout: int) -> dict[str, Any]:
    url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
    result: dict[str, Any] = {
        "url": url,
        "path": path,
        "attempted": True,
        "status_code": None,
        "body_excerpt": "",
        "json": None,
        "error": "",
    }
    body = ""
    try:
        req = Request(url, headers={"User-Agent": "EduBoost-Phase14-Live-Stack-Readiness/1.0"})
        with urlopen(req, timeout=timeout) as response:  # nosec B310
            body = response.read(8 * 1024 * 1024).decode("utf-8", errors="replace")
            result["status_code"] = int(getattr(response, "status", 0))
            result["body_excerpt"] = body[:4000]
    except HTTPError as exc:
        body = exc.read(8 * 1024 * 1024).decode("utf-8", errors="replace")
        result["status_code"] = exc.code
        result["body_excerpt"] = body[:4000]
        result["error"] = f"http error {exc.code}"
    except URLError as exc:
        result["error"] = f"url error: {exc.reason}"
    except Exception as exc:  # pragma: no cover
        result["error"] = f"{type(exc).__name__}: {exc}"
    if body:
        try:
            result["json"] = json.loads(body)
        except Exception:
            result["json"] = None
    return result


def component_statuses(payload: dict[str, Any]) -> tuple[dict[str, str], dict[str, str]]:
    data = payload.get("json")
    if not isinstance(data, dict):
        return {}, {}
    critical_raw = data.get("critical") if isinstance(data.get("critical"), dict) else {}
    optional_raw = data.get("optional") if isinstance(data.get("optional"), dict) else {}
    critical = {str(k): str(v.get("status")) if isinstance(v, dict) else "missing" for k, v in critical_raw.items()}
    optional = {str(k): str(v.get("status")) if isinstance(v, dict) else "missing" for k, v in optional_raw.items()}
    return critical, optional


def validate_probe_set(probes: dict[str, dict[str, Any]], *, allow_optional_degraded: bool) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    summary: dict[str, Any] = {
        "critical_components": {},
        "optional_components": {},
        "overall_statuses": {},
    }

    health = probes.get("health") or {}
    if health.get("status_code") != 200:
        errors.append("/health must return HTTP 200")
    elif not isinstance(health.get("json"), dict) or health["json"].get("status") != "ok":
        errors.append("/health JSON status must be ok")

    openapi = probes.get("openapi") or {}
    if openapi.get("status_code") != 200:
        errors.append("/openapi.json must return HTTP 200")
    elif not isinstance(openapi.get("json"), dict) or "openapi" not in openapi["json"]:
        errors.append("/openapi.json must contain an OpenAPI document")

    for name in ("ready", "deep_v2", "deep_api_v2"):
        probe = probes.get(name) or {}
        if probe.get("status_code") != 200:
            errors.append(f"{probe.get('path', name)} must return HTTP 200")
            continue
        data = probe.get("json")
        if not isinstance(data, dict):
            errors.append(f"{probe.get('path', name)} must return JSON")
            continue
        status = data.get("status")
        summary["overall_statuses"][name] = status
        if status not in {"ok", "degraded"}:
            errors.append(f"{probe.get('path', name)} status must be ok or degraded")
        critical, optional = component_statuses(probe)
        if name == "ready":
            summary["critical_components"] = critical
            summary["optional_components"] = optional
        for component in CRITICAL_COMPONENTS:
            if critical.get(component) != "ok":
                errors.append(f"{probe.get('path', name)} critical.{component}.status must be ok")
        if not allow_optional_degraded:
            for component, status_value in optional.items():
                if status_value not in {"ok", "skipped"}:
                    errors.append(f"{probe.get('path', name)} optional.{component}.status must be ok or skipped")

    return errors, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--claim-live-stack-readiness", action="store_true")
    parser.add_argument("--readiness-owner", default="")
    parser.add_argument("--allow-optional-degraded", action="store_true")
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    branch = git_value(["branch", "--show-current"])
    head_sha = git_value(["rev-parse", "HEAD"])
    remote_sha = git_value(["rev-parse", f"origin/{args.target_branch}"])
    tracked_status = run(["git", "status", "--porcelain", "--untracked-files=no"])
    all_status = run(["git", "status", "--porcelain", "--untracked-files=normal"])
    git_state = {
        "branch": branch,
        "head_sha": head_sha,
        "target_branch": args.target_branch,
        "remote_target_sha": remote_sha,
        "tracked_worktree_clean_before_capture": tracked_status["stdout"].strip() == "",
        "tracked_status_before_capture": tracked_status["stdout"].splitlines(),
        "status_before_capture_including_untracked": all_status["stdout"].splitlines(),
    }

    if branch != args.target_branch:
        errors.append(f"live-stack readiness must be captured from {args.target_branch}; current branch is {branch}")
    if head_sha and remote_sha and head_sha != remote_sha:
        errors.append(f"HEAD must match origin/{args.target_branch}; HEAD={head_sha}, origin/{args.target_branch}={remote_sha}")
    if tracked_status["stdout"].strip():
        errors.append("tracked worktree must be clean before live-stack readiness capture")
    if args.claim_live_stack_readiness and not args.readiness_owner.strip():
        errors.append("--readiness-owner is required when claiming live-stack readiness")

    post_merge = collect_verifier(POST_MERGE_VERIFIER)
    if post_merge.get("valid") is not True:
        errors.append("post-merge protected-branch baseline verifier must be valid before Phase 14 capture")

    probes = {
        "health": http_probe(args.base_url, "/health", args.timeout),
        "ready": http_probe(args.base_url, "/ready", args.timeout),
        "deep_v2": http_probe(args.base_url, "/v2/health/deep", args.timeout),
        "deep_api_v2": http_probe(args.base_url, "/api/v2/health/deep", args.timeout),
        "openapi": http_probe(args.base_url, "/openapi.json", args.timeout),
    }
    probe_errors, readiness_summary = validate_probe_set(probes, allow_optional_degraded=args.allow_optional_degraded)
    errors.extend(probe_errors)

    valid = not errors and args.claim_live_stack_readiness
    if args.require_valid and not valid:
        warnings.append("--require-valid was supplied and live-stack readiness is not valid")

    raw_dir = EVIDENCE_DIR / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    write_json(raw_dir / "git_state.json", git_state)
    write_json(raw_dir / "post_merge_baseline_verification.json", post_merge)
    for name, payload in probes.items():
        write_json(raw_dir / f"probe_{name}.json", payload)

    result = {
        "valid": valid,
        "live_stack_readiness_claimed": bool(args.claim_live_stack_readiness),
        "live_stack_readiness_recorded": valid,
        "base_url": args.base_url,
        "source_commit": head_sha,
        "target_branch": args.target_branch,
        "post_merge_baseline_valid": post_merge.get("valid") is True,
        "critical_components": readiness_summary.get("critical_components", {}),
        "optional_components": readiness_summary.get("optional_components", {}),
        "overall_statuses": readiness_summary.get("overall_statuses", {}),
        "allow_optional_degraded": bool(args.allow_optional_degraded),
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "live_learner_traffic_authorised": False,
        "runtime_kg_implementation_claimed": False,
        "errors": errors,
        "warnings": warnings,
        "generated_at_utc": utc_now(),
    }
    write_json(raw_dir / "live_stack_readiness_result.json", result)

    evidence_index = EVIDENCE_DIR / "evidence_index.md"
    evidence_index.write_text(
        "# Phase 14 Live-Stack Readiness Evidence\n\n"
        f"Generated at: {result['generated_at_utc']}\n\n"
        f"Live-stack readiness recorded: {str(valid).lower()}\n\n"
        f"Base URL: `{args.base_url}`\n\n"
        f"Source commit: `{head_sha}`\n\n"
        "Critical components required: secrets, postgres, redis, migrations, audit_repository\n\n"
        "Post-merge protected-branch baseline valid: " + str(post_merge.get("valid") is True).lower() + "\n\n"
        "Production release authorised: false\n\n"
        "Deployment authorised: false\n\n"
        "Live learner traffic authorised: false\n\n"
        "Runtime KG implementation claimed: false\n\n"
        "This evidence proves a controlled live-stack readiness probe only. It does not authorise production release.\n",
        encoding="utf-8",
    )
    sums = write_sha256sums(EVIDENCE_DIR)

    record = {
        "schema_version": 1,
        "slice": "PHASE-14-LIVE-STACK-READINESS-AUTHORITY",
        "status": "live_stack_readiness_recorded" if valid else "live_stack_readiness_not_recorded",
        "base_url": args.base_url,
        "target_branch": args.target_branch,
        "readiness_owner": args.readiness_owner.strip(),
        "source_commit": head_sha,
        "remote_target_sha": remote_sha,
        "post_merge_baseline_valid": post_merge.get("valid") is True,
        "live_stack_readiness_claimed": bool(args.claim_live_stack_readiness),
        "live_stack_readiness_recorded": valid,
        "postgres_readiness_claimed": readiness_summary.get("critical_components", {}).get("postgres") == "ok",
        "redis_readiness_claimed": readiness_summary.get("critical_components", {}).get("redis") == "ok",
        "migration_readiness_claimed": readiness_summary.get("critical_components", {}).get("migrations") == "ok",
        "audit_repository_readiness_claimed": readiness_summary.get("critical_components", {}).get("audit_repository") == "ok",
        "allow_optional_degraded": bool(args.allow_optional_degraded),
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "live_learner_traffic_authorised": False,
        "runtime_kg_implementation_claimed": False,
        "evidence_dir": EVIDENCE_DIR.as_posix(),
        "evidence_index": evidence_index.as_posix(),
        "sha256sums": sums.as_posix(),
        "updated_at_utc": result["generated_at_utc"],
    }
    write_json(RECORD_PATH, record)

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"valid: {valid}")
        for error in errors:
            print(f"ERROR: {error}")
    return 0 if valid or not args.require_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
