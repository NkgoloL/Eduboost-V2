#!/usr/bin/env python3
"""Run the Phase 03 frontend/tooling authority commands and capture evidence.

The runner is intentionally strict: the default path includes a frozen-lockfile
install so that passing evidence proves the frontend lockfile and scripts are
usable under pnpm. Use --skip-install only for diagnostics, not passing evidence.
"""
from __future__ import annotations
import subprocess  # nosec B404 — subprocess constants support the controlled wrapper

import argparse
import json
import os
from scripts._subprocess import run
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_ROOT = REPO_ROOT / "app" / "frontend"
EXPECTED_STEP_NAMES = (
    "pnpm_version",
    "pnpm_install_frozen_lockfile",
    "frontend_env_check",
    "frontend_type_check",
    "frontend_lint",
    "frontend_vitest",
)


@dataclass(frozen=True)
class CommandResult:
    name: str
    command: list[str]
    cwd: str
    returncode: int
    duration_seconds: float
    stdout_file: str
    stderr_file: str


def _git(args: list[str], default: str) -> str:
    try:
        completed = run(
            ["git", *args],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        return default
    if completed.returncode != 0:
        return default
    value = completed.stdout.strip()
    return value or default


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run_step(name: str, command: list[str], cwd: Path, output_dir: Path, timeout: int) -> CommandResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = output_dir / f"{name}_stdout.txt"
    stderr_path = output_dir / f"{name}_stderr.txt"
    started = time.monotonic()
    try:
        completed = run(
            command,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            env={**os.environ, "CI": os.environ.get("CI", "1")},
        )
        returncode = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except FileNotFoundError as exc:
        returncode = 127
        stdout = ""
        stderr = f"{exc}\n"
    except subprocess.TimeoutExpired as exc:
        returncode = 124
        stdout = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        stderr = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
        stderr += f"\nCommand timed out after {timeout} seconds.\n"
    duration = time.monotonic() - started
    stdout_path.write_text(stdout, encoding="utf-8", errors="replace")
    stderr_path.write_text(stderr, encoding="utf-8", errors="replace")
    result = CommandResult(
        name=name,
        command=command,
        cwd=str(cwd.relative_to(REPO_ROOT) if cwd.is_relative_to(REPO_ROOT) else cwd),
        returncode=returncode,
        duration_seconds=round(duration, 3),
        stdout_file=str(stdout_path.relative_to(output_dir)),
        stderr_file=str(stderr_path.relative_to(output_dir)),
    )
    _write_json(output_dir / f"{name}_result.json", asdict(result))
    return result


def _commands(skip_install: bool) -> list[tuple[str, list[str], Path]]:
    commands: list[tuple[str, list[str], Path]] = [
        ("pnpm_version", ["pnpm", "--version"], REPO_ROOT),
    ]
    if not skip_install:
        commands.append(
            (
                "pnpm_install_frozen_lockfile",
                ["pnpm", "--dir", str(FRONTEND_ROOT.relative_to(REPO_ROOT)), "install", "--frozen-lockfile"],
                REPO_ROOT,
            )
        )
    commands.extend(
        [
            ("frontend_env_check", ["pnpm", "--dir", str(FRONTEND_ROOT.relative_to(REPO_ROOT)), "run", "env-check"], REPO_ROOT),
            ("frontend_type_check", ["pnpm", "--dir", str(FRONTEND_ROOT.relative_to(REPO_ROOT)), "run", "type-check"], REPO_ROOT),
            ("frontend_lint", ["pnpm", "--dir", str(FRONTEND_ROOT.relative_to(REPO_ROOT)), "run", "lint"], REPO_ROOT),
            ("frontend_vitest", ["pnpm", "--dir", str(FRONTEND_ROOT.relative_to(REPO_ROOT)), "run", "test"], REPO_ROOT),
        ]
    )
    return commands


def run(output_dir: Path, *, timeout: int, skip_install: bool) -> dict[str, object]:
    results = [_run_step(name, command, cwd, output_dir, timeout) for name, command, cwd in _commands(skip_install)]
    expected = list(EXPECTED_STEP_NAMES)
    if skip_install:
        expected.remove("pnpm_install_frozen_lockfile")
    missing = sorted(set(expected) - {result.name for result in results})
    failed = [asdict(result) for result in results if result.returncode != 0]
    payload: dict[str, object] = {
        "valid": not missing and not failed and not skip_install,
        "diagnostic_only": skip_install,
        "authority": "frontend-tooling-authority",
        "source_commit": _git(["rev-parse", "HEAD"], "unknown"),
        "branch": _git(["rev-parse", "--abbrev-ref", "HEAD"], "unknown"),
        "frontend_root": str(FRONTEND_ROOT.relative_to(REPO_ROOT)),
        "expected_steps": expected,
        "missing_steps": missing,
        "failed_steps": failed,
        "steps": [asdict(result) for result in results],
    }
    _write_json(output_dir / "frontend_tooling_authority_result.json", payload)
    return payload


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--skip-install", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    payload = run(args.output_dir, timeout=args.timeout, skip_install=args.skip_install)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"frontend tooling authority valid={payload['valid']}")
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
