"""Runtime KG study-plan helper used by PRD-2 feature-flagged rollout."""
from __future__ import annotations

from typing import Any

from app.services.runtime_kg.integration import runtime_kg_study_plan_focus


def build_runtime_kg_week_focus(context: dict[str, Any]) -> dict[str, Any]:
    """Create a deterministic study-plan block from runtime KG gaps.

    Returns an empty disabled block when the runtime KG context is unavailable,
    preserving the legacy study-plan path.
    """

    focus_items = runtime_kg_study_plan_focus(context)
    if not focus_items:
        return {"runtime_kg_enabled": False, "focus_items": []}
    return {
        "runtime_kg_enabled": True,
        "graph_version": context.get("graph_version"),
        "focus_items": focus_items,
    }
