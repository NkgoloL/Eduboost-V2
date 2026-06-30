from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
INDEX = REPO_ROOT / "docs" / "ai" / "ai_safety_evidence_index.md"


@pytest.mark.unit
def test_ai_safety_evidence_index_exists() -> None:
    assert INDEX.exists()


@pytest.mark.unit
def test_ai_safety_evidence_index_links_contracts() -> None:
    text = INDEX.read_text(encoding="utf-8")

    assert "AI Safety Evidence Index" in text
    assert "Cluster F Closure" in text
    assert "Curriculum Alignment" in text
    assert "Safety Boundaries" in text
    assert "Provider and Output Contracts" in text
    assert "docs/ai/caps_alignment_contract.md" in text
    assert "docs/ai/ai_safety_boundary_contract.md" in text
    assert "docs/ai/llm_provider_fallback_contract.md" in text


@pytest.mark.unit
def test_ai_safety_evidence_index_links_required_commands() -> None:
    text = INDEX.read_text(encoding="utf-8")

    assert "make cluster-f-closure-check" in text
    assert "make lesson-generation-safety-check" in text
    assert "make remediation-safety-contract-check" in text
    assert "make ai-output-schema-contract-check" in text
