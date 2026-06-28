#!/usr/bin/env python3
"""Run the TA Phase 06 Playwright/E2E execution authority gate.

The authority is intentionally scoped to the deterministic mocked frontend
journeys. It proves Playwright ownership, lockfile discipline, browser
installation, config discovery, and executable E2E command wiring without
claiming full backend-backed production journey readiness.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "release-evidence" / "technical-audit" / "e2e-playwright-authority" / "raw"


@dataclass(frozen=True)
class StepResult:
    name: str
    command: list[str]
    returncode: int
    duration_seconds: float
    stdout_path: str
    stderr_path: str


def _run_step(name: str, command: list[str], output_dir: Path, env: dict[str, str], timeout: int) -> StepResult:
    start = time.monotonic()
    stdout_path = output_dir / f"{name}.stdout.txt"
    stderr_path = output_dir / f"{name}.stderr.txt"
    try:
        proc = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        returncode = proc.returncode
        stdout = proc.stdout
        stderr = proc.stderr
    except subprocess.TimeoutExpired as exc:
        returncode = 124
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = (exc.stderr if isinstance(exc.stderr, str) else "") + f"\nTIMEOUT after {timeout}s"
    duration = time.monotonic() - start
    stdout_path.write_text(stdout or "", encoding="utf-8")
    stderr_path.write_text(stderr or "", encoding="utf-8")
    return StepResult(
        name=name,
        command=command,
        returncode=returncode,
        duration_seconds=round(duration, 3),
        stdout_path=str(stdout_path.relative_to(output_dir)),
        stderr_path=str(stderr_path.relative_to(output_dir)),
    )


def run_authority(output_dir: Path = DEFAULT_OUTPUT_DIR, install_browsers: bool = True, run_tests: bool = True) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.setdefault("CI", "true")
    env.setdefault("PLAYWRIGHT_MOCK_API", "1")
    env.setdefault("PLAYWRIGHT_BASE_URL", "http://127.0.0.1:3050")
    env.setdefault("FRONTEND_BASE_URL", env["PLAYWRIGHT_BASE_URL"])
    env.setdefault("LEARNER_JOURNEY_PATH", "/")
    env.setdefault("PARENT_JOURNEY_PATH", "/")

    commands: list[tuple[str, list[str], int]] = [
        ("pnpm_version", ["pnpm", "--version"], 60),
        ("root_pnpm_install", ["pnpm", "install", "--frozen-lockfile"], 900),
        ("frontend_pnpm_install", ["pnpm", "--dir", "app/frontend", "install", "--frozen-lockfile"], 900),
        ("playwright_version", ["pnpm", "exec", "playwright", "--version"], 120),
    ]
    if install_browsers:
        commands.append(("playwright_install_chromium", ["pnpm", "exec", "playwright", "install", "chromium"], 900))
    if run_tests:
        commands.append((
            "playwright_mocked_journeys",
            [
                "pnpm",
                "exec",
                "playwright",
                "test",
                "tests/e2e/learner-mocked-api-journey.spec.ts",
                "tests/e2e/parent-mocked-api-journey.spec.ts",
                "--project=chromium",
                "--reporter=list",
            ],
            1200,
        ))

    results = [_run_step(name, command, output_dir, env, timeout) for name, command, timeout in commands]
    payload = {
        "valid": all(result.returncode == 0 for result in results),
        "authority_scope": "mocked_frontend_playwright_journeys",
        "remote_ci_run_claimed": False,
        "full_backend_backed_e2e_claimed": False,
        "steps": [asdict(result) for result in results],
    }
    (output_dir / "e2e_playwright_authority_result.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--skip-browser-install", action="store_true")
    parser.add_argument("--skip-tests", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    payload = run_authority(args.output_dir, install_browsers=not args.skip_browser_install, run_tests=not args.skip_tests)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for step in payload["steps"]:
            print(f"{'PASS' if step['returncode'] == 0 else 'FAIL'} {step['name']} rc={step['returncode']}")
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
