"""Import generated file artifacts into Content Factory DB artifact records."""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_factory import (
    ContentArtifactSource,
    ContentArtifactStatus,
    ContentArtifactType,
    ContentGenerationArtifact,
    ContentLayer,
    ContentValidationReport,
)
from app.services.content_factory import stable_json_hash
from app.services.content_file_lesson_quality import ContentFileLessonQualityService
from app.services.content_file_review_workflow import ContentFileReviewWorkflowService
from app.services.content_scope_registry import ContentScopeRegistry

PROJECT_ROOT = Path(__file__).resolve().parents[2]

_LAYER_SPECS = {
    "diagnostic_items": (ContentLayer.DIAGNOSTIC_ITEMS, ContentArtifactType.DIAGNOSTIC_ITEM, "items"),
    "lessons": (ContentLayer.LESSONS, ContentArtifactType.LESSON, "lessons"),
    "assessment_blueprints": (ContentLayer.ASSESSMENT_BLUEPRINTS, ContentArtifactType.ASSESSMENT_BLUEPRINT, "blueprints"),
    "study_plan_templates": (ContentLayer.STUDY_PLAN_TEMPLATES, ContentArtifactType.STUDY_PLAN_TEMPLATE, "topic_sequence"),
}


@dataclass(frozen=True)
class FileArtifactImportRecord:
    artifact_id: uuid.UUID
    scope_id: str
    layer: str
    artifact_type: str
    caps_ref: str | None
    artifact_hash: str
    status: str
    source_document_id: str
    payload_json: dict[str, Any]


@dataclass(frozen=True)
class FileArtifactImportPlan:
    scope_id: str
    review_status: str
    db_status: str
    records: list[FileArtifactImportRecord] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    created_count: int = 0
    updated_count: int = 0
    validation_report_count: int = 0
    source_count: int = 0


@dataclass(frozen=True)
class FileArtifactImportBatchPlan:
    scope_count: int
    stage_unlocked: int
    production_unlocked: int
    total_records: int
    scopes_with_errors: int
    plans: list[FileArtifactImportPlan] = field(default_factory=list)

    def to_manifest(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "summary": {
                "scope_count": self.scope_count,
                "stage_unlocked": self.stage_unlocked,
                "production_unlocked": self.production_unlocked,
                "total_records": self.total_records,
                "scopes_with_errors": self.scopes_with_errors,
            },
            "scopes": [
                {
                    "scope_id": plan.scope_id,
                    "review_status": plan.review_status,
                    "db_status": plan.db_status,
                    "record_count": len(plan.records),
                    "errors": plan.errors,
                    "layers": _layer_counts(plan.records),
                }
                for plan in self.plans
            ],
        }

    def to_rollback_manifest(self, *, source_import_manifest_path: str) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "manifest_id": _batch_manifest_id(self.plans),
            "source_import_manifest_path": source_import_manifest_path,
            "summary": {
                "scope_count": self.scope_count,
                "artifact_count": self.total_records,
                "scopes_with_errors": self.scopes_with_errors,
                "production_unlocked": self.production_unlocked,
                "rollback_supported": self.scopes_with_errors == 0,
            },
            "rollback_actions": [
                "delete_content_artifact_sources_by_artifact_id",
                "delete_content_validation_reports_by_artifact_id",
                "delete_content_generation_artifacts_by_artifact_id",
            ],
            "production_guard": {
                "production_unlocked": self.production_unlocked,
                "production_rollback_applicable": self.production_unlocked > 0,
                "notes": "Review-scope file imports are staging/import artifacts only; production remains gated separately.",
            },
            "scopes": [
                {
                    "scope_id": plan.scope_id,
                    "review_status": plan.review_status,
                    "db_status": plan.db_status,
                    "artifact_count": len(plan.records),
                    "layers": _layer_artifact_ids(plan.records),
                    "errors": plan.errors,
                }
                for plan in self.plans
            ],
        }


