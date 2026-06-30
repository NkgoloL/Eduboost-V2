from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from app.modules.roadmap.production_readiness_contracts import (
    DEFAULT_BASELINE_BOUNDARIES,
    DEFAULT_DEFERRED_SCOPE,
    DEFAULT_DEPENDENCIES,
    DEFAULT_GRADUATION_CRITERIA,
    DEFAULT_POST_BASELINE_RISKS,
    DEFAULT_REVIEW_CADENCE,
    DEFAULT_ROADMAP_DECISION,
    DEFAULT_ROADMAP_ITEMS,
    _SAMPLE_DATE,
    compute_roadmap_checksum,
    summarize_roadmap_horizons,
    validate_roadmap_bundle,
)
from scripts.check_roadmap_after_production_readiness_baseline import run_checks

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_roadmap_after_production_readiness_baseline_passes() -> None:
    assert [result for result in run_checks() if not result.ok] == []


@pytest.mark.unit
def test_roadmap_after_production_readiness_baseline_cli_passes() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_roadmap_after_production_readiness_baseline.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Roadmap after production readiness baseline check" in result.stdout


@pytest.mark.unit
def test_roadmap_contracts_validate() -> None:
    assert DEFAULT_ROADMAP_DECISION.validate() == []
    assert [issue for item in DEFAULT_BASELINE_BOUNDARIES for issue in item.validate()] == []
    assert [issue for item in DEFAULT_ROADMAP_ITEMS for issue in item.validate()] == []
    assert [issue for item in DEFAULT_DEFERRED_SCOPE for issue in item.validate(_SAMPLE_DATE)] == []
    assert [issue for dependency in DEFAULT_DEPENDENCIES for issue in dependency.validate()] == []
    assert [issue for criterion in DEFAULT_GRADUATION_CRITERIA for issue in criterion.validate()] == []
    assert DEFAULT_REVIEW_CADENCE.validate() == []
    assert [issue for risk in DEFAULT_POST_BASELINE_RISKS for issue in risk.validate()] == []
    assert validate_roadmap_bundle(DEFAULT_ROADMAP_ITEMS, DEFAULT_DEFERRED_SCOPE, DEFAULT_DEPENDENCIES, _SAMPLE_DATE) == []


@pytest.mark.unit
def test_roadmap_horizon_summary() -> None:
    summary = summarize_roadmap_horizons(DEFAULT_ROADMAP_ITEMS)
    assert summary["next"] == 2
    assert summary["later"] == 2
    assert summary["now"] == 0
    assert summary["parked"] == 0


@pytest.mark.unit
def test_roadmap_checksum_is_sha256_hex() -> None:
    checksum = compute_roadmap_checksum("post-baseline-roadmap-evidence")
    assert len(checksum) == 64
    assert checksum == compute_roadmap_checksum("post-baseline-roadmap-evidence")
    assert checksum != compute_roadmap_checksum("other-roadmap-evidence")


@pytest.mark.unit
def test_makefile_exposes_roadmap_after_baseline_target() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "roadmap-after-production-readiness-baseline-check:" in text
    assert "scripts/check_roadmap_after_production_readiness_baseline.py" in text
