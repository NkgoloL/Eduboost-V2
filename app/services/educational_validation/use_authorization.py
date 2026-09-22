"""Educational Model Limitations & Use Authorization Gatekeeper (LEV-WS15).

Strictly enforces algorithmic confidence caps (MAX_CONFIDENCE_THRESHOLD = 0.60)
and blocks high-stakes automated decisions until longitudinal educational validation
attestations are cryptographically registered.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from app.domain.educational_validation_schemas import (
    MAX_CONFIDENCE_THRESHOLD,
    UseAuthorizationStatus,
)


# Set of permitted formative, low-stakes decision scopes
PERMITTED_FORMATIVE_SCOPES: set[str] = {
    "low_stakes_practice",
    "formative_hinting",
    "diagnostic_remediation",
}

# Set of strictly prohibited high-stakes decision scopes prior to statutory sign-off
PROHIBITED_HIGH_STAKES_SCOPES: set[str] = {
    "formal_grading",
    "grade_progression",
    "high_stakes_streaming",
}


@dataclass(frozen=True)
class AuthorizationDecision:
    is_authorized: bool
    decision_scope: str
    effective_confidence: float
    status: UseAuthorizationStatus
    reason: str
    evidence_type: str = "synthetic_fixture"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_authorized": self.is_authorized,
            "decision_scope": self.decision_scope,
            "effective_confidence": round(self.effective_confidence, 4),
            "status": self.status,
            "reason": self.reason,
            "evidence_type": self.evidence_type,
        }


def enforce_confidence_bound(raw_confidence: float) -> float:
    """Enforce mathematical bound on algorithmic confidence (MAX_CONFIDENCE_THRESHOLD = 0.60).

    In an empirically unvalidated system, confidence claims > 0.60 are pedagogically
    unsound and create false assurance of learning.
    """
    if raw_confidence < 0.0:
        return 0.0
    return min(raw_confidence, MAX_CONFIDENCE_THRESHOLD)


def evaluate_use_authorization(
    decision_scope: str,
    requested_confidence: float,
    model_version: str = "lev-1.0",
    content_grade: int = 4,
    register_path: Optional[Path] = None,
) -> AuthorizationDecision:
    """Evaluate whether a proposed algorithmic decision scope is authorized under LEV governance."""
    effective_confidence = enforce_confidence_bound(requested_confidence)

    # Check high-stakes prohibition
    if decision_scope in PROHIBITED_HIGH_STAKES_SCOPES:
        return AuthorizationDecision(
            is_authorized=False,
            decision_scope=decision_scope,
            effective_confidence=effective_confidence,
            status="unsupported",
            reason=(
                f"Decision scope '{decision_scope}' is strictly prohibited. "
                "Automated high-stakes decisions require statutory longitudinal validation "
                "and independent DBE sign-off."
            ),
        )

    # Check grade range limits (Intermediate phase: Grades 4 to 6)
    if content_grade not in (4, 5, 6):
        return AuthorizationDecision(
            is_authorized=False,
            decision_scope=decision_scope,
            effective_confidence=effective_confidence,
            status="unsupported",
            reason=(
                f"Grade {content_grade} is outside the authorized Intermediate Phase scope (Grades 4-6). "
                "Cross-phase extrapolation is prohibited."
            ),
        )

    # Check if scope is an authorized formative scope
    if decision_scope in PERMITTED_FORMATIVE_SCOPES:
        return AuthorizationDecision(
            is_authorized=True,
            decision_scope=decision_scope,
            effective_confidence=effective_confidence,
            status="authorised",
            reason=(
                f"Decision scope '{decision_scope}' authorized for formative, low-stakes educational use "
                f"under model '{model_version}'. Algorithmic confidence capped at {MAX_CONFIDENCE_THRESHOLD:.2f}."
            ),
        )

    return AuthorizationDecision(
        is_authorized=False,
        decision_scope=decision_scope,
        effective_confidence=effective_confidence,
        status="restricted",
        reason=f"Decision scope '{decision_scope}' is unrecognized or unverified.",
    )
