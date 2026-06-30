"""File-backed promotion readiness for generated scope artifacts."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.domain.content_scope import ContentScopeStatus
from app.services.content_file_lesson_quality import ContentFileLessonQualityService
from app.services.content_file_review_workflow import ContentFileReviewWorkflowService
from app.services.content_scope_registry import ContentScopeRegistry
from scripts.curriculum.validate_source_manifest import generation_ready

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROMOTION_MANIFEST_DIR = PROJECT_ROOT / "data" / "generated" / "promotion_manifests"

_LAYER_PATH_KEYS = {
    "topic_map": "topic_map_path",
    "diagnostic_items": "diagnostic_items",
    "lessons": "lessons",
    "assessment_blueprints": "assessment_blueprints",
    "study_plan_templates": "study_plan_templates",
}


@dataclass(frozen=True)
class PromotionReadinessResult:
    scope_id: str
    learner_visible: bool
    source_ready: bool
    staging_eligible: bool
    production_eligible: bool
    blockers: list[str]
    manifest: dict[str, Any]


class ContentFilePromotionReadinessService:
    """Evaluate generated JSON files before DB staging or production promotion.

    This service is intentionally file-backed. It bridges the new generated
    artifact layer files into the existing DB staging/promotion flow by producing
    deterministic manifests, hashes, idempotency keys, and rollback metadata.
    """

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
        self.review_service = review_service or ContentFileReviewWorkflowService(
            project_root=self.project_root,
            registry=self.registry,
            readiness_service=self,
        )
        self.lesson_quality_service = lesson_quality_service or ContentFileLessonQualityService(
            project_root=self.project_root,
            registry=self.registry,
        )

    def evaluate_scope(self, scope_id: str) -> PromotionReadinessResult:
        scope = self.registry.get_scope(scope_id)
        now = _now_utc()
        source_ready = generation_ready(scope_id, registry=self.registry)
        learner_visible = scope.status == ContentScopeStatus.ACTIVE
        blockers: list[str] = []

        if not source_ready:
            blockers.append("Scope source material is not generation-ready.")

        layer_manifests: dict[str, dict[str, Any]] = {}
        for layer, key in _LAYER_PATH_KEYS.items():
            configured = scope.topic_map_path if layer == "topic_map" else scope.artifact_paths.get(key)
            layer_manifests[layer] = self._layer_manifest(scope.scope_id, layer, configured)
            if not layer_manifests[layer]["exists"]:
                blockers.append(f"Missing {layer} artifact file: {configured or 'not configured'}.")
            elif layer_manifests[layer]["record_count"] <= 0:
                blockers.append(f"{layer} artifact file contains no records.")

        review_evidence = self.review_service.review_status(scope_id)
        lesson_quality = self.lesson_quality_service.audit_scope(scope_id)
        if lesson_quality.quarantined:
            blockers.extend(lesson_quality.blockers)
        if scope.status == ContentScopeStatus.REVIEW:
            if review_evidence.stage_unlocked:
                blockers.append("Scope is still review; activate scope intentionally before learner visibility.")
                blockers.extend(review_evidence.production_blockers)
            else:
                blockers.append("Scope is still in review and requires dev_approved or educator approval before staging unlock.")
                blockers.extend(review_evidence.stage_blockers)
                blockers.extend(review_evidence.production_blockers)
        elif scope.status != ContentScopeStatus.ACTIVE:
            blockers.append(f"Scope status {scope.status.value} is not production-promotable.")

        staging_eligible = (
            source_ready
            and all(layer["exists"] and layer["record_count"] > 0 for layer in layer_manifests.values())
            and not lesson_quality.quarantined
        )
        production_eligible = staging_eligible and learner_visible and not blockers

        manifest = {
            "schema_version": "1.0",
            "generated_at": now,
            "scope_id": scope.scope_id,
            "grade": scope.grade,
            "phase": scope.phase,
            "subject_code": scope.subject_code,
            "subject": scope.subject,
            "language": scope.language,
            "status": scope.status.value,
            "learner_visible": learner_visible,
            "source_ready": source_ready,
            "review_evidence": {
                "status": review_evidence.status,
                "approved": review_evidence.approved,
                "stage_unlocked": review_evidence.stage_unlocked,
                "production_unlocked": review_evidence.production_unlocked,
                "manifest_path": str(review_evidence.manifest_path.relative_to(self.project_root)) if review_evidence.manifest_path else None,
                "stage_blockers": review_evidence.stage_blockers,
                "production_blockers": review_evidence.production_blockers,
                "blockers": review_evidence.blockers,
            },
            "lesson_quality": {
                "passed": lesson_quality.passed,
                "quarantined": lesson_quality.quarantined,
                "lesson_count": lesson_quality.lesson_count,
                "failed_lesson_count": lesson_quality.failed_lesson_count,
                "blockers": lesson_quality.blockers,
                "aggregate": lesson_quality.aggregate,
            },
            "staging_eligible": staging_eligible,
            "production_eligible": production_eligible,
            "caps_ref_count": len(scope.caps_refs),
            "layers": layer_manifests,
            "blockers": blockers,
            "idempotency_keys": {
                layer: data["idempotency_key"]
                for layer, data in layer_manifests.items()
                if data.get("idempotency_key")
            },
            "rollback_manifest": {
                "scope_id": scope.scope_id,
                "restore_scope_status": scope.status.value,
                "artifact_paths": {
                    layer: data["relative_path"]
                    for layer, data in layer_manifests.items()
                    if data.get("relative_path")
                },
                "artifact_hashes": {
                    layer: data["sha256"]
                    for layer, data in layer_manifests.items()
                    if data.get("sha256")
                },
            },
        }
        return PromotionReadinessResult(
            scope_id=scope.scope_id,
            learner_visible=learner_visible,
            source_ready=source_ready,
            staging_eligible=staging_eligible,
            production_eligible=production_eligible,
            blockers=blockers,
            manifest=manifest,
        )

    def build_all(self) -> dict[str, Any]:
        results = [self.evaluate_scope(scope.scope_id) for scope in self.registry.list_scopes()]
        summary = {
            "scope_count": len(results),
            "staging_eligible": sum(1 for result in results if result.staging_eligible),
            "production_eligible": sum(1 for result in results if result.production_eligible),
            "review_blocked": sum(1 for result in results if not result.production_eligible and result.staging_eligible),
            "lesson_quarantined": sum(
                1 for result in results if result.manifest.get("lesson_quality", {}).get("quarantined")
            ),
            "learner_visible": sum(1 for result in results if result.learner_visible),
        }
        return {
            "schema_version": "1.0",
            "generated_at": _now_utc(),
            "summary": summary,
            "scopes": [result.manifest for result in results],
        }

    def write_manifests(self, *, output_dir: Path | None = None) -> dict[str, Any]:
        output_dir = output_dir or PROMOTION_MANIFEST_DIR
        output_dir.mkdir(parents=True, exist_ok=True)
        summary = self.build_all()
        for scope_manifest in summary["scopes"]:
            path = output_dir / f"{scope_manifest['scope_id']}_promotion_readiness.json"
            _write_json(path, scope_manifest)
        summary_path = output_dir / "all_scopes_promotion_readiness_summary.json"
        _write_json(summary_path, summary)
        return summary

    def _layer_manifest(self, scope_id: str, layer: str, relative_path: str | None) -> dict[str, Any]:
        if not relative_path:
            return {
                "layer": layer,
                "relative_path": None,
                "exists": False,
                "sha256": None,
                "record_count": 0,
                "approved_count": 0,
                "review_ready_count": 0,
                "idempotency_key": None,
            }
        path = self.project_root / relative_path
        if not path.exists():
            return {
                "layer": layer,
                "relative_path": relative_path,
                "exists": False,
                "sha256": None,
                "record_count": 0,
                "approved_count": 0,
                "review_ready_count": 0,
                "idempotency_key": None,
            }
        payload = json.loads(path.read_text(encoding="utf-8"))
        record_count, approved_count, review_ready_count = _counts_for_layer(layer, payload)
        digest = _sha256(path)
        return {
            "layer": layer,
            "relative_path": relative_path,
            "exists": True,
            "sha256": digest,
            "record_count": record_count,
            "approved_count": approved_count,
            "review_ready_count": review_ready_count,
            "idempotency_key": f"{scope_id}:{layer}:{digest}",
        }


def _counts_for_layer(layer: str, payload: dict[str, Any]) -> tuple[int, int, int]:
    if layer == "topic_map":
        refs = []
        for term in payload.get("terms", []):
            for topic in term.get("topics", []):
                if topic.get("caps_ref"):
                    refs.append(topic["caps_ref"])
                refs.extend(subtopic["caps_ref"] for subtopic in topic.get("subtopics", []) if subtopic.get("caps_ref"))
        return len(refs), len(refs), len(refs)
    if layer == "diagnostic_items":
        records = payload.get("items", [])
    elif layer == "lessons":
        records = payload.get("lessons", [])
    elif layer == "assessment_blueprints":
        records = payload.get("blueprints", [])
    elif layer == "study_plan_templates":
        records = payload.get("topic_sequence", [])
    else:
        records = []
    approved = sum(1 for record in records if str(record.get("review_status") or record.get("status") or "approved") == "approved")
    review_ready = sum(1 for record in records if str(record.get("review_status") or record.get("status") or "approved") in {"approved", "review_ready", "human_reviewed"})
    return len(records), approved, review_ready


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
