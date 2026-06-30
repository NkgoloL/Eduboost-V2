from __future__ import annotations

from scripts.verify_repo_state import REPO_ROOT, RepoState, run_checks


def make_state(**overrides: object) -> RepoState:
    data = {
        "root": str(REPO_ROOT),
        "branch": "master",
        "head_sha": "abc123",
        "head_message": "Merge pull request #52 from NkgoloL/chore/slow-query-logging",
        "remote_url": "https://github.com/NkgoloL/Eduboost-V2.git",
        "dirty": False,
    }
    data.update(overrides)
    return RepoState(**data)


def test_repo_state_check_accepts_canonical_release_state() -> None:
    results = run_checks(
        make_state(),
        expected_branch="master",
        allowed_remotes=("https://github.com/NkgoloL/Eduboost-V2.git",),
        freshness_marker="Merge pull request #52 from NkgoloL/chore/slow-query-logging",
        allow_dirty=False,
        allow_branch_mismatch=False,
    )

    assert [result for result in results if not result.ok] == []


def test_repo_state_check_rejects_wrong_branch_unless_allowed() -> None:
    strict = run_checks(
        make_state(branch="codex/pr1-repo-truth"),
        expected_branch="master",
        allowed_remotes=("https://github.com/NkgoloL/Eduboost-V2.git",),
        freshness_marker="Merge pull request #52 from NkgoloL/chore/slow-query-logging",
        allow_dirty=False,
        allow_branch_mismatch=False,
    )
    relaxed = run_checks(
        make_state(branch="codex/pr1-repo-truth"),
        expected_branch="master",
        allowed_remotes=("https://github.com/NkgoloL/Eduboost-V2.git",),
        freshness_marker="Merge pull request #52 from NkgoloL/chore/slow-query-logging",
        allow_dirty=False,
        allow_branch_mismatch=True,
    )

    assert any(result.name == "branch" and not result.ok for result in strict)
    assert all(result.ok for result in relaxed)


def test_repo_state_check_rejects_dirty_tree_without_override() -> None:
    results = run_checks(
        make_state(dirty=True),
        expected_branch="master",
        allowed_remotes=("https://github.com/NkgoloL/Eduboost-V2.git",),
        freshness_marker="Merge pull request #52 from NkgoloL/chore/slow-query-logging",
        allow_dirty=False,
        allow_branch_mismatch=False,
    )

    assert any(result.name == "working-tree" and not result.ok for result in results)
