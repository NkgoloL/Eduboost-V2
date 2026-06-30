"""Phase 7 curriculum coverage and training-dataset governance services."""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.content_factory import ContentArtifactSource, ContentArtifactStatus, ContentGenerationArtifact
from app.models.curriculum_expansion import (
    CurriculumCoverageSnapshot,
    CurriculumExpansionRun,
    TrainingDatasetEntry,
    TrainingDatasetManifest,
)
from app.services.content_scope_registry import ContentScopeRegistry

ALLOWED_SOURCE_LICENSES = {
    "government_open",
    "public_domain",
    "cc-by",
    "cc-by-sa",
    "department_approved",
}
SAFE_STATUSES = {"safe", "passed", "approved"}
INELIGIBLE_STATUSES = {
    "generated",
    "pending_review",
    "revision_required",
    "rejected",
    "quarantined",
    "retired",
    "superseded",
}
FORBIDDEN_TRAINING_KEYS = {
    "learner_id",
    "user_id",
    "guardian_id",
    "parent_id",
    "reviewer_id",
    "email",
    "phone",
    "address",
    "consent",
    "audit_log",
    "tutor_question",
    "tutor_answer",
    "diagnostic_response",
    "free_text_response",
    "review_comments",
}
PII_PATTERNS = (
    re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"\b(?:\+27|0)[6-8][0-9](?:[ -]?[0-9]){7}\b"),
    re.compile(r"\b\d{13}\b"),
)
PLACEHOLDER_PATTERN = re.compile(r"\b(?:TODO|TBD|LOREM IPSUM|PLACEHOLDER)\b", re.I)


def _enum_value(value: Any) -> str:
    return str(getattr(value, "value", value)).lower()


def _artifact_version(artifact: ContentGenerationArtifact) -> int:
    return int(
        getattr(artifact, "version_number", None)
        or getattr(artifact, "artifact_version", None)
        or 1
    )


def _normalised_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def record_sha256(record: dict[str, Any]) -> str:
    return hashlib.sha256(_normalised_json(record).encode("utf-8")).hexdigest()


