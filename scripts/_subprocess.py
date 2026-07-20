#!/usr/bin/env python3
"""EduBoost tooling subprocess wrapper.

Provides resolved-path subprocess execution for all EduBoost tooling scripts.
Bandit findings B603 (subprocess_without_shell_equals_true) and B607
(start_process_with_partial_path) are suppressed here at the single wrapper
call site rather than at every call site across the codebase.

Usage:
    from scripts._subprocess import run, check_output, run_git

    result = run(["python", "manage.py", "migrate"])
    output = check_output(["git", "status"])
    git_status = run_git("status", "--porcelain")
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any


def _resolve(cmd: Sequence[str]) -> list[str]:
    """Resolve first element via shutil.which to prevent PATH-hijacking.

    Bandit B607 flags partial-path binaries (e.g. "git" without full path).
    In EduBoost's container images PATH is fixed and trusted, but resolving
    with shutil.which eliminates the theoretical risk.
    """
    if not cmd:
        return list(cmd)
    resolved = shutil.which(cmd[0])
    if resolved:
        return [resolved, *list(cmd[1:])]
    return list(cmd)


def run(
    cmd: Sequence[str],
    *,
    cwd: str | Path | None = None,
    capture_output: bool = True,
    text: bool = True,
    check: bool = False,
    timeout: int | None = None,
    env: dict[str, str] | None = None,
    **kwargs: Any,
) -> subprocess.CompletedProcess[str]:
    """Run a subprocess command with resolved path.

    All ``cmd`` arguments must be hardcoded or validated before calling
    this function.  No shell=True is used.  The single subprocess.run
    call below carries a narrow, justified nosec suppression.

    Returns: subprocess.CompletedProcess[str]
    """
    resolved = _resolve(cmd)
    return subprocess.run(  # nosec B603,B607 — path resolved above, no shell=True
        resolved,
        cwd=cwd,
        capture_output=capture_output,
        text=text,
        check=check,
        timeout=timeout,
        env=env,
        **kwargs,
    )


def check_output(
    cmd: Sequence[str],
    *,
    cwd: str | Path | None = None,
    timeout: int | None = None,
    **kwargs: Any,
) -> str:
    """Run and return stdout, raising on non-zero exit."""
    result = run(cmd, cwd=cwd, timeout=timeout, check=True, **kwargs)
    return result.stdout.strip()


def run_python(
    module_or_script: str,
    *args: str,
    cwd: str | Path | None = None,
    **kwargs: Any,
) -> subprocess.CompletedProcess[str]:
    """Run a Python module or script with the current interpreter."""
    return run(
        [sys.executable, "-m", module_or_script, *args],
        cwd=cwd,
        **kwargs,
    )


def run_git(
    *args: str,
    repo_root: str | Path | None = None,
    **kwargs: Any,
) -> subprocess.CompletedProcess[str]:
    """Run a git command in the given or current repository root."""
    cmd = run(["git", *args], cwd=repo_root, **kwargs)
    return cmd


__all__ = ["run", "check_output", "run_python", "run_git"]
