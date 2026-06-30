#!/usr/bin/env python3
"""Run lightweight static accessibility checks over frontend source files.

This is intentionally dependency-free and CI-safe. Browser-level axe checks are
covered by later Playwright wiring.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = (
    REPO_ROOT / "frontend" / "src",
    REPO_ROOT / "src",
)
FRONTEND_EXTENSIONS = (".tsx", ".jsx", ".vue")

INTERACTIVE_PATTERN = re.compile(r"<(button|a|input|select|textarea)\b", re.IGNORECASE)
ACCESSIBLE_NAME_PATTERN = re.compile(
    r"(aria-label=|aria-labelledby=|title=|alt=|>\s*[^<{][^<]*\s*</)",
    re.IGNORECASE,
)
BAD_IMAGE_PATTERN = re.compile(r"<img\b(?![^>]*\balt=)", re.IGNORECASE)
BAD_BUTTON_PATTERN = re.compile(r"<button\b(?![^>]*(aria-label=|aria-labelledby=|title=))\s*></button>", re.IGNORECASE)


@dataclass(frozen=True)
class AccessibilityStaticResult:
    path: str
    ok: bool
    detail: str


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


def _check_file(path: Path) -> list[AccessibilityStaticResult]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    rel = str(path.relative_to(REPO_ROOT))
    results: list[AccessibilityStaticResult] = []

    bad_images = BAD_IMAGE_PATTERN.findall(text)
    results.append(
        AccessibilityStaticResult(
            rel,
            not bad_images,
            "images include alt attributes" if not bad_images else "image tags missing alt attributes",
        )
    )

    empty_buttons = BAD_BUTTON_PATTERN.findall(text)
    results.append(
        AccessibilityStaticResult(
            rel,
            not empty_buttons,
            "buttons are not empty without accessible names" if not empty_buttons else "empty button without accessible name",
        )
    )

    if INTERACTIVE_PATTERN.search(text):
        results.append(
            AccessibilityStaticResult(
                rel,
                ACCESSIBLE_NAME_PATTERN.search(text) is not None,
                "interactive file contains accessible-name evidence"
                if ACCESSIBLE_NAME_PATTERN.search(text) is not None
                else "interactive file lacks accessible-name evidence",
            )
        )

    return results


def run_checks() -> list[AccessibilityStaticResult]:
    files = _iter_frontend_files()
    results: list[AccessibilityStaticResult] = [
        AccessibilityStaticResult(
            "frontend source",
            True,
            f"scanned {len(files)} frontend component files",
        )
    ]

    for path in files:
        results.extend(_check_file(path))

    return results


def main() -> int:
    results = run_checks()
    print("Frontend accessibility static check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.path}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
