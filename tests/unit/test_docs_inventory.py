from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import docs_inventory


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.unit
def test_docs_inventory_extracts_structure_and_signals() -> None:
    text = """# POPIA Compliance Contract

Status: TODO review by release owner.

See [evidence](docs/release/EVIDENCE_INDEX.md) and https://example.test/ref.

Reviewed on 2026-05-19.

## Evidence
"""
    path = REPO_ROOT / "docs" / "popia" / "sample.md"

    headings = docs_inventory.extract_headings(text)
    links = docs_inventory.extract_links(path, text)
    local_paths = docs_inventory.extract_local_path_references(text)

    assert headings[0] == {"level": 1, "text": "POPIA Compliance Contract", "line": 1}
    assert docs_inventory.extract_title(path, text, headings) == "POPIA Compliance Contract"
    assert docs_inventory.classify(path, "POPIA Compliance Contract", text) == "compliance_popia"
    assert docs_inventory.extract_statuses(text) == ["todo"]
    assert docs_inventory.extract_dates(text) == ["2026-05-19"]
    assert links[0]["kind"] == "local"
    assert links[1]["kind"] == "external"
    assert docs_inventory.extract_evidence_references(links, local_paths) == [
        "docs/release/EVIDENCE_INDEX.md"
    ]


@pytest.mark.unit
def test_docs_inventory_cli_generates_expected_artifacts(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/docs_inventory.py",
            "--source-root",
            "README.md",
            "--output-dir",
            str(tmp_path),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "docs_inventory.json").exists()
    assert (tmp_path / "docs_inventory.md").exists()
    assert (tmp_path / "docs_gap_report.md").exists()
    assert (tmp_path / "docs_generation_plan.md").exists()

    payload = json.loads((tmp_path / "docs_inventory.json").read_text(encoding="utf-8"))
    assert payload["files_scanned"] == 1
    assert payload["documents"][0]["path"] == "README.md"


@pytest.mark.unit
def test_makefile_exposes_docs_inventory_targets() -> None:
    text = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "docs-inventory:" in text
    assert "docs-inventory-check:" in text
