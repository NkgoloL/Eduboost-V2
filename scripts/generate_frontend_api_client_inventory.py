#!/usr/bin/env python3
"""Generate an inventory of frontend API client surfaces."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "frontend" / "frontend_api_client_inventory.md"

SCAN_ROOTS = (
    REPO_ROOT / "frontend" / "src",
    REPO_ROOT / "src",
)
FRONTEND_EXTENSIONS = (".tsx", ".ts", ".jsx", ".js")

API_MARKERS = (
    "fetch(",
    "axios",
    "apiClient",
    "useQuery",
    "useMutation",
    "/api/v2",
    "/v2",
)

DOMAIN_MARKERS = (
    "learner",
    "parent",
    "diagnostic",
    "lesson",
    "assessment",
    "study",
    "progress",
    "consent",
    "popia",
    "dashboard",
)


@dataclass(frozen=True)
class FrontendApiSurface:
    path: str
    api_markers: tuple[str, ...]
    domain_markers: tuple[str, ...]


def _iter_frontend_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        if root.exists():
            files.extend(
                path
                for path in root.rglob("*")
                if path.is_file()
                and path.suffix in FRONTEND_EXTENSIONS
                and "node_modules" not in path.parts
                and "dist" not in path.parts
                and "build" not in path.parts
            )
    return sorted(set(files))


def discover_surfaces() -> list[FrontendApiSurface]:
    surfaces: list[FrontendApiSurface] = []
    for path in _iter_frontend_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        lowered = text.lower()
        api_hits = tuple(marker for marker in API_MARKERS if marker.lower() in lowered)
        domain_hits = tuple(marker for marker in DOMAIN_MARKERS if marker.lower() in lowered)
        if api_hits or (domain_hits and ("api" in lowered or "client" in lowered)):
            surfaces.append(
                FrontendApiSurface(
                    path=str(path.relative_to(REPO_ROOT)),
                    api_markers=api_hits,
                    domain_markers=domain_hits,
                )
            )
    return surfaces


def render_inventory(surfaces: list[FrontendApiSurface]) -> str:
    lines = [
        "# Frontend API Client Inventory",
        "",
        "## Purpose",
        "",
        "This inventory records frontend API client, fetch, and domain call surfaces.",
        "",
        "## Required API Domains",
        "",
        "- learner-scoped reads",
        "- learner-scoped writes",
        "- parent-scoped reads",
        "- consent status and consent mutation",
        "- diagnostic start and submit",
        "- lesson generation and lesson retrieval",
        "- study plan or assessment attempt",
        "- progress/mastery retrieval",
        "- error envelope parsing",
        "",
        "## Discovered Surfaces",
        "",
        "| Path | API markers | Domain markers |",
        "| --- | --- | --- |",
    ]

    if not surfaces:
        lines.append("| _none found_ | _none_ | _none_ |")
    else:
        for surface in surfaces:
            api_text = ", ".join(surface.api_markers) or "_none_"
            domain_text = ", ".join(surface.domain_markers) or "_none_"
            lines.append(f"| `{surface.path}` | `{api_text}` | `{domain_text}` |")

    lines.extend(
        [
            "",
            "## Command",
            "",
            "```bash",
            "make frontend-api-client-inventory",
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
