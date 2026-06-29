#!/usr/bin/env python3
"""Capture Phase 15 backend-backed E2E smoke evidence.

This phase proves controlled browser/API wiring against a live local stack. It
requires Phase 14 live-stack readiness to verify first and intentionally does
not authorise production release, deployment, release tagging, live learner
traffic, or runtime knowledge-graph implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

RECORD_PATH = pathlib.Path("docs/roadmap/execution/runtime_readiness/phase_15_backend_backed_e2e_record.json")
EVIDENCE_DIR = pathlib.Path("docs/release-evidence/runtime-readiness/phase-15-backend-backed-e2e")
LIVE_STACK_VERIFIER = "scripts/runtime_readiness/verify_live_stack_readiness.py"
DEFAULT_SPECS = (
    "tests/e2e/auth.setup.ts",
    "tests/e2e/learner-vertical-journey.spec.ts",
    "tests/e2e/parent-vertical-journey.spec.ts",
)
BOUNDARY_FALSE_FIELDS = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "live_learner_traffic_authorised",
    "runtime_kg_implementation_claimed",
)


@dataclass(frozen=True)
class StepResult:
    name: str
    command: list[str]
    returncode: int
    duration_seconds: float
    stdout_path: str
    stderr_path: str


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run(cmd: list[str], *, env: dict[str, str] | None = None, timeout: int | None = None) -> dict[str, Any]:
    try:
        proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=timeout)
        return {"cmd": cmd, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
    except subprocess.TimeoutExpired as exc:
        return {
            "cmd": cmd,
            "returncode": 124,
            "stdout": exc.stdout if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr if isinstance(exc.stderr, str) else "") + f"\nTIMEOUT after {timeout}s",
        }


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


def http_probe(base_url: str, path: str, timeout: int, *, method: str = "GET") -> dict[str, Any]:
    url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
    result: dict[str, Any] = {
        "url": url,
        "path": path,
        "method": method,
        "attempted": True,
        "status_code": None,
        "body_excerpt": "",
        "json": None,
        "error": "",
    }
    body = ""
    try:
        req = Request(url, headers={"User-Agent": "EduBoost-Phase15-Backend-Backed-E2E/1.0"}, method=method)
        with urlopen(req, timeout=timeout) as response:
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


def normalize_api_v2_url(value: str) -> str:
    trimmed = value.strip().rstrip("/")
    return trimmed if trimmed.endswith("/api/v2") else f"{trimmed}/api/v2"


def _run_step(name: str, command: list[str], output_dir: pathlib.Path, env: dict[str, str], timeout: int) -> StepResult:
    start = time.monotonic()
    stdout_path = output_dir / f"{name}.stdout.txt"
    stderr_path = output_dir / f"{name}.stderr.txt"
    proc = run(command, env=env, timeout=timeout)
    stdout_path.write_text(str(proc.get("stdout") or ""), encoding="utf-8")
    stderr_path.write_text(str(proc.get("stderr") or ""), encoding="utf-8")
    return StepResult(
        name=name,
        command=command,
        returncode=int(proc["returncode"]),
        duration_seconds=round(time.monotonic() - start, 3),
        stdout_path=str(stdout_path.relative_to(output_dir)),
        stderr_path=str(stderr_path.relative_to(output_dir)),
    )


def validate_api_probes(probes: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    health = probes.get("api_health") or {}
    if health.get("status_code") != 200:
        errors.append("API /health must return HTTP 200")
    elif not isinstance(health.get("json"), dict) or health["json"].get("status") != "ok":
        errors.append("API /health JSON status must be ok")
    ready = probes.get("api_ready") or {}
    if ready.get("status_code") != 200:
        errors.append("API /ready must return HTTP 200")
    deep = probes.get("api_deep") or {}
    if deep.get("status_code") != 200:
        errors.append("API /api/v2/health/deep must return HTTP 200")
    frontend = probes.get("frontend_root") or {}
    if frontend.get("status_code") != 200:
        errors.append("frontend root must return HTTP 200 before backend-backed E2E capture")
    elif len(str(frontend.get("body_excerpt") or "").strip()) < 20:
        errors.append("frontend root must not be blank before backend-backed E2E capture")
    rewrite = probes.get("frontend_api_rewrite") or {}
    if rewrite.get("status_code") != 200:
        errors.append("frontend /api/v2/system/health rewrite must return HTTP 200")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-base-url", default="http://127.0.0.1:8000/api/v2")
    parser.add_argument("--frontend-base-url", default="http://127.0.0.1:3050")
    parser.add_argument("--target-branch", default="master")
    parser.add_argument("--spec", action="append", default=[], help="Playwright spec to run. Defaults to controlled backend-backed smoke specs.")
    parser.add_argument("--skip-install", action="store_true")
    parser.add_argument("--skip-browser-install", action="store_true")
    parser.add_argument("--reuse-existing-frontend", action="store_true", help="Set PLAYWRIGHT_SKIP_WEB_SERVER=1; otherwise Playwright may start the configured frontend server.")
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--playwright-timeout", type=int, default=1200)
    parser.add_argument("--claim-backend-backed-e2e", action="store_true")
    parser.add_argument("--e2e-owner", default="")
    parser.add_argument("--require-valid", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    api_base_url = normalize_api_v2_url(args.api_base_url)
    api_root_url = api_base_url[: -len("/api/v2")] if api_base_url.endswith("/api/v2") else api_base_url
    frontend_base_url = args.frontend_base_url.rstrip("/")
    specs = tuple(args.spec or DEFAULT_SPECS)

    if any("mocked-api" in spec or "mock" in pathlib.Path(spec).name.lower() for spec in specs):
        errors.append("backend-backed E2E capture must not run mocked Playwright specs")
    if args.claim_backend_backed_e2e and not args.e2e_owner.strip():
        errors.append("--e2e-owner is required when claiming backend-backed E2E readiness")

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
        errors.append(f"backend-backed E2E readiness must be captured from {args.target_branch}; current branch is {branch}")
    if head_sha and remote_sha and head_sha != remote_sha:
        errors.append(f"HEAD must match origin/{args.target_branch}; HEAD={head_sha}, origin/{args.target_branch}={remote_sha}")
    if tracked_status["stdout"].strip():
        errors.append("tracked worktree must be clean before backend-backed E2E capture")

    live_stack = collect_verifier(LIVE_STACK_VERIFIER)
    if live_stack.get("valid") is not True:
        errors.append("Phase 14 live-stack readiness verifier must be valid before Phase 15 capture")

    probes = {
        "api_health": http_probe(api_root_url, "/health", args.timeout),
        "api_ready": http_probe(api_root_url, "/ready", args.timeout),
        "api_deep": http_probe(api_root_url, "/api/v2/health/deep", args.timeout),
        "frontend_root": http_probe(frontend_base_url, "/", args.timeout),
        "frontend_api_rewrite": http_probe(frontend_base_url, "/api/v2/system/health", args.timeout),
    }
    errors.extend(validate_api_probes(probes))

    raw_dir = EVIDENCE_DIR / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    write_json(raw_dir / "git_state.json", git_state)
    write_json(raw_dir / "live_stack_readiness_verification.json", live_stack)
    for name, payload in probes.items():
        write_json(raw_dir / f"probe_{name}.json", payload)

    env = os.environ.copy()
    env["CI"] = "true"
    env["PLAYWRIGHT_MOCK_API"] = "0"
    env["PLAYWRIGHT_BASE_URL"] = frontend_base_url
    env["FRONTEND_BASE_URL"] = frontend_base_url
    env["API_BASE_URL"] = api_base_url
    env["NEXT_PUBLIC_API_URL"] = api_base_url
    env["NEXT_PUBLIC_APP_ENV"] = env.get("NEXT_PUBLIC_APP_ENV", "development")
    env["NEXT_PUBLIC_ENABLE_DEV_SESSION"] = env.get("NEXT_PUBLIC_ENABLE_DEV_SESSION", "true")
    if args.reuse_existing_frontend:
        env["PLAYWRIGHT_SKIP_WEB_SERVER"] = "1"
    else:
        env.pop("PLAYWRIGHT_SKIP_WEB_SERVER", None)

    commands: list[tuple[str, list[str], int]] = [("pnpm_version", ["pnpm", "--version"], 60)]
    if not args.skip_install:
        commands.extend([
            ("root_pnpm_install", ["pnpm", "install", "--frozen-lockfile"], 900),
            ("frontend_pnpm_install", ["pnpm", "--dir", "app/frontend", "install", "--frozen-lockfile"], 900),
        ])
    commands.append(("playwright_version", ["pnpm", "exec", "playwright", "--version"], 120))
    if not args.skip_browser_install:
        commands.append(("playwright_install_chromium", ["pnpm", "exec", "playwright", "install", "chromium"], 900))
    commands.append((
        "playwright_backend_backed_smoke",
        ["pnpm", "exec", "playwright", "test", *specs, "--project=chromium", "--reporter=list"],
        args.playwright_timeout,
    ))

    step_results = [_run_step(name, command, raw_dir, env, timeout) for name, command, timeout in commands]
    steps_valid = all(step.returncode == 0 for step in step_results)
    if not steps_valid:
        errors.append("one or more backend-backed E2E execution steps failed")

    payload: dict[str, Any] = {
        "valid": len(errors) == 0 and bool(args.claim_backend_backed_e2e),
        "schema_version": 1,
        "slice": "PHASE-15-BACKEND-BACKED-E2E-AUTHORITY",
        "captured_at": utc_now(),
        "target_branch": args.target_branch,
        "source_commit": head_sha,
        "remote_target_sha": remote_sha,
        "api_base_url": api_base_url,
        "frontend_base_url": frontend_base_url,
        "e2e_owner": args.e2e_owner.strip() or None,
        "backend_backed_e2e_claimed": bool(args.claim_backend_backed_e2e),
        "backend_backed_e2e_recorded": len(errors) == 0 and bool(args.claim_backend_backed_e2e),
        "e2e_scope": "backend_backed_smoke",
        "full_production_e2e_claimed": False,
        "live_stack_readiness_valid": bool(live_stack.get("valid")),
        "playwright_mock_api": env["PLAYWRIGHT_MOCK_API"],
        "mocked_api_used": False,
        "specs": list(specs),
        "steps": [asdict(step) for step in step_results],
        "errors": errors,
        "warnings": warnings,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "live_learner_traffic_authorised": False,
        "runtime_kg_implementation_claimed": False,
    }
    write_json(raw_dir / "backend_backed_e2e_result.json", payload)

    evidence_index = EVIDENCE_DIR / "evidence_index.md"
    evidence_index.write_text(
        "# Phase 15 Backend-Backed E2E Smoke Evidence\n\n"
        f"Captured at: {payload['captured_at']}\n\n"
        f"Source commit: `{head_sha}`\n\n"
        f"Target branch: `{args.target_branch}`\n\n"
        f"API base URL: `{api_base_url}`\n\n"
        f"Frontend base URL: `{frontend_base_url}`\n\n"
        "Required predecessor: Phase 14 live-stack readiness verifier valid.\n\n"
        "Mocked API used: false\n\n"
        "E2E scope: backend_backed_smoke\n\n"
        "Production release authorised: false\n\n"
        "Deployment authorised: false\n\n"
        "Release tag authorised: false\n\n"
        "Live learner traffic authorised: false\n\n"
        "Runtime KG implementation claimed: false\n",
        encoding="utf-8",
    )
    sums_path = write_sha256sums(EVIDENCE_DIR)

    record = {
        "schema_version": 1,
        "slice": "PHASE-15-BACKEND-BACKED-E2E-AUTHORITY",
        "status": "backend_backed_e2e_recorded" if payload["valid"] else "backend_backed_e2e_capture_invalid",
        "captured_at": payload["captured_at"],
        "target_branch": args.target_branch,
        "source_commit": head_sha,
        "remote_target_sha": remote_sha,
        "api_base_url": api_base_url,
        "frontend_base_url": frontend_base_url,
        "e2e_owner": args.e2e_owner.strip() or None,
        "backend_backed_e2e_claimed": bool(args.claim_backend_backed_e2e),
        "backend_backed_e2e_recorded": bool(payload["valid"]),
        "e2e_scope": "backend_backed_smoke",
        "full_production_e2e_claimed": False,
        "live_stack_readiness_valid": bool(live_stack.get("valid")),
        "playwright_mock_api": env["PLAYWRIGHT_MOCK_API"],
        "mocked_api_used": False,
        "production_release_authorised": False,
        "deployment_authorised": False,
        "release_tag_authorised": False,
        "live_learner_traffic_authorised": False,
        "runtime_kg_implementation_claimed": False,
        "evidence_dir": EVIDENCE_DIR.as_posix(),
        "evidence_index": evidence_index.as_posix(),
        "sha256sums": sums_path.as_posix(),
    }
    write_json(RECORD_PATH, record)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("valid:", payload["valid"])
        for error in errors:
            print("ERROR:", error)
    if args.require_valid and not payload["valid"]:
        return 1
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
