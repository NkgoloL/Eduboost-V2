#!/usr/bin/env python3
from __future__ import annotations

import ast
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "app/api_v2_routers/auth.py"
REPORT = ROOT / "docs/release/auth_forward_ref_repair_report.md"
BLOCKER = ROOT / "docs/release/auth_forward_ref_repair_blockers.md"

ALWAYS_CHECK = {
    "RegisterRequest",
    "LoginRequest",
    "RefreshTokenRequest",
    "DevSessionRequest",
    "TokenResponse",
}


def _module_for_path(path: Path) -> str:
    return ".".join(path.relative_to(ROOT).with_suffix("").parts)


def _write_blocker(lines: list[str]) -> None:
    BLOCKER.write_text(
        "\n".join(
            [
                "# Auth Forward-Reference Repair Blocker",
                "",
                f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
                "",
                *lines,
                "",
            ]
        ),
        encoding="utf-8",
    )


def _defined_or_imported_symbols(tree: ast.Module) -> set[str]:
    symbols: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                symbols.add(alias.asname or alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                symbols.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    symbols.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            symbols.add(node.target.id)
    return symbols


def _decorator_text(source: str, node: ast.AST) -> str:
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return ""
    lines = source.splitlines()
    chunks = []
    for decorator in node.decorator_list:
        start = decorator.lineno - 1
        end = decorator.end_lineno or decorator.lineno
        chunks.append("\n".join(lines[start:end]))
    return "\n".join(chunks)


def _annotation_names(annotation: ast.AST | None) -> set[str]:
    names: set[str] = set()
    if annotation is None:
        return names

    for child in ast.walk(annotation):
        if isinstance(child, ast.Name):
            names.add(child.id)
        elif isinstance(child, ast.Constant) and isinstance(child.value, str):
            names.update(re.findall(r"\b[A-Z][A-Za-z0-9_]+\b", child.value))
    return names


def _route_annotation_symbols(source: str, tree: ast.Module) -> set[str]:
    symbols: set[str] = set(ALWAYS_CHECK)
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        decorators = _decorator_text(source, node)
        if "router." not in decorators and "@router" not in decorators:
            continue

        for arg in [*node.args.args, *node.args.kwonlyargs]:
            symbols.update(_annotation_names(arg.annotation))
        symbols.update(_annotation_names(node.returns))
        symbols.update(re.findall(r"response_model\s*=\s*([A-Z][A-Za-z0-9_]+)", decorators))

    ignored = {
        "Annotated",
        "Depends",
        "Response",
        "Request",
        "BackgroundTasks",
        "AsyncSession",
        "Optional",
        "Union",
        "Any",
        "List",
        "Dict",
        "UUID",
    }
    return {name for name in symbols if name not in ignored and (name.endswith("Request") or name.endswith("Response"))}


def _find_symbol_module(symbol: str) -> str | None:
    candidates: list[Path] = []
    for base in (ROOT / "app").rglob("*.py"):
        if base == AUTH or base.name == "__init__.py":
            continue
        candidates.append(base)

    class_pattern = re.compile(rf"^\s*class\s+{re.escape(symbol)}\b", re.MULTILINE)
    assign_pattern = re.compile(rf"^\s*{re.escape(symbol)}\s*=", re.MULTILINE)

    for path in sorted(candidates):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if class_pattern.search(text) or assign_pattern.search(text):
            return _module_for_path(path)

    for path in sorted(candidates):
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = "/" + str(path.relative_to(ROOT))
        if re.search(rf"\b{re.escape(symbol)}\b", text) and "/schemas/" in rel:
            return _module_for_path(path)

    return None


def _ensure_import(text: str, module: str, symbols: list[str]) -> str:
    symbols = sorted(set(symbols))
    if not symbols:
        return text

    lines = text.splitlines(keepends=True)
    import_prefix = f"from {module} import "
    for idx, line in enumerate(lines):
        if line.startswith(import_prefix):
            existing = [part.strip() for part in line[len(import_prefix):].strip().split(",") if part.strip()]
            merged = sorted(set(existing + symbols))
            lines[idx] = import_prefix + ", ".join(merged) + "\n"
            return "".join(lines)

    insert_at = 0
    if lines and lines[0].startswith('"""'):
        insert_at = 1
        while insert_at < len(lines) and '"""' not in lines[insert_at]:
            insert_at += 1
        insert_at = min(insert_at + 1, len(lines))

    if insert_at < len(lines) and lines[insert_at].startswith("from __future__"):
        insert_at += 1

    while insert_at < len(lines) and (lines[insert_at].startswith("import ") or lines[insert_at].startswith("from ")):
        insert_at += 1

    lines.insert(insert_at, import_prefix + ", ".join(symbols) + "\n")
    return "".join(lines)


def main() -> int:
    if not AUTH.exists():
        _write_blocker(["Missing `app/api_v2_routers/auth.py`."])
        return 1

    source = AUTH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    defined = _defined_or_imported_symbols(tree)
    needed = _route_annotation_symbols(source, tree)
    missing = sorted(symbol for symbol in needed if symbol not in defined and symbol in source)

    imports_by_module: dict[str, list[str]] = {}
    unresolved: list[str] = []
    for symbol in missing:
        module = _find_symbol_module(symbol)
        if module is None:
            unresolved.append(symbol)
        else:
            imports_by_module.setdefault(module, []).append(symbol)

    if unresolved:
        _write_blocker(
            [
                "Could not locate module definitions for the following auth route model symbols:",
                "",
                *[f"- `{symbol}`" for symbol in unresolved],
                "",
                "Define or import these models before FastAPI route decorators execute.",
            ]
        )
        print("Unresolved auth route symbols:", ", ".join(unresolved))
        return 1

    updated = source
    for module, symbols in sorted(imports_by_module.items()):
        updated = _ensure_import(updated, module, symbols)

    ast.parse(updated)
    if updated != source:
        AUTH.write_text(updated, encoding="utf-8")

    REPORT.write_text(
        "\n".join(
            [
                "# Auth Forward-Reference Repair Report",
                "",
                f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
                "",
                "**Status:** implemented",
                "",
                "## Missing route annotation symbols repaired",
                "",
                *(f"- `{symbol}`" for symbol in missing),
                "",
                "## Imports added",
                "",
                *[
                    f"- `from {module} import {', '.join(sorted(symbols))}`"
                    for module, symbols in sorted(imports_by_module.items())
                ],
                "",
                "## Purpose",
                "",
                "FastAPI/Pydantic route registration must resolve request/response model symbols from auth.py globals during app import.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    if BLOCKER.exists():
        BLOCKER.unlink()

    print(f"Patched {AUTH.relative_to(ROOT)}")
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
