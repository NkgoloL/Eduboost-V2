from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from app.domain.llm_schemas import DiagnosticItemContract
from app.services.caps_validator import CAPSAlignmentValidator


@dataclass(frozen=True, slots=True)
class DiagnosticItemValidation:
    valid: bool
    reasons: tuple[str, ...] = ()


class DiagnosticItemValidator:
    def __init__(self, caps_validator: CAPSAlignmentValidator | None = None) -> None:
        self._caps_validator = caps_validator or CAPSAlignmentValidator()

    def validate_mapping(self, item: dict[str, Any]) -> DiagnosticItemValidation:
        reasons: list[str] = []
        try:
            contract = DiagnosticItemContract.model_validate(item)
        except Exception as exc:  # noqa: BLE001 - pydantic aggregates useful messages
            return DiagnosticItemValidation(False, (str(exc),))

        caps = self._caps_validator.validate_caps_reference(contract.caps_reference)
        if not caps.caps_aligned:
            reasons.append(caps.reason)
        if not math.isfinite(contract.difficulty) or not -4 <= contract.difficulty <= 4:
            reasons.append("difficulty must be finite and between -4 and 4")
        if not math.isfinite(contract.discrimination) or not 0 < contract.discrimination <= 4:
            reasons.append("discrimination must be finite and between 0 and 4")
        if len(set(contract.distractors.values())) < 4:
            reasons.append("distractors must be mutually distinct")
        if contract.review_status == "approved" and not contract.explanation.strip():
            reasons.append("approved items require an explanation")
        return DiagnosticItemValidation(not reasons, tuple(reasons))

    def from_orm(self, item: Any) -> DiagnosticItemValidation:
        payload = {
            "item_id": getattr(item, "id"),
            "subject": getattr(item, "subject"),
            "grade": getattr(item, "grade"),
            "topic": getattr(item, "topic"),
            "skill": getattr(item, "skill", None) or getattr(item, "topic", "general"),
            "difficulty": getattr(item, "b_param"),
            "discrimination": getattr(item, "a_param"),
            "correct_answer": getattr(item, "correct_option"),
            "distractors": getattr(item, "options"),
            "explanation": getattr(item, "explanation", "Review the worked solution."),
            "caps_reference": getattr(item, "caps_reference", None) or "CAPS:missing",
            "review_status": getattr(getattr(item, "review_status", "draft"), "value", getattr(item, "review_status", "draft")),
            "misconception_tag": getattr(item, "misconception_tag", None),
        }
        return self.validate_mapping(payload)
