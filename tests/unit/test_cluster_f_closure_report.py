from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT = REPO_ROOT / "docs" / "ai" / "CLUSTER_F_CLOSURE.md"


@pytest.mark.unit
def test_cluster_f_closure_report_exists() -> None:
    assert REPORT.exists()


@pytest.mark.unit
def test_cluster_f_closure_report_has_required_commands() -> None:
    text = REPORT.read_text(encoding="utf-8")

    assert "Cluster F AI/CAPS/Diagnostics Safety Closure" in text
    assert "make cluster-f-closure-check" in text
    assert "make diagnostic-generation-safety-check" in text
    assert "make lesson-generation-safety-check" in text
    assert "make remediation-safety-contract-check" in text


@pytest.mark.unit
def test_cluster_f_closure_report_links_required_artifacts() -> None:
    text = REPORT.read_text(encoding="utf-8")

    assert "docs/ai/ai_safety_evidence_index.md" in text
    assert "docs/ai/llm_provider_fallback_contract.md" in text
    assert ".github/workflows/cluster-f-ai-safety.yml" in text
