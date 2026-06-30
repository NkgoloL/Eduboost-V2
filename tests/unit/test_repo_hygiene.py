from pathlib import Path

from scripts.maintenance.check_repo_hygiene import ROOT_ALLOWED_FILES, run_checks


def test_repo_hygiene_has_no_current_failures() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    failures = run_checks(repo_root)

    assert failures == []


def test_operational_root_configs_are_explicitly_allowed() -> None:
    assert 'prometheus.yml' in ROOT_ALLOWED_FILES
    assert 'Makefile.arch' in ROOT_ALLOWED_FILES
