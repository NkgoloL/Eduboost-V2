#!/usr/bin/env python3
"""EduBoost tooling subprocess wrapper.

Provides resolved-path subprocess execution for all EduBoost tooling scripts.
Bandit findings B603 (subprocess_without_shell_equals_true) and B607
(start_process_with_partial_path) are suppressed here at the single wrapper
call site rather than at every call site across the codebase.

``run()`` is for argv-list commands and never invokes a shell — it rejects
``shell=True`` explicitly (see below) rather than silently mishandling it.
For the small number of callers that genuinely need shell semantics (pipes,
redirects, `&&`), use ``run_shell()`` instead, which takes a command string
and is the single, narrowly-scoped place B604 is suppressed.

Usage:
    from scripts._subprocess import run, run_shell, check_output, run_git

    result = run(["python", "manage.py", "migrate"])
    output = check_output(["git", "status"])
    git_status = run_git("status", "--porcelain")
    shell_result = run_shell("pytest tests/ -k smoke | tee smoke.log")
"""
from __future__ import annotations

import os
import shutil
import subprocess  # nosec B404 — this is the wrapper module; all calls go through run()/run_shell() above
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any


def _resolve(cmd: Sequence[str]) -> list[str]:
    """Resolve first element via shutil.which to prevent PATH-hijacking.

    Searches both the system PATH and the active venv bin directory so that
    both activated and un-activated venv sessions work correctly.
    """
    if not cmd:
        return list(cmd)
    # Add venv bin/ to PATH so shutil.which finds console_scripts (alembic, mypy, etc.)
    venv_bin = str(Path(sys.executable).parent.resolve())
    extra_path = venv_bin + os.pathsep + os.environ.get("PATH", "")
    resolved = shutil.which(cmd[0], path=extra_path)
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
    """Run a subprocess command (argv list) with resolved path.

    ``cmd`` must be a sequence of arguments (e.g. ``["git", "status"]``),
    all hardcoded or validated before calling this function. No shell is
    invoked. ``shell=True`` is rejected explicitly: ``_resolve()`` indexes
    ``cmd[0]`` and falls back to ``list(cmd)``, both of which silently
    shred a *string* command into individual characters rather than
    running it — passing shell=True here previously failed this way at
    every call site that did it. Use ``run_shell()`` if shell semantics
    are genuinely required.

    Returns: subprocess.CompletedProcess[str]
    """
    if kwargs.get("shell"):
        raise TypeError(
            "run() does not support shell=True (it silently mis-executes "
            "string commands — see module docstring). Use run_shell() instead."
        )
    if isinstance(cmd, (str, bytes)):
        raise TypeError(
            "run() expects an argv sequence, e.g. ['git', 'status'], not a "
            "single string. Use run_shell() for string commands."
        )
    resolved = _resolve(cmd)
    return subprocess.run(  # nosec B603 B607 — path resolved above, no shell=True
        resolved,
        cwd=cwd,
        capture_output=capture_output,
        text=text,
        check=check,
        timeout=timeout,
        env=env,
        **kwargs,
    )


def run_shell(
    command: str,
    *,
    cwd: str | Path | None = None,
    capture_output: bool = True,
    text: bool = True,
    check: bool = False,
    timeout: int | None = None,
    env: dict[str, str] | None = None,
    **kwargs: Any,
) -> subprocess.CompletedProcess[str]:
    """Run a shell command string (pipes, redirects, `&&`, etc.).

    ``command`` must be a hardcoded string or one assembled entirely from
    trusted, non-user-controlled configuration (e.g. a gate/command
    registry checked into the repo) — never from unsanitized external
    input. This is the single, narrowly-scoped location where B604
    (any_other_function_with_shell_equals_true) is suppressed for shell
    invocations; callers should not add their own nosec for shell=True.

    Returns: subprocess.CompletedProcess[str]
    """
    return subprocess.run(
        command,
        shell=True,  # nosec B602 — trusted command strings only, single suppression point
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


__all__ = ["run", "run_shell", "check_output", "run_python", "run_git"]
