"""RR-002 POPIA erasure safety helpers.

This module keeps the POPIA right-to-erasure safety rules in one place so
routers and lifecycle services cannot silently bypass legal-hold, export-offer,
or authorisation preflight requirements.

The helpers are intentionally side-effect free. Persistence remains in
``POPIADataRightsService``.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

LEGAL_HOLD_ATTRIBUTE_NAMES = (
    "legal_hold",
    "legal_hold_active",
    "retention_hold",
    "billing_hold",
    "school_retention_hold",
    "investigation_hold",
)


@dataclass(frozen=True)
class ErasurePreflightDecision:
    """Machine-readable erasure preflight result."""

    subject_exists: bool
    requester_authorized: bool
    legal_hold_checked: bool
    legal_hold: bool
    export_offered: bool
    export_waived: bool
    export_requirement_satisfied: bool
    grace_period_required: bool
    preserve_audit_records: bool
    requires_admin_review: bool
    all_checks_passed: bool

    def to_dict(self) -> dict[str, bool]:
        return asdict(self)


def learner_has_legal_hold(learner: Any) -> bool:
    """Return True when any known learner-retention/legal-hold flag is truthy."""

    if learner is None:
        return False
    for attribute_name in LEGAL_HOLD_ATTRIBUTE_NAMES:
        if bool(getattr(learner, attribute_name, False)):
            return True
    return False


def build_erasure_preflight_decision(
    *,
    learner: Any,
    requester_authorized: bool,
    export_offered: bool,
    export_waived: bool = False,
) -> ErasurePreflightDecision:
    """Build the canonical pre-erasure safety decision.

    POPIA erasure must never proceed unless a legal-hold check was performed,
    the actor is authorised for the learner, audit records are preserved, and a
    data export was offered or explicitly waived. A legal hold does not prevent
    request creation, but it forces admin review and blocks execution until the
    hold is cleared or an approved override exists.
    """

    subject_exists = learner is not None
    legal_hold = learner_has_legal_hold(learner)
    export_requirement_satisfied = bool(export_offered or export_waived)
    requires_admin_review = bool(legal_hold or not requester_authorized or not export_requirement_satisfied)
    all_checks_passed = bool(
        subject_exists
        and requester_authorized
        and not legal_hold
        and export_requirement_satisfied
    )

    return ErasurePreflightDecision(
        subject_exists=subject_exists,
        requester_authorized=bool(requester_authorized),
        legal_hold_checked=True,
        legal_hold=legal_hold,
        export_offered=bool(export_offered),
        export_waived=bool(export_waived),
        export_requirement_satisfied=export_requirement_satisfied,
        grace_period_required=True,
        preserve_audit_records=True,
        requires_admin_review=requires_admin_review,
        all_checks_passed=all_checks_passed,
    )


__all__ = [
    "ErasurePreflightDecision",
    "LEGAL_HOLD_ATTRIBUTE_NAMES",
    "build_erasure_preflight_decision",
    "learner_has_legal_hold",
]
