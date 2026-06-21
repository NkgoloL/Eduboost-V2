"""Claim-validation helpers for Phase 2R Gate 2R.6."""
from __future__ import annotations

from dataclasses import dataclass, field


class ClaimValidationError(ValueError):
    pass


@dataclass(frozen=True)
class Claim:
    claim_type: str
    text: str
    supporting_chunk_ids: list[str] = field(default_factory=list)
    overlap_ratio: float = 0.0


@dataclass(frozen=True)
class ClaimValidationOutcome:
    status: str
    errors: list[str]


CURRICULUM_CLAIM_TYPES = {"curriculum_requirement", "assessment_claim"}
ALLOWED_CLAIM_TYPES = CURRICULUM_CLAIM_TYPES | {"pedagogical_guidance", "mathematical_fact", "enrichment"}


class ClaimValidator:
    def __init__(self, *, maximum_overlap_ratio: float = 0.35) -> None:
        self.maximum_overlap_ratio = maximum_overlap_ratio

    def validate(self, claims: list[Claim]) -> ClaimValidationOutcome:
        errors: list[str] = []
        for index, claim in enumerate(claims):
            if claim.claim_type not in ALLOWED_CLAIM_TYPES:
                errors.append(f"claim[{index}] unsupported claim_type {claim.claim_type}")
            if claim.claim_type in CURRICULUM_CLAIM_TYPES and not claim.supporting_chunk_ids:
                errors.append(f"claim[{index}] requires supporting source chunks")
            if claim.overlap_ratio > self.maximum_overlap_ratio:
                errors.append(f"claim[{index}] exceeds permitted textual overlap")
            if claim.claim_type == "enrichment" and "CAPS requires" in claim.text:
                errors.append(f"claim[{index}] enrichment cannot be promoted to a CAPS requirement")
        return ClaimValidationOutcome("failed" if errors else "passed", errors)
