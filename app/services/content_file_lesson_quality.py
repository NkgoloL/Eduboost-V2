"""File-backed lesson quality audit and quarantine manifests."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.services.content_generation.generated_lesson_contract import GeneratedLessonQualityValidator
from app.services.content_scope_registry import ContentScopeRegistry

PROJECT_ROOT = Path(__file__).resolve().parents[2]
QUALITY_MANIFEST_DIR = PROJECT_ROOT / "data" / "generated" / "quality_manifests"


@dataclass(frozen=True)
class LessonFileQualityResult:
    scope_id: str
    relative_path: str | None
    exists: bool
    passed: bool
    lesson_count: int
    failed_lesson_count: int
    quarantined: bool
    blockers: list[str]
    aggregate: dict[str, int]
    issues: list[dict[str, str]]


class ContentFileLessonQualityService:
    """Audit generated lesson files and produce quarantine manifests."""

    def __init__(
        self,
        *,
        project_root: Path | None = None,
        registry: ContentScopeRegistry | None = None,
        validator: GeneratedLessonQualityValidator | None = None,
    ) -> None:
        self.project_root = project_root or PROJECT_ROOT
        self.registry = registry or ContentScopeRegistry(project_root=self.project_root)
        self.validator = validator or GeneratedLessonQualityValidator()

    def audit_scope(self, scope_id: str) -> LessonFileQualityResult:
        scope = self.registry.get_scope(scope_id)
        relative_path = scope.artifact_paths.get("lessons")
        if not relative_path:
            return LessonFileQualityResult(
                scope_id=scope_id,
                relative_path=None,
                exists=False,
                passed=False,
                lesson_count=0,
                failed_lesson_count=0,
                quarantined=True,
                blockers=["Lessons artifact path is not configured."],
                aggregate={},
                issues=[],
            )

        path = self.project_root / relative_path
        if not path.exists():
            return LessonFileQualityResult(
                scope_id=scope_id,
                relative_path=relative_path,
                exists=False,
                passed=False,
                lesson_count=0,
                failed_lesson_count=0,
                quarantined=True,
                blockers=[f"Lessons artifact file is missing: {relative_path}."],
                aggregate={},
                issues=[],
            )

        payload = json.loads(path.read_text(encoding="utf-8"))
        result = self.validator.validate_file_payload(
            payload,
            scope_id=scope.scope_id,
            subject_code=scope.subject_code,
            subject=scope.subject,
            source_document_ids=scope.source_documents,
        )
        blockers: list[str] = []
        if not result.passed:
            blockers.append(
                f"Lesson layer failed quality audit: {result.failed_lesson_count}/{result.lesson_count} lessons invalid."
            )
        return LessonFileQualityResult(
            scope_id=scope_id,
            relative_path=relative_path,
            exists=True,
            passed=result.passed,
            lesson_count=result.lesson_count,
            failed_lesson_count=result.failed_lesson_count,
            quarantined=not result.passed,
            blockers=blockers,
            aggregate=result.aggregate,
            issues=[
                {
                    "lesson_id": issue.lesson_id,
                    "caps_ref": issue.caps_ref,
                    "field": issue.field,
                    "reason": issue.reason,
                }
                for issue in result.issues[:50]
            ],
        )

    def build_all(self) -> dict[str, Any]:
        results = [self.audit_scope(scope.scope_id) for scope in self.registry.list_scopes()]
        summary = {
            "scope_count": len(results),
            "lesson_files_present": sum(1 for result in results if result.exists),
            "lesson_quality_passed": sum(1 for result in results if result.passed),
            "lesson_layers_quarantined": sum(1 for result in results if result.quarantined),
            "total_lessons": sum(result.lesson_count for result in results),
            "failed_lessons": sum(result.failed_lesson_count for result in results),
        }
        return {
            "schema_version": "1.0",
            "generated_at": _now_utc(),
            "summary": summary,
            "scopes": [self._scope_manifest(result) for result in results],
        }

    def write_manifests(self, *, output_dir: Path | None = None) -> dict[str, Any]:
        output_dir = output_dir or QUALITY_MANIFEST_DIR
        output_dir.mkdir(parents=True, exist_ok=True)
        summary = self.build_all()
        for scope_manifest in summary["scopes"]:
            path = output_dir / f"{scope_manifest['scope_id']}_lesson_quality.json"
            _write_json(path, scope_manifest)
        summary_path = output_dir / "all_scopes_lesson_quality_summary.json"
        _write_json(summary_path, summary)
        return summary

    def _scope_manifest(self, result: LessonFileQualityResult) -> dict[str, Any]:
        return {
            "scope_id": result.scope_id,
            "relative_path": result.relative_path,
            "exists": result.exists,
            "passed": result.passed,
            "quarantined": result.quarantined,
            "lesson_count": result.lesson_count,
            "failed_lesson_count": result.failed_lesson_count,
            "blockers": result.blockers,
            "aggregate": result.aggregate,
            "issues": result.issues,
        }


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
