"""
adaptive_remediation.py
=======================
Phase 4 — L4-05

Adaptive remediation path for the lesson generator.

Flow:
  1. Diagnostic engine completes and produces misconception_tags[] for a learner.
  2. lesson_generator.py calls select_remediation_strategy() with those tags.
  3. The strategy determines which of the 4 remediation modes to use:
       re-explain | worked_example_focus | practice_drill | misconception_correction
  4. The selected strategy adjusts the prompt template with targeted instructions.
  5. The generated lesson directly addresses the learner's specific misconceptions.

This implements TODO §6.4.2:
  "Detect misconception → choose explanation strategy →
   generate targeted practice → re-assess"
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Remediation strategy types
# ---------------------------------------------------------------------------

class RemediationStrategy(str, Enum):
    """
    The four remediation strategies that adapt the lesson generation prompt.
    The strategy is selected based on the pattern and severity of
    misconception_tags returned by the diagnostic engine.
    """
    RE_EXPLAIN = "re_explain"
    """
    Learner understands the procedure partially but has conceptual gaps.
    Strategy: rebuild the concept from first principles using a different
    analogy or representation (CPA: concrete → pictorial → abstract).
    """

    WORKED_EXAMPLE_FOCUS = "worked_example_focus"
    """
    Learner can recognise the concept but cannot execute the procedure.
    Strategy: provide more worked examples (4 instead of 2), each building
    on the previous, with explicit narration of the thinking process.
    """

    PRACTICE_DRILL = "practice_drill"
    """
    Learner understands the concept but needs fluency through repetition.
    Strategy: reduce explanation length, maximise practice questions (6 instead
    of 3), graduated difficulty (easy → medium → hard).
    """

    MISCONCEPTION_CORRECTION = "misconception_correction"
    """
    Learner has a specific, identifiable wrong mental model.
    Strategy: directly confront the misconception, show why it is wrong with
    a counterexample, then rebuild the correct model.
    """


# ---------------------------------------------------------------------------
# Misconception tag taxonomy
# ---------------------------------------------------------------------------

# Map from misconception tag patterns to remediation strategies.
# Tags come from the diagnostic engine and follow a structured naming
# convention: {subject}_{topic}_{specific_error}
#
# Priority order matters: MISCONCEPTION_CORRECTION is applied when a
# specific named misconception is detected. WORKED_EXAMPLE_FOCUS when
# procedure tags dominate. PRACTICE_DRILL for fluency gaps.
# RE_EXPLAIN as the fallback for general conceptual confusion.

MISCONCEPTION_TAG_TO_STRATEGY: dict[str, RemediationStrategy] = {
    # Place value misconceptions
    "place_value_digit_confusion": RemediationStrategy.MISCONCEPTION_CORRECTION,
    "place_value_adds_digits": RemediationStrategy.MISCONCEPTION_CORRECTION,
    "place_value_ignores_zeros": RemediationStrategy.MISCONCEPTION_CORRECTION,
    "place_value_reverses_columns": RemediationStrategy.MISCONCEPTION_CORRECTION,

    # Ordering / comparison misconceptions
    "ordering_longer_number_is_larger": RemediationStrategy.MISCONCEPTION_CORRECTION,
    "ordering_ignores_leading_digit": RemediationStrategy.MISCONCEPTION_CORRECTION,
    "ordering_compares_digit_by_digit_incorrectly": RemediationStrategy.MISCONCEPTION_CORRECTION,

    # Fractions misconceptions
    "fraction_larger_denominator_larger_fraction": RemediationStrategy.MISCONCEPTION_CORRECTION,
    "fraction_adds_numerators_and_denominators": RemediationStrategy.MISCONCEPTION_CORRECTION,
    "fraction_ignores_denominator_when_comparing": RemediationStrategy.MISCONCEPTION_CORRECTION,
    "fraction_confuses_numerator_denominator_roles": RemediationStrategy.RE_EXPLAIN,

    # Operations misconceptions
    "addition_no_carry": RemediationStrategy.WORKED_EXAMPLE_FOCUS,
    "subtraction_no_borrow": RemediationStrategy.WORKED_EXAMPLE_FOCUS,
    "subtraction_subtracts_smaller_from_larger_always": RemediationStrategy.MISCONCEPTION_CORRECTION,
    "multiplication_treats_as_addition": RemediationStrategy.RE_EXPLAIN,
    "multiplication_skips_zero_placeholder": RemediationStrategy.WORKED_EXAMPLE_FOCUS,
    "division_ignores_remainder": RemediationStrategy.WORKED_EXAMPLE_FOCUS,

    # Shapes/geometry
    "shapes_conflates_area_perimeter": RemediationStrategy.MISCONCEPTION_CORRECTION,
    "shapes_counts_corners_as_sides": RemediationStrategy.MISCONCEPTION_CORRECTION,
    "shapes_identifies_by_orientation_only": RemediationStrategy.WORKED_EXAMPLE_FOCUS,

    # Fluency / speed gaps (not conceptual — need drilling)
    "fluency_slow_number_bonds": RemediationStrategy.PRACTICE_DRILL,
    "fluency_slow_times_tables": RemediationStrategy.PRACTICE_DRILL,
    "fluency_slow_place_value_reading": RemediationStrategy.PRACTICE_DRILL,

    # General confusion (fallback)
    "general_conceptual_confusion": RemediationStrategy.RE_EXPLAIN,
}


# ---------------------------------------------------------------------------
# Strategy selection logic
# ---------------------------------------------------------------------------

def select_remediation_strategy(
    misconception_tags: list[str],
) -> RemediationStrategy:
    """
    Given a list of misconception tags from the diagnostic engine,
    select the most appropriate remediation strategy.

    Priority rules:
    1. If ANY tag maps to MISCONCEPTION_CORRECTION → use that (highest priority:
       wrong mental models must be directly confronted before anything else).
    2. If majority of tags map to WORKED_EXAMPLE_FOCUS → use that.
    3. If majority of tags map to PRACTICE_DRILL → use that.
    4. Default: RE_EXPLAIN (rebuild from scratch).

    Args:
        misconception_tags: List of diagnostic tag strings.

    Returns:
        The selected RemediationStrategy.
    """
    if not misconception_tags:
        logger.debug("No misconception tags provided — using RE_EXPLAIN as default.")
        return RemediationStrategy.RE_EXPLAIN

    resolved_strategies: list[RemediationStrategy] = []
    unrecognised_tags: list[str] = []

    for tag in misconception_tags:
        strategy = MISCONCEPTION_TAG_TO_STRATEGY.get(tag)
        if strategy:
            resolved_strategies.append(strategy)
        else:
            logger.warning("Unrecognised misconception tag '%s' — treating as RE_EXPLAIN.", tag)
            unrecognised_tags.append(tag)
            resolved_strategies.append(RemediationStrategy.RE_EXPLAIN)

    # Rule 1: Any MISCONCEPTION_CORRECTION wins
    if RemediationStrategy.MISCONCEPTION_CORRECTION in resolved_strategies:
        logger.info(
            "Remediation strategy: MISCONCEPTION_CORRECTION (triggered by tags: %s)",
            [t for t in misconception_tags
             if MISCONCEPTION_TAG_TO_STRATEGY.get(t) == RemediationStrategy.MISCONCEPTION_CORRECTION],
        )
        return RemediationStrategy.MISCONCEPTION_CORRECTION

    # Rules 2–4: majority vote
    strategy_counts: dict[RemediationStrategy, int] = {}
    for s in resolved_strategies:
        strategy_counts[s] = strategy_counts.get(s, 0) + 1

    selected = max(strategy_counts, key=lambda s: strategy_counts[s])
    logger.info(
        "Remediation strategy: %s (vote counts: %s)",
        selected.value,
        {s.value: c for s, c in strategy_counts.items()},
    )
    return selected


# ---------------------------------------------------------------------------
# Strategy → Prompt injection
# ---------------------------------------------------------------------------

class RemediationPromptConfig(BaseModel):
    """
    Prompt injection parameters for a remediation strategy.
    Rendered into the lesson generation Jinja2 template when a
    remediation path is active.
    """
    strategy: RemediationStrategy
    strategy_label: str
    misconception_tags: list[str]

    # Prompt injection fields
    remediation_framing: str = Field(
        description="Opening instruction injected at the top of the prompt."
    )
    explanation_adjustment: str = Field(
        description="How to adjust the explanation for this strategy."
    )
    example_adjustment: str = Field(
        description="How to adjust worked examples for this strategy."
    )
    question_adjustment: str = Field(
        description="How to adjust practice questions for this strategy."
    )
    counterexample_instruction: Optional[str] = Field(
        None,
        description="For MISCONCEPTION_CORRECTION only: how to present the counterexample.",
    )


STRATEGY_PROMPT_TEMPLATES: dict[RemediationStrategy, str] = {

    RemediationStrategy.RE_EXPLAIN: """
