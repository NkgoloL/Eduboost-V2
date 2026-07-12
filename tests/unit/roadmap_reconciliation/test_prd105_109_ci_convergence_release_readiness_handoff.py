from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from scripts.production_readiness.apply_prd105_109_ci_convergence_release_readiness_handoff import apply

TRACKED_OUTPUTS = (
    Path("docs/roadmap/production_readiness/prd1_ci_convergence_release_readiness_handoff.json"),
    Path("docs/roadmap/production_readiness/prd_105_109_ci_convergence_release_readiness_handoff_record.json"),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def prd1_handoff_repo(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict[str, str]]:
    source = Path.cwd()
    before = {str(path): _sha256(source / path) for path in TRACKED_OUTPUTS}
    target = tmp_path_factory.mktemp("prd1-handoff") / "repo"
    ignore = shutil.ignore_patterns(
        ".git", ".venv", "node_modules", "var", "htmlcov", ".pytest_cache",
        ".ruff_cache", "__pycache__",
    )
    shutil.copytree(source, target, ignore=ignore)
    return target, before


def test_prd105_109_current_archival_record_preserves_boundaries() -> None:
    record = json.loads(
        Path("docs/roadmap/production_readiness/prd_105_109_ci_convergence_release_readiness_handoff_record.json").read_text()
    )
    assert record["prd1_sequence_complete"] is True
    assert record["prd1_final_evidence_recorded"] is True
    assert record["production_release_authorised"] is False
    assert record["deployment_authorised"] is False
    assert record["prd2_implementation_authorised"] is False


def test_prd105_109_apply_uses_isolated_repository(prd1_handoff_repo: tuple[Path, dict[str, str]]) -> None:
    repo, _ = prd1_handoff_repo
    apply(repo, write_files=True)
    data = json.loads(
        (repo / "docs/roadmap/production_readiness/prd1_ci_convergence_release_readiness_handoff.json").read_text()
    )
    assert data["merged_prd_slices"] == ["PRD-1.5", "PRD-1.6", "PRD-1.7", "PRD-1.8", "PRD-1.9"]
    assert data["ci_convergence_evidence"]["python_m_pytest_workflow_count"] == 0
    assert data["release_readiness_register"]["production_release_authorised"] is False
    assert data["handoff_to_prd2"]["prd2_implementation_authorised"] is False


def test_prd105_109_preserves_release_boundaries_in_isolated_output(
    prd1_handoff_repo: tuple[Path, dict[str, str]],
) -> None:
    repo, _ = prd1_handoff_repo
    apply(repo, write_files=True)
    record = json.loads(
        (repo / "docs/roadmap/production_readiness/prd_105_109_ci_convergence_release_readiness_handoff_record.json").read_text()
    )
    for key in (
        "production_release_authorised", "deployment_authorised", "release_tag_authorised",
        "public_beta_authorised", "live_learner_traffic_authorised", "billing_launch_authorised",
        "live_payment_processing_authorised", "prd2_implementation_authorised",
        "required_checks_enforced", "release_gate_enforced", "branch_protection_modified",
    ):
        assert record[key] is False


def test_prd105_109_generator_does_not_mutate_source_repository(
    prd1_handoff_repo: tuple[Path, dict[str, str]],
) -> None:
    _, before = prd1_handoff_repo
    source = Path.cwd()
    after = {str(path): _sha256(source / path) for path in TRACKED_OUTPUTS}
    assert after == before
