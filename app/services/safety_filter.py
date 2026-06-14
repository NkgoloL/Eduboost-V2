"""
EduBoost Phase 1 — Safety Filter
===================================
Screens text for PII and unsafe content before sending to an LLM provider
and before persisting generated artefacts (EC-05, POPIA).

POPIA obligations:
  - No personal information about learners or guardians may be sent to an
    external LLM provider.
  - No personal information extracted from source material may appear in
    generated content or telemetry logs.

Child-safety obligations:
  - Generated content must not contain violent, sexual, or disturbing content
    inappropriate for the target grade level.
  - Any suspicious output must fail closed: the artefact is quarantined, not
    published automatically.

Usage::

    sf = SafetyFilter()
    result = sf.check_text(source_text, context="etl_source_chunk")
    if not result.passed:
        raise ValueError(f"Source contains PII: {result.violations}")

    output_result = sf.check_text(generated_json, context="llm_output")
    if not output_result.passed:
        # quarantine artefact; do not publish
        ...
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


# ---------------------------------------------------------------------------
# Violation types
# ---------------------------------------------------------------------------


class ViolationCategory(str, Enum):
    PII_SA_ID = "pii_sa_id_number"
    PII_PHONE = "pii_phone_number"
    PII_EMAIL = "pii_email_address"
    PII_BANK_ACCOUNT = "pii_bank_account"
    UNSAFE_VIOLENCE = "unsafe_violence"
    UNSAFE_ADULT = "unsafe_adult_content"
    UNSAFE_SELF_HARM = "unsafe_self_harm"
    UNSAFE_HATE = "unsafe_hate_speech"


@dataclass(frozen=True)
class SafetyViolation:
    category: ViolationCategory
    description: str
    # Redacted excerpt — never log the full match
    redacted_excerpt: str = ""


@dataclass(frozen=True)
class SafetyCheckResult:
    passed: bool
    context: str
    violations: list[SafetyViolation] = field(default_factory=list)

    @property
    def violation_categories(self) -> list[str]:
        return [v.category.value for v in self.violations]

    @property
    def summary(self) -> str:
        if self.passed:
            return "pass"
        cats = ", ".join(set(self.violation_categories))
        return f"fail:{cats}"


# ---------------------------------------------------------------------------
# Compiled patterns
# ---------------------------------------------------------------------------

# South African ID number: 13 consecutive digits (YYMMDDXXXXXXX)
# We do NOT attempt to validate checksum here; detection is conservative.
_SA_ID_RE = re.compile(r"\b(\d{13})\b")

# SA phone numbers: +27, 0XX, 27XX patterns
_PHONE_RE = re.compile(
    r"""
    (?:\+27|0)          # country or trunk prefix
    [\s\-\.]?           # optional separator
    (?:\(0\))?          # optional area (0)
    [\s\-\.]?
    [6-8]\d             # two-digit area code
    [\s\-\.]?
    \d{3}               # three digits
    [\s\-\.]?
    \d{4}               # four digits
    """,
    re.VERBOSE,
)

# Email addresses
_EMAIL_RE = re.compile(
    r"\b[a-zA-Z0-9._%+\-]{1,64}@[a-zA-Z0-9.\-]{1,253}\.[a-zA-Z]{2,}\b"
)

# SA bank account numbers: 9–11 consecutive digits (heuristic; context-sensitive)
# We only flag when preceded by words suggesting a bank context.
_BANK_ACCOUNT_RE = re.compile(
    r"""
    (?:account|acc|bankreken(?:ing)?)\s*[:\-#]?\s*
    (\d{9,11})
    """,
    re.IGNORECASE | re.VERBOSE,
)

# Unsafe content for children (English keywords; extend with Afrikaans/Zulu as needed)
_VIOLENCE_KEYWORDS = re.compile(
    r"\b(murder(?:ed|ing)?|kill(?:ed|ing)?|stabb?(?:ed|ing)?|shoot(?:er|ing|s|shot)?|bomb(?:ed|ing)?|weapon(?:s)?|blood(?:y)?|tortur(?:e|ed|ing)|terror(?:ist|ism)?)\b",
    re.IGNORECASE,
)

_ADULT_KEYWORDS = re.compile(
    r"\b(sex(?:ual)?|porn(?:ography)?|nude|naked|erotic|genitali[ae])\b",
    re.IGNORECASE,
)

_SELF_HARM_KEYWORDS = re.compile(
    r"\b(suicide|self[\-\s]?harm|cut(?:ting)?\s+(?:my|your|her|his)\s+(?:wrist|arm|skin))\b",
    re.IGNORECASE,
)

_HATE_KEYWORDS = re.compile(
    r"\b(kaffir|chink|faggot|slur|racial(?:ist)?|genocide)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Filter
# ---------------------------------------------------------------------------


def _redact(match_text: str, keep_chars: int = 4) -> str:
    """Return a redacted excerpt safe for logging."""
    if len(match_text) <= keep_chars:
        return "*" * len(match_text)
    return match_text[:keep_chars] + "*" * (len(match_text) - keep_chars)


class SafetyFilter:
    """
    Stateless safety and PII filter.
    Construct once; reuse across requests.

    check_text() is synchronous and fast (regex only).
    It is designed to be called:
      - on ETL source chunks *before* they are concatenated into prompts
      - on raw LLM output *before* the artefact is persisted
    """

    def check_text(self, text: str, context: str = "unknown") -> SafetyCheckResult:
        """
        Run all PII and unsafe-content checks on *text*.
        Returns a :class:`SafetyCheckResult` — never raises.

        *context* is a non-personal label used in log messages (e.g.
        ``"etl_source_chunk"``, ``"llm_output"``, ``"prompt_input"``).
        """
        violations: list[SafetyViolation] = []

        # PII: SA ID number
        for match in _SA_ID_RE.finditer(text):
            violations.append(
                SafetyViolation(
                    category=ViolationCategory.PII_SA_ID,
                    description="Possible SA ID number detected",
                    redacted_excerpt=_redact(match.group()),
                )
            )

        # PII: phone numbers
        for match in _PHONE_RE.finditer(text):
            violations.append(
                SafetyViolation(
                    category=ViolationCategory.PII_PHONE,
                    description="Possible SA phone number detected",
                    redacted_excerpt=_redact(match.group().replace(" ", "")),
                )
            )

        # PII: email addresses
        for match in _EMAIL_RE.finditer(text):
            violations.append(
                SafetyViolation(
                    category=ViolationCategory.PII_EMAIL,
                    description="Email address detected",
                    redacted_excerpt=_redact(match.group()),
                )
            )

        # PII: bank account
        for match in _BANK_ACCOUNT_RE.finditer(text):
            violations.append(
                SafetyViolation(
                    category=ViolationCategory.PII_BANK_ACCOUNT,
                    description="Possible bank account number detected",
                    redacted_excerpt=_redact(match.group(1)),
                )
            )

        # Unsafe: violence
        for match in _VIOLENCE_KEYWORDS.finditer(text):
            violations.append(
                SafetyViolation(
                    category=ViolationCategory.UNSAFE_VIOLENCE,
                    description=f"Violence keyword: {match.group().lower()!r}",
                    redacted_excerpt=match.group().lower(),
                )
            )

        # Unsafe: adult content
        for match in _ADULT_KEYWORDS.finditer(text):
            violations.append(
                SafetyViolation(
                    category=ViolationCategory.UNSAFE_ADULT,
                    description=f"Adult keyword: {match.group().lower()!r}",
                    redacted_excerpt=match.group().lower(),
                )
            )

        # Unsafe: self-harm
        for match in _SELF_HARM_KEYWORDS.finditer(text):
            violations.append(
                SafetyViolation(
                    category=ViolationCategory.UNSAFE_SELF_HARM,
                    description="Self-harm language detected",
                    redacted_excerpt=match.group()[:8] + "…",
                )
            )

        # Unsafe: hate speech
        for match in _HATE_KEYWORDS.finditer(text):
            violations.append(
                SafetyViolation(
                    category=ViolationCategory.UNSAFE_HATE,
                    description="Hate speech keyword detected",
                    redacted_excerpt="[REDACTED]",
                )
            )

        return SafetyCheckResult(
            passed=len(violations) == 0,
            context=context,
            violations=violations,
        )

    def check_source_bundle(
        self, sources: list[dict], context: str = "source_bundle"
    ) -> SafetyCheckResult:
        """
        Check all text fields in a list of source-chunk dicts.
        Fields checked: 'text', 'citation_text', 'title', 'source_title'.
        """
        combined_violations: list[SafetyViolation] = []
        text_fields = ("text", "citation_text", "title", "source_title")
        for idx, source in enumerate(sources):
            for field_name in text_fields:
                value = source.get(field_name)
                if isinstance(value, str) and value:
                    result = self.check_text(
                        value, context=f"{context}[{idx}].{field_name}"
                    )
                    combined_violations.extend(result.violations)
        return SafetyCheckResult(
            passed=len(combined_violations) == 0,
            context=context,
            violations=combined_violations,
        )
