"""
CAPS Aligner  (Pipeline Stage 2)
==================================
Enriches NormalisedContent records with the full CAPS taxonomy:

  • caps_phase         (foundation / intermediate / senior / fet)
  • caps_subject       (canonical CAPSSubject value)
  • caps_topic_code    (e.g. "NOR", "PFA", "DC")
  • caps_learning_outcome  (verbatim CAPS descriptor)
  • caps_content_item_code (e.g. "10.M.NOR.1")

Alignment strategy (cascade, first match wins):
  1. Source-declared caps_* fields already populated → validate and pass through
  2. KA topic slug → KA_TOPIC_TO_CAPS lookup
  3. Common Core standard prefix → CC_TO_CAPS lookup
  4. Subject + grade → CAPS_MATHS_TOPICS / CAPS_SCIENCE_TOPICS
  5. Keyword heuristics on title / body
  6. Default: mark as unaligned (caps_phase only, no topic code)
"""
from __future__ import annotations

import logging
from typing import Any

from scripts.ingestion.config import (
    CC_TO_CAPS,
    CAPSPhase,
    CAPSSubject,
    GRADE_TO_PHASE,
    KA_TOPIC_TO_CAPS,
)
from scripts.ingestion.models import NormalisedContent

logger = logging.getLogger(__name__)


# ── CAPS Learning Outcomes (abbreviated — extend as needed) ───────────────────

_MATHS_LO: dict[str, dict[str, str]] = {
    "NOR": {
        "foundation":   "Count, order, compare and represent whole numbers; perform calculations.",
        "intermediate": "Recognise, describe and represent numbers including fractions and decimals.",
        "senior":       "Describe, represent, analyse and explain properties of numbers.",
    },
    "PFA": {
        "foundation":   "Copy, extend, describe and create patterns.",
        "intermediate": "Investigate, describe and represent geometric and numeric patterns.",
        "senior":       "Investigate and extend patterns, describe rules and relationships.",
        "fet":          "Investigate, analyse, describe and represent a wide range of functions.",
    },
    "DC":  {"fet": "Use limit notation and determine derivatives; apply differential calculus."},
    "T":   {"fet": "Explore, investigate and prove properties of special angle pairs; solve trigonometric equations."},
    "EG":  {"fet": "Investigate, describe, represent and prove Euclidean geometry theorems."},
    "ST":  {"fet": "Collect, organise, analyse and interpret data including bivariate data."},
    "F":   {"fet": "Determine the defining characteristics of functions and related inverse functions."},
    "AG":  {"fet": "Represent geometric figures on a Cartesian co-ordinate system."},
    "A":   {"fet": "Demonstrate understanding of the real number system; simplify expressions."},
    "NPS": {"fet": "Investigate number patterns including arithmetic and geometric sequences."},
    "FGD": {"fet": "Use simple and compound interest to describe and solve real-world problems."},
    "P":   {"fet": "Correctly interpret mutually exclusive and complementary events."},
}

_SCIENCE_LO: dict[str, dict[str, str]] = {
    "LL":  {
        "intermediate": "Describe and explain life processes and living systems.",
        "senior":       "Investigate, describe and explain biodiversity and classifications.",
        "fet":          "Demonstrate understanding of cell biology, ecology and genetics.",
    },
    "MM":  {
        "intermediate": "Classify and describe properties of materials; explain physical and chemical changes.",
        "senior":       "Describe bonding, reactions and properties of matter.",
    },
    "EC":  {
        "intermediate": "Describe energy forms, their inter-conversion and impact on the environment.",
        "senior":       "Investigate electrical circuits and energy transfer.",
    },
    "PEB": {
        "intermediate": "Describe features of planet Earth and the solar system.",
        "senior":       "Explain Earth's dynamic processes including the rock cycle.",
    },
    "M":   {"fet": "Apply Newton's Laws; solve problems involving momentum and energy."},
    "W":   {"fet": "Describe transverse and longitudinal waves; apply the Doppler effect."},
    "CH":  {"fet": "Explain electrochemical reactions; investigate chemical cells and batteries."},
    "CR":  {"fet": "Identify types of chemical reactions; quantitatively describe stoichiometry."},
}


