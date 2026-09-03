"""Batch 290 — Comprehensive branch coverage expansion for GeneratedLessonQualityValidator."""
from __future__ import annotations

import pytest

from app.services.content_generation.generated_lesson_contract import (
    GeneratedLessonQualityIssue,
    GeneratedLessonQualityResult,
    GeneratedLessonQualityValidator,
    subject_family,
)


@pytest.mark.unit
def test_generated_lesson_quality_result_methods():
    issue1 = GeneratedLessonQualityIssue(
        lesson_id="les_1",
        caps_ref="5.M.1.1",
        field="title",
        reason="below minimum length 8",
    )
    issue2 = GeneratedLessonQualityIssue(
        lesson_id="les_1",
        caps_ref="5.M.1.1",
        field="lesson_body",
        reason="missing",
    )
    result = GeneratedLessonQualityResult(
        passed=False,
        lesson_count=1,
        failed_lesson_count=1,
        issues=[issue1, issue2],
    )
    msgs = result.failure_messages()
    assert len(msgs) == 2
    assert "les_1/5.M.1.1 title: below minimum length 8" in msgs[0]
    assert "les_1/5.M.1.1 lesson_body: missing" in msgs[1]


@pytest.mark.unit
def test_subject_family_fallback_inference():
    # Direct code matches
    assert subject_family("M") == "mathematics"
    assert subject_family("HL") == "languages"
    assert subject_family("FAL") == "languages"
    assert subject_family("LS") == "life_skills"
    assert subject_family("LO") == "life_orientation"
    assert subject_family("NST") == "natural_sciences"
    assert subject_family("NS") == "natural_sciences"
    assert subject_family("TECH") == "technology"
    assert subject_family("SS") == "social_sciences"
    assert subject_family("EMS") == "social_sciences"
    assert subject_family("CA") == "creative_arts"
    assert subject_family("CR") == "coding_and_robotics"

    # Fallback to subject text matching
    assert subject_family("UNKNOWN", subject="English First Additional Language") == "languages"
    assert subject_family("UNKNOWN", subject="Life Skills and Personal Wellbeing") == "life_skills"
    assert subject_family("UNKNOWN", subject="Life Orientation") == "life_skills"
    assert subject_family("UNKNOWN", subject="Natural Sciences and Technology") == "natural_sciences"
    assert subject_family("UNKNOWN", subject="Social Studies and History") == "social_sciences"
    assert subject_family("UNKNOWN", subject="Economic Management") == "social_sciences"
    assert subject_family("UNKNOWN", subject="Creative Arts and Music") == "creative_arts"
    assert subject_family("UNKNOWN", subject="Coding and Robotics Grade 7") == "coding_and_robotics"
    assert subject_family("UNKNOWN", subject="Pure Geometry") == "mathematics"
    assert subject_family("UNKNOWN", subject=None) == "mathematics"



@pytest.mark.unit
def test_validator_required_fields_and_scope_mismatch():
    validator = GeneratedLessonQualityValidator()

    # Short/empty fields
    lesson = {
        "lesson_id": "L1",
        "caps_ref": "5.M.1",
        "title": "Short",  # < 8
        "scope_id": "scope_A",
        "variant": "unsupported_variant",
        "lesson_body": "Too short body",  # < 200
        "teacher_notes": "Short teacher note",  # < 80
        "parent_notes": "Short parent note",  # < 60
        "extension_prompts": ["Short prompt"],  # < 40
        "source_citations": [{"source_document_id": "doc_X"}],
        "learning_objectives": ["Work with fractions", "Work with numbers"],  # starts with 'work with '
        "worked_examples": [
            {
                "answer": "The final answer is checked and explained.",  # placeholder answer
                "step_by_step_solution": ["start with the known facts", "work one step at a time"],  # placeholder steps
            },
            {
                "answer": "valid answer 42",
                "step_by_step_solution": ["step 1 calculate 5 * 8 = 40", "step 2 add 2 = 42"],
            },
        ],
        "practice_questions": [
            {
                "question_text": "What should you do first?",  # generic pattern
                "options": {"A": "guess the answer before reading", "B": "calculate 40 + 2"},  # generic option
                "correct_option": "A",
            },
            {
                "question_text": "Calculate 5 * 8 + 2",
                "options": {"A": "42", "B": "40"},
                "correct_option": "A",
            },
            {
                "question_text": "Calculate 5 * 8 + 2",  # duplicate question text
                "options": {"A": "42", "B": "40"},
                "correct_option": "A",
            },
        ],
        "answer_key": [
            {"correct_option": "A", "correct_answer_text": "Same answer"},
            {"correct_option": "A", "correct_answer_text": "Same answer"},
            {"correct_option": "A", "correct_answer_text": "Same answer"},
        ],
    }

    issues = validator.validate_lesson(
        lesson,
        scope_id="scope_B",  # mismatch with scope_A
        subject_code="M",
        source_document_ids=["doc_Y"],  # mismatch with doc_X
    )
    field_reasons = {(issue.field, issue.reason) for issue in issues}

    assert any(f == "title" and "below minimum length" in r for f, r in field_reasons)
    assert any(f == "scope_id" and "expected scope_B" in r for f, r in field_reasons)
    assert any(f == "variant" and "unsupported variant" in r for f, r in field_reasons)
    assert any(f == "lesson_body" and "below minimum length" in r for f, r in field_reasons)
    assert any(f == "teacher_notes" and "below minimum length" in r for f, r in field_reasons)
    assert any(f == "parent_notes" and "below minimum length" in r for f, r in field_reasons)
    assert any(f == "extension_prompts" and "too short" in r for f, r in field_reasons)
    assert any(f == "source_citations" and "citations do not trace" in r for f, r in field_reasons)
    assert any(f == "learning_objectives" and "generic topic restatements" in r for f, r in field_reasons)
    assert any("placeholder answer" in r for f, r in field_reasons)
    assert any("placeholder solution steps" in r for f, r in field_reasons)
    assert any("duplicate question_text" in r for f, r in field_reasons)
    assert any("generic question pattern" in r for f, r in field_reasons)
    assert any("all practice questions use correct option A" in r for f, r in field_reasons)
    assert any("all answer-key entries share identical answer text" in r for f, r in field_reasons)