=== ADAPTIVE REMEDIATION: RE-EXPLAIN ===
This lesson is for a learner who has NOT yet grasped the core concept.
Do NOT assume prior understanding. Start completely from scratch.

EXPLANATION ADJUSTMENT:
- Use a DIFFERENT analogy or real-world context than the standard lesson.
- Begin with physical/concrete objects a SA Grade 4 learner can touch or see.
- Follow the CPA progression strictly: Concrete → Pictorial → Abstract.
- Introduce abstract notation (symbols, equations) ONLY after the concept is
  grounded in the concrete representation.
- Use simpler numbers in the initial explanation (e.g. start with 2-digit numbers
  before 4-digit numbers for place value topics).

WORKED EXAMPLES ADJUSTMENT:
- Provide 2 worked examples, starting with the simplest possible version of
  the concept (minimal numbers, no edge cases).
- Narrate the thinking process in first-person: "First, I look at... Then I ask myself..."

PRACTICE QUESTIONS ADJUSTMENT:
- Start with 2 very easy questions (no distractors — just the concept stated simply),
  then 1 medium question with distractors.
- Include a 'BEFORE YOU START' reminder box before each question.

MISCONCEPTION TAGS TO ADDRESS:
{% for tag in misconception_tags %}- {{ tag }}
{% endfor %}
""",

    RemediationStrategy.WORKED_EXAMPLE_FOCUS: """
