import pytest

from app.services.content_generation.prompt_payloads import (
    DiagnosticGenerationRequest,
    GeneratedDiagnosticItem,
    GeneratedLesson,
    LessonGenerationRequest,
    SourceContextChunk,
)


from app.services.content_safety.pii import (
    build_llm_context,
    contains_pii,
    detect_pii_text,
    redact_pii_text,
    scrub_feedback_for_rlhf,
)


def test_pii_detection_redaction_and_context():
    sample_text = (
        "Contact Sipho at sipho@example.com or 082 123 4567. "
        "His ID is 9001015009087 and UUID is 123e4567-e89b-12d3-a456-426614174000. "
        "Living at 123 Main Street."
    )


    # 1. Detection
    findings = detect_pii_text(sample_text)
    assert len(findings) >= 4
    assert contains_pii(sample_text) is True
    assert contains_pii("No sensitive data here.") is False

    # 2. Redaction
    redacted = redact_pii_text(sample_text)
    assert "[redacted-email]" in redacted
    assert "[redacted-phone]" in redacted
    assert "[redacted-id-number]" in redacted
    assert "[redacted-uuid]" in redacted
    assert "[redacted-address]" in redacted

    # 3. LLM Context building
    profile = {
        "learner_name": "Sipho",
        "first_name": "Sipho",
        "email": "sipho@example.com",
        "grade": 4,
        "language": "en",
        "learner_uuid": "raw-uuid",
    }
    context = {"note": "Reach him at 0821234567"}
    built = build_llm_context(
        pseudonym_id="pseudo-123",
        learner_profile=profile,
        learning_context=context,
    )
    assert built["pseudonym_id"] == "pseudo-123"
    assert "learner_name" not in built["learner_profile"]
    assert "email" not in built["learner_profile"]
    assert built["learner_profile"]["grade"] == 4
    assert "[redacted-phone]" in built["learning_context"]["note"]

    # 4. RLHF scrub
    with pytest.raises(PermissionError, match="active consent"):
        scrub_feedback_for_rlhf({"feedback": "text"}, consent_granted=False)

    scrubbed = scrub_feedback_for_rlhf(
        {"feedback": "Good job", "learner_name": "Sipho", "email": "test@example.com"},
        consent_granted=True,
    )
    assert scrubbed["pii_scrubbed"] is True
    assert "learner_name" not in scrubbed
    assert "email" not in scrubbed


def test_content_generation_prompt_payloads():
    chunk = SourceContextChunk(
        source_document_id="doc_1",
        source_chunk_id="chunk_1",
        text="Content text here.",
    )
    assert chunk.document_status == "approved"

    req = DiagnosticGenerationRequest(
        scope_id="scope_1",
        caps_ref="4.M.1",
        grade=4,
        subject_code="MATH",
        language="en",
        topic_title="Numbers",
        required_count=5,
        approved_count=2,
        missing_count=3,
        source_chunks=[chunk],
    )
    assert req.prompt_version == "cf-gen-v1"

    diag_item = GeneratedDiagnosticItem(
        question_text="What is 2 + 2?",
        options=["1", "2", "3", "4"],
        correct_answer="4",
        explanation="2+2=4",
        caps_ref="4.M.1",
        grade=4,
        subject_code="MATH",
        language="en",
        source_chunk_ids=["chunk_1"],
    )
    diag_json = diag_item.to_artifact_json()
    assert diag_json["item_type"] == "single_choice"
    assert diag_json["question_text"] == "What is 2 + 2?"

    lesson = GeneratedLesson(
        title="Place Value",
        summary="Place values summary",
        learning_objectives=["Understand units and tens"],
        teacher_notes="Guide learners slowly",
        learner_activity="Count with beads",
        worked_examples=["Example 1"],
        practice_questions=["What is 10 + 2?"],
        answer_key=["12"],
        caps_ref="4.M.1",
        grade=4,
        subject_code="MATH",
        language="en",
        source_chunk_ids=["chunk_1"],
    )
    lesson_json = lesson.to_artifact_json()
    assert lesson_json["title"] == "Place Value"
    assert lesson_json["summary"] == "Place values summary"

