#!/usr/bin/env python3
"""Apply PRD-0.7 OpenAPI/generated artifact canonicalisation.

This script does not import the FastAPI app or regenerate API behavior. It treats
`docs/openapi.json` as the committed canonical contract and refreshes root-level
mirrors from that canonical artifact.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

CANONICAL_OPENAPI = Path("docs/openapi.json")
ROOT_OPENAPI_JSON = Path("openapi.json")
ROOT_OPENAPI_YAML = Path("openapi.yaml")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def render_json(schema: dict[str, Any]) -> str:
    return json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_yaml(schema: dict[str, Any]) -> str:
    """Render YAML when PyYAML is available; otherwise emit JSON-valid YAML."""
    try:
        import yaml  # type: ignore
    except Exception:
        return render_json(schema)
    return yaml.safe_dump(schema, allow_unicode=True, sort_keys=False)


def canonicalise(root: Path = Path("."), write: bool = False) -> dict[str, Any]:
    canonical_path = root / CANONICAL_OPENAPI
    root_json_path = root / ROOT_OPENAPI_JSON
    root_yaml_path = root / ROOT_OPENAPI_YAML
    if not canonical_path.exists():
        raise FileNotFoundError(f"missing canonical OpenAPI artifact: {CANONICAL_OPENAPI}")
    schema = read_json(canonical_path)
    canonical_text = canonical_path.read_text(encoding="utf-8")
    canonical_rendered = render_json(schema)
    json_changed = (not root_json_path.exists()) or root_json_path.read_text(encoding="utf-8") != canonical_text
    yaml_text = render_yaml(schema)
    yaml_changed = (not root_yaml_path.exists()) or root_yaml_path.read_text(encoding="utf-8") != yaml_text
    if write:
        root_json_path.write_text(canonical_text if canonical_text == canonical_rendered else canonical_rendered, encoding="utf-8")
        root_yaml_path.write_text(yaml_text, encoding="utf-8")
    return {
        "canonical_openapi_path": str(CANONICAL_OPENAPI),
        "root_openapi_json_path": str(ROOT_OPENAPI_JSON),
        "root_openapi_yaml_path": str(ROOT_OPENAPI_YAML),
        "root_json_changed": json_changed,
        "root_yaml_changed": yaml_changed,
        "openapi_path_count": len(schema.get("paths", {})),
        "openapi_operation_count": sum(len(value) for value in schema.get("paths", {}).values() if isinstance(value, dict)),
        "openapi_title": schema.get("info", {}).get("title"),
        "openapi_version": schema.get("info", {}).get("version"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = canonicalise(Path(args.root), write=args.write)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"OpenAPI canonicalisation checked. root_json_changed={result['root_json_changed']} root_yaml_changed={result['root_yaml_changed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
