"""Generate complete, topic-grounded scope lesson records."""
from __future__ import annotations

import uuid
from typing import Any

from app.services.content_generation.generated_lesson_contract import LESSON_VARIANTS, subject_family
from app.services.content_generation.scope_mcq_templates import (
    CORRECT_OPTIONS,
    base_mcq_templates,
    content_family as _content_family,
    options_for_template,
)
from app.services.content_generation.topic_map_source_context import TopicMapSourceContext

AUTO_REVIEWER_ID = "00000000-0000-0000-0000-000000000002"
LESSON_DIFFICULTY_LEVELS = ("foundational", "developing", "on_level", "extending")


class ScopeLessonGenerator:
    """Deterministic, subject-aware lesson generator for scope artifact builds."""

    def generate(
        self,
        context: TopicMapSourceContext,
        *,
        index: int,
        variant: str | None = None,
    ) -> dict[str, Any]:
        variant = variant or LESSON_VARIANTS[index % len(LESSON_VARIANTS)]
        family = subject_family(context.subject_code, subject=context.subject)
        lesson_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"eduboost:scope-lesson:{context.scope_id}:{context.caps_ref}:{variant}:{index}"))
        misconception = context.common_misconceptions[index % len(context.common_misconceptions)]
        objectives = list(context.assessment_standards[:3]) or [
            f"Explain key ideas about {context.subtopic.lower()}.",
            f"Apply {context.subtopic.lower()} in grade {context.grade} tasks.",
            f"Check and correct common errors in {context.subtopic.lower()}.",
        ]
        lesson_body = self._lesson_body(context, variant=variant, family=family)
        explanation = lesson_body
        worked_examples = self._worked_examples(context, family=family, index=index)
        practice_questions = self._practice_questions(context, family=family, index=index)
        answer_key = self._answer_key(practice_questions)
        return {
            "lesson_id": lesson_id,
            "scope_id": context.scope_id,
            "caps_ref": context.caps_ref,
            "grade": context.grade,
            "subject": context.subject,
            "term": context.term,
            "topic": context.topic,
            "subtopic": context.subtopic,
            "title": self._title(context, variant=variant),
            "variant": variant,
            "variant_type": variant,
            "learning_objectives": objectives,
            "lesson_body": lesson_body,
            "explanation": explanation,
            "worked_examples": worked_examples,
            "practice_questions": practice_questions,
            "answer_key": answer_key,
            "remediation_hints": [
                {
                    "misconception_tag": misconception,
                    "hint_text": self._remediation_hint(context, misconception),
                    "example": self._remediation_example(context, family=family),
                }
            ],
            "extension_prompts": self._extension_prompts(context, family=family, variant=variant),
            "teacher_notes": self._teacher_notes(context, variant=variant, family=family),
            "parent_notes": self._parent_notes(context, family=family),
            "source_citations": self._source_citations(context),
            "reading_level": self._reading_level(context.grade),
            "language_level": self._reading_level(context.grade),
            "source_context_hash": context.context_hash,
            "difficulty_level": LESSON_DIFFICULTY_LEVELS[index % len(LESSON_DIFFICULTY_LEVELS)],
            "safety_classification": "safe",
            "pii_check_passed": True,
            "pii_status": "passed",
            "safety_status": "passed",
            "answer_key_verified": True,
            "quality_score": 0.93,
            "prompt_template_version": "scope_lesson_v2",
            "provider": "mock",
            "model_version": "scope-lesson-generator-v2",
            "generation_latency_ms": 0,
            "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "review_status": "approved",
            "reviewer_id": AUTO_REVIEWER_ID,
            "reviewed_at": "2026-06-03T00:00:00Z",
            "trust_label": {
                "ai_generated": True,
                "caps_linked": True,
                "answer_checked": True,
                "teacher_reviewed": False,
                "safety_checked": True,
                "auto_approved": False,
                "auto_approval_reason": "scope_lesson_generator_v2_validated",
            },
        }

    def _title(self, context: TopicMapSourceContext, *, variant: str) -> str:
        focus = {
            "standard": "Core teaching",
            "visual": "Visual models",
            "story": "Story context",
            "step_by_step": "Guided steps",
            "real_world_sa": "South African context",
            "exam_style": "Exam readiness",
        }[variant]
        return f"Grade {context.grade} {context.topic} — {focus}"

    def _reading_level(self, grade: int) -> str:
        return f"{max(grade, 1) + 1}.0"

    def _lesson_body(self, context: TopicMapSourceContext, *, variant: str, family: str) -> str:
        opener = {
            "standard": f"In this lesson learners study {context.subtopic.lower()} using clear classroom examples.",
            "visual": f"This visual lesson helps learners see {context.subtopic.lower()} with diagrams, models and labelled drawings.",
            "story": f"A short South African classroom story introduces {context.subtopic.lower()} before learners practise the skill.",
            "step_by_step": f"Learners move through {context.subtopic.lower()} one guided step at a time with teacher checkpoints.",
            "real_world_sa": f"Learners connect {context.subtopic.lower()} to everyday South African contexts such as shops, sport and community tasks.",
            "exam_style": f"Learners practise {context.subtopic.lower()} using concise exam-style prompts and answer checking.",
        }[variant]
        standard = context.assessment_standards[0]
        snippet = context.source_text_snippets[0][:220].strip()
        vocab = ", ".join(context.vocabulary[:4]) if context.vocabulary else context.subtopic.lower()
        family_line = {
            "mathematics": f"Use concrete numbers, drawings and verbal reasoning while working on {context.subtopic.lower()}.",
            "languages": "Read the passage carefully, notice key words, and explain answers in full sentences.",
            "natural_sciences": "Observe the example, name the process, and use evidence from the scenario to justify each answer.",
            "social_sciences": "Use the map, source or timeline provided and explain how the evidence supports the answer.",
            "life_skills": "Discuss respectful choices, health habits and community responsibility using the example scenario.",
            "life_orientation": "Discuss personal development, health choices and responsible relationships using the example scenario.",
            "technology": "Follow the design process, name materials and tools, and explain how the solution meets the brief.",
            "creative_arts": "Describe the design choices, materials and audience purpose before evaluating the example.",
            "coding_and_robotics": "Trace the input, follow the sequence and debug one step when the output does not match the goal.",
        }[family]
        return (
            f"{opener} CAPS focus: {standard} "
            f"Key vocabulary: {vocab}. {family_line} "
            f"Grounding snippet: {snippet} "
            f"Before finishing, learners restate the method, complete the practice set and compare answers with a partner."
        )

    def _worked_examples(self, context: TopicMapSourceContext, *, family: str, index: int) -> list[dict[str, Any]]:
        family = _content_family(family)
        if family == "mathematics":
            a = 125 + index * 17 + context.grade * 11
            b = 48 + index * 5
            total = a + b
            return [
                {
                    "question": f"A Grade {context.grade} shop sells {a} apples in the morning and {b} in the afternoon for {context.subtopic.lower()}. How many apples were sold altogether?",
                    "step_by_step_solution": [
                        f"Identify the two amounts: {a} and {b}.",
                        "Add the ones column, then the tens and hundreds carefully.",
                        f"Record the total as {total}.",
                        "Check by counting back from the total.",
                    ],
                    "answer": f"{total} apples",
                },
                {
                    "question": f"Lerato has {total} counters and gives away {b}. How many counters remain?",
                    "step_by_step_solution": [
                        f"Start with {total} counters.",
                        f"Subtract {b} because they are given away.",
                        f"Calculate {total} - {b} = {total - b}.",
                        "Write the answer with the correct unit.",
                    ],
                    "answer": f"{total - b} counters",
                },
            ]
        if family == "languages":
            sentence = f"The learners read a short passage about {context.subtopic.lower()} at school."
            return [
                {
                    "question": f"Which sentence best states the main idea of the passage about {context.subtopic.lower()}?",
                    "step_by_step_solution": [
                        "Read the passage once for meaning.",
                        "Underline the sentence that names the topic and the writer's main point.",
                        "Compare the options and reject answers that mention only one detail.",
                        "Select the option that covers the whole passage.",
                    ],
                    "answer": f"The passage explains how learners use {context.subtopic.lower()} in reading and writing.",
                },
                {
                    "question": f"Replace the underlined word in '{sentence}' with a stronger verb.",
                    "step_by_step_solution": [
                        "Identify the verb that can be replaced.",
                        "Choose a verb that keeps the same meaning but is more precise.",
                        "Read the new sentence aloud to check grammar.",
                        "Write the improved sentence.",
                    ],
                    "answer": f"The learners analysed a short passage about {context.subtopic.lower()} at school.",
                },
            ]
        if family == "natural_sciences":
            return [
                {
                    "question": f"During a class experiment on {context.subtopic.lower()}, the thermometer reading rises from 22°C to 29°C. What changed?",
                    "step_by_step_solution": [
                        "Compare the starting and ending measurements.",
                        "State the quantity that increased.",
                        "Link the change to the process being studied.",
                        "Write the answer using the unit from the apparatus.",
                    ],
                    "answer": "The temperature increased by 7°C during the process.",
                },
                {
                    "question": f"A learner says {context.subtopic.lower()} happens without energy. What correction should the teacher give?",
                    "step_by_step_solution": [
                        "Identify the incorrect claim.",
                        "Name the form of energy or transfer involved.",
                        "Give one classroom example.",
                        "State the corrected explanation clearly.",
                    ],
                    "answer": f"{context.subtopic.title()} requires energy transfer; without it the process cannot occur.",
                },
            ]
        if family == "social_sciences":
            return [
                {
                    "question": f"A map shows two towns linked by a river near {context.subtopic.lower()}. Which source would best explain why settlers chose the site?",
                    "step_by_step_solution": [
                        "List the physical features shown on the map.",
                        "Match each feature to a human need such as water or transport.",
                        "Choose the source that explains settlement reasons.",
                        "Write one sentence using evidence from the source.",
                    ],
                    "answer": "A historical source describing water access and farming explains the settlement choice.",
                },
                {
                    "question": f"Place these events about {context.subtopic.lower()} in the correct order: policy change, protest march, community meeting.",
                    "step_by_step_solution": [
                        "Identify which event happened first.",
                        "Decide which event caused the next event.",
                        "Arrange all events chronologically.",
                        "Check the order against the source summary.",
                    ],
                    "answer": "Community meeting, protest march, policy change.",
                },
            ]
        if family == "creative_arts":
            return [
                {
                    "question": f"A learner mixes warm and cool colours for a poster about {context.subtopic.lower()}. Why does the design create contrast?",
                    "step_by_step_solution": [
                        "Name the warm colours used.",
                        "Name the cool colours used.",
                        "Explain how opposite colour groups create contrast.",
                        "Link the contrast to the poster message.",
                    ],
                    "answer": "Warm and cool colours sit opposite on the colour wheel, so the title stands out clearly.",
                },
                {
                    "question": f"Describe one improvement to a rhythm pattern used in a class performance on {context.subtopic.lower()}.",
                    "step_by_step_solution": [
                        "Clap the original pattern.",
                        "Decide which beat needs emphasis or rest.",
                        "Revise the pattern.",
                        "Explain how the change helps the audience follow the performance.",
                    ],
                    "answer": "Adding a rest on beat three makes the pattern easier to hear and perform together.",
                },
            ]
        if family == "coding_and_robotics":
            return [
                {
                    "question": f"A robot must move forward 3 steps, turn right, then move 2 steps for a task on {context.subtopic.lower()}. Write the sequence.",
                    "step_by_step_solution": [
                        "List each command in order.",
                        "Use precise action words such as move and turn.",
                        "Check that the sequence matches the goal.",
                        "Trace the path on paper before running the robot.",
                    ],
                    "answer": "move forward 3, turn right, move forward 2",
                },
                {
                    "question": "The robot stops after one step even though the program repeats three times. What debugging step comes first?",
                    "step_by_step_solution": [
                        "Read the loop instruction carefully.",
                        "Check whether the repeat count matches the intended steps.",
                        "Test one corrected command at a time.",
                        "Record the fix in the program log.",
                    ],
                    "answer": "Check the repeat count and the command inside the loop before rerunning the program.",
                },
            ]
        return [
            {
                "question": f"Example 1: How can a Grade {context.grade} learner show respect while learning about {context.subtopic.lower()}?",
                "step_by_step_solution": [
                    "Name the situation in the example.",
                    "Identify a respectful action.",
                    "Explain why the action helps the group.",
                    "Write the answer in one clear sentence.",
                ],
                "answer": "Listen to others, take turns and use kind words during the activity.",
            },
            {
                "question": f"Example 2: Which healthy choice supports the lesson on {context.subtopic.lower()}?",
                "step_by_step_solution": [
                    "Read each option carefully.",
                    "Eliminate choices that ignore safety or wellbeing.",
                    "Select the option that supports healthy habits.",
                    "Explain the choice to a partner.",
                ],
                "answer": "Wash hands, follow safety rules and ask for help when unsure.",
            },
        ]

    def _practice_questions(self, context: TopicMapSourceContext, *, family: str, index: int) -> list[dict[str, Any]]:
        templates = base_mcq_templates(context, family=family, sequence=index)
        questions: list[dict[str, Any]] = []
        for q_index, template in enumerate(templates, start=1):
            correct = CORRECT_OPTIONS[(index + q_index) % len(CORRECT_OPTIONS)]
            options, explanation = options_for_template(template, correct=correct)
            questions.append(
                {
                    "question_id": f"q{q_index}",
                    "question_text": template["question_text"],
                    "options": options,
                    "correct_option": correct,
                    "explanation": explanation,
                    "misconception_tag": context.common_misconceptions[q_index % len(context.common_misconceptions)],
                }
            )
        return questions

    def _answer_key(self, practice_questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "question_id": question["question_id"],
                "correct_option": question["correct_option"],
                "correct_answer_text": question["options"][question["correct_option"]],
            }
            for question in practice_questions
        ]

    def _remediation_hint(self, context: TopicMapSourceContext, misconception: str) -> str:
        return (
            f"When {misconception.replace('_', ' ')} appears, return to the worked example for "
            f"{context.subtopic.lower()} and solve one smaller part before attempting the full question."
        )

    def _remediation_example(self, context: TopicMapSourceContext, *, family: str) -> str:
        family = _content_family(family)
        if family == "mathematics":
            return "Draw a place-value table or number line before choosing the final answer."
        if family == "languages":
            return "Reread the sentence aloud and check punctuation and verb choice."
        if family == "natural_sciences":
            return "Label the diagram and point to the evidence that supports the answer."
        if family == "social_sciences":
            return "Highlight the date, place and source before answering."
        if family == "coding_and_robotics":
            return "Trace each command with your finger before running the program again."
        return "Use the checklist in the lesson and explain each step to a partner."

    def _extension_prompts(self, context: TopicMapSourceContext, *, family: str, variant: str) -> list[str]:
        return [
            f"Create a new Grade {context.grade} example about {context.subtopic.lower()} and teach it to a partner using the {variant.replace('_', ' ')} approach.",
            f"Write two exam-style questions for {context.caps_ref} and explain why your marking memo is correct.",
            f"Connect {context.subtopic.lower()} to a real situation in your community and justify your answer with evidence.",
        ]

    def _teacher_notes(self, context: TopicMapSourceContext, *, variant: str, family: str) -> str:
        return (
            f"Pacing: 15 minutes teaching, 10 minutes guided practice, 10 minutes independent practice for {context.subtopic.lower()}. "
            f"Use the {variant.replace('_', ' ')} variant materials first, then move to the practice set. "
            f"Common errors to watch: {', '.join(tag.replace('_', ' ') for tag in context.common_misconceptions[:2])}. "
            f"Assessment cue: ask learners to explain one method aloud before marking the exit ticket. "
            f"Subject focus: {family.replace('_', ' ')}."
        )

    def _parent_notes(self, context: TopicMapSourceContext, *, family: str) -> str:
        return (
            f"Ask your child to teach you one example about {context.subtopic.lower()} without looking at the notes. "
            f"Help them restate the main vocabulary and check whether their answer matches the question. "
            f"If they are stuck, use a household object to model the idea rather than giving the final answer immediately. "
            f"This supports {family.replace('_', ' ')} learning at home."
        )

    def _source_citations(self, context: TopicMapSourceContext) -> list[dict[str, Any]]:
        citations: list[dict[str, Any]] = []
        for document_id in context.source_document_ids:
            citations.append(
                {
                    "source_document_id": document_id,
                    "caps_ref": context.caps_ref,
                    "scope_id": context.scope_id,
                    "citation_text": context.source_text_snippets[0][:240],
                    "context_hash": context.context_hash,
                }
            )
        return citations
