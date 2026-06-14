"""
Phase 1 — EC-07: Complete generation run tests using DeterministicProvider.
No real LLM calls are made.  The tests exercise the full engine path:
  create_run → process_run → artifact persisted / rejected.
"""
from __future__ import annotations

import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.content_factory import ContentLayer
from app.services.batch_generation import (
    BatchGenerationEngine,
    GenerationTaskSpec,
)
from app.services.content_validator import ContentValidator
from app.services.llm_provider import (
    DeterministicProvider,
    ProviderRouter,
)
from app.services.prompt_registry import PromptRegistry
from app.services.safety_filter import SafetyFilter
from tests.phase01.conftest import VALID_DIAGNOSTIC_ITEM


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_engine(det_provider: DeterministicProvider) -> BatchGenerationEngine:
    router = ProviderRouter([det_provider])
    return BatchGenerationEngine(
        provider_router=router,
        prompt_registry=PromptRegistry.default(),
        safety_filter=SafetyFilter(),
        validator=ContentValidator(),
    )


def _make_task_specs(
    caps_ref: str = "4.M.1.1",
    content_type: str = "diagnostic_item",
) -> list[GenerationTaskSpec]:
    return [
        GenerationTaskSpec(
            caps_ref=caps_ref,
            content_layer=ContentLayer.DIAGNOSTIC_ITEMS,
            content_type=content_type,
            count=2,
            grade=4,
            subject="Mathematics",
            subject_code="MATHS",
        )
    ]


def _clean_sources(caps_ref: str = "4.M.1.1") -> dict[str, list[dict]]:
    return {
        caps_ref: [
            {
                "source_document_id": "doc-test-001",
                "source_chunk_id": "chunk-001",
                "source_title": "Grade 4 Mathematics Textbook",
                "text": (
                    "Multiplication is the process of adding a number to itself "
                    "multiple times. For example, 4 × 3 = 12."
                ),
                "license_status": "government_open",
                "document_status": "approved",
                "caps_ref": caps_ref,
                "source_hash": "sha256:test-source",
                "chunk_quality_score": 0.9,
            }
        ]
    }


# ---------------------------------------------------------------------------
# PromptRegistry
# ---------------------------------------------------------------------------


class TestPromptRegistry:
    def test_default_registry_has_diagnostic_item(self):
        r = PromptRegistry.default()
        tmpl = r.get("diagnostic_item")
        assert tmpl.version == "1.0"
        assert tmpl.prompt_version_tag == "diagnostic_item@1.0"

    def test_default_registry_has_lesson(self):
        r = PromptRegistry.default()
        tmpl = r.get("lesson")
        assert tmpl.schema_version == "1.0"

    def test_render_user_substitutes_placeholders(self):
        r = PromptRegistry.default()
        tmpl = r.get("diagnostic_item")
        rendered = tmpl.render_user(
            caps_ref="4.M.1.1",
            grade=4,
            subject="Mathematics",
            language="en",
            source_context="test content",
            count=5,
        )
        assert "4.M.1.1" in rendered
        assert "test content" in rendered

    def test_missing_placeholder_raises(self):
        r = PromptRegistry.default()
        tmpl = r.get("diagnostic_item")
        with pytest.raises(ValueError, match="placeholder"):
            tmpl.render_user(caps_ref="4.M.1.1")  # missing grade, subject, etc.

    def test_duplicate_registration_raises(self):
        r = PromptRegistry.default()
        from app.services.prompt_registry import PromptTemplate
        with pytest.raises(ValueError, match="already registered"):
            r.register(
                PromptTemplate(
                    id="diagnostic_item",
                    version="1.0",
                    content_type="diagnostic_item",
                    schema_version="1.0",
                    system="sys",
                    user_template="usr",
                )
            )

    def test_unknown_content_type_raises(self):
        r = PromptRegistry.default()
        with pytest.raises(KeyError):
            r.get("unknown_type")


# ---------------------------------------------------------------------------
# Full generation run (DeterministicProvider)
# ---------------------------------------------------------------------------


