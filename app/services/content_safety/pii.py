"""POPIA-safe prompt and feedback helpers."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(r"\b(?:\+27|0)[6-8][0-9][\s-]?[0-9]{3}[\s-]?[0-9]{4}\b")
UUID_RE = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b", re.I)
SA_ID_RE = re.compile(r"\b\d{13}\b")
ADDRESS_RE = re.compile(r"\b\d{1,5}\s+[A-Za-z][A-Za-z\s]{2,}\s+(Street|St|Road|Rd|Avenue|Ave|Drive|Dr|Lane|Ln)\b", re.I)
NAME_KEYS = {"learner_name", "guardian_name", "parent_name", "first_name", "last_name", "email", "phone", "address"}


@dataclass(frozen=True, slots=True)
class PIIFinding:
    kind: str
    value: str


def detect_pii_text(value: str) -> list[PIIFinding]:
    findings: list[PIIFinding] = []
    patterns = (
        ("email", EMAIL_RE),
        ("phone", PHONE_RE),
        ("uuid", UUID_RE),
        ("id_number", SA_ID_RE),
        ("address", ADDRESS_RE),
    )
    for kind, pattern in patterns:
        findings.extend(PIIFinding(kind, match.group(0)) for match in pattern.finditer(value))
    return findings


def contains_pii(value: str) -> bool:
    return bool(detect_pii_text(value))


def redact_pii_text(value: str) -> str:
    redacted = EMAIL_RE.sub("[redacted-email]", value)
    redacted = PHONE_RE.sub("[redacted-phone]", redacted)
    redacted = UUID_RE.sub("[redacted-uuid]", redacted)
    redacted = SA_ID_RE.sub("[redacted-id-number]", redacted)
    redacted = ADDRESS_RE.sub("[redacted-address]", redacted)
    return redacted


def _scrub_value(value: Any) -> Any:
    if isinstance(value, str):
        return redact_pii_text(value)
    if isinstance(value, list):
        return [_scrub_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_scrub_value(item) for item in value)
    if isinstance(value, dict):
        return {key: _scrub_value(item) for key, item in value.items() if str(key) not in NAME_KEYS}
    return value


def build_llm_context(*, pseudonym_id: str, learner_profile: dict[str, Any], learning_context: dict[str, Any]) -> dict[str, Any]:
    """Build an external-prompt context using pseudonym_id and scrubbed learning data."""
    safe_profile = {key: value for key, value in learner_profile.items() if key not in NAME_KEYS}
    safe_profile.pop("learner_uuid", None)
    safe_profile["pseudonym_id"] = pseudonym_id
    return {
        "pseudonym_id": pseudonym_id,
        "learner_profile": _scrub_value(safe_profile),
        "learning_context": _scrub_value(learning_context),
    }


def scrub_feedback_for_rlhf(feedback: dict[str, Any], *, consent_granted: bool) -> dict[str, Any]:
    if not consent_granted:
        raise PermissionError("RLHF processing requires active consent")
    scrubbed = _scrub_value(feedback)
    scrubbed["pii_scrubbed"] = True
    scrubbed["rlhf_schema_version"] = "rlhf-feedback-v1"
    return scrubbed
