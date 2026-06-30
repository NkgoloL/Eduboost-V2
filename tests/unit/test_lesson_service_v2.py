"""tests/unit/test_lesson_service_v2.py
Unit tests for LessonServiceV2 lesson generation.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.lesson_service_v2 import LessonServiceV2


@pytest.mark.unit
async def test_get_lesson_returns_none_when_not_found():
    """Verify get_lesson returns None when lesson not found."""
    mock_repo = AsyncMock()
    mock_repo.get_by_id = AsyncMock(return_value=None)
    service = LessonServiceV2(mock_repo, redis_client=None)

    result = await service.get_lesson("nonexistent-id")
    assert result is None


@pytest.mark.unit
async def test_get_lesson_returns_cached_lesson_from_redis():
    """Verify get_lesson returns cached lesson from Redis."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value='{"lesson_id": "123", "title": "Test"}')
    mock_repo = AsyncMock()
    service = LessonServiceV2(mock_repo, redis_client=mock_redis)

    result = await service.get_lesson("lesson-123")
    assert result["lesson_id"] == "123"
    assert result["title"] == "Test"


@pytest.mark.unit
async def test_get_lesson_returns_lesson_from_database():
    """Verify get_lesson returns lesson from database when not cached."""
    mock_row = MagicMock()
    mock_row.lesson_id = "lesson-123"
    mock_row.title = "Test Lesson"
    mock_row.subject_code = "MAT"
    mock_row.grade_level = 4
    mock_row.topic = "Numbers"
    mock_row.content = {"story": "test"}
    mock_row.generated_by = "V2_LLM"

    mock_repo = AsyncMock()
    mock_repo.get_by_id = AsyncMock(return_value=mock_row)
    service = LessonServiceV2(mock_repo, redis_client=None)

    result = await service.get_lesson("lesson-123")
    assert result["lesson_id"] == "lesson-123"
    assert result["title"] == "Test Lesson"
    assert result["source"] == "database"


@pytest.mark.unit
async def test_submit_feedback_logs_audit_event():
    """Verify submit_feedback logs audit event and returns success."""
    mock_repo = AsyncMock()
    service = LessonServiceV2(mock_repo, redis_client=None)

    with patch("app.services.lesson_service_v2.AuditService") as mock_audit:
        mock_audit.return_value.log_event = AsyncMock()
        result = await service.submit_feedback("lesson-123", "learner-456", 5, "Great lesson")

        assert result["recorded"] is True
        assert result["lesson_id"] == "lesson-123"
        mock_audit.return_value.log_event.assert_called_once()


@pytest.mark.unit
async def test_generate_lesson_without_redis_checks_quota():
    """Verify generate_lesson checks quota when quota service available."""
    mock_repo = AsyncMock()
    mock_repo.create = AsyncMock(return_value=MagicMock(id="lesson-123"))
    service = LessonServiceV2(mock_repo, redis_client=None)

    with patch("app.services.lesson_service_v2.AuditService") as mock_audit:
        mock_audit.return_value.log_event = AsyncMock()
        result = await service.generate_lesson(
            learner_id="learner-123",
            subject_code="MAT",
            topic="Numbers",
            grade_level=4,
        )

        assert result["lesson_id"] == "lesson-123"
        assert result["subject_code"] == "MAT"
        assert result["topic"] == "Numbers"


@pytest.mark.unit
async def test_generate_lesson_with_cache_returns_cached():
    """Verify generate_lesson returns cached lesson when available."""
    mock_redis = AsyncMock()
    mock_cache_service = MagicMock()
    mock_cache_service.build_cache_key = MagicMock(return_value="cache-key-123")
    mock_cache_service.get = AsyncMock(return_value='{"lesson_id": "cached-123", "content": "test"}')

    mock_repo = AsyncMock()
    service = LessonServiceV2(mock_repo, redis_client=mock_redis)
    service.cache_service = mock_cache_service

    result = await service.generate_lesson(
        learner_id="learner-123",
        subject_code="MAT",
        topic="Numbers",
        grade_level=4,
    )

    assert result["lesson_id"] == "cached-123"
    mock_cache_service.get.assert_called_once_with("cache-key-123")


@pytest.mark.unit
async def test_generate_lesson_creates_lesson_and_caches():
    """Verify generate_lesson creates lesson and caches result."""
    mock_redis = AsyncMock()
    mock_cache_service = MagicMock()
    mock_cache_service.build_cache_key = MagicMock(return_value="cache-key-123")
    mock_cache_service.get = AsyncMock(return_value=None)
    mock_cache_service.set = AsyncMock()
    mock_quota_service = MagicMock()
    mock_quota_service.check_and_reserve = AsyncMock()

    mock_row = MagicMock()
    mock_row.id = "lesson-123"
    mock_repo = AsyncMock()
    mock_repo.create = AsyncMock(return_value=mock_row)

    service = LessonServiceV2(mock_repo, redis_client=mock_redis)
    service.cache_service = mock_cache_service
    service.quota_service = mock_quota_service

    with patch("app.services.lesson_service_v2.AuditService") as mock_audit:
        mock_audit.return_value.log_event = AsyncMock()
        result = await service.generate_lesson(
            learner_id="learner-123",
            subject_code="MAT",
            topic="Numbers",
            grade_level=4,
        )

        assert result["lesson_id"] == "lesson-123"
        mock_cache_service.set.assert_called_once()


