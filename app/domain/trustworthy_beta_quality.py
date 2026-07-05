"""RR-018 trustworthy beta product-quality contracts."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

IssueChannel = Literal["learner", "guardian", "educator", "support", "system"]
IssueSeverity = Literal["low", "medium", "high", "critical"]
ReviewLane = Literal["content_correction", "human_review", "educator_caps_priority", "privacy_safety"]


@dataclass(frozen=True)
class TrustworthyBetaQualityRequirement:
    """A product-facing RR-018 quality requirement."""

    key: str
    lane: ReviewLane
    required: bool
    evidence: str


TRUSTWORTHY_BETA_REQUIRED_REQUIREMENTS: tuple[TrustworthyBetaQualityRequirement, ...] = (
    TrustworthyBetaQualityRequirement(
        key="feedback_report_issue_button",
        lane="human_review",
        required=True,
        evidence="Report issue button is visible and privacy-safe.",
    ),
    TrustworthyBetaQualityRequirement(
        key="content_correction_workflow",
        lane="content_correction",
        required=True,
        evidence="Content issues can be triaged, corrected, reviewed, and closed.",
    ),
    TrustworthyBetaQualityRequirement(
        key="human_review_queue",
        lane="human_review",
        required=True,
        evidence="Sensitive quality issues are routed to human review before closure.",
    ),
    TrustworthyBetaQualityRequirement(
        key="educator_caps_priority_review",
        lane="educator_caps_priority",
        required=True,
        evidence="Priority CAPS Mathematics topics have educator review coverage.",
    ),
    TrustworthyBetaQualityRequirement(
        key="feedback_privacy_boundary",
        lane="privacy_safety",
        required=True,
        evidence="Feedback evidence excludes learner PII, payment card data, and raw AI prompts/output.",
    ),
)
