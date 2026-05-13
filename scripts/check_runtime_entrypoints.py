#!/usr/bin/env python3
"""Verify canonical and compatibility FastAPI runtime entrypoints."""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from fastapi import FastAPI

REPO_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_ENTRYPOINTS = (
    "app.api_v2:app",
    "app.api.main:app",
    "app.legacy.api.main:app",
)

REQUIRED_CANONICAL_ROUTES = (
    "/",
    "/health",
    "/ready",
    "/metrics",
    "/v2/health/deep",
    "/openapi.json",
)

REQUIRED_V2_PREFIXES = (
    "/api/v2",
    "/v2",
)


@dataclass(frozen=True)
class EntrypointResult:
    spec: str
    ok: bool
    title: str | None
    version: str | None
    app_id: int | None
    route_count: int
    missing_routes: list[str]
    missing_prefixes: list[str]
    error: str | None = None


def _ensure_repo_root_on_path() -> None:
    repo_root = str(REPO_ROOT)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def load_app(spec: str) -> FastAPI:
    """Load a FastAPI app from a ``module:attribute`` spec."""
    _ensure_repo_root_on_path()

    if ":" not in spec:
        raise ValueError("Entrypoint spec must use the format 'module:attribute'.")

    module_name, attribute_name = spec.split(":", 1)
    module = importlib.import_module(module_name)
    app = getattr(module, attribute_name)

    if not isinstance(app, FastAPI):
        raise TypeError(f"{spec!r} did not resolve to a FastAPI application.")

    return app


def route_paths(app: FastAPI) -> set[str]:
    """Return all route paths registered on a FastAPI application."""
    return {getattr(route, "path", "") for route in app.routes}


def check_entrypoint(spec: str, *, canonical: bool) -> EntrypointResult:
    """Check one runtime entrypoint."""
    try:
        app = load_app(spec)
        paths = route_paths(app)

        missing_routes = [
            route for route in REQUIRED_CANONICAL_ROUTES if canonical and route not in paths
        ]
        missing_prefixes = [
            prefix
            for prefix in REQUIRED_V2_PREFIXES
            if canonical and not any(path == prefix or path.startswith(f"{prefix}/") for path in paths)
        ]

        ok = not missing_routes and not missing_prefixes

        return EntrypointResult(
            spec=spec,
            ok=ok,
            title=app.title,
            version=app.version,
            app_id=id(app),
            route_count=len(paths),
            missing_routes=missing_routes,
            missing_prefixes=missing_prefixes,
        )
    except Exception as exc:  # pragma: no cover - exercised through CLI failure path
        return EntrypointResult(
            spec=spec,
            ok=False,
            title=None,
            version=None,
            app_id=None,
            route_count=0,
            missing_routes=[],
            missing_prefixes=[],
            error=f"{type(exc).__name__}: {exc}",
        )


def check_entrypoints(entrypoints: list[str]) -> list[EntrypointResult]:
    """Check all configured entrypoints."""
    results: list[EntrypointResult] = []

    for index, spec in enumerate(entrypoints):
        results.append(check_entrypoint(spec, canonical=index == 0))

    canonical = results[0] if results else None
    if canonical and canonical.ok:
        for result in results[1:]:
            if result.ok and result.title != canonical.title:
                results[results.index(result)] = EntrypointResult(
                    spec=result.spec,
                    ok=False,
                    title=result.title,
                    version=result.version,
                    app_id=result.app_id,
                    route_count=result.route_count,
                    missing_routes=result.missing_routes,
                    missing_prefixes=result.missing_prefixes,
                    error=(
                        f"Compatibility entrypoint title {result.title!r} does not match "
                        f"canonical title {canonical.title!r}."
                    ),
                )

    return results


def render_text(results: list[EntrypointResult]) -> str:
    """Render human-readable check output."""
    lines = ["Runtime entrypoint check"]

    for result in results:
        status = "PASS" if result.ok else "FAIL"
        lines.append(f"- {status} {result.spec}")

        if result.title is not None:
            lines.append(f"  title: {result.title}")
        if result.version is not None:
            lines.append(f"  version: {result.version}")
        if result.route_count:
            lines.append(f"  route_count: {result.route_count}")
        if result.missing_routes:
            lines.append(f"  missing_routes: {', '.join(result.missing_routes)}")
        if result.missing_prefixes:
            lines.append(f"  missing_prefixes: {', '.join(result.missing_prefixes)}")
        if result.error:
            lines.append(f"  error: {result.error}")

    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify canonical and compatibility FastAPI runtime entrypoints."
    )
    parser.add_argument(
        "--entrypoint",
        action="append",
        dest="entrypoints",
        help=(
            "Entrypoint to verify in module:attribute form. "
            "May be supplied multiple times. Defaults to canonical and compatibility entrypoints."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    entrypoints = args.entrypoints or list(DEFAULT_ENTRYPOINTS)
    results = check_entrypoints(entrypoints)

    if args.json:
        print(json.dumps([asdict(result) for result in results], indent=2, sort_keys=True))
    else:
        print(render_text(results), end="")

    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
