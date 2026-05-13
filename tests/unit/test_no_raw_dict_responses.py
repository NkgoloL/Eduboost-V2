"""Guard production V2 routers against unenveloped raw dict responses.

Routers may satisfy the PR-002R envelope migration contract either by returning
explicit ``ok()`` / ``fail()`` / ``paginated()`` helpers or by using
``route_class=EnvelopedRoute`` on their ``APIRouter``. Non-router helper modules
inside ``app/api_v2_routers`` are ignored.
"""
from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTERS_DIR = REPO_ROOT / "app" / "api_v2_routers"
EXEMPT_COMMENT = "envelope-exempt"
ALLOWED_ENVELOPE_CALLS = {"ok", "fail", "paginated"}


def _is_api_router_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    return (isinstance(func, ast.Name) and func.id == "APIRouter") or (
        isinstance(func, ast.Attribute) and func.attr == "APIRouter"
    )


def _uses_enveloped_route(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if not _is_api_router_call(node):
            continue
        for keyword in node.keywords:
            if (
                keyword.arg == "route_class"
                and isinstance(keyword.value, ast.Name)
                and keyword.value.id == "EnvelopedRoute"
            ):
                return True
    return False


def _is_envelope_call(node: ast.expr) -> bool:
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name) and func.id in ALLOWED_ENVELOPE_CALLS:
            return True
        if isinstance(func, ast.Attribute) and func.attr in ALLOWED_ENVELOPE_CALLS:
            return True
    return False


def _collect_violations(source: str, filepath: Path) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    has_router = any(_is_api_router_call(node) for node in ast.walk(tree))
    if not has_router or _uses_enveloped_route(tree):
        return []

    violations: list[str] = []
    lines = source.splitlines()

    for node in ast.walk(tree):
        if not isinstance(node, ast.Return) or node.value is None:
            continue

        raw_line = lines[node.lineno - 1] if node.lineno - 1 < len(lines) else ""
        if EXEMPT_COMMENT in raw_line:
            continue

        if isinstance(node.value, ast.Dict):
            violations.append(
                f"{filepath.relative_to(REPO_ROOT)}:{node.lineno} - "
                "bare dict return without ok()/fail()/paginated() or EnvelopedRoute"
            )
            continue

        if isinstance(node.value, ast.Call) and _is_envelope_call(node.value):
            continue

    return violations


def _get_router_files() -> list[Path]:
    if not ROUTERS_DIR.exists():
        return []
    return sorted(ROUTERS_DIR.rglob("*.py"))


def test_no_raw_dict_responses_in_production_routers() -> None:
    all_violations: list[str] = []
    for filepath in _get_router_files():
        if filepath.name.startswith("_"):
            continue
        source = filepath.read_text(encoding="utf-8")
        all_violations.extend(_collect_violations(source, filepath))

    if all_violations:
        msg = (
            "\nRaw dict responses detected in production routers.\n"
            "Use ok(), fail(), paginated(), route_class=EnvelopedRoute, or "
            "add # envelope-exempt: <reason>.\n\n"
            + "\n".join(f"  {violation}" for violation in all_violations)
        )
        raise AssertionError(msg)