@pytest.mark.unit
def test_validator_empty_and_missing_collections():
    validator = GeneratedLessonQualityValidator()

    lesson = {
        "lesson_id": "",
        "caps_ref": "",
        "title": "",
        "scope_id": "",
        "variant": "",
        "lesson_body": "",
        "teacher_notes": "",
        "parent_notes": "",
        "extension_prompts": [],
        "source_citations": [],
        "learning_objectives": [],
        "worked_examples": [{"answer": "1"}],  # fewer than 2
        "practice_questions": [{"question_text": "q1"}],  # fewer than 3
        "answer_key": [],  # missing
    }

    issues = validator.validate_lesson(lesson, scope_id="scope_1", subject_code="M")
    fields = [issue.field for issue in issues]

    assert "title" in fields
    assert "scope_id" in fields
    assert "variant" in fields
    assert "lesson_body" in fields
    assert "teacher_notes" in fields
    assert "parent_notes" in fields
    assert "extension_prompts" in fields
    assert "source_citations" in fields
    assert "learning_objectives" in fields
    assert "worked_examples" in fields
    assert "practice_questions" in fields
    assert "answer_key" in fields


@pytest.mark.unit
def test_validator_guidance_and_subject_families():
    validator = GeneratedLessonQualityValidator()

    body_text = "This is a detailed explanation of fractions and decimals with examples " * 5

    # 1. Teacher and parent notes duplicating explanation
    lesson = {
        "lesson_id": "L2",
        "caps_ref": "5.M.1.2",
        "title": "Fractions and Decimals Comprehensive Guide",
        "scope_id": "scope_1",
        "variant": "standard",
        "lesson_body": body_text,
        "explanation": body_text,
        "teacher_notes": body_text,  # duplicate of explanation
        "parent_notes": "Ask your child to explain fractions in their own words.",  # matches generic pattern
        "extension_prompts": [
            "Explore real world fraction applications at a local South African grocery store."
        ],
        "source_citations": [{"source_document_id": "doc_1"}],
        "learning_objectives": ["Understand numerator and denominator in fractions."],
        "worked_examples": [
            {
                "answer": "3/4 of a pizza is 6 slices out of 8 slices.",
                "step_by_step_solution": [
                    "Divide total 8 slices by 4 to get 2 slices per quarter.",
                    "Multiply 2 slices by 3 to get 6 slices in total.",
                ],
            },
            {
                "answer": "1/2 of 100 rand is 50 rand.",
                "step_by_step_solution": [
                    "Take 100 rand and divide into 2 equal portions.",
                    "Each portion equals 50 rand.",
                ],
            },
        ],
        "practice_questions": [
            {
                "question_text": "What is 1/4 of 20 apples?",
                "options": {"A": "5 apples", "B": "10 apples", "C": "15 apples", "D": "20 apples"},
                "correct_option": "A",
            },
            {
                "question_text": "What is 2/3 of 90 rands?",
                "options": {"A": "30 rands", "B": "60 rands", "C": "90 rands", "D": "15 rands"},
                "correct_option": "B",
            },
            {
                "question_text": "Which fraction is equivalent to 1/2?",
                "options": {"A": "2/4", "B": "1/3", "C": "3/5", "D": "4/7"},
                "correct_option": "A",
            },
        ],
        "answer_key": [
            {"correct_option": "A", "correct_answer_text": "5 apples"},
            {"correct_option": "B", "correct_answer_text": "60 rands"},
            {"correct_option": "A", "correct_answer_text": "2/4"},
        ],
        "topic": "fractions",
    }

    issues = validator.validate_lesson(
        lesson,
        scope_id="scope_1",
        subject_code="M",
        source_document_ids=["doc_1"],
    )
    field_reasons = {(issue.field, issue.reason) for issue in issues}
    assert any(f == "teacher_notes" and "generic or duplicated" in r for f, r in field_reasons)
    assert any(f == "parent_notes" and "generic or duplicated" in r for f, r in field_reasons)


