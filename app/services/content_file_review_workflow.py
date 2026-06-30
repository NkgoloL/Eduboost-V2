"""File-backed educator review workflow for generated scope artifacts."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from typing import TYPE_CHECKING

from app.services.content_scope_registry import ContentScopeRegistry

if TYPE_CHECKING:
    from app.services.content_file_promotion_readiness import ContentFilePromotionReadinessService

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REVIEW_MANIFEST_DIR = PROJECT_ROOT / "data" / "generated" / "review_manifests"


@dataclass(frozen=True)
class ScopeReviewEvidenceStatus:
    scope_id: str
    status: str
    approved: bool
    stage_unlocked: bool
    production_unlocked: bool
    blockers: list[str]
    stage_blockers: list[str]
    production_blockers: list[str]
    manifest_path: Path | None
    manifest: dict[str, Any] | None


class ContentFileReviewWorkflowService:
    """Create and verify educator review evidence for generated scope files."""

    def __init__(
        self,
        *,
        project_root: Path | None = None,
        registry: ContentScopeRegistry | None = None,
        readiness_service: "ContentFilePromotionReadinessService | None" = None,
        manifest_dir: Path | None = None,
    ) -> None:
        self.project_root = project_root or PROJECT_ROOT
        self.registry = registry or ContentScopeRegistry(project_root=self.project_root)
        self.manifest_dir = manifest_dir or REVIEW_MANIFEST_DIR
        if readiness_service is None:
            from app.services.content_file_promotion_readiness import ContentFilePromotionReadinessService

            readiness_service = ContentFilePromotionReadinessService(
                project_root=self.project_root,
                registry=self.registry,
                review_service=self,
            )
        self.readiness_service = readiness_service

    def build_review_packet(
        self,
        scope_id: str,
        *,
        reviewer_id: str = "pending",
        decision: str = "pending",
        evidence_url: str = "pending",
        legal_decision: str = "pending",
        legal_evidence_url: str = "pending",
        notes: str = "Educator review not yet completed.",
        output_dir: Path | None = None,
    ) -> dict[str, Any]:
        scope = self.registry.get_scope(scope_id)
        readiness = self.readiness_service.evaluate_scope(scope_id).manifest
        stage_unlocked = _stage_unlocked_decision(decision) and not _pending(reviewer_id) and not _pending(evidence_url)
        educator_approved = _educator_approved_decision(decision) and not _pending(reviewer_id) and not _pending(evidence_url)
        legal_approved = _legal_approved_decision(legal_decision) and not _pending(legal_evidence_url)
        approved_at = _now_utc() if stage_unlocked else None
        packet = {
            "schema_version": "1.0",
            "generated_at": _now_utc(),
            "scope_id": scope.scope_id,
            "scope_status": scope.status.value,
            "review_policy_id": scope.review_policy_id,
            "decision": decision,
            "dev_approved": _dev_approved_decision(decision),
            "stage_unlocked": stage_unlocked,
            "approved": educator_approved,
            "legal_decision": legal_decision,
            "legal_approved": legal_approved,
            "reviewer_id": reviewer_id,
            "evidence_url": evidence_url,
            "legal_evidence_url": legal_evidence_url,
            "approved_at": approved_at,
            "notes": notes,
            "layer_review": {
                layer: {
                    "path": data["relative_path"],
                    "sha256": data["sha256"],
                    "record_count": data["record_count"],
                    "review_ready_count": data["review_ready_count"],
                    "review_status": "dev_approved" if _dev_approved_decision(decision) else "approved" if educator_approved else "pending_educator_review",
                }
                for layer, data in readiness["layers"].items()
            },
            "promotion_readiness": {
                "staging_eligible": readiness["staging_eligible"],
                "production_eligible": readiness["production_eligible"],
                "blockers": readiness["blockers"],
            },
        }
        output_dir = output_dir or self.manifest_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"{scope_id}_educator_review.json"
        _write_json(path, packet)
        return packet

    def review_status(self, scope_id: str, *, manifest_dir: Path | None = None) -> ScopeReviewEvidenceStatus:
        manifest_dir = manifest_dir or self.manifest_dir
        path = manifest_dir / f"{scope_id}_educator_review.json"
        if not path.exists():
            return ScopeReviewEvidenceStatus(scope_id, "missing", False, False, False, ["Review evidence packet is missing."], ["Review evidence packet is missing."], ["Educator approval is required for production.", "Legal approval is required for production."], None, None)
        manifest = json.loads(path.read_text(encoding="utf-8"))
        stage_blockers: list[str] = []
        production_blockers: list[str] = []
        decision = manifest.get("decision")
        legal_decision = manifest.get("legal_decision")
        stage_unlocked = _stage_unlocked_decision(decision)
        educator_approved = _educator_approved_decision(decision)
        legal_approved = _legal_approved_decision(legal_decision)

        if not stage_unlocked:
            stage_blockers.append("Review decision is not dev_approved or approved.")
        if _pending(manifest.get("reviewer_id")):
            stage_blockers.append("Reviewer ID is pending.")
        if _pending(manifest.get("evidence_url")):
            stage_blockers.append("Review evidence_url is pending.")
        if _pending(manifest.get("approved_at")):
            stage_blockers.append("Review approved_at timestamp is pending.")
        if manifest.get("scope_id") != scope_id:
            stage_blockers.append("Review packet scope_id does not match request.")

        if not educator_approved:
            production_blockers.append("Educator approval is required for production.")
        if not legal_approved:
            production_blockers.append("Legal approval is required for production.")
        if educator_approved and not _valid_evidence_url(manifest.get("evidence_url")):
            production_blockers.append("Educator approval evidence_url must be a real non-placeholder HTTPS URL.")
        if legal_approved and not _valid_evidence_url(manifest.get("legal_evidence_url")):
            production_blockers.append("Legal approval evidence_url must be a real non-placeholder HTTPS URL.")

        for layer, data in (manifest.get("layer_review") or {}).items():
            if int(data.get("record_count") or 0) <= 0:
                stage_blockers.append(f"{layer} review packet has no records.")
            if not data.get("sha256"):
                stage_blockers.append(f"{layer} review packet is missing artifact hash.")

        stage_unlocked = not stage_blockers
        production_unlocked = stage_unlocked and not production_blockers
        if production_unlocked:
            status = "approved"
        elif stage_unlocked and _dev_approved_decision(decision):
            status = "dev_approved"
        elif stage_unlocked:
            status = "educator_approved"
        else:
            status = "pending"
        blockers = stage_blockers + production_blockers
        return ScopeReviewEvidenceStatus(
            scope_id=scope_id,
            status=status,
            approved=educator_approved and stage_unlocked,
            stage_unlocked=stage_unlocked,
            production_unlocked=production_unlocked,
            blockers=blockers,
            stage_blockers=stage_blockers,
            production_blockers=production_blockers,
            manifest_path=path,
            manifest=manifest,
        )


def _stage_unlocked_decision(value: Any) -> bool:
    return _dev_approved_decision(value) or _educator_approved_decision(value)


def _dev_approved_decision(value: Any) -> bool:
    return str(value or "").strip().lower() == "dev_approved"


def _educator_approved_decision(value: Any) -> bool:
    return str(value or "").strip().lower() in {"approved", "approve", "accepted", "pass", "passed"}


def _legal_approved_decision(value: Any) -> bool:
    return str(value or "").strip().lower() in {"approved", "approve", "accepted", "pass", "passed"}


def _pending(value: Any) -> bool:
    return value is None or str(value).strip().lower() in {"", "pending", "none", "null"}


def _valid_evidence_url(value: Any) -> bool:
    if _pending(value):
        return False
    raw = str(value).strip()
    parsed = urlparse(raw)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not host:
        return False
    placeholder_tokens = ("example.com", ".example", "localhost", "127.0.0.1", "0.0.0.0")
    return not any(token in host for token in placeholder_tokens)


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