# ── Public interface ──────────────────────────────────────────────────────────

def align(content: NormalisedContent) -> NormalisedContent:
    """
    Attach CAPS taxonomy to a NormalisedContent record (mutates and returns it).
    """
    grade   = content.grade
    subject = content.subject
    phase   = GRADE_TO_PHASE.get(grade).value if grade else None

    # ── 1. Pass-through if already aligned ───────────────────────────────────
    if content.caps_topic_code and content.caps_subject:
        if not content.caps_phase:
            content.caps_phase = phase
        if not content.caps_learning_outcome:
            content.caps_learning_outcome = _lookup_lo(
                content.caps_topic_code, phase, subject
            )
        return content

    # ── 2. KA topic-slug lookup ───────────────────────────────────────────────
    ka_slug = (content.extra or {}).get("source_meta", {}).get("topic_slug", "")
    if ka_slug:
        ka_map = KA_TOPIC_TO_CAPS.get(ka_slug)
        if ka_map:
            return _apply_mapping(content, ka_map, phase, "ka_topic")

    # ── 3. Common Core standard prefix lookup ─────────────────────────────────
    cc_code = _extract_cc_prefix(content)
    if cc_code:
        cc_map = CC_TO_CAPS.get(cc_code)
        if cc_map:
            return _apply_mapping(content, cc_map, phase, "cc_standard")

    # ── 4. Subject + grade → topic-tree lookup ────────────────────────────────
    if grade and phase:
        topic_code = _keyword_topic_lookup(content.title + " " + content.body[:500],
                                           subject, phase)
        if topic_code:
            lo = _lookup_lo(topic_code, phase, subject)
            content.caps_topic_code     = topic_code
            content.caps_learning_outcome = lo
            content.caps_phase          = phase
            content.caps_subject        = _caps_subject(subject)
            content.confidence_score    = max(0.5, content.confidence_score - 0.1)
            return content

    # ── 5. Minimum binding — phase only ──────────────────────────────────────
    if grade:
        content.caps_phase   = phase
        content.caps_subject = _caps_subject(subject)

    return content


def align_batch(items: list[NormalisedContent]) -> list[NormalisedContent]:
    """Align a batch of NormalisedContent records."""
    results: list[NormalisedContent] = []
    for item in items:
        try:
            results.append(align(item))
        except Exception as exc:
            logger.error("[CAPSAligner] Failed on %s: %s", item.source_id, exc)
            results.append(item)
    return results


# ── Helpers ───────────────────────────────────────────────────────────────────

def _apply_mapping(
    content: NormalisedContent,
    mapping: dict[str, Any],
    phase: str | None,
    method: str,
) -> NormalisedContent:
    topic_code = mapping.get("topic_code")
    subj       = mapping.get("subject", content.subject)
    grades     = mapping.get("grades", [])
    grade      = grades[0] if grades and not content.grade else content.grade
    ph         = GRADE_TO_PHASE.get(grade).value if grade else phase

    content.caps_phase        = ph
    content.caps_subject      = _caps_subject(subj)
    content.caps_topic_code   = topic_code
    content.caps_learning_outcome = _lookup_lo(topic_code, ph, subj)
    if grade and not content.grade:
        content.grade = grade
    if not content.subject or content.subject == "unknown":
        content.subject = subj
    content.extra = {**(content.extra or {}), "alignment_method": method}
    return content


def _caps_subject(subject: str) -> str | None:
    """Return the CAPSSubject enum value if it matches, else the raw string."""
    try:
        return CAPSSubject(subject).value
    except ValueError:
        return subject or None


def _lookup_lo(
    topic_code: str | None, phase: str | None, subject: str
) -> str | None:
    """Look up a CAPS learning outcome string."""
    if not topic_code or not phase:
        return None
    maths_like = subject in {"mathematics", "mathematical_literacy"}
    table      = _MATHS_LO if maths_like else _SCIENCE_LO
    topic_map  = table.get(topic_code, {})
    return (
        topic_map.get(phase)
        or topic_map.get("fet")
        or topic_map.get("senior")
        or next(iter(topic_map.values()), None)
    )