class TestBatchGenerationEngineRun:
    """
    These tests use a real BatchGenerationEngine but mock the database
    layer.  The purpose is to verify the orchestration logic, not ORM
    behaviour.
    """

    def _make_mock_db(self):
        db = AsyncMock()
        db.add = MagicMock()
        db.flush = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        # execute().scalar_one_or_none() pattern used in engine
        mock_execute = AsyncMock()
        mock_execute.scalar_one_or_none = MagicMock(return_value=None)
        mock_execute.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
        db.execute = AsyncMock(return_value=mock_execute)
        return db

    @pytest.mark.asyncio
    async def test_valid_output_produces_artifact_with_pending_review_status(self):
        """EC-01, EC-07: Valid output validated and artefact created at PENDING_REVIEW."""
        det = DeterministicProvider()
        det.register_default(json.dumps([VALID_DIAGNOSTIC_ITEM]))
        engine = _make_engine(det)

        # Mock the full run path with a controlled task
        from app.models.content_factory import ContentGenerationTask, ContentGenerationRun

        mock_run = MagicMock(spec=ContentGenerationRun)
        mock_run.run_id = uuid.uuid4()
        mock_run.scope_id = "grade4-maths-en"
        mock_run.status = "created"

        mock_task = MagicMock(spec=ContentGenerationTask)
        mock_task.task_id = uuid.uuid4()
        mock_task.run_id = mock_run.run_id
        mock_task.scope_id = "grade4-maths-en"
        mock_task.caps_ref = "4.M.1.1"
        mock_task.content_layer = ContentLayer.DIAGNOSTIC_ITEMS
        mock_task.status = "queued"
        mock_task.task_metadata = {
            "content_type": "diagnostic_item",
            "count": 2,
            "language": "en",
            "grade": 4,
            "subject": "Mathematics",
            "subject_code": "MATHS",
        }

        # Track added objects
        added_objects = []

        db = AsyncMock()
        db.add = MagicMock(side_effect=lambda obj: added_objects.append(obj))
        db.flush = AsyncMock()
        db.commit = AsyncMock()

        run_execute = AsyncMock()
        run_execute.scalar_one_or_none = MagicMock(return_value=mock_run)
        run_execute.scalars = MagicMock(
            return_value=MagicMock(all=MagicMock(return_value=[mock_task]))
        )
        db.execute = AsyncMock(return_value=run_execute)

        # Patch lock acquisition to always succeed
        with patch(
            "app.services.batch_generation._acquire_task_lock",
            new=AsyncMock(return_value=True),
        ):
            result = await engine.process_run(
                mock_run.run_id,
                _clean_sources("4.M.1.1"),
                db,
                worker_id="test-worker",
            )

        # Artefact was added to session
        from app.models.content_factory import ContentGenerationArtifact
        artifact_objects = [o for o in added_objects if isinstance(o, ContentGenerationArtifact)]
        assert len(artifact_objects) >= 1
        artifact = artifact_objects[0]
        assert artifact.status.value == "pending_review"
        assert artifact.prompt_version == "diagnostic_item@1.0"
        assert artifact.provider == "deterministic"
        assert result.succeeded >= 1

    @pytest.mark.asyncio
    async def test_invalid_output_sets_task_to_validation_failed(self):
        """EC-02: Structurally invalid LLM output must not create an artefact."""
        det = DeterministicProvider()
        det.register_default("this is not valid json {{{")
        engine = _make_engine(det)

        from app.models.content_factory import ContentGenerationTask, ContentGenerationRun

        mock_run = MagicMock(spec=ContentGenerationRun)
        mock_run.run_id = uuid.uuid4()
        mock_run.scope_id = "grade4-maths-en"

        mock_task = MagicMock(spec=ContentGenerationTask)
        mock_task.task_id = uuid.uuid4()
        mock_task.run_id = mock_run.run_id
        mock_task.scope_id = "grade4-maths-en"
        mock_task.caps_ref = "4.M.1.1"
        mock_task.content_layer = ContentLayer.DIAGNOSTIC_ITEMS
        mock_task.status = "queued"
        mock_task.task_metadata = {
            "content_type": "diagnostic_item", "count": 2, "language": "en",
            "grade": 4, "subject": "Mathematics", "subject_code": "MATHS",
        }

        db = AsyncMock()
        db.add = MagicMock()
        db.flush = AsyncMock()
        db.commit = AsyncMock()
        run_exec = AsyncMock()
        run_exec.scalar_one_or_none = MagicMock(return_value=mock_run)
        run_exec.scalars = MagicMock(
            return_value=MagicMock(all=MagicMock(return_value=[mock_task]))
        )
        db.execute = AsyncMock(return_value=run_exec)

        with patch(
            "app.services.batch_generation._acquire_task_lock",
            new=AsyncMock(return_value=True),
        ):
            result = await engine.process_run(
                mock_run.run_id, _clean_sources(), db, worker_id="test-worker"
            )

        assert result.failed >= 1
        assert result.succeeded == 0

    @pytest.mark.asyncio
    async def test_pii_in_source_blocks_generation(self):
        """EC-05: PII in source must block generation before any LLM call."""
        det = DeterministicProvider()
        det.register_default(json.dumps([VALID_DIAGNOSTIC_ITEM]))

        call_count = 0
        original_generate = det.generate

        async def tracking_generate(**kwargs):
            nonlocal call_count
            call_count += 1
            return await original_generate(**kwargs)

        det.generate = tracking_generate
        engine = _make_engine(det)

        pii_sources = {
            "4.M.1.1": [
                {
                    "source_document_id": "doc-pii",
                    "source_chunk_id": "chunk-pii",
                    "text": "Student ID: 8507125800086 scored 80%.",
                    "license_status": "government_open",
                    "document_status": "approved",
                    "caps_ref": "4.M.1.1",
                    "source_hash": "sha256:pii-source",
                    "chunk_quality_score": 0.9,
                }
            ]
        }

        from app.models.content_factory import ContentGenerationTask, ContentGenerationRun

        mock_run = MagicMock(spec=ContentGenerationRun)
        mock_run.run_id = uuid.uuid4()
        mock_run.scope_id = "grade4-maths-en"

        mock_task = MagicMock(spec=ContentGenerationTask)
        mock_task.task_id = uuid.uuid4()
        mock_task.run_id = mock_run.run_id
        mock_task.scope_id = "grade4-maths-en"
        mock_task.caps_ref = "4.M.1.1"
        mock_task.content_layer = ContentLayer.DIAGNOSTIC_ITEMS
        mock_task.status = "queued"
        mock_task.task_metadata = {
            "content_type": "diagnostic_item", "count": 2, "language": "en",
            "grade": 4, "subject": "Mathematics", "subject_code": "MATHS",
        }

        db = AsyncMock()
        db.add = MagicMock()
        db.flush = AsyncMock()
        db.commit = AsyncMock()
        run_exec = AsyncMock()
        run_exec.scalar_one_or_none = MagicMock(return_value=mock_run)
        run_exec.scalars = MagicMock(
            return_value=MagicMock(all=MagicMock(return_value=[mock_task]))
        )
        db.execute = AsyncMock(return_value=run_exec)

        with patch(
            "app.services.batch_generation._acquire_task_lock",
            new=AsyncMock(return_value=True),
        ):
            result = await engine.process_run(
                mock_run.run_id, pii_sources, db, worker_id="test-worker"
            )

        # LLM must NOT have been called
        assert call_count == 0, "LLM was called despite PII in source material"
        assert result.safety_blocked >= 1

    @pytest.mark.asyncio
    async def test_pii_in_llm_output_blocks_artifact_persistence(self):
        """EC-05: PII in LLM output must quarantine the task."""
        pii_output = json.dumps(
            [{**VALID_DIAGNOSTIC_ITEM, "explanation": "See learner 8507125800086 for reference."}]
        )
        det = DeterministicProvider()
        det.register_default(pii_output)
        engine = _make_engine(det)

        from app.models.content_factory import ContentGenerationTask, ContentGenerationRun, ContentGenerationArtifact

        mock_run = MagicMock(spec=ContentGenerationRun)
        mock_run.run_id = uuid.uuid4()
        mock_run.scope_id = "grade4-maths-en"

        mock_task = MagicMock(spec=ContentGenerationTask)
        mock_task.task_id = uuid.uuid4()
        mock_task.run_id = mock_run.run_id
        mock_task.scope_id = "grade4-maths-en"
        mock_task.caps_ref = "4.M.1.1"
        mock_task.content_layer = ContentLayer.DIAGNOSTIC_ITEMS
        mock_task.status = "queued"
        mock_task.task_metadata = {
            "content_type": "diagnostic_item", "count": 2, "language": "en",
            "grade": 4, "subject": "Mathematics", "subject_code": "MATHS",
        }

        added_objects = []
        db = AsyncMock()
        db.add = MagicMock(side_effect=lambda o: added_objects.append(o))
        db.flush = AsyncMock()
        db.commit = AsyncMock()
        run_exec = AsyncMock()
        run_exec.scalar_one_or_none = MagicMock(return_value=mock_run)
        run_exec.scalars = MagicMock(
            return_value=MagicMock(all=MagicMock(return_value=[mock_task]))
        )
        db.execute = AsyncMock(return_value=run_exec)

        with patch(
            "app.services.batch_generation._acquire_task_lock",
            new=AsyncMock(return_value=True),
        ):
            result = await engine.process_run(
                mock_run.run_id, _clean_sources(), db, worker_id="test-worker"
            )

        # No ContentGenerationArtifact must have been added
        artifact_objects = [o for o in added_objects if isinstance(o, ContentGenerationArtifact)]
        assert len(artifact_objects) == 0, (
            "Artifact was persisted despite PII in LLM output"
        )
        assert result.safety_blocked >= 1

    @pytest.mark.asyncio
    async def test_token_telemetry_emitted(self):
        """EC-06: Token counters are incremented after successful generation."""
        from app.services.batch_generation import _TOKEN_USAGE

        det = DeterministicProvider()
        det.register_default(json.dumps([VALID_DIAGNOSTIC_ITEM]))
        engine = _make_engine(det)

        before = _TOKEN_USAGE.labels(
            provider="deterministic", content_type="diagnostic_item"
        )._value.get()

        from app.models.content_factory import ContentGenerationTask, ContentGenerationRun

        mock_run = MagicMock(spec=ContentGenerationRun)
        mock_run.run_id = uuid.uuid4()
        mock_run.scope_id = "grade4-maths-en"

        mock_task = MagicMock(spec=ContentGenerationTask)
        mock_task.task_id = uuid.uuid4()
        mock_task.run_id = mock_run.run_id
        mock_task.scope_id = "grade4-maths-en"
        mock_task.caps_ref = "4.M.1.1"
        mock_task.content_layer = ContentLayer.DIAGNOSTIC_ITEMS
        mock_task.status = "queued"
        mock_task.task_metadata = {
            "content_type": "diagnostic_item", "count": 2, "language": "en",
            "grade": 4, "subject": "Mathematics", "subject_code": "MATHS",
        }

        db = AsyncMock()
        db.add = MagicMock()
        db.flush = AsyncMock()
        db.commit = AsyncMock()
        run_exec = AsyncMock()
        run_exec.scalar_one_or_none = MagicMock(return_value=mock_run)
        run_exec.scalars = MagicMock(
            return_value=MagicMock(all=MagicMock(return_value=[mock_task]))
        )
        db.execute = AsyncMock(return_value=run_exec)

        with patch(
            "app.services.batch_generation._acquire_task_lock",
            new=AsyncMock(return_value=True),
        ):
            await engine.process_run(
                mock_run.run_id, _clean_sources(), db, worker_id="test-worker"
            )

        after = _TOKEN_USAGE.labels(
            provider="deterministic", content_type="diagnostic_item"
        )._value.get()
        assert after > before, "Token counter was not incremented"
