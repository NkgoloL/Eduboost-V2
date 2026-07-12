#!/usr/bin/env python3
"""Execution-7 targeted baseline reconciliation helpers."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

TEST_ENVIRONMENT = {
    "APP_ENV": "test",
    "ENVIRONMENT": "test",
    "DEBUG": "false",
    "PYTHONHASHSEED": "0",
}

FALSE_RELEASE_BOUNDARIES = (
    "production_release_authorised",
    "deployment_authorised",
    "release_tag_authorised",
    "public_beta_authorised",
    "live_learner_traffic_authorised",
    "billing_launch_authorised",
    "live_payment_processing_authorised",
    "execution_8_authorised",
)


def sanitized_test_environment(base: Mapping[str, str] | None = None) -> dict[str, str]:
    """Return a deterministic test environment, overriding contaminated shell values."""
    env = dict(os.environ if base is None else base)
    env.update(TEST_ENVIRONMENT)
    return env


def assert_archival_or_current_valid(
    result: Mapping[str, Any],
    *,
    authority_key: str = "authority_valid",
    valid_key: str = "valid",
) -> None:
    """Assert that a historical/current authority remains valid after progression."""
    assert result.get(authority_key) is True, result.get("errors", result)
    assert result.get(valid_key) is True, result.get("errors", result)
    assert not result.get("errors", []), result.get("errors")


def assert_release_boundaries_closed(result: Mapping[str, Any]) -> None:
    """Ensure reconciliation does not authorise downstream release actions."""
    for key in FALSE_RELEASE_BOUNDARIES:
        if key in result:
            assert result[key] is False, f"{key} must remain false"


@dataclass(frozen=True)
class TimedProbeResult:
    nodeid: str
    command: list[str]
    started_at_epoch: float
    completed_at_epoch: float
    duration_seconds: float
    exit_code: int | None
    timed_out: bool
    stdout_path: str
    stderr_path: str
    green: bool


def run_pytest_probe(
    root: Path,
    nodeid: str,
    output_dir: Path,
    *,
    timeout_seconds: int = 120,
    python_bin: str | None = None,
) -> dict[str, Any]:
    """Run one node with faulthandler and bounded timeout for precise diagnosis."""
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_id = nodeid.replace("/", "_").replace(":", "_")
    stdout_path = output_dir / f"{safe_id}.stdout.txt"
    stderr_path = output_dir / f"{safe_id}.stderr.txt"
    python = python_bin or sys.executable
    command = [
        python,
        "-X",
        "faulthandler",
        "-m",
        "pytest",
        "-c",
        "pytest.ini",
        nodeid,
        "--no-cov",
        "-vv",
        "--tb=short",
        "-ra",
    ]
    started = time.time()
    try:
        completed = subprocess.run(
            command,
            cwd=root,
            env=sanitized_test_environment(),
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        exit_code: int | None = completed.returncode
        timed_out = False
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        exit_code = None
        timed_out = True
        stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        stderr += f"\nTimed out after {timeout_seconds} seconds.\n"
    completed_at = time.time()
    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")
    result = TimedProbeResult(
        nodeid=nodeid,
        command=command,
        started_at_epoch=started,
        completed_at_epoch=completed_at,
        duration_seconds=round(completed_at - started, 3),
        exit_code=exit_code,
        timed_out=timed_out,
        stdout_path=str(stdout_path),
        stderr_path=str(stderr_path),
        green=exit_code == 0 and not timed_out,
    )
    payload = asdict(result)
    (output_dir / f"{safe_id}.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return payload


def verify_environment_contract(env: Mapping[str, str]) -> list[str]:
    errors: list[str] = []
    for key, expected in TEST_ENVIRONMENT.items():
        if env.get(key) != expected:
            errors.append(f"{key} must be {expected!r}, got {env.get(key)!r}")
    return errors


def verify_mcp_compatibility(root: Path) -> dict[str, Any]:
    compat = root / "tools" / "etl" / "mcp_compat.py"
    errors: list[str] = []
    if not compat.exists():
        errors.append("tools/etl/mcp_compat.py is missing")
    else:
        text = compat.read_text(encoding="utf-8")
        for required in ("mcp.server.fastmcp", "fastmcp", "FastMCP"):
            if required not in text:
                errors.append(f"MCP compatibility adapter missing {required}")
    for rel in (
        "tools/etl/etl_mcp_server.py",
        "tools/etl/etl_mcp_server_v2.py",
        "tools/etl/etl_mcp_server_v3_additions.py",
    ):
        path = root / rel
        if not path.exists() or "tools.etl.mcp_compat import FastMCP" not in path.read_text(encoding="utf-8"):
            errors.append(f"{rel} is not wired to the compatibility adapter")
    return {"valid": not errors, "errors": errors}
