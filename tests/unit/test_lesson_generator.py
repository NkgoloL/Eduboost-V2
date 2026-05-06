import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.lesson_generator import LessonGenerator

@pytest.mark.unit
@pytest.mark.asyncio
async def test_lesson_generator_calls_provider():
    # Mock cache
    import app.core.llm
    app.core.llm.cache_get = AsyncMock(return_value=None)
    app.core.llm.cache_set = AsyncMock()
    app.core.llm.check_and_consume_quota = AsyncMock(return_value=1)
    generator = LessonGenerator()
    generator._call_with_fallback = AsyncMock(return_value='{"title": "Test"}')
    
    # We need a stamp_lesson mock if it uses Judiciary
    generator._judiciary = MagicMock()
    generator._judiciary.stamp_lesson.return_value = MagicMock(
        introduction="Intro", main_content="Content", worked_example="Example"
    )
    generator._caps_validator = MagicMock()
    generator._caps_validator.validate.return_value = MagicMock(caps_aligned=True)
    generator._caps_validator.validate_generated_content.return_value = MagicMock(caps_aligned=True)
    
    payload, from_cache = await generator.generate_lesson(
        pseudonym_id="p-1",
        grade=4,
        subject="MATH",
        topic="Fractions",
        language="en",
        archetype="visual",
        user_id="u-1",
        tier="free"
    )
    
    assert payload is not None
    generator._call_with_fallback.assert_called_once()