def _extract_cc_prefix(content: NormalisedContent) -> str | None:
    """
    Try to find a Common Core standard code in source metadata.
    Checks for patterns like '3.OA', 'HSA', 'MS-LS'.
    """
    meta    = (content.extra or {}).get("source_meta", {})
    std_ids = meta.get("standard_ids") or meta.get("common_core") or []
    if isinstance(std_ids, str):
        std_ids = [std_ids]
    for std in std_ids:
        for prefix in CC_TO_CAPS:
            if str(std).startswith(prefix):
                return prefix
    return None


# ── Keyword-based topic classifier ───────────────────────────────────────────

_MATHS_KEYWORD_MAP: dict[str, list[str]] = {
    "F":   ["function", "inverse", "exponential", "logarithm"],
    "DC":  ["calculus", "derivative", "differentiat", "gradient"],
    "T":   ["trigonometr", "sine", "cosine", "tangent", "radian"],
    "EG":  ["euclidean", "geometry", "circle theorem", "quadrilateral", "polygon"],
    "AG":  ["analytical geometry", "coordinate", "midpoint", "distance formula"],
    "ST":  ["statistic", "regression", "correlation", "normal distribution"],
    "P":   ["probabilit", "event", "sample space", "permutation", "combination"],
    "A":   ["algebra", "factori", "equation", "inequalit", "polynomial"],
    "NPS": ["sequence", "series", "arithmetic", "geometric"],
    "FGD": ["compound interest", "annuity", "depreciation", "inflation"],
    "NOR": ["fraction", "decimal", "ratio", "percent", "integer", "whole number"],
    "PFA": ["pattern", "variable", "expression", "substitut"],
    "SS":  ["shape", "symmetry", "angle", "triangle", "rectangle"],
    "SSM": ["surface area", "volume", "measurement", "perimeter"],
    "M":   ["measurement", "mass", "length", "capacity", "temperature"],
    "DH":  ["data", "graph", "median", "mode", "mean", "bar chart", "pie chart"],
}

_SCIENCE_KEYWORD_MAP: dict[str, list[str]] = {
    "LL":  ["cell", "organism", "photosynthesis", "respiration", "ecology"],
    "MM":  ["atom", "molecule", "element", "compound", "periodic table"],
    "EC":  ["energy", "current", "electricity", "circuit", "magnetism"],
    "PEB": ["rock", "earthquake", "atmosphere", "solar system", "weather"],
    "BA":  ["biodiversity", "classification", "taxonomy"],
    "CE":  ["cell biology", "mitosis", "meiosis"],
    "HH":  ["disease", "immune", "virus", "bacteria"],
    "GE":  ["genetics", "dna", "heredity", "allele", "chromosome"],
    "EV":  ["evolution", "natural selection", "adaptation"],
    "M":   ["force", "momentum", "newton", "projectile", "mechanics"],
    "W":   ["wave", "doppler", "sound", "light", "refraction"],
    "CH":  ["electrolysis", "redox", "galvanic", "electrochemical"],
    "CR":  ["reaction", "stoichiometry", "mole", "yield"],
    "MR":  ["bonding", "intermolecular", "organic", "hydrocarbons"],
}


def _keyword_topic_lookup(text: str, subject: str, phase: str) -> str | None:
    """Scan text for CAPS topic keywords and return the best-matching code."""
    text_lower = text.lower()
    maths_like = subject in {"mathematics", "mathematical_literacy"}
    keyword_map = _MATHS_KEYWORD_MAP if maths_like else _SCIENCE_KEYWORD_MAP

    # Restrict to phase-appropriate topics
    valid_topics: set[str]
    if maths_like:
        from scripts.ingestion.config import CAPS_MATHS_TOPICS
        phase_enum  = CAPSPhase(phase) if phase else None
        valid_topics = set(CAPS_MATHS_TOPICS.get(phase_enum, {}).keys()) if phase_enum else set(keyword_map)
    else:
        valid_topics = set(keyword_map)

    best_code:  str | None = None
    best_score: int        = 0

    for code, keywords in keyword_map.items():
        if code not in valid_topics:
            continue
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > best_score:
            best_score = score
            best_code  = code

    return best_code if best_score >= 1 else None
