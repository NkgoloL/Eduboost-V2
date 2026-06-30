from __future__ import annotations

import pytest

from scripts.curriculum.resolve_dbe_caps_urls import Link, resolve_targets


pytestmark = pytest.mark.unit


def test_resolve_targets_matches_section_and_label_pairs() -> None:
    links = [
        Link("foundation", "Mathematics", "English", "https://example.test/foundation-maths.pdf"),
        Link("foundation", "Mathematics Grade R", "English", "https://example.test/grade-r-maths.pdf"),
        Link("foundation", "First Additional Language", "Sepedi", "https://example.test/sepedi-fal.pdf"),
        Link("senior", "NON LANGUAGES IN ENGLISH", "Mathematics", "https://example.test/senior-maths.pdf"),
    ]

    resolved = resolve_targets(links)

    assert resolved["caps_foundation_mathematics_en"] == "https://example.test/foundation-maths.pdf"
    assert resolved["caps_foundation_mathematics_grade_r_en"] == "https://example.test/grade-r-maths.pdf"
    assert resolved["caps_foundation_sepedi_first_additional_language_en"] == "https://example.test/sepedi-fal.pdf"
    assert resolved["caps_senior_mathematics_en"] == "https://example.test/senior-maths.pdf"


def test_resolve_targets_does_not_fall_back_to_wrong_phase_subject() -> None:
    links = [
        Link("foundation", "Mathematics", "English", "https://example.test/foundation-maths.pdf"),
        Link("foundation", "Home Languages", "English", "https://example.test/foundation-home-language.pdf"),
    ]

    resolved = resolve_targets(links)

    assert "caps_foundation_mathematics_en" in resolved
    assert "caps_foundation_mathematics_grade_r_en" not in resolved
    assert "caps_senior_mathematics_en" not in resolved
    assert "caps_intermediate_home_language_en" not in resolved