=== ADAPTIVE REMEDIATION: WORKED EXAMPLE FOCUS ===
This learner understands the concept but cannot execute the procedure reliably.
They need to SEE more examples of the procedure before attempting independently.

EXPLANATION ADJUSTMENT:
- Keep the explanation brief (2–3 paragraphs maximum).
- Focus the explanation on the PROCEDURE, not the concept.
- Highlight the exact steps using a numbered checklist.

WORKED EXAMPLES ADJUSTMENT:
- Provide 4 worked examples instead of 2 (override the standard requirement).
- Each example must build on the previous in difficulty:
  Example 1: Simplest case (2-digit numbers, no carrying/borrowing).
  Example 2: Slightly harder (3-digit, one carrying/borrowing step).
  Example 3: Standard Grade 4 difficulty (4-digit, full procedure).
  Example 4: Near-transfer (same procedure, slightly different context).
- Each step in the solution must be narrated: "I do this because..."

PRACTICE QUESTIONS ADJUSTMENT:
- Provide 3 practice questions, each preceded by a 'THINKING PROMPT':
  "Before you start, which step comes first?" (multiple choice, 2 options).
- The THINKING PROMPT does not require an answer key — it is scaffolding only.

MISCONCEPTION TAGS TO ADDRESS:
{% for tag in misconception_tags %}- {{ tag }}
{% endfor %}
""",

    RemediationStrategy.PRACTICE_DRILL: """