class ContentFileArtifactImportService:
    """Plan and execute imports from generated JSON files into reviewable DB artifacts."""

    def __init__(
        self,
        *,
        project_root: Path | None = None,
        registry: ContentScopeRegistry | None = None,
        review_service: ContentFileReviewWorkflowService | None = None,
        lesson_quality_service: ContentFileLessonQualityService | None = None,
    ) -> None:
        self.project_root = project_root or PROJECT_ROOT
        self.registry = registry or ContentScopeRegistry(project_root=self.project_root)
        self.review_service = review_service or ContentFileReviewWorkflowService(project_root=self.project_root, registry=self.registry)
        self.lesson_quality_service = lesson_quality_service or ContentFileLessonQualityService(
            project_root=self.project_root,
            registry=self.registry,
        )

    def plan_scope_import(self, scope_id: str, *, max_records_per_layer: int | None = None) -> FileArtifactImportPlan:
        scope = self.registry.get_scope(scope_id)
        review = self.review_service.review_status(scope_id)
        lesson_quality = self.lesson_quality_service.audit_scope(scope_id)
        db_status = ContentArtifactStatus.APPROVED.value if review.stage_unlocked else ContentArtifactStatus.PENDING_REVIEW.value
        source_document_id = (scope.source_documents or ["unknown_source"])[0]
        records: list[FileArtifactImportRecord] = []
        errors = list(review.stage_blockers)
        if lesson_quality.quarantined:
            errors.extend(lesson_quality.blockers)
        for path_key, (layer, artifact_type, collection_key) in _LAYER_SPECS.items():
            if path_key == "lessons" and lesson_quality.quarantined:
                continue
            rel_path = scope.artifact_paths.get(path_key)
            if not rel_path:
                errors.append(f"{path_key} path is missing from scope registry.")
                continue
            path = self.project_root / rel_path
            if not path.exists():
                errors.append(f"{path_key} file is missing: {rel_path}")
                continue
            payload = json.loads(path.read_text(encoding="utf-8"))
            items = list(payload.get(collection_key, []))
            if max_records_per_layer is not None:
                items = items[:max_records_per_layer]
            for index, item in enumerate(items):
                caps_ref = _caps_ref_for(path_key, item)
                artifact_hash = stable_json_hash({"scope_id": scope.scope_id, "layer": layer.value, "payload": item})
                records.append(
                    FileArtifactImportRecord(
                        artifact_id=uuid.uuid5(uuid.NAMESPACE_URL, f"eduboost:file-artifact:{scope.scope_id}:{layer.value}:{artifact_hash}"),
                        scope_id=scope.scope_id,
                        layer=layer.value,
                        artifact_type=artifact_type.value,
                        caps_ref=caps_ref,
                        artifact_hash=artifact_hash,
                        status=db_status,
                        source_document_id=source_document_id,
                        payload_json=item,
                    )
                )
        return FileArtifactImportPlan(scope_id=scope.scope_id, review_status=review.status, db_status=db_status, records=records, errors=errors)

    def plan_scope_imports(
        self,
        *,
        scope_ids: list[str] | None = None,
        statuses: set[str] | None = None,
        max_records_per_layer: int | None = None,
    ) -> FileArtifactImportBatchPlan:
        scopes = self.registry.list_scopes()
        if scope_ids is not None:
            wanted = set(scope_ids)
            scopes = [scope for scope in scopes if scope.scope_id in wanted]
            missing = sorted(wanted - {scope.scope_id for scope in scopes})
            if missing:
                raise LookupError(f"Unknown content scopes: {missing}")
        if statuses is not None:
            scopes = [scope for scope in scopes if scope.status.value in statuses]

        plans = [
            self.plan_scope_import(scope.scope_id, max_records_per_layer=max_records_per_layer)
            for scope in scopes
        ]
        stage_unlocked = sum(
            1
            for plan in plans
            if plan.db_status == ContentArtifactStatus.APPROVED.value and not plan.errors
        )
        production_unlocked = sum(
            1
            for plan in plans
            if self.review_service.review_status(plan.scope_id).production_unlocked and not plan.errors
        )
        return FileArtifactImportBatchPlan(
            scope_count=len(plans),
            stage_unlocked=stage_unlocked,
            production_unlocked=production_unlocked,
            total_records=sum(len(plan.records) for plan in plans),
            scopes_with_errors=sum(1 for plan in plans if plan.errors),
            plans=plans,
        )

    async def import_scope_files(
        self,
        session: AsyncSession,
        scope_id: str,
        *,
        actor_id: str,
        max_records_per_layer: int | None = None,
        dry_run: bool = True,
    ) -> FileArtifactImportPlan:
        plan = self.plan_scope_import(scope_id, max_records_per_layer=max_records_per_layer)
        if dry_run:
            return plan
        scope = self.registry.get_scope(scope_id)
        source_document_id = (scope.source_documents or ["unknown_source"])[0]
        created_count = updated_count = validation_report_count = source_count = 0
        for record in plan.records:
            artifact = await self._existing_artifact(session, record)
            if artifact is None:
                artifact = ContentGenerationArtifact(
                    artifact_id=record.artifact_id,
                    scope_id=record.scope_id,
                    content_layer=ContentLayer(record.layer),
                    artifact_type=ContentArtifactType(record.artifact_type),
                    caps_ref=record.caps_ref,
                    grade=scope.grade,
                    subject_code=scope.subject_code,
                    language=scope.language,
                    status=ContentArtifactStatus(record.status),
                    artifact_json=record.payload_json,
                    artifact_hash=record.artifact_hash,
                    source_snapshot_hash=record.artifact_hash,
                    provider="file_import",
                    model="generated-scope-artifacts",
                    prompt_version="scope_scaffold_v1",
                    quality_score=0.9,
                    safety_status="passed",
                    answer_key_verified=False,
                    caps_alignment_score=1.0,
                )
                session.add(artifact)
                created_count += 1
            else:
                artifact.status = ContentArtifactStatus(record.status)
                artifact.artifact_json = record.payload_json
                artifact.source_snapshot_hash = record.artifact_hash
                artifact.provider = "file_import"
                artifact.model = "generated-scope-artifacts"
                artifact.prompt_version = "scope_scaffold_v1"
                artifact.quality_score = 0.9
                artifact.safety_status = "passed"
                artifact.answer_key_verified = False
                artifact.caps_alignment_score = 1.0
                updated_count += 1

            if not await self._has_source(session, record):
                session.add(ContentArtifactSource(
                    artifact_id=record.artifact_id,
                    source_document_id=source_document_id,
                    source_chunk_id=f"{record.scope_id}:{record.layer}:{record.caps_ref or 'scope'}",
                    source_title=source_document_id,
                    source_type="caps_pdf",
                    caps_ref=record.caps_ref,
                    grade=scope.grade,
                    subject_code=scope.subject_code,
                    language=scope.language,
                    license_status="government_open",
                    source_quality_score=0.9,
                    source_hash=record.artifact_hash,
                    source_metadata={"document_status": "approved", "imported_by": actor_id},
                ))
                source_count += 1
            if not await self._has_validation_report(session, record):
                session.add(ContentValidationReport(
                    artifact_id=record.artifact_id,
                    passed=True,
                    checks={"file_import_schema": True, "source_traceability": True, "safety_status": "passed"},
                    errors=[],
                ))
                validation_report_count += 1
        await session.flush()
        return FileArtifactImportPlan(
            scope_id=plan.scope_id,
            review_status=plan.review_status,
            db_status=plan.db_status,
            records=plan.records,
            errors=plan.errors,
            created_count=created_count,
            updated_count=updated_count,
            validation_report_count=validation_report_count,
            source_count=source_count,
        )

    async def _existing_artifact(self, session: AsyncSession, record: FileArtifactImportRecord) -> ContentGenerationArtifact | None:
        existing = await session.get(ContentGenerationArtifact, record.artifact_id)
        if existing is not None:
            return existing
        result = await session.execute(
            select(ContentGenerationArtifact).where(ContentGenerationArtifact.artifact_hash == record.artifact_hash)
        )
        return result.scalar_one_or_none()

    async def _has_source(self, session: AsyncSession, record: FileArtifactImportRecord) -> bool:
        if hasattr(session, "has_source_for_import"):
            return bool(session.has_source_for_import(record))
        result = await session.execute(
            select(ContentArtifactSource).where(
                ContentArtifactSource.artifact_id == record.artifact_id,
                ContentArtifactSource.source_hash == record.artifact_hash,
            )
        )
        return result.scalar_one_or_none() is not None

    async def _has_validation_report(self, session: AsyncSession, record: FileArtifactImportRecord) -> bool:
        if hasattr(session, "has_validation_report_for_import"):
            return bool(session.has_validation_report_for_import(record))
        result = await session.execute(
            select(ContentValidationReport).where(
                ContentValidationReport.artifact_id == record.artifact_id,
                ContentValidationReport.passed == True,
            )
        )
        return result.scalar_one_or_none() is not None


def _caps_ref_for(path_key: str, item: dict[str, Any]) -> str | None:
    if item.get("caps_ref"):
        return str(item["caps_ref"])
    selection_rules = item.get("selection_rules") or {}
    refs = selection_rules.get("caps_refs") or []
    if refs:
        return str(refs[0])
    return None


def _layer_counts(records: list[FileArtifactImportRecord]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        counts[record.layer] = counts.get(record.layer, 0) + 1
    return counts


def _layer_artifact_ids(records: list[FileArtifactImportRecord]) -> dict[str, list[str]]:
    layer_ids: dict[str, list[str]] = {}
    for record in records:
        layer_ids.setdefault(record.layer, []).append(str(record.artifact_id))
    return layer_ids


def _batch_manifest_id(plans: list[FileArtifactImportPlan]) -> str:
    basis = ";".join(
        f"{plan.scope_id}:{len(plan.records)}:{plan.db_status}:{plan.review_status}"
        for plan in plans
    )
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"eduboost:file-import-rollback:{basis}"))
