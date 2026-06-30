#!/usr/bin/env python3
"""Fail closed when the Content Factory registry is unavailable or inconsistent."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.services.content_scope_registry import ContentScopeRegistry


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    registry = ContentScopeRegistry()
    scopes = registry.list_scopes()
    active = registry.list_active_scopes()
    targets = sum(len(registry.get_scope_targets(scope.scope_id)) for scope in scopes)
    result = {
        "scopes": len(scopes),
        "active_scopes": len(active),
        "targets": targets,
        "scopes_path": str(registry.scopes_path),
        "targets_path": str(registry.targets_path),
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("Content Factory registry OK")
        for key, value in result.items():
            print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