@pytest.mark.unit
async def test_generate_lesson_with_language_and_archetype():
    """Verify generate_lesson respects language and archetype parameters."""
    mock_repo = AsyncMock()
    mock_row = MagicMock()
    mock_row.id = "lesson-123"
    mock_repo.create = AsyncMock(return_value=mock_row)
    service = LessonServiceV2(mock_repo, redis_client=None)

    with patch("app.services.lesson_service_v2.AuditService") as mock_audit:
        mock_audit.return_value.log_event = AsyncMock()
        result = await service.generate_lesson(
            learner_id="learner-123",
            subject_code="MAT",
            topic="Numbers",
            grade_level=4,
            language="af",
            archetype="visual",
            tier="premium",
        )

        assert result["lesson_id"] == "lesson-123"
        assert result["subject_code"] == "MAT"


@pytest.mark.unit
async def test_generate_lesson_with_cached_dict():
    """Verify generate_lesson handles cached result as dict."""
    mock_redis = AsyncMock()
    mock_cache_service = MagicMock()
    mock_cache_service.build_cache_key = MagicMock(return_value="cache-key-123")
    mock_cache_service.get = AsyncMock(return_value={"lesson_id": "cached-123", "content": "test"})

    mock_repo = AsyncMock()
    service = LessonServiceV2(mock_repo, redis_client=mock_redis)
    service.cache_service = mock_cache_service

    result = await service.generate_lesson(
        learner_id="learner-123",
        subject_code="MAT",
        topic="Numbers",
    )

    assert result["lesson_id"] == "cached-123"


@pytest.mark.unit
async def test_get_lesson_with_cached_dict():
    """Verify get_lesson handles cached result as dict."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value={"lesson_id": "123", "title": "Test"})
    mock_repo = AsyncMock()
    service = LessonServiceV2(mock_repo, redis_client=mock_redis)

    result = await service.get_lesson("lesson-123")
    assert result["lesson_id"] == "123"
    assert result["title"] == "Test"


@pytest.mark.unit
async def test_submit_feedback_without_comment():
    """Verify submit_feedback works without comment."""
    mock_repo = AsyncMock()
    service = LessonServiceV2(mock_repo, redis_client=None)

    with patch("app.services.lesson_service_v2.AuditService") as mock_audit:
        mock_audit.return_value.log_event = AsyncMock()
        result = await service.submit_feedback("lesson-123", "learner-456", 5)

        assert result["recorded"] is True
        mock_audit.return_value.log_event.assert_called_once()


@pytest.mark.unit
async def test_generate_lesson_with_quota_but_no_cache():
    """Verify generate_lesson checks quota when cache_service is None."""
    mock_redis = AsyncMock()
    mock_quota_service = MagicMock()
    mock_quota_service.check_and_reserve = AsyncMock()

    mock_row = MagicMock()
    mock_row.id = "lesson-123"
    mock_repo = AsyncMock()
    mock_repo.create = AsyncMock(return_value=mock_row)

    service = LessonServiceV2(mock_repo, redis_client=mock_redis)
    service.cache_service = None
    service.quota_service = mock_quota_service

    with patch("app.services.lesson_service_v2.AuditService") as mock_audit:
        mock_audit.return_value.log_event = AsyncMock()
        result = await service.generate_lesson(
            learner_id="learner-123",
            subject_code="MAT",
            topic="Numbers",
        )

        assert result["lesson_id"] == "lesson-123"
        mock_quota_service.check_and_reserve.assert_called_once()


@pytest.mark.unit
async def test_generate_lesson_without_grade_level():
    """Verify generate_lesson handles None grade_level."""
    mock_repo = AsyncMock()
    mock_row = MagicMock()
    mock_row.id = "lesson-123"
    mock_repo.create = AsyncMock(return_value=mock_row)
    service = LessonServiceV2(mock_repo, redis_client=None)

    with patch("app.services.lesson_service_v2.AuditService") as mock_audit:
        mock_audit.return_value.log_event = AsyncMock()
        result = await service.generate_lesson(
            learner_id="learner-123",
            subject_code="MAT",
            topic="Numbers",
            grade_level=None,
        )

        assert result["lesson_id"] == "lesson-123"
        mock_repo.create.assert_called_once()
        # Verify grade defaults to 0 when None
        call_kwargs = mock_repo.create.call_args[1]
        assert call_kwargs["grade"] == 0
