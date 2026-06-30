"""File-backed Content Factory scope and coverage target registry."""
from __future__ import annotations

import json
from functools import cached_property
from pathlib import Path

from app.domain.content_coverage import ContentLayer, CoverageTarget, CoverageTargetRegistryDocument
from app.domain.content_scope import ContentScope, ContentScopeRegistryDocument, ContentScopeStatus

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_SCOPES_PATH = _PROJECT_ROOT / "data" / "content_factory" / "scopes.json"
_DEFAULT_TARGETS_PATH = _PROJECT_ROOT / "data" / "content_factory" / "coverage_targets.json"


class ContentScopeRegistryError(ValueError):
    """Raised when registry data is internally inconsistent."""


class ContentScopeRegistry:
    def __init__(
        self,
        scopes_path: Path | None = None,
        targets_path: Path | None = None,
        project_root: Path | None = None,
    ) -> None:
        self.project_root = project_root or _PROJECT_ROOT
        self.scopes_path = scopes_path or _DEFAULT_SCOPES_PATH
        self.targets_path = targets_path or _DEFAULT_TARGETS_PATH

    @cached_property
    def _scopes(self) -> dict[str, ContentScope]:
        document = ContentScopeRegistryDocument.model_validate_json(self.scopes_path.read_text(encoding="utf-8"))
        scopes = {scope.scope_id: scope for scope in document.scopes}
        if len(scopes) != len(document.scopes):
            raise ContentScopeRegistryError("Duplicate scope_id values in Content Factory scope registry.")
        self._validate_scope_topic_maps(scopes)
        return scopes

    @cached_property
    def _targets(self) -> dict[tuple[str, str], CoverageTarget]:
        document = CoverageTargetRegistryDocument.model_validate_json(self.targets_path.read_text(encoding="utf-8"))
        targets = {(target.scope_id, target.caps_ref): target for target in document.targets}
        if len(targets) != len(document.targets):
            raise ContentScopeRegistryError("Duplicate scope_id/caps_ref values in Content Factory coverage registry.")
        self._validate_targets(targets.values())
        return targets

    def list_scopes(self) -> list[ContentScope]:
        return sorted(self._scopes.values(), key=lambda scope: scope.scope_id)

    def list_active_scopes(self) -> list[ContentScope]:
        return [scope for scope in self.list_scopes() if scope.status == ContentScopeStatus.ACTIVE]

    def is_scope_active(self, scope_id: str) -> bool:
        return self.get_scope(scope_id).status == ContentScopeStatus.ACTIVE

    def require_active_scope(self, scope_id: str) -> ContentScope:
        scope = self.get_scope(scope_id)
        if scope.status != ContentScopeStatus.ACTIVE:
            raise LookupError(f"Content scope {scope_id} is not active.")
        return scope

    def get_scope(self, scope_id: str) -> ContentScope:
        try:
            return self._scopes[scope_id]
        except KeyError as exc:
            raise LookupError(f"Unknown content scope: {scope_id}") from exc

    def get_scope_caps_refs(self, scope_id: str) -> list[str]:
        scope = self.get_scope(scope_id)
        return list(scope.caps_refs)

    def get_scope_targets(self, scope_id: str) -> list[CoverageTarget]:
        self.validate_scope_exists(scope_id)
        return [
            target
            for (_target_scope_id, _caps_ref), target in sorted(self._targets.items())
            if target.scope_id == scope_id
        ]

    def get_coverage_target(self, scope_id: str, caps_ref: str, layer: ContentLayer) -> int:
        target = self._get_target(scope_id, caps_ref)
        key = f"{layer.value}.approved"
        if key not in target.targets:
            raise LookupError(f"No coverage target for {scope_id}/{caps_ref}/{layer.value}.")
        return target.targets[key]

    def validate_scope_exists(self, scope_id: str) -> None:
        self.get_scope(scope_id)

    def _get_target(self, scope_id: str, caps_ref: str) -> CoverageTarget:
        self.validate_scope_exists(scope_id)
        try:
            return self._targets[(scope_id, caps_ref)]
        except KeyError as exc:
            raise LookupError(f"No coverage target for {scope_id}/{caps_ref}.") from exc

    def _validate_scope_topic_maps(self, scopes: dict[str, ContentScope]) -> None:
        for scope in scopes.values():
            if scope.status == ContentScopeStatus.ACTIVE and not scope.topic_map_path:
                raise ContentScopeRegistryError(f"Active scope {scope.scope_id} must declare topic_map_path.")
            if not scope.topic_map_path:
                if scope.caps_refs:
                    raise ContentScopeRegistryError(
                        f"Scope {scope.scope_id} declares CAPS refs without a topic_map_path."
                    )
                continue
            topic_map_refs = self._load_topic_map_refs(scope.topic_map_path)
            missing = sorted(set(scope.caps_refs) - topic_map_refs)
            if missing:
                raise ContentScopeRegistryError(
                    f"Scope {scope.scope_id} references CAPS refs not present in {scope.topic_map_path}: {missing}"
                )

    def _validate_targets(self, targets: list[CoverageTarget]) -> None:
        for target in targets:
            scope = self.get_scope(target.scope_id)
            if target.caps_ref not in scope.caps_refs:
                raise ContentScopeRegistryError(
                    f"Coverage target {target.scope_id}/{target.caps_ref} is outside the declared scope refs."
                )
            if not scope.topic_map_path:
                raise ContentScopeRegistryError(
                    f"Coverage target {target.scope_id}/{target.caps_ref} requires a topic_map_path."
                )
            self._load_topic_map_refs(scope.topic_map_path)

    def _load_topic_map_refs(self, topic_map_path: str) -> set[str]:
        path = self.project_root / topic_map_path
        raw = json.loads(path.read_text(encoding="utf-8"))
        refs: set[str] = set()
        for term in raw.get("terms", []):
            for topic in term.get("topics", []):
                if topic.get("caps_ref"):
                    refs.add(topic["caps_ref"])
                for subtopic in topic.get("subtopics", []):
                    if subtopic.get("caps_ref"):
                        refs.add(subtopic["caps_ref"])
        return refs
