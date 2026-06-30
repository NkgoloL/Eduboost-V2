from __future__ import annotations

from pathlib import Path

import pytest

from scripts.curriculum.extract_caps_source_text import sha256_text, text_extract_path


pytestmark = pytest.mark.unit


def test_text_extract_path_uses_ignored_caps_text_directory(tmp_path: Path) -> None:
    assert text_extract_path("caps_senior_mathematics_en", text_dir=tmp_path).name == "caps_senior_mathematics_en.txt"


def test_sha256_text_is_stable_utf8_hash() -> None:
    assert sha256_text("CAPS\n") == "0d8fc6fbd5fcdefd7cf5740cd2d9e33c762ce8ee40a9c5302cca79b8ac2aa138"
