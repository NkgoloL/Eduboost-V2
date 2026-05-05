from app.core.llm_gateway import ExecutiveService


def test_lesson_prompt_includes_learner_context():
    service = ExecutiveService()

    prompt = service._build_lesson_prompt(
        grade=4,
        subject="MATH",
        topic="Fractions",
        language="en",
        archetype="explorer",
        requested_topic="Fractions",
        learner_context={
            "knowledge_gaps": [{"topic": "equivalent fractions", "severity": 0.8}],
            "recent_lessons": [{"subject": "MATH", "topic": "number patterns", "completed": True}],
        },
    )

    assert "Learner context:" in prompt
    assert "equivalent fractions" in prompt
    assert "number patterns" in prompt
