#!/usr/bin/env python3
"""
scripts/generate_dep_graph.py
------------------------------
Generates a Mermaid dependency graph of all first-party module imports
inside the `app/` directory.

Outputs a Mermaid `graph TD` block to stdout (pipe to a .md file).

Usage
-----
    python scripts/generate_dep_graph.py > docs/module_dependency_graph.md
    python scripts/generate_dep_graph.py --format dot   # Graphviz DOT
    python scripts/generate_dep_graph.py --format json  # adjacency JSON

Only intra-app imports are tracked (i.e. `from app.X import Y` or
`import app.X.Y`). Third-party and stdlib imports are ignored.
"""

from __future__ import annotations

import ast
import json
import sys
from collections import defaultdict
from pathlib import Path

APP_ROOT = Path("app")
PACKAGE_PREFIX = "app"


def module_label(mod: str) -> str:
    """Shorten 'app.api_v2_routers.auth' → 'routers/auth'."""
    parts = mod.split(".")
    if len(parts) <= 2:
        return ".".join(parts[1:]) or parts[0]
    # e.g. app.api_v2_routers.auth → routers/auth
    label = "/".join(parts[1:])
    label = label.replace("api_v2_routers", "routers")
    return label


def path_to_module(path: Path) -> str:
    parts = list(path.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def collect_imports(path: Path, source_module: str) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return []

    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith(PACKAGE_PREFIX):
                    imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith(PACKAGE_PREFIX):
                imports.append(node.module)
            elif node.level and node.module:
                # Relative import — resolve against source_module
                base_parts = source_module.split(".")[: -node.level]
                resolved = ".".join(base_parts + [node.module])
                if resolved.startswith(PACKAGE_PREFIX):
                    imports.append(resolved)
    return imports


def build_graph() -> dict[str, set[str]]:
    graph: dict[str, set[str]] = defaultdict(set)
    for path in sorted(APP_ROOT.rglob("*.py")):
        mod = path_to_module(path)
        deps = collect_imports(path, mod)
        for dep in deps:
            if dep != mod:
                graph[mod].add(dep)
    return graph


def to_mermaid(graph: dict[str, set[str]]) -> str:
    lines = ["# Module Dependency Graph", "", "```mermaid", "graph TD"]
    seen_edges: set[tuple[str, str]] = set()
    for source, targets in sorted(graph.items()):
        for target in sorted(targets):
            edge = (source, target)
            if edge in seen_edges:
                continue
            seen_edges.add(edge)
            src_label = module_label(source)
            tgt_label = module_label(target)
            # Sanitise Mermaid node IDs (no dots)
            src_id = source.replace(".", "_")
            tgt_id = target.replace(".", "_")
            lines.append(f'    {src_id}["{src_label}"] --> {tgt_id}["{tgt_label}"]')
    lines += ["```", "", "_Generated from `app/` source tree by `scripts/generate_dep_graph.py`_"]
    return "\n".join(lines)


def to_dot(graph: dict[str, set[str]]) -> str:
    lines = ["digraph app {", '    rankdir="LR";']
    seen: set[tuple[str, str]] = set()
    for source, targets in sorted(graph.items()):
        for target in sorted(targets):
            if (source, target) not in seen:
                seen.add((source, target))
                lines.append(f'    "{source}" -> "{target}";')
    lines.append("}")
    return "\n".join(lines)


def main() -> int:
    fmt = "mermaid"
    for arg in sys.argv[1:]:
        if arg.startswith("--format="):
            fmt = arg.split("=", 1)[1]

    if not APP_ROOT.exists():
        print(f"ERROR: {APP_ROOT} not found. Run from repository root.", file=sys.stderr)
        return 1

    graph = build_graph()

    if fmt == "mermaid":
        print(to_mermaid(graph))
    elif fmt == "dot":
        print(to_dot(graph))
    elif fmt == "json":
        print(json.dumps({k: sorted(v) for k, v in graph.items()}, indent=2))
    else:
        print(f"Unknown format: {fmt}. Choose mermaid | dot | json.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