@pytest.mark.unit
def test_validator_subject_family_concrete_markers():
    validator = GeneratedLessonQualityValidator()

    def make_lesson(body: str, topic: str):
        return {
            "lesson_id": "L_fam",
            "caps_ref": "CAPS.1",
            "title": f"Comprehensive Lesson on {topic.capitalize()}",
            "scope_id": "scope_1",
            "variant": "visual",
            "lesson_body": body + (" Extra descriptive sentences to meet minimum body length requirement easily." * 5),
            "teacher_notes": "Teachers should introduce the topic using clear South African contextual materials and classroom discussion." * 2,
            "parent_notes": "Parents can review homework questions every evening and encourage discussion about key concepts." * 2,
            "extension_prompts": ["Investigate broader real world applications in South African society."],
            "source_citations": [{"source_document_id": "doc_1"}],
            "learning_objectives": [f"Master key concepts in {topic}"],
            "worked_examples": [
                {"answer": "Answer 1", "step_by_step_solution": ["Step 1 detailed breakdown", "Step 2 final verification"]},
                {"answer": "Answer 2", "step_by_step_solution": ["Step 1 initial analysis", "Step 2 complete evaluation"]},
            ],
            "practice_questions": [
                {"question_text": "Detailed question 1 regarding topic?", "options": {"A": "Opt A", "B": "Opt B"}, "correct_option": "A"},
                {"question_text": "Detailed question 2 regarding topic?", "options": {"A": "Opt A", "B": "Opt B"}, "correct_option": "B"},
                {"question_text": "Detailed question 3 regarding topic?", "options": {"A": "Opt A", "B": "Opt B"}, "correct_option": "A"},
            ],
            "answer_key": [
                {"correct_option": "A", "correct_answer_text": "Distinct answer text A"},
                {"correct_option": "B", "correct_answer_text": "Distinct answer text B"},
                {"correct_option": "A", "correct_answer_text": "Distinct answer text C"},
            ],
            "topic": topic,
        }

    # Test with source_document_ids=None (branch 161->166)
    l_no_source_filter = make_lesson("Read the paragraph carefully and identify each noun and verb in the sentence.", "grammar")
    assert validator.validate_lesson(l_no_source_filter, scope_id="scope_1", subject_code="HL", source_document_ids=None) == []

    # Languages
    l_lang = make_lesson("Read the paragraph carefully and identify each noun and verb in the sentence.", "grammar")
    assert validator.validate_lesson(l_lang, scope_id="scope_1", subject_code="HL", source_document_ids=["doc_1"]) == []


    # Natural Sciences
    l_ns = make_lesson("We will observe an experiment to measure the energy transformation in an electric circuit.", "energy")
    assert validator.validate_lesson(l_ns, scope_id="scope_1", subject_code="NS", source_document_ids=["doc_1"]) == []

    # Social Sciences
    l_ss = make_lesson("Examine the historical map of the community to find evidence on the timeline.", "history")
    assert validator.validate_lesson(l_ss, scope_id="scope_1", subject_code="SS", source_document_ids=["doc_1"]) == []

    # Life Skills
    l_ls = make_lesson("Understanding personal feelings and showing respect in the community promotes health.", "feelings")
    assert validator.validate_lesson(l_ls, scope_id="scope_1", subject_code="LS", source_document_ids=["doc_1"]) == []

    # Life Orientation
    l_lo = make_lesson("Personal development, healthy relationships and responsible choices support wellbeing.", "development")
    assert validator.validate_lesson(l_lo, scope_id="scope_1", subject_code="LO", source_document_ids=["doc_1"]) == []

    # Technology
    l_tech = make_lesson("Use the design process to select a material and build a strong structure with a tool.", "structures")
    assert validator.validate_lesson(l_tech, scope_id="scope_1", subject_code="TECH", source_document_ids=["doc_1"]) == []

    # Creative Arts
    l_ca = make_lesson("Create a colourful pattern and draw a geometric design to perform in art class.", "patterns")
    assert validator.validate_lesson(l_ca, scope_id="scope_1", subject_code="CA", source_document_ids=["doc_1"]) == []

    # Coding & Robotics
    l_cr = make_lesson("Write code to sequence an algorithm that will control robot output and debug errors.", "algorithm")
    assert validator.validate_lesson(l_cr, scope_id="scope_1", subject_code="CR", source_document_ids=["doc_1"]) == []

    # Missing topic reference
    l_no_topic = {
        "lesson_id": "L_no_top",
        "caps_ref": "CAPS.1",
        "title": "Comprehensive Lesson on Everything",
        "scope_id": "scope_1",
        "variant": "visual",
        "lesson_body": "Write code to sequence an algorithm that will control robot output and debug errors." + (" Extra text." * 10),
        "teacher_notes": "Teachers should introduce the topic using clear South African contextual materials." * 2,
        "parent_notes": "Parents can review homework questions every evening and discuss concepts." * 2,
        "extension_prompts": ["Investigate broader real world applications in South African society."],
        "source_citations": [{"source_document_id": "doc_1"}],
        "learning_objectives": ["Master key concepts in general programming"],
        "worked_examples": [
            {"answer": "Answer 1", "step_by_step_solution": ["Step 1 detailed breakdown", "Step 2 final verification"]},
            {"answer": "Answer 2", "step_by_step_solution": ["Step 1 initial analysis", "Step 2 complete evaluation"]},
        ],
        "practice_questions": [
            {
                "question_text": "Detailed question 1 regarding topic?",
                "options": {"A": "guess the answer before reading", "B": "Opt B"},
                "correct_option": "A",
            },
            {"question_text": "Detailed question 2 regarding topic?", "options": {"A": "Opt A", "B": "Opt B"}, "correct_option": "B"},
            {"question_text": "Detailed question 3 regarding topic?", "options": {"A": "Opt A", "B": "Opt B"}, "correct_option": "A"},
        ],
        "answer_key": [
            {"correct_option": "A", "correct_answer_text": "Distinct answer text A"},
            {"correct_option": "B", "correct_answer_text": "Distinct answer text B"},
            {"correct_option": "A", "correct_answer_text": "Distinct answer text C"},
        ],
        "topic": "completely_unrelated_topic",
    }
    issues_topic = validator.validate_lesson(l_no_topic, scope_id="scope_1", subject_code="CR", source_document_ids=["doc_1"])
    assert any("does not reference the scope topic" in issue.reason for issue in issues_topic)
    assert any("options use generic study-behaviour distractors" in issue.reason for issue in issues_topic)