=== ADAPTIVE REMEDIATION: PRACTICE DRILL ===
This learner understands the concept but needs fluency through repetition.
Maximise the number of practice opportunities. Minimise explanation length.

EXPLANATION ADJUSTMENT:
- Provide a SHORT recap explanation only (1 paragraph, maximum 100 words).
- Do NOT re-teach the concept from scratch.
- Use the recap to activate prior knowledge: "You already know that..."

WORKED EXAMPLES ADJUSTMENT:
- Provide 1 worked example only (the most representative case).
- Make the example very fast to read — short, direct, no extended narration.

PRACTICE QUESTIONS ADJUSTMENT:
- Provide 6 practice questions instead of 3 (override the standard requirement).
- Graduated difficulty:
  Questions 1–2: Easy (recall / recognition)
  Questions 3–4: Medium (application)
  Questions 5–6: Hard (near-transfer / multi-step)
- Include a TIMER SUGGESTION: "Try to answer each question in under 2 minutes."
- Include a SCORE TRACKER at the end: "My score: ___ / 6"

MISCONCEPTION TAGS TO ADDRESS:
{% for tag in misconception_tags %}- {{ tag }}
{% endfor %}
""",

    RemediationStrategy.MISCONCEPTION_CORRECTION: """
=== ADAPTIVE REMEDIATION: MISCONCEPTION CORRECTION ===
This learner has a SPECIFIC WRONG MENTAL MODEL that must be directly confronted
before any new teaching can succeed. Do NOT avoid the misconception — address it
head-on with a counterexample that proves it wrong.

EXPLANATION ADJUSTMENT:
- Begin the explanation with the misconception itself (stated gently, not accusatorially):
  "Some learners think that [misconception]. Let's find out why that is not correct."
- Immediately provide a COUNTEREXAMPLE that disproves the misconception:
  A concrete case where applying the wrong rule gives an obviously wrong answer.
- Then explain the CORRECT rule, contrasting it with the wrong rule.
- Use a side-by-side comparison table where possible:
  | WRONG way (common mistake) | CORRECT way |
  | [wrong procedure] | [correct procedure] |

WORKED EXAMPLES ADJUSTMENT:
- Worked Example 1: Show the misconception in action → show the wrong answer it produces
  → show why the wrong answer is clearly wrong → correct the approach.
- Worked Example 2: Standard correct approach (reinforcing the right mental model).

PRACTICE QUESTIONS ADJUSTMENT:
- Question 1 must DIRECTLY TEST whether the learner has corrected their misconception
  (the distractor for the wrong option must be the exact answer the misconception predicts).
- After this question, include a 'MISCONCEPTION CHECK' callout box:
  "If you chose [wrong option], here's what happened: [brief explanation]."
- Questions 2 and 3 are standard practice.

MISCONCEPTIONS TO CORRECT DIRECTLY:
{% for tag in misconception_tags %}- {{ tag }}
{% endfor %}
""",
}


def build_remediation_prompt_injection(
    misconception_tags: list[str],
) -> tuple[RemediationStrategy, str]:
    """
    Given misconception_tags from the diagnostic, returns:
    - The selected RemediationStrategy
    - The prompt injection string to embed in the lesson generation template

    Usage in lesson_generator.py:
        strategy, injection = build_remediation_prompt_injection(misconception_tags)
        prompt = render_template(..., remediation_injection=injection, ...)
    """
    from jinja2 import Template

    strategy = select_remediation_strategy(misconception_tags)
    template_str = STRATEGY_PROMPT_TEMPLATES[strategy]
    rendered = Template(template_str).render(misconception_tags=misconception_tags)

    logger.info(
        "Remediation prompt built: strategy=%s, tags=%s",
        strategy.value,
        misconception_tags,
    )
    return strategy, rendered.strip()
