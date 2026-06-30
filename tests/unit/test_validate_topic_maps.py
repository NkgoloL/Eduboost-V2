from __future__ import annotations

import pytest

from scripts.curriculum.validate_topic_maps import validate_topic_maps


pytestmark = pytest.mark.unit


def test_topic_map_validator_accepts_current_draft_and_runtime_state() -> None:
    result = validate_topic_maps()

    assert result.passed is True
    assert result.draft_count == 50
    assert result.runtime_count == 51
    assert result.draft_status_summary["draft_reviewed"] == 50
    assert "draft_unreviewed" not in result.draft_status_summary
    assert result.runtime_ref_count > 0