@pytest.mark.unit
def test_validate_file_payload_aggregate_metrics():
    validator = GeneratedLessonQualityValidator()

    # Payload with various aggregate triggers
    payload = {
        "lessons": [
            {
                # Missing all required fields
                "lesson_id": "L_empty",
                "caps_ref": "ref_1",
                "title": "",
                "scope_id": "",
                "variant": "",
                "lesson_body": "",
                "teacher_notes": "",
                "parent_notes": "",
                "extension_prompts": [],
                "practice_questions": [
                    {"question_text": "q1", "correct_option": "A"},
                    {"question_text": "q2", "correct_option": "A"},
                ],
                "answer_key": [
                    {"correct_option": "A", "correct_answer_text": "Identical"},
                    {"correct_option": "A", "correct_answer_text": "Identical"},
                ],
                "worked_examples": [
                    {
                        "step_by_step_solution": ["start with the known facts and work one step at a time"],
                    }
                ],
            }
        ]
    }

    res = validator.validate_file_payload(payload, scope_id="scope_1", subject_code="M")
    assert res.passed is False
    assert res.lesson_count == 1
    assert res.failed_lesson_count == 1
    assert res.aggregate["missing_lesson_body"] == 1
    assert res.aggregate["missing_title"] == 1
    assert res.aggregate["missing_scope_id"] == 1
    assert res.aggregate["missing_variant"] == 1
    assert res.aggregate["missing_teacher_notes"] == 1
    assert res.aggregate["missing_parent_notes"] == 1
    assert res.aggregate["missing_extension_prompts"] == 1
    assert res.aggregate["practice_questions_correct_option_a"] == 2
    assert res.aggregate["lessons_with_identical_answer_keys"] == 1
    assert res.aggregate["placeholder_worked_example_steps"] == 1
