"""Runtime PII Sanitization and Redaction Layer (TSR-8).

Provides recursive payload scrubbing, identity token hashing, and strict
sanitization before audit logs or external telemetry serialization.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any

# Keys that are known to contain direct personal information
SENSITIVE_PII_KEYS = {
    "email",
    "email_address",
    "phone",
    "phone_number",
    "mobile",
    "cellphone",
    "name",
    "first_name",
    "last_name",
    "full_name",
    "guardian_name",
    "parent_name",
    "id_number",
    "sa_id_number",
    "national_id",
    "passport_number",
    "address",
    "physical_address",
    "residential_address",
    "street_address",
    "postal_code",
    "date_of_birth",
    "dob",
    "password",
    "password_hash",
    "secret",
    "token",
    "access_token",
    "refresh_token",
    "auth_token",
    "jwt",
}

# Regex patterns for high-confidence PII values
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
SA_ID_REGEX = re.compile(r"\b\d{13}\b")
PHONE_REGEX = re.compile(r"(?:\+27|0)\d{9}\b")


def hash_pseudonym(value: str, salt: str = "eduboost_pii_salt") -> str:
    """Produce a deterministic SHA-256 pseudonym for an identity token."""
    h = hashlib.sha256(f"{salt}:{value}".encode("utf-8"))
    return f"pseudonym_{h.hexdigest()[:16]}"


def sanitize_string_value(val: str) -> str:
    """Scrub inline PII patterns from free-text strings."""
    val = EMAIL_REGEX.sub("[REDACTED_EMAIL]", val)
    val = SA_ID_REGEX.sub("[REDACTED_ID]", val)
    val = PHONE_REGEX.sub("[REDACTED_PHONE]", val)
    return val


def sanitize_payload(obj: Any) -> Any:
    """Recursively scrub sensitive keys and inline PII from objects.

    Dictionaries with sensitive keys have their values pseudonymized or redacted.
    Strings containing PII regex patterns are scrubbed.
    """
    if isinstance(obj, dict):
        sanitized = {}
        for k, v in obj.items():
            k_lower = str(k).lower()
            if k_lower in SENSITIVE_PII_KEYS:
                if v is None:
                    sanitized[k] = None
                elif isinstance(v, (str, int)):
                    sanitized[k] = hash_pseudonym(str(v))
                else:
                    sanitized[k] = "[REDACTED_SENSITIVE_OBJECT]"
            else:
                sanitized[k] = sanitize_payload(v)
        return sanitized
    elif isinstance(obj, list):
        return [sanitize_payload(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(sanitize_payload(item) for item in obj)
    elif isinstance(obj, set):
        return {sanitize_payload(item) for item in obj}
    elif isinstance(obj, str):
        return sanitize_string_value(obj)
    return obj
