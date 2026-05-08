#!/usr/bin/env python3
"""Generate or verify the committed EduBoost V2 OpenAPI document.

Usage examples:
    python scripts/generate_openapi.py
    python scripts/generate_openapi.py --output docs/openapi.json
    python scripts/generate_openapi.py --check
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_APP = "app.api_v2:app"
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "openapi.json"


def _ensure_repo_root_on_path() -> None:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))


def load_app(spec: str) -> FastAPI:
    """Load a FastAPI app from a uvicorn-style ``module:attribute`` spec."""
    module_path, separator, attribute = spec.partition(":")
    if separator != ":":
        raise ValueError(f"Invalid ASGI app spec {spec!r}; expected 'module:attribute'.")

    _ensure_repo_root_on_path()
    module = importlib.import_module(module_path)
    app = getattr(module, attribute)

    if not isinstance(app, FastAPI):
        raise TypeError(f"{spec!r} did not resolve to a FastAPI application.")

    return app


def render_openapi(app: FastAPI) -> str:
    """Render deterministic OpenAPI JSON with a trailing newline."""
    schema: dict[str, Any] = app.openapi()
    return json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def write_openapi(output_path: Path, content: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def check_openapi(output_path: Path, content: str) -> bool:
    if not output_path.exists():
        print(f"OpenAPI file is missing: {output_path}", file=sys.stderr)
        return False

    existing = output_path.read_text(encoding="utf-8")
    if existing != content:
        print(
            f"OpenAPI drift detected: regenerate {output_path} with "
            "`python scripts/generate_openapi.py`.",
            file=sys.stderr,
        )
        return False

    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--app",
        default=DEFAULT_APP,
        help=f"ASGI app spec to import. Default: {DEFAULT_APP}",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output JSON path. Default: {DEFAULT_OUTPUT.relative_to(REPO_ROOT)}",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify the output file is current without modifying it.",
    )
    return parser.parse_args()


def _display_path(path: Path) -> str:
    """Return a readable output path for both repo-local and absolute paths."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def main() -> int:
    args = parse_args()
    output_path = args.output if args.output.is_absolute() else REPO_ROOT / args.output

    app = load_app(args.app)
    content = render_openapi(app)

    if args.check:
        return 0 if check_openapi(output_path, content) else 1

    write_openapi(output_path, content)
    print(f"Wrote OpenAPI schema to {_display_path(output_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
