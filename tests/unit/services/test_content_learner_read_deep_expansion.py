"""Comprehensive unit tests for ContentLearnerReadService models and read modes."""
from __future__ import annotations

import pytest

from app.services.content_learner_read_service import (
    LearnerDiagnosticItem,
    LearnerLesson,
    LearnerScopeContentSummary,
    LearnerReadMode,
    ContentLearnerReadService,
)


class TestLearnerReadModels:
    def test_learner_diagnostic_item_dataclass(self):
        item = LearnerDiagnosticItem(
            artifact_id="art-100",
            scope_id="grade4_mathematics_en",
            caps_ref="4.M.1.1",
            grade=4,
            subject_code="MATH",
            language="en",
            title="Addition Practice",
            payload={"question": "2 + 2 = ?"},
            source_artifact_hash="hash-123",
            promotion_event_id="prom-1",
            created_at="2026-08-28T00:00:00Z",
        )
        assert item.artifact_id == "art-100"
        assert item.grade == 4
        assert item.subject_code == "MATH"

    def test_learner_lesson_dataclass(self):
        lesson = LearnerLesson(
            artifact_id="les-200",
            scope_id="grade4_mathematics_en",
            caps_ref="4.M.1.1",
            grade=4,
            subject_code="MATH",
            language="en",
            title="Understanding Fractions",
            payload={"explanation": "Fractions represent parts of a whole."},
            source_artifact_hash="hash-456",
            promotion_event_id="prom-2",
            created_at="2026-08-28T00:00:00Z",
        )
        assert lesson.artifact_id == "les-200"
        assert lesson.title == "Understanding Fractions"

    def test_learner_scope_content_summary_dataclass(self):
        summary = LearnerScopeContentSummary(
            scope_id="grade4_mathematics_en",
            diagnostic_items_count=40,
            lessons_count=20,
            total_artifacts_count=60,
            last_promotion_at="2026-08-28T00:00:00Z",
        )
        assert summary.scope_id == "grade4_mathematics_en"
        assert summary.total_artifacts_count == 60

    def test_learner_read_modes(self):
        assert LearnerReadMode.PRODUCTION_ONLY == "production_only"
        assert LearnerReadMode.PRODUCTION_WITH_LEGACY_FALLBACK == "production_with_legacy_fallback"
        assert LearnerReadMode.LEGACY_ONLY == "legacy_only"

    def test_content_learner_read_service_init(self):
        service = ContentLearnerReadService()
        assert service is not None


