"""Comprehensive unit tests for ContentFilePromotionReadiness models and layer keys."""
from __future__ import annotations

import pytest

from app.services.content_file_promotion_readiness import (
    PromotionReadinessResult,
    _LAYER_PATH_KEYS,
)


class TestContentFilePromotionReadiness:
    def test_promotion_readiness_result_dataclass(self):
        res = PromotionReadinessResult(
            scope_id="grade4_mathematics_en",
            learner_visible=True,
            source_ready=True,
            staging_eligible=True,
            production_eligible=False,
            blockers=["Pending final educator signoff"],
            manifest={"scope_id": "grade4_mathematics_en"},
        )
        assert res.scope_id == "grade4_mathematics_en"
        assert res.staging_eligible is True
        assert res.production_eligible is False
        assert len(res.blockers) == 1

    def test_layer_path_keys_mapping(self):
        assert _LAYER_PATH_KEYS["topic_map"] == "topic_map_path"
        assert _LAYER_PATH_KEYS["diagnostic_items"] == "diagnostic_items"
        assert _LAYER_PATH_KEYS["lessons"] == "lessons"
        assert _LAYER_PATH_KEYS["assessment_blueprints"] == "assessment_blueprints"
        assert _LAYER_PATH_KEYS["study_plan_templates"] == "study_plan_templates"
