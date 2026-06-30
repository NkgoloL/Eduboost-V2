#!/usr/bin/env python3
"""Generate an inventory of likely AI prompt construction surfaces."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "ai" / "ai_prompt_surface_inventory.md"
SCAN_ROOTS = (
    REPO_ROOT / "app",
    REPO_ROOT / "services",
    REPO_ROOT / "scripts",
)
PROMPT_MARKERS = (
    "prompt",
    "system_message",
    "user_message",
    "llm",
    "anthropic",
    "groq",
    "generate_lesson",
    "diagnostic",
    "remediation",
)


@dataclass(frozen=True)
class PromptSurface:
    path: str
    markers: tuple[str, ...]


def _iter_python_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        if root.exists():
            files.extend(path for path in root.rglob("*.py") if "__pycache__" not in path.parts)
    return sorted(set(files))


def discover_surfaces() -> list[PromptSurface]:
    surfaces: list[PromptSurface] = []
    for path in _iter_python_files():
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        markers = tuple(marker for marker in PROMPT_MARKERS if marker.lower() in text)
        if markers:
            surfaces.append(PromptSurface(str(path.relative_to(REPO_ROOT)), markers))
    return surfaces


def render_inventory(surfaces: list[PromptSurface]) -> str:
    lines = [
        "# AI Prompt Surface Inventory",
        "",
        "## Purpose",
        "",
        "This inventory records likely prompt construction or AI generation surfaces.",
        "",
        "## Required Safety Markers",
        "",
        "- CAPS alignment",
        "- learner grade and subject",
        "- consent-authorized learner context",
        "- AI safety boundary instructions",
        "- no cross-learner data leakage",
        "",
        "## Discovered Surfaces",
        "",
        "| Path | Markers |",
        "| --- | --- |",
    ]

    if not surfaces:
        lines.append("| _none found_ | _none_ |")
    else:
        for surface in surfaces:
            lines.append(f"| `{surface.path}` | `{', '.join(surface.markers)}` |")

    lines.extend(
        [
            "",
            "## Command",
            "",
            "```bash",
            "python scripts/generate_ai_prompt_surface_inventory.py",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    surfaces = discover_surfaces()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render_inventory(surfaces), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)} with {len(surfaces)} surfaces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