class TestContentLearnerReadServiceBranches:
    def test_is_learner_visible_artifact_all_branches(self):
        from types import SimpleNamespace
        from app.models.content_factory import ContentArtifactStatus

        service = ContentLearnerReadService()

        gen_art = SimpleNamespace(
            status=ContentArtifactStatus.PROMOTED_PRODUCTION,
            sources=[SimpleNamespace(source_hash="h1")],
        )
        prod_art = SimpleNamespace(production_status="active")

        # 1. Valid active promoted artifact with sources
        assert service.is_learner_visible_artifact(gen_art, prod_art) is True

        # 2. production_artifact is None
        assert service.is_learner_visible_artifact(gen_art, None) is False

        # 3. production_status != "active"
        prod_inactive = SimpleNamespace(production_status="inactive")
        assert service.is_learner_visible_artifact(gen_art, prod_inactive) is False

        # 4. generation_artifact.status != PROMOTED_PRODUCTION
        gen_draft = SimpleNamespace(status=ContentArtifactStatus.DRAFT, sources=[SimpleNamespace()])
        assert service.is_learner_visible_artifact(gen_draft, prod_art) is False

        # 5. status in QUARANTINED, REJECTED, RETIRED, VALIDATION_FAILED
        for bad_status in (
            ContentArtifactStatus.QUARANTINED,
            ContentArtifactStatus.REJECTED,
            ContentArtifactStatus.RETIRED,
            ContentArtifactStatus.VALIDATION_FAILED,
        ):
            gen_bad = SimpleNamespace(status=bad_status, sources=[SimpleNamespace()])
            assert service.is_learner_visible_artifact(gen_bad, prod_art) is False

        # 6. sources is None or empty
        gen_no_src = SimpleNamespace(status=ContentArtifactStatus.PROMOTED_PRODUCTION, sources=[])
        assert service.is_learner_visible_artifact(gen_no_src, prod_art) is False

        gen_none_src = SimpleNamespace(status=ContentArtifactStatus.PROMOTED_PRODUCTION, sources=None)
        assert service.is_learner_visible_artifact(gen_none_src, prod_art) is False

    @pytest.mark.asyncio
    async def test_get_diagnostic_items_and_legacy_fallback(self):
        from unittest.mock import AsyncMock, MagicMock
        from datetime import datetime, timezone
        from types import SimpleNamespace
        from app.models.content_factory import ContentArtifactStatus

        mock_registry = MagicMock()
        service = ContentLearnerReadService(scope_registry=mock_registry)
        service._read_mode = LearnerReadMode.PRODUCTION_WITH_LEGACY_FALLBACK

        # Mock DB session
        mock_session = AsyncMock()

        gen_art = SimpleNamespace(
            artifact_id="art-1",
            grade=4,
            subject_code="MATH",
            language="en",
            title="Addition",
            status=ContentArtifactStatus.PROMOTED_PRODUCTION,
            sources=[SimpleNamespace(source_hash="h1")],
        )
        prod_art = SimpleNamespace(
            scope_id="grade4_mathematics_en",
            caps_ref="4.M.1.1",
            payload_json={"q": "1+1"},
            source_artifact_hash="hash1",
            created_by_promotion_event_id="prom-event-1",
            created_at=datetime(2026, 8, 28, tzinfo=timezone.utc),
            production_status="active",
        )

        mock_session.execute.return_value = [(prod_art, gen_art)]

        items = await service.get_diagnostic_items(
            mock_session,
            scope_id="grade4_mathematics_en",
            caps_ref="4.M.1.1",
            limit=10,
        )
        assert len(items) == 1
        assert items[0].artifact_id == "art-1"
        assert items[0].promotion_event_id == "prom-event-1"

        # Fallback branch when DB query is empty
        mock_session.execute.return_value = []
        fallback_items = await service.get_diagnostic_items(
            mock_session,
            scope_id="grade4_mathematics_en",
            caps_ref="4.M.1.1",
        )
        assert fallback_items == []

    @pytest.mark.asyncio
    async def test_get_lessons_and_summary(self):
        from unittest.mock import AsyncMock, MagicMock
        from datetime import datetime, timezone
        from types import SimpleNamespace
        from app.models.content_factory import ContentArtifactStatus

        mock_registry = MagicMock()
        service = ContentLearnerReadService(scope_registry=mock_registry)
        service._read_mode = LearnerReadMode.PRODUCTION_ONLY

        mock_session = AsyncMock()

        gen_lesson = SimpleNamespace(
            artifact_id="les-1",
            grade=4,
            subject_code="MATH",
            language="en",
            title="Lesson 1",
            status=ContentArtifactStatus.PROMOTED_PRODUCTION,
            sources=[SimpleNamespace(source_hash="h1")],
        )
        prod_lesson = SimpleNamespace(
            scope_id="grade4_mathematics_en",
            caps_ref="4.M.1.1",
            payload_json={"body": "lesson text"},
            source_artifact_hash="hash-l1",
            created_by_promotion_event_id=None,
            created_at=datetime(2026, 8, 28, tzinfo=timezone.utc),
            production_status="active",
        )

        mock_session.execute.return_value = [(prod_lesson, gen_lesson)]

        lessons = await service.get_lessons(mock_session, scope_id="grade4_mathematics_en")
        assert len(lessons) == 1
        assert lessons[0].title == "Lesson 1"
        assert lessons[0].promotion_event_id is None

        # Scope summary
        now = datetime(2026, 8, 28, tzinfo=timezone.utc)
        mock_session.scalar.side_effect = [40, 20, 60, now]

        summary = await service.get_scope_content_summary(mock_session, scope_id="grade4_mathematics_en")
        assert summary.diagnostic_items_count == 40
        assert summary.lessons_count == 20
        assert summary.total_artifacts_count == 60
        assert summary.last_promotion_at is not None
