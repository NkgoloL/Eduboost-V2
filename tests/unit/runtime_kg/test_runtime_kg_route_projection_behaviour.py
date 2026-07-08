from app.services.runtime_kg.route_integration import legacy_runtime_kg_result, projection_to_route_result
from app.services.runtime_kg.schemas import LearnerKGNodeProjection, RuntimeKGProjection


def test_runtime_kg_legacy_result_is_explicit_rollback_payload():
    payload = legacy_runtime_kg_result("runtime_kg_feature_flag_disabled", graph_version="v1").to_payload()
    assert payload["runtime_kg_enabled"] is False
    assert payload["fallback_to_legacy"] is True
    assert payload["rollback_reason"] == "runtime_kg_feature_flag_disabled"
    assert payload["graph_version"] == "v1"


def test_projection_to_route_result_exposes_gap_focus_items():
    projection = RuntimeKGProjection(
        learner_id="learner-1",
        subject_code="Mathematics",
        graph_version="caps-grade4-math-runtime-v1",
        nodes=(
            LearnerKGNodeProjection("CAPS.MATH.4.N.1", "Place value", 0.2, 0.8, True, 2),
            LearnerKGNodeProjection("CAPS.MATH.4.N.2", "Addition", 0.9, 0.7, False, 3),
        ),
    )
    payload = projection_to_route_result(projection).to_payload()
    assert payload["runtime_kg_enabled"] is True
    assert payload["fallback_to_legacy"] is False
    assert payload["open_gap_count"] == 1
    assert payload["focus_items"][0]["stable_code"] == "CAPS.MATH.4.N.1"
