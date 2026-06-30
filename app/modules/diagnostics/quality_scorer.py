"""
app/modules/diagnostics/quality_scorer.py
─────────────────────────────────────────────────────────────────────────────
Phase 3: Per-Item Quality Scorer (P3-11)

Computes a composite quality_score for each item:

    quality_score = 0.40 × correctness_score
                  + 0.30 × caps_alignment_score
                  + 0.20 × readability_score
                  + 0.10 × south_african_context_score

Weights match the roadmap specification. All component scores are 0.0–1.0.
The final quality_score is a float in [0.0, 1.0].

Usage:
    scorer = QualityScorer(topic_map=topic_map)
    item_with_score = scorer.score(item)

Or in batch via the CLI:
    python scripts/score_items.py --input data/caps/grade4_maths_item_bank.json
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import re
import logging
from typing import Optional

from app.modules.diagnostics.item_validator import flesch_kincaid_grade

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# South African context signals
# ---------------------------------------------------------------------------

SA_CURRENCY_PATTERN = re.compile(r"\b(rand|rands|cent|cents|R\s?\d|r\s?\d)\b", re.I)

SA_NAMES_PATTERN = re.compile(
    r"\b(sipho|nomsa|thabo|lerato|zanele|mpho|bongani|ayanda|lindiwe|nkosi"
    r"|pieter|annelie|fatima|priya|amahle|sibusiso|lungelo|thandeka)\b",
    re.I,
)

SA_CONTEXT_WORDS = re.compile(
    r"\b(township|veld|braai|samp|pap|taxi|stoep|dorp|kraal|shebeen"
    r"|ubuntu|lekker|borehole|maize|mielie|rondavel|kwaito|sangoma"
    r"|south african|south africa|gauteng|kwazulu|limpopo|pretoria"
    r"|johannesburg|cape town|durban|soweto)\b",
    re.I,
)

SA_METRIC_UNITS = re.compile(r"\b(km|metre|meter|kg|gram|litre|liter|ml)\b", re.I)


# ---------------------------------------------------------------------------
# CAPS alignment signals
# ---------------------------------------------------------------------------

def _topic_lookup(topic_map: dict) -> dict[str, dict]:
    topics = topic_map.get("topics", {})
    if isinstance(topics, dict) and topics:
        return topics

    lookup: dict[str, dict] = {}
    for term in topic_map.get("terms", []):
        term_no = term.get("term")
        for topic in term.get("topics", []):
            topic_ref = topic.get("caps_ref")
            if topic_ref:
                standards = []
                misconceptions = []
                for subtopic in topic.get("subtopics", []):
                    standards.extend(subtopic.get("assessment_standards", []))
                    misconceptions.extend(subtopic.get("common_misconceptions", []))
                lookup[topic_ref] = {
                    "grade": topic_map.get("grade"),
                    "subject": topic_map.get("subject"),
                    "term": term_no,
                    "topic": topic.get("topic"),
                    "subtopic": topic.get("topic"),
                    "skill": topic.get("topic"),
                    "assessment_standards": standards,
                    "common_misconceptions": misconceptions,
                }
            for subtopic in topic.get("subtopics", []):
                subtopic_ref = subtopic.get("caps_ref")
                if subtopic_ref:
                    lookup[subtopic_ref] = {
                        "grade": topic_map.get("grade"),
                        "subject": topic_map.get("subject"),
                        "term": term_no,
                        "topic": topic.get("topic"),
                        "subtopic": subtopic.get("subtopic"),
                        "skill": subtopic.get("subtopic"),
                        "assessment_standards": subtopic.get("assessment_standards", []),
                        "common_misconceptions": subtopic.get("common_misconceptions", []),
                    }
    return lookup


def _caps_alignment_score(item: dict, topic_map: dict) -> float:
    """
    1.0  - caps_ref is in topic map AND skill/topic/subtopic match.
    0.7  - caps_ref is in topic map but fields do not fully match.
    0.3  - caps_ref not in topic map (unknown reference).
    """
    caps_ref = item.get("caps_ref", "")
    topics = _topic_lookup(topic_map)

    if caps_ref not in topics:
        return 0.3

    topic_entry = topics[caps_ref]
    item_subtopic = item.get("subtopic")
    expected_subtopic = topic_entry.get("subtopic")
    is_topic_level_ref = len(str(caps_ref).split(".")) == 4
    subtopic_matches = is_topic_level_ref or item_subtopic in {expected_subtopic, topic_entry.get("topic")}
    skill_matches = is_topic_level_ref or item.get("skill") in {topic_entry.get("skill"), topic_entry.get("topic"), expected_subtopic}
    matches = sum([
        item.get("topic") == topic_entry.get("topic"),
        subtopic_matches,
        skill_matches,
        item.get("grade") == topic_entry.get("grade"),
        item.get("term") == topic_entry.get("term"),
    ])
    return round(0.3 + 0.7 * (matches / 5), 2)


# ---------------------------------------------------------------------------
# Correctness score (proxy — uses answer-key and distractor quality signals)
# ---------------------------------------------------------------------------

def _correctness_score(item: dict) -> float:
    """
    Proxy correctness score based on structural signals.
    True correctness is established by the two-call LLM verification (P2-07).
    This scoring is for ranking, not gating.

    Signals:
      - explanation mentions the answer key label                (+0.20)
      - distractor_rationale is complete and non-empty          (+0.30)
      - misconception_tags are present                           (+0.20)
      - options have distinct text (no duplicates)               (+0.15)
      - explanation is adequately long (≥ 20 words)             (+0.15)
    """
    score = 0.0
    answer_key  = str(item.get("answer_key", "")).upper()
    explanation = item.get("explanation", "")
    options     = item.get("options", [])
    distractor  = item.get("distractor_rationale", {})
    tags        = item.get("misconception_tags", [])

    # Explanation references the answer
    if answer_key and answer_key.lower() in explanation.lower():
        score += 0.20

    # Distractor rationale complete
    wrong_count = sum(
        1 for o in options
        if str(o.get("label", "")).upper() != answer_key
    )
    filled = sum(
        1 for k, v in distractor.items()
        if str(k).upper() != answer_key and str(v).strip()
    )
    if wrong_count > 0:
        score += 0.30 * (filled / wrong_count)

    # Misconception tags
    if tags:
        score += 0.20

    # Distinct option texts
    texts = [str(o.get("text", "")).lower().strip() for o in options]
    if len(set(texts)) == len(texts):
        score += 0.15

    # Explanation length
    if len(explanation.split()) >= 20:
        score += 0.15

    return round(min(score, 1.0), 3)


# ---------------------------------------------------------------------------
# Readability score
# ---------------------------------------------------------------------------

def _readability_score(item: dict) -> float:
    """
    1.0  — FK ≤ 4.0  (very accessible)
    0.8  — FK ≤ 5.0
    0.6  — FK ≤ 6.0  (target max)
    0.3  — FK ≤ 8.0  (borderline)
    0.0  — FK  > 8.0  (too complex)
    """
    stem = item.get("stem", "")
    if not stem.strip():
        return 0.0
    fk = flesch_kincaid_grade(stem)
    if fk <= 4.0:
        return 1.0
    if fk <= 5.0:
        return 0.8
    if fk <= 6.0:
        return 0.6
    if fk <= 8.0:
        return 0.3
    return 0.0


# ---------------------------------------------------------------------------
# South African context score
# ---------------------------------------------------------------------------

def _sa_context_score(item: dict) -> float:
    """
    Checks stem + options for South African language signals.
    0.0–1.0 based on signal density.
    """
    texts = [item.get("stem", "")]
    for opt in item.get("options", []):
        texts.append(opt.get("text", ""))
    combined = " ".join(texts)

    signals = 0
    if SA_CURRENCY_PATTERN.search(combined):
        signals += 1
    if SA_NAMES_PATTERN.search(combined):
        signals += 1
    if SA_CONTEXT_WORDS.search(combined):
        signals += 1
    if SA_METRIC_UNITS.search(combined):
        signals += 0.5

    return round(min(signals / 2, 1.0), 3)


# ---------------------------------------------------------------------------
# Scorer
# ---------------------------------------------------------------------------

class QualityScorer:
    """
    Computes the composite quality_score for a diagnostic item.

    quality_score = 0.40 × correctness
                  + 0.30 × caps_alignment
                  + 0.20 × readability
                  + 0.10 × south_african_context
    """

    WEIGHTS = {
        "correctness":    0.40,
        "caps_alignment": 0.30,
        "readability":    0.20,
        "sa_context":     0.10,
    }

    def __init__(self, topic_map: Optional[dict] = None) -> None:
        self._topic_map = topic_map or {}

    def score(self, item: dict) -> dict:
        """
        Compute quality_score and return a copy of item with the score set.
        Also adds component_scores for transparency.
        """
        components = {
            "correctness":    _correctness_score(item),
            "caps_alignment": _caps_alignment_score(item, self._topic_map),
            "readability":    _readability_score(item),
            "sa_context":     _sa_context_score(item),
        }

        quality_score = round(
            sum(components[k] * self.WEIGHTS[k] for k in self.WEIGHTS),
            3,
        )

        enriched = dict(item)
        enriched["quality_score"]      = quality_score
        enriched["component_scores"]   = components

        logger.debug(
            "Item %s quality_score=%.3f %s",
            str(item.get("item_id", "?"))[:8],
            quality_score,
            components,
        )
        return enriched

    def score_batch(self, items: list[dict]) -> list[dict]:
        """Score a list of items. Returns new list with quality_score populated."""
        return [self.score(item) for item in items]

    def report(self, items: list[dict]) -> None:
        """Print a quality distribution report for a list of pre-scored items."""
        scored = [i for i in items if i.get("quality_score") is not None]
        if not scored:
            print("No scored items to report.")
            return

        scores = [i["quality_score"] for i in scored]
        avg    = sum(scores) / len(scores)
        above  = sum(1 for s in scores if s >= 0.7)

        print(f"\n{'─'*55}")
        print(f"  Quality Score Report ({len(scored)} items)")
        print(f"{'─'*55}")
        print(f"  Average quality_score:   {avg:.3f}")
        print(f"  Items ≥ 0.7 (threshold): {above}/{len(scored)}")
        print(f"  Min / Max:               {min(scores):.3f} / {max(scores):.3f}")

        # Distribution by caps_ref
        refs = sorted({i.get("caps_ref", "?") for i in scored})
        for ref in refs:
            ref_scores = [i["quality_score"] for i in scored if i.get("caps_ref") == ref]
            ref_avg    = sum(ref_scores) / len(ref_scores) if ref_scores else 0
            print(f"  {ref:12s}  avg={ref_avg:.3f}  n={len(ref_scores)}")
        print()
