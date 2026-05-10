#!/usr/bin/env python3
"""Generate an inventory of frontend route/page/component surfaces."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "frontend" / "frontend_route_inventory.md"

SCAN_ROOTS = (
    REPO_ROOT / "frontend" / "src",
    REPO_ROOT / "src",
    REPO_ROOT / "app",
)

FRONTEND_EXTENSIONS = (".tsx", ".ts", ".jsx", ".js", ".vue")
ROUTE_MARKERS = (
    "Route",
    "Routes",
    "BrowserRouter",
    "createBrowserRouter",
    "path:",
    "href=",
    "Link",
    "useNavigate",
)
JOURNEY_MARKERS = (
    "learner",
    "parent",
    "dashboard",
    "lesson",
    "diagnostic",
    "assessment",
    "progress",
    "consent",
    "onboarding",
)


@dataclass(frozen=True)
class FrontendSurface:
    path: str
    route_markers: tuple[str, ...]
    journey_markers: tuple[str, ...]


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


def discover_surfaces() -> list[FrontendSurface]:
    surfaces: list[FrontendSurface] = []
    for path in _iter_frontend_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        lowered = text.lower()
        route_hits = tuple(marker for marker in ROUTE_MARKERS if marker.lower() in lowered)
        journey_hits = tuple(marker for marker in JOURNEY_MARKERS if marker.lower() in lowered)
        if route_hits or journey_hits:
            surfaces.append(
                FrontendSurface(
                    path=str(path.relative_to(REPO_ROOT)),
                    route_markers=route_hits,
                    journey_markers=journey_hits,
                )
            )
    return surfaces


def render_inventory(surfaces: list[FrontendSurface]) -> str:
    lines = [
        "# Frontend Route Inventory",
        "",
        "## Purpose",
        "",
        "This inventory records frontend route, page, and journey-related surfaces.",
        "",
        "## Required Journey Areas",
        "",
        "- learner onboarding",
        "- learner dashboard",
        "- diagnostic start and submit",
        "- lesson generation and lesson view",
        "- study plan or practice flow",
        "- parent dashboard and learner progress",
        "- consent and trust surfaces",
        "",
        "## Discovered Surfaces",
        "",
        "| Path | Route markers | Journey markers |",
        "| --- | --- | --- |",
    ]

    if not surfaces:
        lines.append("| _none found_ | _none_ | _none_ |")
    else:
        for surface in surfaces:
            route_text = ", ".join(surface.route_markers) or "_none_"
            journey_text = ", ".join(surface.journey_markers) or "_none_"
            lines.append(f"| `{surface.path}` | `{route_text}` | `{journey_text}` |")

    lines.extend(
        [
            "",
            "## Command",
            "",
            "```bash",
            "make frontend-route-inventory",
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
