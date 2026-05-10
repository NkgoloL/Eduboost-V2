#!/usr/bin/env python3
"""Validate dev-only endpoint production exposure guards."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIREMENTS = {
    "app/api_v2_routers/auth.py": (
        "/dev-session",
        "settings.is_production()",
        "status.HTTP_404_NOT_FOUND",
        "Not found",
        "DEV_SESSION_BOOTSTRAPPED",
    ),
    "docs/security/dev_session_environment_gate.md": (
        "POST /api/v2/auth/dev-session",
        "settings.is_production()",
        "HTTP_404_NOT_FOUND",
    ),
}


@dataclass(frozen=True)
class DevEndpointResult:
    target: str
    ok: bool
    detail: str


def run_checks() -> list[DevEndpointResult]:
    results: list[DevEndpointResult] = []
    for rel_path, snippets in REQUIREMENTS.items():
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        for snippet in snippets:
            results.append(
                DevEndpointResult(
                    target=rel_path,
                    ok=snippet in text,
                    detail=f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}",
                )
            )
    return results


def main() -> int:
    results = run_checks()
    print("Dev-only endpoint exposure check")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.target}: {result.detail}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
