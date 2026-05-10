#!/usr/bin/env python3
"""Validate route-source evidence for active-consent boundaries."""
from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.generate_popia_consent_boundary_matrix import collect_rows


ROUTER_DIR = REPO_ROOT / "app" / "api_v2_routers"
CENTRAL_CONSENT = "require_active_consent_for_current_user"


@dataclass(frozen=True)
class SourceResult:
    target: str
    ok: bool
    detail: str


def _function_source(path: Path, function_name: str) -> str:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)) and node.name == function_name:
            lines = source.splitlines()
            return "\n".join(lines[node.lineno - 1 : node.end_lineno or node.lineno])
    return ""


def run_checks() -> list[SourceResult]:
    results: list[SourceResult] = []
    seen: set[tuple[str, str]] = set()

    for row in collect_rows():
        key = (row.router, row.function)
        if key in seen or row.decision != "active_consent_required":
            continue
        seen.add(key)

        path = ROUTER_DIR / row.router
        source = _function_source(path, row.function) if path.exists() else ""
        target = f"{row.router}::{row.function}"

        results.append(
            SourceResult(
                target,
                CENTRAL_CONSENT in source,
                "uses central active-consent adapter" if CENTRAL_CONSENT in source else "missing central active-consent adapter",
            )
        )

        results.append(
            SourceResult(
                target,
                "ConsentService(db).require_active_consent" not in source,
                "does not bypass central adapter" if "ConsentService(db).require_active_consent" not in source else "bypasses central adapter",
            )
        )

    return results


def main() -> int:
    results = run_checks()
    print("Active-consent route-source check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
