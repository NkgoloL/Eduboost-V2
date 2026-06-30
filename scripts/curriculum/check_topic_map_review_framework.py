#!/usr/bin/env python3
"""Verify the Phase 2 topic-map review framework and inventory."""
from __future__ import annotations

import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.content_scope_registry import ContentScopeRegistry
from scripts.curriculum.validate_source_manifest import validate_source_manifest

CHECKLIST_PATH = ROOT / "docs" / "curriculum" / "TOPIC_MAP_REVIEW_CHECKLIST.md"
TOPIC_MAP_DIR = ROOT / "data" / "caps" / "topic_maps"


@dataclass
class FrameworkCheckResult:
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    facts: dict[str, object] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return not self.failures

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.failures.append(message)


def check_framework() -> FrameworkCheckResult:
    result = FrameworkCheckResult()
    result.require(CHECKLIST_PATH.exists(), f"missing checklist: {CHECKLIST_PATH.relative_to(ROOT)}")
    if CHECKLIST_PATH.exists():
        text = CHECKLIST_PATH.read_text(encoding="utf-8")
        required_phrases = [
            "Status Levels",
            "DRAFT",
            "UNDER_REVIEW",
            "REVISION_NEEDED",
            "APPROVED",
            "READY_FOR_GENERATION",
            "Curriculum Expert",
            "Phase Lead",
            "Pedagogy QA",
            "Review Tracking",
            "Revision Request Template",
            "Quality Standards for Approval",
        ]
        for phrase in required_phrases:
            result.require(phrase in text, f"checklist missing required phrase: {phrase}")

    topic_maps = sorted(TOPIC_MAP_DIR.glob("*.json"))
    result.facts["topic_map_file_count"] = len(topic_maps)
    result.require(len(topic_maps) >= 50, f"expected at least 50 topic-map files, found {len(topic_maps)}")

    registry = ContentScopeRegistry()
    scopes = registry.list_scopes()
    status_counts = Counter(scope.status.value for scope in scopes)
    result.facts["scope_count"] = len(scopes)
    result.facts["scope_status_counts"] = dict(sorted(status_counts.items()))
    result.require(status_counts.get("review", 0) == 50, f"expected 50 review scopes, found {status_counts.get('review', 0)}")
    result.require(status_counts.get("active", 0) == 1, f"expected 1 active launch scope, found {status_counts.get('active', 0)}")

    validation = validate_source_manifest(registry=registry)
    result.facts["source_manifest_passed"] = validation.passed
    result.facts["generation_ready_scope_count"] = len(validation.generation_ready_scope_ids)
    result.require(validation.passed, "source manifest validation failed")
    result.require(
        len(validation.generation_ready_scope_ids) >= 50,
        f"expected at least 50 generation-ready scopes, found {len(validation.generation_ready_scope_ids)}",
    )
    if validation.warnings:
        result.warnings.extend(validation.warnings)
    if validation.errors:
        result.failures.extend(validation.errors)
    return result


def print_result(result: FrameworkCheckResult) -> None:
    print("Topic-map review framework check")
    for key, value in result.facts.items():
        print(f"- INFO {key}: {value}")
    for warning in result.warnings:
        print(f"- WARN {warning}")
    if result.failures:
        for failure in result.failures:
            print(f"- FAIL {failure}")
    else:
        print("- PASS review framework document contains required workflow, roles, and tracking markers")
        print("- PASS topic-map and source-manifest inventory satisfies Phase 2 Step 1 readiness")


def main() -> int:
    result = check_framework()
    print_result(result)
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
