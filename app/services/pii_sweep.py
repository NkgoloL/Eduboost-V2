"""
RLHF PII Minimisation Gate — Task #25
======================================
Pre-export PII scan for the RLHF pipeline.

Before any preference dataset is exported (OpenAI or Anthropic format),
this module runs a multi-layer PII detection pass across all free-text fields:

  Layer 1 — Regex patterns:
    - SA ID numbers (13-digit, Luhn-validated)
    - Email addresses
    - Phone numbers (ZA & international)
    - Names-in-context heuristics (salutation patterns)

  Layer 2 — phonenumbers library (libphonenumber):
    - Structural phone number detection regardless of format

  Layer 3 — bleach HTML sanitisation:
    - Strips any HTML/JS that might encode or obfuscate PII

Raises ``PIISweepError`` if any PII is detected, aborting the export.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Sequence

# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------

class PIISweepError(Exception):
    """
    Raised when PII is detected in RLHF export data.

    Attributes:
        findings: List of PII finding descriptors.
        field_name: The field in which PII was detected.
    """

    def __init__(self, message: str, findings: list[dict], field_name: str = "") -> None:
        super().__init__(message)
        self.findings = findings
        self.field_name = field_name


# ---------------------------------------------------------------------------
# Detection patterns
# ---------------------------------------------------------------------------

# South African ID: 13 digits, validated with Luhn algorithm below
_SA_ID_PATTERN = re.compile(r"\b(\d{13})\b")

# Email addresses
_EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"
)

# Generic phone numbers: supports +27, 0x, (0x), spaces/hyphens
_PHONE_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:\+27|0)"
    r"[\s\-]?"
    r"(?:\d[\s\-]?){8,10}"
    r"(?!\d)"
)

# Salutation-prefixed names (Mr/Mrs/Ms/Dr/Prof)
_SALUTATION_PATTERN = re.compile(
    r"\b(?:Mr|Mrs|Ms|Miss|Dr|Prof|Professor)\.?\s+[A-Z][a-z]+"
    r"(?:\s+[A-Z][a-z]+)?\b"
)


def _luhn_valid(number: str) -> bool:
    """Return True if the digit string passes the Luhn checksum."""
    digits = [int(d) for d in number]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    total = sum(odd_digits)
    for d in even_digits:
        total += sum(divmod(d * 2, 10))
    return total % 10 == 0


# ---------------------------------------------------------------------------
# Core scanner
# ---------------------------------------------------------------------------

@dataclass
class PIIFinding:
    pattern_name: str
    matched_value: str  # Redacted in production logs; kept for test assertions
    field_name: str
    position: int = 0


@dataclass
class SweepResult:
    is_clean: bool
    findings: list[PIIFinding] = field(default_factory=list)

    def add(self, finding: PIIFinding) -> None:
        self.findings.append(finding)
        self.is_clean = False


class PIIScanner:
    """
    Stateless scanner.  Call ``scan_text(text, field_name)`` per field,
    or ``scan_record(record)`` for a dict of field_name → value pairs.
    """

    def scan_text(self, text: str, field_name: str = "unknown") -> SweepResult:
        result = SweepResult(is_clean=True)

        if not isinstance(text, str) or not text.strip():
            return result

        # Layer 3 first: strip HTML so patterns cannot be hidden in tags
        sanitised = self._strip_html(text)

        self._check_sa_id(sanitised, field_name, result)
        self._check_email(sanitised, field_name, result)
        self._check_phone_regex(sanitised, field_name, result)
        self._check_phone_lib(sanitised, field_name, result)
        self._check_salutation(sanitised, field_name, result)

        return result

    def scan_record(self, record: dict[str, Any]) -> SweepResult:
        combined = SweepResult(is_clean=True)
        for field_name, value in record.items():
            if isinstance(value, str):
                sub = self.scan_text(value, field_name)
                if not sub.is_clean:
                    for f in sub.findings:
                        combined.add(f)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, str):
                        sub = self.scan_text(item, f"{field_name}[{i}]")
                        if not sub.is_clean:
                            for f in sub.findings:
                                combined.add(f)
        return combined

    # ------------------------------------------------------------------
    # Layer checks
    # ------------------------------------------------------------------

    @staticmethod
    def _strip_html(text: str) -> str:
        try:
            import bleach  # type: ignore[import]
            return bleach.clean(text, tags=[], strip=True)
        except ImportError:
            # Fallback: basic tag removal if bleach not installed
            return re.sub(r"<[^>]+>", " ", text)

    @staticmethod
    def _check_sa_id(text: str, field_name: str, result: SweepResult) -> None:
        for match in _SA_ID_PATTERN.finditer(text):
            candidate = match.group(1)
            if _luhn_valid(candidate):
                result.add(PIIFinding(
                    pattern_name="sa_id_number",
                    matched_value=f"{candidate[:3]}**********",
                    field_name=field_name,
                    position=match.start(),
                ))

    @staticmethod
    def _check_email(text: str, field_name: str, result: SweepResult) -> None:
        for match in _EMAIL_PATTERN.finditer(text):
            result.add(PIIFinding(
                pattern_name="email_address",
                matched_value="[REDACTED]",
                field_name=field_name,
                position=match.start(),
            ))

    @staticmethod
    def _check_phone_regex(text: str, field_name: str, result: SweepResult) -> None:
        for match in _PHONE_PATTERN.finditer(text):
            result.add(PIIFinding(
                pattern_name="phone_number_regex",
                matched_value="[REDACTED]",
                field_name=field_name,
                position=match.start(),
            ))

    @staticmethod
    def _check_phone_lib(text: str, field_name: str, result: SweepResult) -> None:
        try:
            import phonenumbers  # type: ignore[import]
            for match in phonenumbers.PhoneNumberMatcher(text, "ZA"):
                result.add(PIIFinding(
                    pattern_name="phone_number_libphonenumber",
                    matched_value="[REDACTED]",
                    field_name=field_name,
                    position=match.start,
                ))
        except ImportError:
            pass  # Optional dependency; regex check above still runs

    @staticmethod
    def _check_salutation(text: str, field_name: str, result: SweepResult) -> None:
        for match in _SALUTATION_PATTERN.finditer(text):
            result.add(PIIFinding(
                pattern_name="salutation_name",
                matched_value="[REDACTED]",
                field_name=field_name,
                position=match.start(),
            ))


# ---------------------------------------------------------------------------
# Export guard
# ---------------------------------------------------------------------------

def assert_no_pii(records: Sequence[dict[str, Any]], scanner: PIIScanner | None = None) -> None:
    """
    Scan all records and raise ``PIISweepError`` if any PII is found.

    This is the single call-site gate: inject at the top of any export function.

    Example usage in RLHFService::
        from app.services.pii_sweep import assert_no_pii
        assert_no_pii(export_records)  # raises PIISweepError on detection

    Args:
        records: Sequence of dicts representing RLHF preference records.
        scanner: Optional pre-constructed scanner (defaults to PIIScanner()).

    Raises:
        PIISweepError: If any PII is detected in any field.
    """
    if scanner is None:
        scanner = PIIScanner()

    all_findings: list[dict] = []
    first_field = ""

    for i, record in enumerate(records):
        result = scanner.scan_record(record)
        if not result.is_clean:
            for finding in result.findings:
                all_findings.append({
                    "record_index": i,
                    "field": finding.field_name,
                    "pattern": finding.pattern_name,
                    "position": finding.position,
                })
                if not first_field:
                    first_field = finding.field_name

    if all_findings:
        raise PIISweepError(
            f"PII detected in {len(all_findings)} location(s) across "
            f"{len(records)} RLHF record(s). Export aborted. "
            "Review and scrub before re-exporting.",
            findings=all_findings,
            field_name=first_field,
        )
