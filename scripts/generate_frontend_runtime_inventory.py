#!/usr/bin/env python3
"""Generate frontend package/runtime command inventory."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "frontend" / "frontend_runtime_inventory.md"

PACKAGE_CANDIDATES = (
    REPO_ROOT / "frontend" / "package.json",
    REPO_ROOT / "package.json",
)

LOCKFILES = (
    "frontend/package-lock.json",
    "frontend/pnpm-lock.yaml",
    "frontend/yarn.lock",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
)

REQUIRED_COMMAND_AREAS = (
    "install dependencies",
    "start development server",
    "build frontend",
    "run frontend unit tests",
    "run Playwright E2E",
    "run accessibility scaffold",
)


@dataclass(frozen=True)
class FrontendRuntimePackage:
    path: str
    scripts: dict[str, str]


def _load_package(path: Path) -> FrontendRuntimePackage | None:
    if not path.exists():
        return None
    try:
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return FrontendRuntimePackage(str(path.relative_to(REPO_ROOT)), {})
    scripts = data.get("scripts")
    if not isinstance(scripts, dict):
        scripts = {}
    return FrontendRuntimePackage(
        path=str(path.relative_to(REPO_ROOT)),
        scripts={str(k): str(v) for k, v in scripts.items()},
    )


def discover_packages() -> list[FrontendRuntimePackage]:
    packages: list[FrontendRuntimePackage] = []
    for path in PACKAGE_CANDIDATES:
        package = _load_package(path)
        if package is not None:
            packages.append(package)
    return packages


def _package_manager_hint() -> str:
    existing = [lock for lock in LOCKFILES if (REPO_ROOT / lock).exists()]
    if any(lock.endswith("pnpm-lock.yaml") for lock in existing):
        return "pnpm"
    if any(lock.endswith("yarn.lock") for lock in existing):
        return "yarn"
    if any(lock.endswith("package-lock.json") for lock in existing):
        return "npm"
    return "npm"


def render_inventory(packages: list[FrontendRuntimePackage]) -> str:
    package_manager = _package_manager_hint()
    lines = [
        "# Frontend Runtime Inventory",
        "",
        "## Purpose",
        "",
        "This inventory records frontend package scripts and runtime command assumptions for Cluster G.",
        "",
        "## Package Manager",
        "",
        f"- inferred package manager: `{package_manager}`",
        "",
        "## Required Command Areas",
        "",
    ]

    for area in REQUIRED_COMMAND_AREAS:
        lines.append(f"- {area}")

    lines.extend(
        [
            "",
            "## Package Scripts",
            "",
        ]
    )

    if not packages:
        lines.extend(
            [
                "No package.json file was found in `frontend/package.json` or repository root.",
                "",
                "Runtime frontend execution remains pending until package metadata is present.",
                "",
            ]
        )
    else:
        for package in packages:
            lines.extend(
                [
                    f"### `{package.path}`",
                    "",
                    "| Script | Command |",
                    "| --- | --- |",
                ]
            )
            if not package.scripts:
                lines.append("| _none_ | _none_ |")
            else:
                for name, command in sorted(package.scripts.items()):
                    safe_command = command.replace("|", "\\|")
                    lines.append(f"| `{name}` | `{safe_command}` |")
            lines.append("")

    lines.extend(
        [
            "## Cluster G Commands",
            "",
            "```bash",
            "make frontend-route-inventory",
            "make frontend-api-client-inventory",
            "make frontend-playwright-scaffold-check",
            "make frontend-playwright-specs-check",
            "make frontend-e2e",
            "```",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> int:
    packages = discover_packages()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render_inventory(packages), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)} with {len(packages)} package file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
