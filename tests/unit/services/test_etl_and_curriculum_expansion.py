"""Comprehensive unit tests for ETL pipeline v1/v2, Curriculum Expansion, and Launch Content Seed."""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.services.etl.etl_pipeline import (
    EduboostETL,
    DocumentChunk,
    QualityCheckResult,
    ProcessingStatus,
)
from app.services.etl.etl_pipeline_v2 import (
    EduboostETLv2,
    MonitoringReport,
)
from app.services.curriculum_expansion import (
    ALLOWED_SOURCE_LICENSES,
    SAFE_STATUSES,
    INELIGIBLE_STATUSES,
    FORBIDDEN_TRAINING_KEYS,
)
from app.services.launch_content_seed import (
    LAUNCH_SCOPE_ID,
    DEFAULT_ITEM_TARGET,
    DEFAULT_LESSON_TARGET,
    seed_launch_content_if_needed,
)


# ---------------------------------------------------------------------------
# ETL Pipeline v1 and v2 Tests
# ---------------------------------------------------------------------------

class TestETLPipelines:
    def test_etl_v1_init_and_paths(self, tmp_path: Path):
        db_path = tmp_path / "test_etl.db"
        storage = tmp_path / "storage"
        etl = EduboostETL(db_url=f"sqlite:///{db_path}", storage_root=str(storage))
        assert etl.storage_root == Path(storage)

        # Test document chunk dataclass
        chunk = DocumentChunk(
            chunk_id="chk-123",
            document_id="doc-456",
            chunk_type="section",
            chunk_index=0,
            parent_chunk_id=None,
            heading="Introduction to Fractions",
            content="Fractions represent equal parts of a whole.",
            token_count=7,
            page_start=1,
            page_end=1,
            section_path="Chapter 1 > 1.1",
            curriculum_code="MATH.G4.NUM",
            created_at="2026-08-27T00:00:00Z",
        )
        assert chunk.chunk_id == "chk-123"
        assert chunk.content.startswith("Fractions")

        # Test QualityCheckResult dataclass
        qc = QualityCheckResult(
            document_id="doc-456",
            metadata_score=1.0,
            extraction_score=0.95,
            structure_score=0.9,
            completeness_score=1.0,
            provenance_score=1.0,
            training_suitability=0.95,
            quality_score=0.96,
            status="validated",
        )
        assert qc.status == "validated"
        assert qc.quality_score == 0.96

    def test_etl_v2_init_and_lifecycle(self, tmp_path: Path):
        db_path = tmp_path / "test_etl_v2.db"
        storage = tmp_path / "storage_v2"
        etl = EduboostETLv2(db_url=f"sqlite:///{db_path}", storage_root=str(storage))
        etl.init_db()
        etl.init_fts()

        # Submit user feedback
        etl.submit_feedback(
            document_id="doc-001",
            feedback_type="typo",
            user_id="learner_1",
            details="Typo on page 2",
        )

        # Get monitoring report
        report = etl.get_monitoring_report()
        assert isinstance(report, MonitoringReport)
        assert report.total_documents >= 0
        assert "typo" in report.feedback_summary


# ---------------------------------------------------------------------------
# Curriculum Expansion Governance Constants & PII Filters
# ---------------------------------------------------------------------------

class TestCurriculumExpansionGovernance:
    def test_allowed_source_licenses(self):
        assert "government_open" in ALLOWED_SOURCE_LICENSES
        assert "public_domain" in ALLOWED_SOURCE_LICENSES
        assert "cc-by" in ALLOWED_SOURCE_LICENSES
        assert "commercial_closed" not in ALLOWED_SOURCE_LICENSES

    def test_safe_and_ineligible_statuses(self):
        assert "approved" in SAFE_STATUSES
        assert "passed" in SAFE_STATUSES
        assert "quarantined" in INELIGIBLE_STATUSES
        assert "rejected" in INELIGIBLE_STATUSES

    def test_forbidden_training_keys(self):
        assert "learner_id" in FORBIDDEN_TRAINING_KEYS
        assert "guardian_id" in FORBIDDEN_TRAINING_KEYS
        assert "email" in FORBIDDEN_TRAINING_KEYS
        assert "phone" in FORBIDDEN_TRAINING_KEYS


# ---------------------------------------------------------------------------
# Launch Content Seed Tests
# ---------------------------------------------------------------------------

class TestLaunchContentSeed:
    def test_constants(self):
        assert LAUNCH_SCOPE_ID == "grade4_mathematics_en"
        assert DEFAULT_ITEM_TARGET == 40
        assert DEFAULT_LESSON_TARGET == 8

    @pytest.mark.asyncio
    async def test_seed_launch_content_disabled(self):
        with patch("app.services.launch_content_seed.settings") as mock_settings:
            mock_settings.CONTENT_STARTUP_SEED_ENABLED = False
            # Should return immediately without exception
            await seed_launch_content_if_needed()
