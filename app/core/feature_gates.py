"""Fail-closed feature gates for learner-facing capabilities."""
from app.core.config import settings
from app.core.exceptions import FeatureDisabledError


def require_learner_diagnostic_enabled() -> None:
    if not settings.LEARNER_DIAGNOSTIC_ENABLED:
        raise FeatureDisabledError("Learner diagnostics are disabled while the question bank is being rebuilt.")


def require_learner_mastery_view_enabled() -> None:
    if not settings.LEARNER_MASTERY_VIEW_ENABLED:
        raise FeatureDisabledError("Learner mastery views are disabled pending independent validation.")