def dataset_sha256(record_hashes: Iterable[str]) -> str:
    payload = "\n".join(sorted(record_hashes)) + "\n"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def forbidden_training_paths(value: Any, path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if str(key).lower() in FORBIDDEN_TRAINING_KEYS:
                findings.append(child_path)
            findings.extend(forbidden_training_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(forbidden_training_paths(child, f"{path}[{index}]"))
    return findings


def obvious_pii_findings(value: Any) -> list[str]:
    text = _normalised_json(value)
    return [pattern.pattern for pattern in PII_PATTERNS if pattern.search(text)]


def validate_language_content(content: dict[str, Any], language: str) -> list[str]:
    text = _normalised_json(content)
    findings: list[str] = []
    if PLACEHOLDER_PATTERN.search(text):
        findings.append("placeholder_text")
    if language not in {"en", "af", "zu", "xh", "st", "tn", "nso"}:
        findings.append("unsupported_language")
    letters = [char for char in text if char.isalpha()]
    if letters:
        latin = sum("LATIN" in __import__("unicodedata").name(char, "") for char in letters)
        if latin / len(letters) < 0.85:
            findings.append("unexpected_script_mix")
    return findings


def build_training_record(artifact: ContentGenerationArtifact) -> dict[str, Any]:
    return {
        "schema_version": "phase7-training-record-v1",
        "artifact_id": str(artifact.artifact_id),
        "artifact_hash": artifact.artifact_hash,
        "artifact_version": _artifact_version(artifact),
        "scope_id": artifact.scope_id,
        "caps_ref": artifact.caps_ref,
        "grade": artifact.grade,
        "subject_code": artifact.subject_code,
        "language": artifact.language,
        "content_layer": _enum_value(artifact.content_layer),
        "source_snapshot_hash": artifact.source_snapshot_hash,
        "quality_score": float(artifact.quality_score) if artifact.quality_score is not None else None,
        "caps_alignment_score": (
            float(artifact.caps_alignment_score)
            if artifact.caps_alignment_score is not None
            else None
        ),
        "content": artifact.artifact_json,
    }


def artifact_eligibility_reasons(
    artifact: ContentGenerationArtifact,
    *,
    require_published: bool,
    min_quality_score: float,
    min_caps_alignment_score: float,
) -> list[str]:
    reasons: list[str] = []
    status = _enum_value(artifact.status)
    permitted = {"published"} if require_published else {"approved", "published"}
    if status not in permitted:
        reasons.append(f"status:{status}")
    if status in INELIGIBLE_STATUSES:
        reasons.append("ineligible_lifecycle_state")
    if not artifact.artifact_hash:
        reasons.append("missing_artifact_hash")
    if not artifact.source_snapshot_hash:
        reasons.append("missing_source_snapshot_hash")
    if artifact.quality_score is None or float(artifact.quality_score) < min_quality_score:
        reasons.append("quality_below_threshold")
    if (
        artifact.caps_alignment_score is None
        or float(artifact.caps_alignment_score) < min_caps_alignment_score
    ):
        reasons.append("caps_alignment_below_threshold")
    if _enum_value(artifact.safety_status or "") not in SAFE_STATUSES:
        reasons.append("safety_not_approved")
    if _enum_value(artifact.content_layer) == "diagnostic_items" and not artifact.answer_key_verified:
        reasons.append("answer_key_not_verified")

    sources = list(getattr(artifact, "sources", []) or [])
    if not sources:
        reasons.append("missing_sources")
    elif any(_enum_value(source.license_status or "") not in ALLOWED_SOURCE_LICENSES for source in sources):
        reasons.append("disallowed_source_license")
    if any(not source.source_hash and not source.chunk_hash for source in sources):
        reasons.append("missing_source_hash")

    if forbidden_training_paths(artifact.artifact_json):
        reasons.append("forbidden_operational_fields")
    if obvious_pii_findings(artifact.artifact_json):
        reasons.append("obvious_pii")
    if validate_language_content(artifact.artifact_json, artifact.language or ""):
        reasons.append("language_validation_failed")
    return sorted(set(reasons))


class CurriculumExpansionService:
    def __init__(self, db: AsyncSession, registry: ContentScopeRegistry | None = None) -> None:
        self.db = db
        self.registry = registry or ContentScopeRegistry()

    @staticmethod
    def _eligible_statuses() -> tuple[str, ...]:
        return ("approved", "published")

    async def coverage_for_scope(self, scope_id: str) -> dict[str, Any]:
        scope = self.registry.require_active_scope(scope_id)
        details: list[dict[str, Any]] = []
        target_total = 0
        approved_total = 0
        published_total = 0
        for target in self.registry.get_scope_targets(scope_id):
            for key, target_count in sorted(target.targets.items()):
                if not key.endswith(".approved"):
                    continue
                layer = key.rsplit(".", 1)[0]
                pipeline_count = await self.db.scalar(
                    select(func.count(ContentGenerationArtifact.artifact_id)).where(
                        ContentGenerationArtifact.scope_id == scope_id,
                        ContentGenerationArtifact.caps_ref == target.caps_ref,
                        ContentGenerationArtifact.content_layer == layer,
                        ContentGenerationArtifact.status.in_(self._eligible_statuses()),
                    )
                )
                published_count = await self.db.scalar(
                    select(func.count(ContentGenerationArtifact.artifact_id)).where(
                        ContentGenerationArtifact.scope_id == scope_id,
                        ContentGenerationArtifact.caps_ref == target.caps_ref,
                        ContentGenerationArtifact.content_layer == layer,
                        ContentGenerationArtifact.status == ContentArtifactStatus.PUBLISHED,
                    )
                )
                pipeline_count = int(pipeline_count or 0)
                published_count = int(published_count or 0)
                target_total += int(target_count)
                approved_total += pipeline_count
                published_total += published_count
                details.append(
                    {
                        "caps_ref": target.caps_ref,
                        "layer": layer,
                        "target": int(target_count),
                        "pipeline_ready": pipeline_count,
                        "published": published_count,
                        "pipeline_gap": max(0, int(target_count) - pipeline_count),
                        "beta_gap": max(0, int(target_count) - published_count),
                    }
                )
        gap_count = sum(item["beta_gap"] for item in details)
        status = "green" if gap_count == 0 else ("amber" if published_total else "red")
        return {
            "scope_id": scope_id,
            "language": scope.language,
            "target_total": target_total,
            "approved_total": approved_total,
            "published_total": published_total,
            "gap_count": gap_count,
            "status": status,
            "coverage_semantics": "beta readiness is based on published learner-eligible artifacts",
            "details": details,
        }

    async def capture_snapshot(self, scope_id: str, source_commit_sha: str | None = None) -> CurriculumCoverageSnapshot:
        coverage = await self.coverage_for_scope(scope_id)
        snapshot = CurriculumCoverageSnapshot(
            scope_id=scope_id,
            language=coverage["language"],
            source_commit_sha=source_commit_sha,
            target_total=coverage["target_total"],
            approved_total=coverage["approved_total"],
            published_total=coverage["published_total"],
            gap_count=coverage["gap_count"],
            status=coverage["status"],
            coverage_json=coverage,
        )
        self.db.add(snapshot)
        await self.db.flush()
        return snapshot

    async def build_expansion_plan(
        self,
        *,
        requested_by: str,
        scope_ids: list[str],
        languages: list[str],
        layers: list[str],
        dry_run: bool = True,
    ) -> CurriculumExpansionRun:
        plans: list[dict[str, Any]] = []
        for scope_id in sorted(scope_ids):
            coverage = await self.coverage_for_scope(scope_id)
            gaps = [
                item
                for item in coverage["details"]
                if item["gap"] > 0
                and item["layer"] in set(layers)
                and coverage["language"] in set(languages)
            ]
            plans.append({"scope_id": scope_id, "language": coverage["language"], "gaps": gaps})
        run = CurriculumExpansionRun(
            requested_by=requested_by,
            status="completed",
            scope_ids=sorted(scope_ids),
            languages=sorted(languages),
            layers=sorted(layers),
            dry_run=True if dry_run else True,  # Phase 7 planner never executes generation directly.
            plan_json={
                "schema_version": "phase7-expansion-plan-v1",
                "generated_at": datetime.now(UTC).isoformat(),
                "plans": plans,
                "requires_phase1_generation": True,
                "requires_phase3_review": True,
                "requires_publication": True,
                "requires_phase6_budget_authority": True,
            },
            completed_at=datetime.now(UTC),
        )
        self.db.add(run)
        await self.db.flush()
        return run


class TrainingDatasetGovernanceService:
    def __init__(self, db: AsyncSession, artifact_root: Path | None = None) -> None:
        self.db = db
        self.artifact_root = (artifact_root or Path("artifacts/training")).resolve()

    async def _candidates(self, scope_ids: list[str], languages: list[str]) -> list[ContentGenerationArtifact]:
        result = await self.db.scalars(
            select(ContentGenerationArtifact)
            .where(
                ContentGenerationArtifact.scope_id.in_(scope_ids),
                ContentGenerationArtifact.language.in_(languages),
            )
            .options(selectinload(ContentGenerationArtifact.sources))
            .order_by(ContentGenerationArtifact.artifact_id)
        )
        return list(result.unique().all())

    async def create_manifest(
        self,
        *,
        dataset_version: str,
        scope_ids: list[str],
        languages: list[str],
        created_by: str,
        require_published: bool,
        min_quality_score: float,
        min_caps_alignment_score: float,
        policy_version: str,
        rubric_version: str,
    ) -> TrainingDatasetManifest:
        existing = await self.db.scalar(
            select(TrainingDatasetManifest).where(
                TrainingDatasetManifest.dataset_version == dataset_version
            )
        )
        if existing is not None:
            return existing

        manifest = TrainingDatasetManifest(
            dataset_version=dataset_version,
            status="draft",
            policy_version=policy_version,
            rubric_version=rubric_version,
            require_published=require_published,
            min_quality_score=min_quality_score,
            min_caps_alignment_score=min_caps_alignment_score,
            created_by=created_by,
        )
        self.db.add(manifest)
        await self.db.flush()

        language_counts: Counter[str] = Counter()
        scope_counts: Counter[str] = Counter()
        entries: list[TrainingDatasetEntry] = []
        for artifact in await self._candidates(scope_ids, languages):
            reasons = artifact_eligibility_reasons(
                artifact,
                require_published=require_published,
                min_quality_score=min_quality_score,
                min_caps_alignment_score=min_caps_alignment_score,
            )
            if reasons:
                continue
            record = build_training_record(artifact)
            digest = record_sha256(record)
            entry = TrainingDatasetEntry(
                manifest_id=manifest.manifest_id,
                artifact_id=artifact.artifact_id,
                artifact_hash=artifact.artifact_hash,
                artifact_version=_artifact_version(artifact),
                scope_id=artifact.scope_id,
                caps_ref=artifact.caps_ref,
                language=artifact.language or "unknown",
                content_layer=_enum_value(artifact.content_layer),
                quality_score=artifact.quality_score,
                caps_alignment_score=artifact.caps_alignment_score,
                source_snapshot_hash=artifact.source_snapshot_hash,
                record_sha256=digest,
            )
            self.db.add(entry)
            entries.append(entry)
            language_counts[entry.language] += 1
            scope_counts[entry.scope_id] += 1

        manifest.artifact_count = len(entries)
        manifest.language_counts = dict(language_counts)
        manifest.scope_counts = dict(scope_counts)
        manifest.status = "ready" if entries else "draft"
        await self.db.flush()
        return manifest

    async def approve_manifest(self, manifest_id: UUID, actor_id: str, decision: str) -> TrainingDatasetManifest:
        manifest = await self.db.scalar(
            select(TrainingDatasetManifest)
            .where(TrainingDatasetManifest.manifest_id == manifest_id)
            .with_for_update()
        )
        if manifest is None:
            raise LookupError("Training dataset manifest not found")
        if manifest.status not in {"ready", "draft"}:
            return manifest
        if decision == "reject":
            manifest.status = "rejected"
            return manifest
        entries = list(
            (
                await self.db.scalars(
                    select(TrainingDatasetEntry)
                    .where(TrainingDatasetEntry.manifest_id == manifest_id)
                    .order_by(TrainingDatasetEntry.record_sha256)
                )
            ).all()
        )
        if not entries:
            raise ValueError("Cannot approve an empty dataset manifest")
        manifest.dataset_sha256 = dataset_sha256(entry.record_sha256 for entry in entries)
        manifest.approved_by = actor_id
        manifest.approved_at = datetime.now(UTC)
        manifest.status = "approved"
        return manifest

    def _safe_output_path(self, output_name: str) -> Path:
        candidate = (self.artifact_root / output_name).resolve()
        if self.artifact_root not in candidate.parents:
            raise ValueError("Output path escapes approved training artifact root")
        return candidate

    async def export_manifest(self, manifest_id: UUID, output_name: str) -> tuple[TrainingDatasetManifest, Path]:
        manifest = await self.db.scalar(
            select(TrainingDatasetManifest)
            .where(TrainingDatasetManifest.manifest_id == manifest_id)
            .with_for_update()
        )
        if manifest is None:
            raise LookupError("Training dataset manifest not found")
        if manifest.status != "approved":
            raise PermissionError("Only approved training dataset manifests may be exported")

        rows = (
            await self.db.execute(
                select(TrainingDatasetEntry, ContentGenerationArtifact)
                .join(
                    ContentGenerationArtifact,
                    ContentGenerationArtifact.artifact_id == TrainingDatasetEntry.artifact_id,
                )
                .where(TrainingDatasetEntry.manifest_id == manifest_id)
                .options(selectinload(ContentGenerationArtifact.sources))
                .order_by(TrainingDatasetEntry.record_sha256)
            )
        ).all()
        output = self._safe_output_path(output_name)
        output.parent.mkdir(parents=True, exist_ok=True)
        records: list[tuple[str, str]] = []
        for entry, artifact in rows:
            reasons = artifact_eligibility_reasons(
                artifact,
                require_published=manifest.require_published,
                min_quality_score=float(manifest.min_quality_score),
                min_caps_alignment_score=float(manifest.min_caps_alignment_score),
            )
            if reasons:
                raise PermissionError(
                    f"Artifact {artifact.artifact_id} is no longer eligible: {','.join(reasons)}"
                )
            record = build_training_record(artifact)
            digest = record_sha256(record)
            if digest != entry.record_sha256:
                raise RuntimeError(f"Artifact {artifact.artifact_id} changed after manifest creation")
            records.append((digest, _normalised_json(record)))
        computed = dataset_sha256(digest for digest, _ in records)
        if computed != manifest.dataset_sha256:
            raise RuntimeError("Dataset manifest hash mismatch")
        output.write_text("\n".join(record for _, record in records) + "\n", encoding="utf-8")
        return manifest, output
