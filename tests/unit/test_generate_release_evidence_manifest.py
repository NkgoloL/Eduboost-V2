from __future__ import annotations

from pathlib import Path

import pytest

from scripts.generate_release_evidence_manifest import EVIDENCE_COMMANDS, render_manifest


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_release_evidence_manifest_command_list_is_complete() -> None:
    commands = "\n".join(command for _, command in EVIDENCE_COMMANDS)

    assert "make runtime-check" in commands
    assert "make openapi-check" in commands
    assert "make route-inventory-check" in commands
    assert "make pr002r-check" in commands
    assert "make phase2-authz-closure" in commands
    assert "make popia-consent-closure-check" in commands
    assert "make cluster-d-closure-check" in commands


@pytest.mark.unit
def test_release_evidence_manifest_renders_required_sections() -> None:
    output = render_manifest()

    assert "# Release Evidence Manifest" in output
    assert "Required Evidence Commands" in output
    assert "Release Evidence Notes" in output
    assert "Artifact References" in output


@pytest.mark.unit
def test_release_evidence_manifest_written_to_docs() -> None:
    manifest = REPO_ROOT / "docs" / "operations" / "release_evidence_manifest.md"

    assert manifest.exists()
    text = manifest.read_text(encoding="utf-8")
    assert "make cluster-d-closure-check" in text
    assert "docs/security/POPIA_CONSENT_GATE_CLOSURE.md" in text
