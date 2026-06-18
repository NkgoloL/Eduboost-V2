"""Fail-closed Phase 2R source-rights policy evaluation."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping


class RightsUse(str, Enum):
    STORE_ORIGINAL = "store_original"
    EXTRACT = "extract"
    EMBED = "embed"
    RETRIEVAL = "retrieval"
    MODEL_PROMPT = "model_prompt"
    GENERATE_DERIVATIVE = "generate_derivative"
    TRANSLATE = "translate"
    PUBLISH_TRANSLATION = "publish_translation"
    SHOW_EDUCATOR_EXCERPT = "show_educator_excerpt"
    SHOW_LEARNER_EXCERPT = "show_learner_excerpt"
    REDISTRIBUTE = "redistribute"
    COMMERCIAL_USE = "commercial_use"
    MODEL_TRAINING = "model_training"


USE_TO_FIELD: dict[RightsUse, str] = {
    RightsUse.STORE_ORIGINAL: "may_store_original",
    RightsUse.EXTRACT: "may_extract",
    RightsUse.EMBED: "may_embed",
    RightsUse.RETRIEVAL: "may_use_for_retrieval",
    RightsUse.MODEL_PROMPT: "may_include_in_model_prompt",
    RightsUse.GENERATE_DERIVATIVE: "may_generate_derivatives",
    RightsUse.TRANSLATE: "may_translate",
    RightsUse.PUBLISH_TRANSLATION: "may_publish_translation",
    RightsUse.SHOW_EDUCATOR_EXCERPT: "may_show_excerpt_to_educator",
    RightsUse.SHOW_LEARNER_EXCERPT: "may_show_excerpt_to_learner",
    RightsUse.REDISTRIBUTE: "may_redistribute",
    RightsUse.COMMERCIAL_USE: "may_use_commercially",
    RightsUse.MODEL_TRAINING: "may_use_for_model_training",
}

ACTIVE_DECISION_STATUSES = frozenset({"approved", "approved_with_conditions"})


class RightsDeniedError(PermissionError):
    """Raised when a requested use is not explicitly permitted."""

    def __init__(self, use: RightsUse, reason: str) -> None:
        super().__init__(f"Rights denied for {use.value}: {reason}")
        self.use = use
        self.reason = reason


@dataclass(frozen=True)
class RightsDecisionView:
    decision_status: str
    permissions: Mapping[str, bool]
    conditions: Mapping[str, Any] = field(default_factory=dict)
    expires_at: datetime | None = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "RightsDecisionView":
        permissions = {field_name: bool(value.get(field_name, False)) for field_name in USE_TO_FIELD.values()}
        expires_at = value.get("expires_at")
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        return cls(
            decision_status=str(value.get("decision_status", "pending")),
            permissions=permissions,
            conditions=dict(value.get("conditions") or {}),
            expires_at=expires_at,
        )


@dataclass(frozen=True)
class RightsRequestContext:
    language: str | None = None
    channel: str | None = None
    jurisdiction: str | None = None
    excerpt_length: int | None = None
    at: datetime | None = None


class RightsPolicyEngine:
    """Evaluate explicit per-use permissions and structured conditions.

    No missing field, ambiguous status, expired decision, or malformed condition
    is treated as permission.  The caller must supply the latest effective
    append-only decision; selecting that decision is a repository concern.
    """

    @staticmethod
    def require_allowed(
        decision: RightsDecisionView | Mapping[str, Any] | None,
        use: RightsUse,
        *,
        context: RightsRequestContext | None = None,
    ) -> None:
        if decision is None:
            raise RightsDeniedError(use, "no rights decision exists")
        if not isinstance(decision, RightsDecisionView):
            decision = RightsDecisionView.from_mapping(decision)

        if decision.decision_status not in ACTIVE_DECISION_STATUSES:
            raise RightsDeniedError(use, f"decision status is {decision.decision_status!r}")

        now = (context.at if context else None) or datetime.now(timezone.utc)
        expires_at = decision.expires_at
        if expires_at is not None:
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if expires_at <= now:
                raise RightsDeniedError(use, "rights decision has expired")

        permission_field = USE_TO_FIELD[use]
        if decision.permissions.get(permission_field) is not True:
            raise RightsDeniedError(use, f"{permission_field} is not explicitly true")

        RightsPolicyEngine._validate_conditions(decision, use, context or RightsRequestContext())

    @staticmethod
    def is_allowed(
        decision: RightsDecisionView | Mapping[str, Any] | None,
        use: RightsUse,
        *,
        context: RightsRequestContext | None = None,
    ) -> bool:
        try:
            RightsPolicyEngine.require_allowed(decision, use, context=context)
        except RightsDeniedError:
            return False
        return True

    @staticmethod
    def _validate_conditions(
        decision: RightsDecisionView,
        use: RightsUse,
        context: RightsRequestContext,
    ) -> None:
        conditions = dict(decision.conditions)
        if decision.decision_status == "approved_with_conditions" and not conditions:
            raise RightsDeniedError(use, "conditional approval has no machine-readable conditions")

        languages = conditions.get("permitted_languages")
        if languages is not None:
            if not isinstance(languages, list) or not all(isinstance(item, str) for item in languages):
                raise RightsDeniedError(use, "permitted_languages is malformed")
            if context.language is None or context.language not in languages:
                raise RightsDeniedError(use, "requested language is not permitted")

        channels = conditions.get("permitted_channels")
        if channels is not None:
            if not isinstance(channels, list) or not all(isinstance(item, str) for item in channels):
                raise RightsDeniedError(use, "permitted_channels is malformed")
            if context.channel is None or context.channel not in channels:
                raise RightsDeniedError(use, "requested channel is not permitted")

        jurisdictions = conditions.get("permitted_jurisdictions")
        if jurisdictions is not None:
            if not isinstance(jurisdictions, list) or not all(isinstance(item, str) for item in jurisdictions):
                raise RightsDeniedError(use, "permitted_jurisdictions is malformed")
            if context.jurisdiction is None or context.jurisdiction not in jurisdictions:
                raise RightsDeniedError(use, "requested jurisdiction is not permitted")

        maximum_excerpt_length = conditions.get("maximum_excerpt_length")
        if maximum_excerpt_length is not None:
            if not isinstance(maximum_excerpt_length, int) or maximum_excerpt_length < 0:
                raise RightsDeniedError(use, "maximum_excerpt_length is malformed")
            if context.excerpt_length is None or context.excerpt_length > maximum_excerpt_length:
                raise RightsDeniedError(use, "requested excerpt exceeds the permitted length")


REQUIRED_REVIEW_DOMAINS = frozenset({"source_authority", "rights", "inventory_completeness"})


def require_independent_gate_reviews(decisions: list[Mapping[str, Any]]) -> None:
    """Require explicit approvals in each Gate 2R.1 review domain.

    An approval in one domain cannot satisfy another.  A later reject or
    request-changes decision for the same domain blocks the gate.
    """

    latest: dict[str, Mapping[str, Any]] = {}
    for decision in decisions:
        domain = str(decision.get("review_domain", ""))
        if domain not in REQUIRED_REVIEW_DOMAINS:
            continue
        created_at = str(decision.get("created_at", ""))
        current = latest.get(domain)
        if current is None or created_at >= str(current.get("created_at", "")):
            latest[domain] = decision

    missing = sorted(REQUIRED_REVIEW_DOMAINS - set(latest))
    if missing:
        raise ValueError(f"Missing review domains: {', '.join(missing)}")

    not_approved = sorted(domain for domain, decision in latest.items() if decision.get("decision") != "approve")
    if not_approved:
        raise ValueError(f"Unapproved review domains: {', '.join(not_approved)}")
