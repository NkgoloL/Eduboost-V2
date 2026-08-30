"""Comprehensive unit tests for Knowledge Graph runtime activation and post-switch review domain packs."""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from app.domain.knowledge_graph_runtime_activation import (
    ACTIVATION_TRUE_KEYS,
    BOUNDARY_FALSE_KEYS as ACT_BOUNDARY_FALSE_KEYS,
    KGACT001_ID,
    KGACT001_GRAPH_ID,
    build_runtime_activation_pack,
)
from app.domain.knowledge_graph_post_switch_review import (
    REQUIRED_RUNTIME_TRUE_KEYS,
    BOUNDARY_FALSE_KEYS as REV_BOUNDARY_FALSE_KEYS,
    KG8_ID,
    KG8_GRAPH_ID,
    build_post_switch_review_pack,
)


class TestKGRuntimeActivationConstantsAndErrors:
    def test_activation_constants(self):
        assert KGACT001_ID == "KG-ACT-001"
        assert "runtime_kg_authority_switch_authorised" in ACTIVATION_TRUE_KEYS
        assert "billing_launch_authorised" in ACT_BOUNDARY_FALSE_KEYS

    def test_build_runtime_activation_pack_invalid_boundary(self, tmp_path):
        bad_pack = tmp_path / "bad_kg7.json"
        bad_pack.write_text(
            json.dumps({"boundary": {"readiness_only": False}}),
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="readiness-only"):
            build_runtime_activation_pack(bad_pack)


class TestKGPostSwitchReviewConstantsAndErrors:
    def test_post_switch_constants(self):
        assert KG8_ID == "KG-8"
        assert "runtime_kg_authority_switch_authorised" in REQUIRED_RUNTIME_TRUE_KEYS
        assert "live_payment_processing_authorised" in REV_BOUNDARY_FALSE_KEYS

    def test_build_post_switch_review_pack_invalid_boundary(self, tmp_path):
        bad_pack = tmp_path / "bad_kg_act.json"
        bad_pack.write_text(
            json.dumps({"activation_flags": {"runtime_kg_implementation_claimed": False}}),
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="runtime activation flag true"):
            build_post_switch_review_pack(bad_pack)
