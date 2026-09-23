"""Unit tests for CAPS curriculum registry consistency."""
from __future__ import annotations

import json
from pathlib import Path

from scripts.curriculum.verify_curriculum_registry_consistency import (
    verify_curriculum_registry_consistency,
)


def test_curriculum_registry_consistency():
    report = verify_curriculum_registry_consistency()
    assert report["verified"] is True
    assert report["total_scopes"] == 51
    assert report["authoritative_scopes_count"] == 51
    assert report["coverage_targets_scopes_count"] == 51
    assert report["source_completeness_scopes_count"] == 51
    assert report["text_extracts_scopes_count"] == 51
    assert len(report["errors"]) == 0


def test_scopes_manifest_exact_set_match():
    repo_root = Path(__file__).resolve().parents[3]
    scopes_data = json.loads(
        (repo_root / "data/content_factory/scopes.json").read_text(encoding="utf-8")
    )["scopes"]
    scope_ids = set(s["scope_id"] for s in scopes_data)

    completeness_data = json.loads(
        (repo_root / "data/curriculum/registries/caps_curriculum_source_completeness.json").read_text(encoding="utf-8")
    )["scopes"]
    comp_ids = set(s["scope_id"] for s in completeness_data)

    assert scope_ids == comp_ids
    assert len(scope_ids) == 51
