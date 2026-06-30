#!/usr/bin/env python3
"""
scripts/refresh_current_state_doc.py
=====================================
Recommendation 6: Refresh docs/current_state.md and produce a dated
technical state report once all regressions are resolved.

This script:
  1. Runs the key verification commands (non-destructive --check / -q forms).
  2. Collects their pass/fail status and brief stdout.
  3. Writes docs/current_state.md with accurate, timestamped findings.
  4. Optionally writes a dated technical state report to
     docs/technical_state_report_YYYY-MM-DD.md

Usage:
    python3 scripts/refresh_current_state_doc.py
    python3 scripts/refresh_current_state_doc.py --dated-report
    python3 scripts/refresh_current_state_doc.py --dry-run   # preview only

Add to Makefile:
    refresh-current-state:
        $(PYTHON) scripts/refresh_current_state_doc.py

    refresh-current-state-report:
        $(PYTHON) scripts/refresh_current_state_doc.py --dated-report
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"
CURRENT_STATE_FILE = DOCS_DIR / "current_state.md"

# ---------------------------------------------------------------------------
# Verification suite definition
# ---------------------------------------------------------------------------
# Each entry: (label, command_list, required_for_green)
CHECKS: list[tuple[str, list[str], bool]] = [
    # Runtime
    ("Runtime entrypoints",       ["make", "runtime-check"],          True),
    ("OpenAPI drift",             ["make", "openapi-check"],           True),
    ("Route inventory",           ["make", "route-inventory-check"],   True),
    ("Architecture import boundaries",
     ["bash", "-lc", "if command -v lint-imports >/dev/null; then lint-imports --config .importlinter; else .venv/bin/lint-imports --config .importlinter; fi"], True),

    # Backend unit gate
    ("Backend unit gate",
     ["python3", "-m", "pytest", "tests/unit",
      "-m", "not llm and not e2e", "--tb=line", "--no-cov", "-q"],    True),

    # Frontend
    ("Frontend lint",
     ["npm", "run", "lint", "--prefix", "app/frontend"],              True),
    ("Frontend type-check",
     ["npm", "run", "type-check", "--prefix", "app/frontend"],        True),
    ("Frontend unit tests",
     ["npm", "test", "--prefix", "app/frontend", "--", "--run"],      True),

    # Evidence / contracts
    ("PR-002R evidence",          ["make", "pr002r-check"],            True),
    ("E2E opt-in workflow",       ["make", "frontend-e2e-opt-in-workflow-check"], True),
    ("Makefile deduplication",
     ["python3", "scripts/deduplicate_makefile_targets.py"],          True),

    # Informational (not required for green gate)
    ("Staging release gate",      ["make", "staging-release-gate-check"],       False),
    ("POPIA legal evidence",      ["make", "popia-legal-check"],                False),
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

class CheckResult:
    def __init__(
        self,
        label: str,
        passed: bool,
        required: bool,
        stdout: str,
        stderr: str,
        duration_s: float,
    ) -> None:
        self.label = label
        self.passed = passed
        self.required = required
        self.stdout = stdout
        self.stderr = stderr
        self.duration_s = duration_s

    @property
    def status_emoji(self) -> str:
        if self.passed:
            return "✅"
        return "❌" if self.required else "⚠️"

    @property
    def status_text(self) -> str:
        if self.passed:
            return "PASS"
        return "FAIL" if self.required else "WARN"


def run_check(label: str, command: list[str], required: bool) -> CheckResult:
    import time
    start = time.monotonic()
    try:
        result = subprocess.run(
            command,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=300,
        )
        passed = result.returncode == 0
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
    except subprocess.TimeoutExpired:
        passed = False
        stdout = ""
        stderr = "TIMEOUT after 300 s"
    except FileNotFoundError as exc:
        passed = False
        stdout = ""
        stderr = f"Command not found: {exc}"
    duration = time.monotonic() - start
    return CheckResult(label, passed, required, stdout, stderr, duration)


# ---------------------------------------------------------------------------
# Document renderer
# ---------------------------------------------------------------------------

def render_current_state(
    results: list[CheckResult],
    assessed_at: datetime,
    git_head: str,
    git_remote_head: str,
    ahead: int,
    behind: int,
) -> str:
    assessed_at.strftime("%Y-%m-%d")
    time_str = assessed_at.strftime("%Y-%m-%d %H:%M UTC")

    required_results = [r for r in results if r.required]
    all_required_pass = all(r.passed for r in required_results)
    gate_status = "🟢 GREEN" if all_required_pass else "🔴 RED"

    passed_count = sum(1 for r in required_results if r.passed)
    total_required = len(required_results)

    rows = "\n".join(
        f"| {r.status_emoji} {r.label} | {r.status_text} | "
        f"{'Required' if r.required else 'Informational'} | {r.duration_s:.1f}s |"
        for r in results
    )

    failure_details = ""
    failed = [r for r in results if not r.passed]
    if failed:
        failure_details = "\n## Failure Details\n\n"
        for r in failed:
            failure_details += f"### {r.label}\n\n"
            if r.stdout:
                excerpt = "\n".join(r.stdout.splitlines()[-20:])
                failure_details += f"```\n{excerpt}\n```\n\n"
            if r.stderr:
                failure_details += f"**stderr:**\n```\n{r.stderr[:500]}\n```\n\n"

    sync_note = ""
    upstream_label = git_upstream_label()
    if behind > 0:
        sync_note = (
            f"\n> ⚠️ **Branch sync warning:** local HEAD is **{behind} commit(s) behind** "
            f"`{upstream_label}`. Sync before "
            f"treating these results as authoritative.\n"
        )
    elif ahead > 0:
        sync_note = (
            f"\n> ℹ️ Local HEAD is {ahead} commit(s) ahead of `{upstream_label}`.\n"
        )

    return textwrap.dedent(f"""\
        # EduBoost V2 — Current State

        **Last refreshed:** {time_str}  
        **Assessed commit:** `{git_head[:12]}`  
        **Upstream branch:** `{git_upstream_label()}`  
        **Upstream commit:** `{git_remote_head[:12]}`  
        **Branch divergence:** {ahead} ahead / {behind} behind  
        **Quality gate:** {gate_status} ({passed_count}/{total_required} required checks passing)
        {sync_note}
        > This document is generated by `scripts/refresh_current_state_doc.py`.
        > Do not edit manually — run `make refresh-current-state` to update it.

        ## Verification Results

        | Check | Status | Type | Duration |
        |---|---|---|---|
        {rows}
        {failure_details}
        ## Architecture Summary

        - **Canonical backend:** `app.api_v2:app` (FastAPI)
        - **Compatibility shim:** `app.legacy.api.main:app`
        - **Frontend:** Next.js 14 / React 18 / TypeScript (Node ≥20)
        - **Key middleware:** PostgreSQL · Redis · Alembic migrations

        ## Known Remaining Issues

        Update this section manually after each verification run.
        Remove items when resolved; add new ones as discovered.

        - [ ] _(List any remaining failures or open action items here)_

        ## Next Steps

        1. Resolve any ❌ failures above before claiming release-green status.
        2. Sync local checkout to the configured upstream branch if behind.
        3. Refresh this document again after fixes: `make refresh-current-state`.
        4. Update `docs/project_status.md` release-readiness assessment.
    """)


def render_dated_report(
    results: list[CheckResult],
    assessed_at: datetime,
    git_head: str,
) -> str:
    date_str = assessed_at.strftime("%Y-%m-%d")
    time_str = assessed_at.strftime("%Y-%m-%d %H:%M UTC")
    required_results = [r for r in results if r.required]
    gate_ok = all(r.passed for r in required_results)

    rows = "\n".join(
        f"| {r.status_emoji} {r.label} | {r.status_text} |"
        for r in results
    )

    return textwrap.dedent(f"""\
        # EduBoost V2 Technical State Report

        **Date assessed:** {date_str}  
        **Assessed commit:** `{git_head[:12]}`  
        **Generated at:** {time_str}  
        **Gate status:** {'🟢 GREEN – checkout is release-green.' if gate_ok else '🔴 RED – regressions present; not release-green.'}

        ## Verification Results

        | Check | Status |
        |---|---|
        {rows}

        ## Notes

        _(Add any contextual observations here before committing this report.)_

        ---
        *Generated by `scripts/refresh_current_state_doc.py --dated-report`*
    """)


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT), text=True
        ).strip()
    except Exception:
        return "unknown"


def git_upstream_label() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
            cwd=str(REPO_ROOT),
            text=True,
        ).strip()
    except Exception:
        return "origin/master"


def git_remote_head(upstream: str | None = None) -> str:
    upstream = upstream or git_upstream_label()
    try:
        return subprocess.check_output(
            ["git", "rev-parse", upstream],
            cwd=str(REPO_ROOT),
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def git_divergence(upstream: str | None = None) -> tuple[int, int]:
    upstream = upstream or git_upstream_label()
    try:
        ahead = int(subprocess.check_output(
            ["git", "rev-list", "--count", f"{upstream}..HEAD"],
            cwd=str(REPO_ROOT), text=True,
        ).strip())
        behind = int(subprocess.check_output(
            ["git", "rev-list", "--count", f"HEAD..{upstream}"],
            cwd=str(REPO_ROOT), text=True,
        ).strip())
        return ahead, behind
    except Exception:
        return 0, 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dated-report", action="store_true",
        help="Also write a dated technical state report.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print the generated document(s) without writing files.",
    )
    parser.add_argument(
        "--skip-checks", action="store_true",
        help="Skip running checks; use for testing the renderer only.",
    )
    args = parser.parse_args(argv)

    assessed_at = datetime.now(tz=timezone.utc)
    head = git_head()
    remote_head = git_remote_head()
    ahead, behind = git_divergence()

    if args.skip_checks:
        results = [
            CheckResult(label, True, required, "skipped", "", 0.0)
            for label, _, required in CHECKS
        ]
    else:
        results: list[CheckResult] = []
        for label, command, required in CHECKS:
            print(f"  Running: {label}...", end=" ", flush=True)
            r = run_check(label, command, required)
            results.append(r)
            print(r.status_text)

    current_state_content = render_current_state(
        results, assessed_at, head, remote_head, ahead, behind
    )

    if args.dry_run:
        print("\n--- docs/current_state.md preview ---")
        print(current_state_content)
    else:
        CURRENT_STATE_FILE.write_text(current_state_content, encoding="utf-8")
        print(f"\n[OK] Written: {CURRENT_STATE_FILE}")

    if args.dated_report:
        date_str = assessed_at.strftime("%Y-%m-%d")
        dated_report_file = DOCS_DIR / f"technical_state_report_{date_str}.md"
        dated_content = render_dated_report(results, assessed_at, head)

        if args.dry_run:
            print(f"\n--- {dated_report_file.name} preview ---")
            print(dated_content)
        else:
            dated_report_file.write_text(dated_content, encoding="utf-8")
            print(f"[OK] Written: {dated_report_file}")

    required_results = [r for r in results if r.required]
    if not all(r.passed for r in required_results):
        failed = [r.label for r in required_results if not r.passed]
        print(f"\n[FAIL] {len(failed)} required check(s) failed: {', '.join(failed)}")
        return 1

    print("\n[PASS] All required checks passed – docs refreshed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
