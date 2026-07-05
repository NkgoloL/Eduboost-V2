"""RR-018 trustworthy beta product-quality service helpers."""
from __future__ import annotations

from app.domain.trustworthy_beta_quality import TRUSTWORTHY_BETA_REQUIRED_REQUIREMENTS


def trustworthy_beta_quality_keys() -> list[str]:
    """Return the product-facing RR-018 quality keys that must be evidenced."""
    return [requirement.key for requirement in TRUSTWORTHY_BETA_REQUIRED_REQUIREMENTS if requirement.required]


def trustworthy_beta_quality_complete(recorded_keys: set[str]) -> bool:
    """Check whether all required RR-018 quality keys are recorded."""
    required = set(trustworthy_beta_quality_keys())
    return required.issubset(recorded_keys)
