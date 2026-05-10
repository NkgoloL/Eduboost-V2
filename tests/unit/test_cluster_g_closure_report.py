from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT = REPO_ROOT / "docs" / "frontend" / "CLUSTER_G_CLOSURE.md"


@pytest.mark.unit
def test_cluster_g_closure_report_exists() -> None:
    assert REPORT.exists()


@pytest.mark.unit
def test_cluster_g_closure_report_has_required_commands() -> None:
    text = REPORT.read_text(encoding="utf-8")

    assert "Cluster G Frontend Vertical Journey Closure" in text
    assert "make cluster-g-closure-check" in text
    assert "make frontend-playwright-mocked-specs-check" in text
    assert "make frontend-accessibility-static-check" in text


@pytest.mark.unit
def test_cluster_g_closure_report_documents_boundary() -> None:
    text = REPORT.read_text(encoding="utf-8")

    assert "opt-in runtime browser" in text
    assert "frontend runtime package and server command are canonical" in text
