"""Comprehensive unit tests for Knowledge Graph product alignment, runtime activation, and post-switch review."""
from __future__ import annotations

from pathlib import Path
import pytest

from app.domain.knowledge_graph_product_alignment import (
    sha256_text as prod_sha256_text,
    file_sha256 as prod_file_sha256,
    stable_id,
    _estimated_minutes,
    _points,
    _badge,
    build_product_alignment_pack,
    DEFAULT_GENERATION_PACK,
)
from app.domain.knowledge_graph_post_switch_review import (
    sha256_text as post_sha256_text,
    file_sha256 as post_file_sha256,
    build_post_switch_review_pack,
    DEFAULT_RUNTIME_ACTIVATION_PACK,
)
from app.domain.knowledge_graph_runtime_activation import (
    sha256_text as act_sha256_text,
    file_sha256 as act_file_sha256,
    build_runtime_activation_pack,
    DEFAULT_KG7_READINESS_PACK,
)


class TestKGProductAlignment:
    def test_sha256_helpers(self, tmp_path: Path):
        t = tmp_path / "sample.txt"
        t.write_text("KG alignment verification payload", encoding="utf-8")
        assert len(prod_sha256_text("hello")) == 64
        assert len(prod_file_sha256(t)) == 64

    def test_stable_id(self):
        sid = stable_id("TUTOR", "4.M.1.1")
        assert sid.startswith("TUTOR_")
        assert len(sid) == 6 + 24

    def test_estimation_and_badges(self):
        assert _estimated_minutes("critical") == 30
        assert _estimated_minutes("low") == 15
        assert _points("high") == 25
        assert _badge("critical", "lesson") == "Gap Closer"
        assert _badge("medium", "assessment_statement") == "Evidence Builder"
        assert _badge("low", "topic") == "CAPS Explorer"

    def test_build_product_alignment_pack(self):
        if DEFAULT_GENERATION_PACK.exists():
            pack = build_product_alignment_pack()
            assert pack is not None
            assert "graph_id" in pack or "alignment_pack_id" in pack or "boundary" in pack


class TestKGRuntimeActivation:
    def test_sha256_helpers(self, tmp_path: Path):
        t = tmp_path / "sample.txt"
        t.write_text("KG runtime activation payload", encoding="utf-8")
        assert len(act_sha256_text("hello")) == 64
        assert len(act_file_sha256(t)) == 64

    def test_build_runtime_activation_pack(self):
        if DEFAULT_KG7_READINESS_PACK.exists():
            pack = build_runtime_activation_pack()
            assert pack is not None
            assert "boundary" in pack or "activation_pack_id" in pack or "controlled_runtime_activation_approved" in pack["boundary"]


class TestKGPostSwitchReview:
    def test_sha256_helpers(self, tmp_path: Path):
        t = tmp_path / "sample.txt"
        t.write_text("KG post switch review payload", encoding="utf-8")
        assert len(post_sha256_text("hello")) == 64
        assert len(post_file_sha256(t)) == 64

    def test_build_post_switch_review_pack(self):
        if DEFAULT_RUNTIME_ACTIVATION_PACK.exists():
            pack = build_post_switch_review_pack()
            assert pack is not None
            assert "boundary" in pack or "review_pack_id" in pack or "graph_id" in pack
