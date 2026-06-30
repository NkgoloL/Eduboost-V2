"""Privacy, prompt-boundary, safeguarding, and quality controls for Phase 5."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from app.services.ai_safety import redact_pii_text

PROMPT_INJECTION_PATTERNS = (
    re.compile(r"\bignore (?:all |any )?(?:previous|earlier|system|developer) (?:instructions?|messages?)\b", re.I),
    re.compile(r"\b(?:reveal|show|print|repeat) (?:the )?(?:system prompt|developer message|hidden instructions?)\b", re.I),
    re.compile(r"\b(?:jailbreak|do anything now|DAN mode)\b", re.I),
    re.compile(r"\bpretend (?:you have no|there are no) (?:rules|restrictions|safety)\b", re.I),
)

HIGH_RISK_PATTERNS = (
    ("self_harm", re.compile(r"\b(?:kill myself|suicide|self[- ]harm|hurt myself)\b", re.I)),
    ("sexual_content", re.compile(r"\b(?:explicit sex|pornography|sexual act)\b", re.I)),
    ("weapons", re.compile(r"\b(?:build|make|use) (?:a )?(?:bomb|gun|weapon)\b", re.I)),
    ("drugs", re.compile(r"\b(?:make|sell|take) (?:meth|cocaine|heroin|illegal drugs?)\b", re.I)),
)

OUTPUT_BLOCK_PATTERNS = (
    re.compile(r"\b(?:system prompt|developer message|hidden instruction)\b", re.I),
    re.compile(r"\b(?:explicit sex|pornography|kill yourself|suicide method|build a bomb)\b", re.I),
)


@dataclass(frozen=True, slots=True)
class PreparedInput:
    text: str
    content_hash: str
    pii_redacted: bool
    blocked_reason: str | None = None


@dataclass(frozen=True, slots=True)
class ValidatedOutput:
    text: str
    quality_score: float
    pii_redacted: bool
    blocked_reason: str | None = None


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def prepare_tutor_input(value: str) -> PreparedInput:
    original = value.strip()
    if len(original) < 2 or len(original) > 600:
        return PreparedInput("", _hash(original), False, "invalid_length")
    for pattern in PROMPT_INJECTION_PATTERNS:
        if pattern.search(original):
            return PreparedInput("", _hash(original), False, "prompt_injection")
    for reason, pattern in HIGH_RISK_PATTERNS:
        if pattern.search(original):
            return PreparedInput("", _hash(original), False, reason)
    redacted = redact_pii_text(original)
    return PreparedInput(redacted, _hash(original), redacted != original, None)


def validate_tutor_output(value: str, *, lesson_topic: str) -> ValidatedOutput:
    original = value.strip()
    if not original:
        return ValidatedOutput("", 0.0, False, "empty_output")
    if len(original) > 2400:
        return ValidatedOutput("", 0.0, False, "oversized_output")
    for pattern in OUTPUT_BLOCK_PATTERNS:
        if pattern.search(original):
            return ValidatedOutput("", 0.0, False, "unsafe_output")
    redacted = redact_pii_text(original)
    words = redacted.split()
    length_score = 1.0 if 20 <= len(words) <= 220 else 0.7 if 8 <= len(words) <= 320 else 0.4
    pedagogy_score = 1.0 if re.search(r"\b(?:because|for example|try|step|remember|hint)\b", redacted, re.I) else 0.65
    context_score = 1.0 if lesson_topic.lower() in redacted.lower() else 0.75
    quality = round((length_score + pedagogy_score + context_score) / 3, 3)
    if quality < 0.6:
        return ValidatedOutput("", quality, redacted != original, "low_quality")
    return ValidatedOutput(redacted, quality, redacted != original, None)


FALLBACK_MESSAGES = {
    "en": "I can’t give a safe answer to that right now. Please use the worked example in this lesson or ask a trusted educator for help.",
    "af": "Ek kan dit nie nou veilig beantwoord nie. Gebruik asseblief die uitgewerkte voorbeeld in die les of vra ’n onderwyser vir hulp.",
    "zu": "Angikwazi ukuphendula lokho ngokuphepha manje. Sebenzisa isibonelo esifundweni noma ucele uthisha akusize.",
}


SELF_HARM_FALLBACK = {
    "en": "I’m sorry you’re feeling this way. Please tell a trusted adult who is with you right now. If you may be in immediate danger, ask them to contact local emergency services.",
    "af": "Ek is jammer dat jy so voel. Vertel asseblief nou vir ’n betroubare volwassene wat by jou is. As jy moontlik in onmiddellike gevaar is, vra hulle om plaaslike nooddienste te kontak.",
    "zu": "Ngiyaxolisa ukuthi uzizwa kanje. Sicela utshele umuntu omdala omethembayo oseduze nawe manje. Uma usengozini esheshayo, cela axhumane nabezimo eziphuthumayo bendawo.",
}


def fallback_message(language: str, *, reason: str | None = None) -> str:
    if reason == "self_harm":
        return SELF_HARM_FALLBACK.get(language, SELF_HARM_FALLBACK["en"])
    return FALLBACK_MESSAGES.get(language, FALLBACK_MESSAGES["en"])
