"""Comprehensive unit tests for Knowledge Graph product alignment pure functions and pack builders."""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from app.domain.knowledge_graph_product_alignment import (
    sha256_text,
    file_sha256,
    stable_id,
    _estimated_minutes,
    _points,
    _badge,
    build_product_alignment_pack,
    KG6_GRAPH_ID,
    KG6_GRAPH_VERSION,
)


class TestKGProductAlignmentPureFunctions:
    def test_sha256_text(self):
        digest = sha256_text("hello-kg6")
        assert isinstance(digest, str)
        assert len(digest) == 64

    def test_file_sha256(self, tmp_path):
        test_file = tmp_path / "sample.txt"
        test_file.write_text("knowledge-graph-data", encoding="utf-8")
        digest = file_sha256(test_file)
        assert len(digest) == 64

    def test_stable_id(self):
        sid = stable_id("kg6_tutor", "topic_4.M.1.1")
        assert sid.startswith("kg6_tutor_")
        assert len(sid) == len("kg6_tutor_") + 24

    def test_estimated_minutes(self):
        assert _estimated_minutes("critical") == 30
        assert _estimated_minutes("high") == 25
        assert _estimated_minutes("medium") == 20
        assert _estimated_minutes("low") == 15
        assert _estimated_minutes("other") == 20

    def test_points(self):
        assert _points("critical") == 30
        assert _points("high") == 25
        assert _points("medium") == 20
        assert _points("low") == 15
        assert _points("unknown") == 20

    def test_badge(self):
        assert _badge("critical", "lesson") == "Gap Closer"
        assert _badge("high", "lesson") == "Gap Closer"
        assert _badge("medium", "assessment_statement") == "Evidence Builder"
        assert _badge("low", "lesson") == "CAPS Explorer"

    def test_build_product_alignment_pack_invalid_boundary(self, tmp_path):
        bad_pack = tmp_path / "bad_pack.json"
        bad_pack.write_text(json.dumps({"boundary": {"generation_preview_only": False}}), encoding="utf-8")

        with pytest.raises(ValueError, match="preview-only"):
            build_product_alignment_pack(bad_pack)

    def test_build_product_alignment_pack_with_live_data_error(self, tmp_path):
        bad_pack = tmp_path / "bad_pack_live.json"
        bad_pack.write_text(
            json.dumps({"boundary": {"generation_preview_only": True, "uses_live_learner_data": True}}),
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match="no live learner data"):
            build_product_alignment_pack(bad_pack)
