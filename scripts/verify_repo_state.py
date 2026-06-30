#!/usr/bin/env python3
"""Verify repository provenance for release evidence."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ALLOWED_REMOTES = (
    "https://github.com/NkgoloL/Eduboost-V2.git",
    "git@github.com:NkgoloL/Eduboost-V2.git",
    "https://github.com/userxrebornbackup-ux/Eduboost-V2.git",
    "git@github.com:userxrebornbackup-ux/Eduboost-V2.git",
)
DEFAULT_FRESHNESS_MARKER = "Merge pull request #52 from NkgoloL/chore/slow-query-logging"


@dataclass(frozen=True)
class RepoState:
    root: str
    branch: str
    head_sha: str
    head_message: str
    remote_url: str
    dirty: bool


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str


def git(args: list[str], cwd: Path = REPO_ROOT) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def collect_state(cwd: Path = REPO_ROOT) -> RepoState:
    root = Path(git(["rev-parse", "--show-toplevel"], cwd=cwd)).resolve()
    branch = git(["branch", "--show-current"], cwd=root) or "DETACHED"
    head_sha = git(["rev-parse", "HEAD"], cwd=root)
    head_message = git(["log", "-1", "--pretty=%B"], cwd=root).splitlines()[0]
    remote_url = git(["config", "--get", "remote.origin.url"], cwd=root)
    dirty = bool(git(["status", "--porcelain"], cwd=root))
    return RepoState(
        root=str(root),
        branch=branch,
        head_sha=head_sha,
        head_message=head_message,
        remote_url=remote_url,
        dirty=dirty,
    )


def run_checks(
    state: RepoState,
    *,
    expected_branch: str,
    allowed_remotes: tuple[str, ...],
    freshness_marker: str,
    allow_dirty: bool,
    allow_branch_mismatch: bool,
) -> list[CheckResult]:
    branch_ok = state.branch == expected_branch or allow_branch_mismatch
    marker_ok = freshness_marker in state.head_message
    if freshness_marker == "HEAD":
        marker_ok = bool(state.head_sha)
    root = Path(state.root)
    root_ok = (root / "TODO.md").exists() and (root / "app").is_dir()

    return [
        CheckResult(
            "repository-root",
            root_ok,
            f"root is {state.root}",
        ),
        CheckResult(
            "remote-url",
            state.remote_url in allowed_remotes,
            f"remote origin is {state.remote_url}",
        ),
        CheckResult(
            "branch",
            branch_ok,
            f"branch is {state.branch}; expected {expected_branch}",
        ),
        CheckResult(
            "head-sha",
            bool(state.head_sha),
            f"head SHA is {state.head_sha}",
        ),
        CheckResult(
            "freshness-marker",
            marker_ok,
            f"head message is {state.head_message!r}",
        ),
        CheckResult(
            "working-tree",
            not state.dirty or allow_dirty,
            "working tree is dirty" if state.dirty else "working tree is clean",
        ),
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-branch", default="master")
    parser.add_argument("--freshness-marker", default=DEFAULT_FRESHNESS_MARKER)
    parser.add_argument("--allow-dirty", action="store_true")
    parser.add_argument(
        "--allow-branch-mismatch",
        action="store_true",
        help="Allow feature/PR branches while still reporting the expected release branch.",
    )
    parser.add_argument(
        "--allowed-remote",
        action="append",
        default=[],
        help="Allowed origin URL. May be passed more than once.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    state = collect_state()
    allowed_remotes = tuple(args.allowed_remote) or DEFAULT_ALLOWED_REMOTES
    results = run_checks(
        state,
        expected_branch=args.expected_branch,
        allowed_remotes=allowed_remotes,
        freshness_marker=args.freshness_marker,
        allow_dirty=args.allow_dirty,
        allow_branch_mismatch=args.allow_branch_mismatch,
    )

    if args.json:
        print(json.dumps({"state": asdict(state), "checks": [asdict(r) for r in results]}, indent=2))
    else:
        print("Repository state verification")
        for result in results:
            status = "PASS" if result.ok else "FAIL"
            print(f"- {status} {result.name}: {result.detail}")

    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
