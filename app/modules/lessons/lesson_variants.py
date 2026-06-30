"""
lesson_variants.py
==================
Phase 4 — L4-04

'Explain it my way' adaptive lesson variant system.

Supported variant types (§6.4.1):
  - visual         : diagram-first, shapes/arrays/number lines, spatial explanations
  - story          : narrative framing, SA story context, characters solving real problems
  - step_by_step   : ultra-granular procedural breakdown, one micro-step per line
  - exam_style     : CAPS exam-format questions, marks allocated, formal phrasing
  - multilingual   : bilingual English/isiZulu or English/Afrikaans scaffolding

The variant_type is accepted by the lesson generator as an input parameter and
is forwarded to the Jinja2 prompt adapter in this module, which injects
variant-specific instructions into the lesson_generation_v1.jinja2 template.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Variant type enum
# ---------------------------------------------------------------------------

class LessonVariantType(str, Enum):
    """
    Lesson presentation variants supported by the generation pipeline.
    Each variant adjusts the prompt template to produce a stylistically
    different explanation of the same CAPS content.
    """
    VISUAL = "visual"
    STORY = "story"
    STEP_BY_STEP = "step_by_step"
    EXAM_STYLE = "exam_style"
    MULTILINGUAL = "multilingual"


# ---------------------------------------------------------------------------
# Variant configuration models
# ---------------------------------------------------------------------------

class VariantPromptConfig(BaseModel):
    """
    Carries all variant-specific prompt injection parameters.
    An instance of this is rendered into the Jinja2 template alongside the
    standard lesson generation variables.
    """
    variant_type: LessonVariantType
    variant_label: str = Field(description="Human-readable label shown in the UI.")

    # Prompt injection fields — rendered inside {{ ... }} in the template
    explanation_style_instruction: str = Field(
        description="Injected into the prompt to shape explanation style."
    )
    example_format_instruction: str = Field(
        description="Injected to control how worked examples are presented."
    )
    question_format_instruction: str = Field(
        description="Injected to control practice question format."
    )
    additional_constraints: list[str] = Field(
        default_factory=list,
        description="Additional hard constraints appended to the prompt.",
    )
    target_language_note: Optional[str] = Field(
        None,
        description="For multilingual variant: language pair and scaffolding instruction.",
    )


# ---------------------------------------------------------------------------
# Variant configuration registry
# ---------------------------------------------------------------------------

VARIANT_CONFIGS: dict[LessonVariantType, VariantPromptConfig] = {

    LessonVariantType.VISUAL: VariantPromptConfig(
        variant_type=LessonVariantType.VISUAL,
        variant_label="Visual / Diagram-First",
        explanation_style_instruction=(
            "Explain this concept using visual, spatial reasoning. "
            "Start with a diagram description (e.g. number line, array, shape partition, "
            "place-value table, or area model) BEFORE introducing any abstract rule or formula. "
            "Describe the diagram in enough detail that a learner can draw it on paper. "
            "Use phrases like 'draw a number line from 0 to 1000', 'shade 3 out of 4 equal parts', "
            "'write the digits in a place-value table with columns: Thousands | Hundreds | Tens | Ones'. "
            "Do NOT start with a formula or rule."
        ),
        example_format_instruction=(
            "Each worked example MUST include: "
            "(1) a diagram description the learner should draw, "
            "(2) a step-by-step solution that refers to the diagram, "
            "(3) the final answer circled or highlighted. "
            "Format the diagram description as: DIAGRAM: [description]."
        ),
        question_format_instruction=(
            "At least one practice question must ask the learner to draw or complete "
            "a diagram (number line, shape, table) as part of the solution. "
            "Describe the expected diagram in the answer key."
        ),
        additional_constraints=[
            "Every abstract concept must be preceded by a concrete visual representation.",
            "Use spatial language: above, below, left, right, inside, between, next to.",
            "Number lines must specify start, end, and interval (e.g. 'number line from 0 to 1000, mark every 100').",
        ],
    ),

    LessonVariantType.STORY: VariantPromptConfig(
        variant_type=LessonVariantType.STORY,
        variant_label="Story-Based / Narrative",
        explanation_style_instruction=(
            "Frame this entire lesson as a short South African story. "
            "Introduce a Grade 4 learner character with a South African name (e.g. Sipho, Amahle, Kagiso, Fatima). "
            "The character faces a real-life SA problem that requires this maths concept to solve "
            "(e.g. sharing bread rolls at a school tuck shop, counting tiles at a community centre, "
            "comparing prices at a spaza shop, dividing maize meal portions). "
            "Weave the mathematical explanation INTO the story — do not interrupt the narrative "
            "with dry definitions. The explanation should emerge naturally as the character solves the problem."
        ),
        example_format_instruction=(
            "Worked examples must be framed as story episodes: "
            "'In the next scene, Sipho needs to...'. "
            "The step-by-step solution should read as the character's thinking process, "
            "written in simple first-person or third-person narrative. "
            "Each example should advance the story slightly."
        ),
        question_format_instruction=(
            "Practice questions should be set in the same story world: "
            "'Help Amahle solve the next problem in the story...'. "
            "This maintains narrative engagement. "
            "Do NOT switch to dry exam-style phrasing mid-story."
        ),
        additional_constraints=[
            "The story must be set in South Africa. Use authentic SA settings: townships, farms, schools, markets.",
            "The character must be the same age as the learner (Grade 4, approximately 9–10 years old).",
            "The story should end with the character successfully solving the problem using the taught concept.",
            "Do not use fantasy settings, overseas settings, or adult problems.",
            "Avoid stereotypes — the character can be from any SA cultural background.",
        ],
    ),

    LessonVariantType.STEP_BY_STEP: VariantPromptConfig(
        variant_type=LessonVariantType.STEP_BY_STEP,
        variant_label="Step-by-Step / Procedural",
        explanation_style_instruction=(
            "Break this concept down into the smallest possible procedural steps. "
            "Use numbered steps for the explanation. Each step must be ONE action only — "
            "never combine two actions in one step. "
            "Example of correct granularity: "
            "Step 1: Write down the number 3 456. "
            "Step 2: Look at the digit in the hundreds place. "
            "Step 3: The hundreds digit is 4. "
            "Step 4: Look at the digit in the tens place. "
            "WRONG: 'Step 1: Write the number and identify the hundreds digit.' (too many actions)."
        ),
        example_format_instruction=(
            "Each worked example must use a numbered checklist format. "
            "Begin with: 'WHAT I NEED TO DO:' followed by the problem statement. "
            "Then: 'HOW I DO IT:' followed by numbered micro-steps. "
            "End with: 'MY ANSWER: [final answer]'. "
            "Every step must be on its own line. "
            "Target: 6–12 steps per worked example for Grade 4 Maths."
        ),
        question_format_instruction=(
            "After each practice question, include a hint card: "
            "'STUCK? Try these steps:' followed by 3 starter steps. "
            "The hint card should NOT give away the answer — "
            "it should prompt the learner to begin the procedure."
        ),
        additional_constraints=[
            "Use imperative verbs to start each step: Write, Look, Circle, Count, Add, Subtract, Multiply, Draw.",
            "Never assume a step is 'obvious' — if a child must do it, it must be a step.",
            "The total number of steps in a worked example should be between 6 and 12 for Grade 4.",
        ],
    ),

    LessonVariantType.EXAM_STYLE: VariantPromptConfig(
        variant_type=LessonVariantType.EXAM_STYLE,
        variant_label="Exam-Style / CAPS Formal",
        explanation_style_instruction=(
            "Write the explanation in formal CAPS examination style. "
            "Use the precise mathematical vocabulary required in CAPS Grade 4 assessments. "
            "Structure the explanation as if it were the 'worked example' section of a CAPS-aligned "
            "Grade 4 formal assessment paper. "
            "Include the mark allocation for each part (e.g. '[2 marks]'). "
            "Use CAPS-prescribed terminology — do not invent informal names for mathematical operations."
        ),
        example_format_instruction=(
            "Format each worked example as a CAPS formal question: "
            "'Question 1 [4 marks]' followed by the question, then 'Solution:' with marks per step. "
            "Example: "
            "Question 1.1 [2 marks]: Arrange the following numbers in descending order: 3 456; 4 356; 3 546 "
            "Solution: 4 356 > 3 546 > 3 456  ✓[1] ✓[1]"
        ),
        question_format_instruction=(
            "All practice questions must be formatted as a formal CAPS question paper. "
            "Include: Question number, mark allocation in brackets [n marks], "
            "sub-questions labelled 1.1, 1.2, 1.3, etc. "
            "The answer key must include marks per step (method marks + accuracy marks). "
            "Total marks for the practice section must be stated."
        ),
        additional_constraints=[
            "Use CAPS-prescribed mathematical vocabulary only.",
            "Include a TOTAL MARKS line at the end of the practice section.",
            "Mark allocations must reflect CAPS formal assessment conventions.",
            "All numbers in questions must be written with spaces as thousand separators (e.g. 3 456 not 3,456).",
        ],
    ),

    LessonVariantType.MULTILINGUAL: VariantPromptConfig(
        variant_type=LessonVariantType.MULTILINGUAL,
        variant_label="Bilingual / Multilingual Scaffolding",
        explanation_style_instruction=(
            "Write the explanation bilingually: English as the primary language, "
            "with isiZulu translations of key mathematical terms and concept sentences provided "
            "immediately after in parentheses or as a sidebar. "
            "Focus bilingual support on: (1) the lesson title, "
            "(2) key mathematical vocabulary (5–8 terms), "
            "(3) the main explanation paragraph, "
            "(4) the instructions for each worked example and practice question. "
            "The goal is to scaffold comprehension for isiZulu-medium learners "
            "who are transitioning to English-medium instruction."
        ),
        example_format_instruction=(
            "Each worked example must include: "
            "- The question in English "
            "- A bilingual vocabulary box: KEY WORDS | AMAGAMA ABALULEKILE with 3–5 terms "
            "- The step-by-step solution in English "
            "- The final answer restated in both English and isiZulu "
            "Example: 'The answer is 3 456. | Impendulo ithi u-3 456.'"
        ),
        question_format_instruction=(
            "Instructions for practice questions must be provided in both English and isiZulu: "
            "'Answer the following questions. | Phendula imibuzo elandelayo.' "
            "Question stems may be in English only, but provide a bilingual hint card if available."
        ),
        target_language_note=(
            "Language pair: English (primary) + isiZulu (scaffolding language). "
            "isiZulu translations must be grammatically correct. "
            "Mathematical terms should use the official isiZulu mathematical vocabulary "
            "as per the DBE Language Policy for Mathematics. "
            "If a term has no established isiZulu equivalent, use the English term with a brief explanation."
        ),
        additional_constraints=[
            "Do not mix languages mid-sentence (code-switching is acceptable in the vocabulary box only).",
            "isiZulu translations must be clearly marked — use italics or the label 'IsiZulu:' as prefix.",
            "The lesson must be fully comprehensible in English alone — the isiZulu is scaffolding, not required.",
        ],
    ),
}


# ---------------------------------------------------------------------------
# Adapter function — used by lesson_generator.py
# ---------------------------------------------------------------------------

def get_variant_prompt_config(
    variant_type: Optional[LessonVariantType],
) -> Optional[VariantPromptConfig]:
    """
    Returns the VariantPromptConfig for the given variant_type.
    Returns None if variant_type is None (standard lesson, no variant adaptation).

    Usage in lesson_generator.py:
        variant_config = get_variant_prompt_config(request.variant_type)
        rendered_prompt = render_lesson_prompt(caps_ref, ..., variant_config=variant_config)
    """
    if variant_type is None:
        return None
    config = VARIANT_CONFIGS.get(variant_type)
    if config is None:
        raise ValueError(
            f"Unknown variant_type '{variant_type}'. "
            f"Supported types: {[v.value for v in LessonVariantType]}"
        )
    logger.debug("Resolved variant config for '%s': %s", variant_type, config.variant_label)
    return config


def list_supported_variants() -> list[dict]:
    """Returns a list of supported variant types for the API capabilities endpoint."""
    return [
        {
            "variant_type": vt.value,
            "label": cfg.variant_label,
            "description": cfg.explanation_style_instruction[:120] + "...",
        }
        for vt, cfg in VARIANT_CONFIGS.items()
    ]
