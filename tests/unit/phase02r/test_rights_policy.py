from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.services.curriculum.rights_policy import (
    RightsDeniedError,
    RightsPolicyEngine,
    RightsRequestContext,
    RightsUse,
    require_independent_gate_reviews,
)


def decision(**overrides):
    value = {
        "decision_status": "approved",
        "may_store_original": False,
        "may_extract": False,
        "may_embed": False,
        "may_use_for_retrieval": False,
        "may_include_in_model_prompt": False,
        "may_generate_derivatives": False,
        "may_translate": False,
        "may_publish_translation": False,
        "may_show_excerpt_to_educator": False,
        "may_show_excerpt_to_learner": False,
        "may_redistribute": False,
        "may_use_commercially": False,
        "may_use_for_model_training": False,
        "conditions": {},
    }
    value.update(overrides)
    return value


def test_missing_or_unspecified_right_is_denied() -> None:
    with pytest.raises(RightsDeniedError):
        RightsPolicyEngine.require_allowed(None, RightsUse.RETRIEVAL)
    with pytest.raises(RightsDeniedError):
        RightsPolicyEngine.require_allowed(decision(), RightsUse.RETRIEVAL)


def test_translation_does_not_imply_publication() -> None:
    value = decision(may_translate=True)
    RightsPolicyEngine.require_allowed(value, RightsUse.TRANSLATE)
    with pytest.raises(RightsDeniedError):
        RightsPolicyEngine.require_allowed(value, RightsUse.PUBLISH_TRANSLATION)


def test_conditions_are_machine_enforced() -> None:
    value = decision(
        decision_status="approved_with_conditions",
        may_show_excerpt_to_learner=True,
        conditions={
            "permitted_languages": ["en"],
            "permitted_channels": ["learner_app"],
            "maximum_excerpt_length": 120,
        },
    )
    RightsPolicyEngine.require_allowed(
        value,
        RightsUse.SHOW_LEARNER_EXCERPT,
        context=RightsRequestContext(language="en", channel="learner_app", excerpt_length=120),
    )
    with pytest.raises(RightsDeniedError):
        RightsPolicyEngine.require_allowed(
            value,
            RightsUse.SHOW_LEARNER_EXCERPT,
            context=RightsRequestContext(language="af", channel="learner_app", excerpt_length=120),
        )
    with pytest.raises(RightsDeniedError):
        RightsPolicyEngine.require_allowed(
            value,
            RightsUse.SHOW_LEARNER_EXCERPT,
            context=RightsRequestContext(language="en", channel="learner_app", excerpt_length=121),
        )


def test_expired_decision_is_denied() -> None:
    value = decision(
        may_extract=True,
        expires_at=(datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat(),
    )
    with pytest.raises(RightsDeniedError):
        RightsPolicyEngine.require_allowed(value, RightsUse.EXTRACT)


def test_training_permission_is_separately_default_denied() -> None:
    value = decision(may_embed=True, may_use_for_retrieval=True)
    RightsPolicyEngine.require_allowed(value, RightsUse.EMBED)
    RightsPolicyEngine.require_allowed(value, RightsUse.RETRIEVAL)
    with pytest.raises(RightsDeniedError):
        RightsPolicyEngine.require_allowed(value, RightsUse.MODEL_TRAINING)


def test_review_domains_cannot_substitute_for_each_other() -> None:
    with pytest.raises(ValueError, match="Missing review domains"):
        require_independent_gate_reviews(
            [
                {
                    "review_domain": "rights",
                    "decision": "approve",
                    "created_at": "2026-06-16T12:00:00Z",
                }
            ]
        )

    require_independent_gate_reviews(
        [
            {"review_domain": "source_authority", "decision": "approve", "created_at": "2026-06-16T12:00:00Z"},
            {"review_domain": "rights", "decision": "approve", "created_at": "2026-06-16T12:01:00Z"},
            {"review_domain": "inventory_completeness", "decision": "approve", "created_at": "2026-06-16T12:02:00Z"},
        ]
    )
