from __future__ import annotations

from pathlib import Path

import pytest

from scripts.curriculum.download_caps_sources import relative_source_path, sha256_file


pytestmark = pytest.mark.unit


def test_relative_source_path_uses_raw_caps_source_directory() -> None:
    assert (
        relative_source_path("caps_foundation_mathematics_grade_r_en")
        == "data/caps/source_documents/raw/caps_foundation_mathematics_grade_r_en.pdf"
    )


def test_sha256_file_hashes_file_content(tmp_path: Path) -> None:
    source = tmp_path / "source.pdf"
    source.write_bytes(b"%PDF-1.7\nexample")

    assert sha256_file(source) == "4c05a9d358d6ae170333b35b69ddf857bde90fe521d98136c23d8cda233fcedd"
