from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LESSONS_ROUTER = ROOT / "app/api_v2_routers/lessons.py"
LESSON_AUTH = ROOT / "app/services/lesson_authorization.py"


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _args(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    return [arg.arg for arg in node.args.args + node.args.kwonlyargs]


def _block(source: str, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    lines = source.splitlines()
    return "\n".join(lines[node.lineno - 1 : node.end_lineno or node.lineno])


def test_lesson_id_read_and_write_routes_authorize_before_service_mutation():
    source = _source(LESSONS_ROUTER)
    tree = ast.parse(source)

    read_routes = []
    write_routes = []
    sync_routes = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        name = node.name.lower()
        args = _args(node)
        block = _block(source, node)
        if "lesson_id" in args and name.startswith("get_"):
            read_routes.append(block)
        if "lesson_id" in args and "complete" in name:
            write_routes.append(block)
        if "sync" in name:
            sync_routes.append(block)

    assert read_routes, "expected a lesson read route"
    assert write_routes, "expected a lesson complete/write route"
    assert sync_routes, "expected a lesson sync route"

    for block in read_routes:
        assert block.index("require_lesson_read_access_for_current_user") < block.index("service.get_lesson_by_id")
    for block in write_routes:
        assert block.index("require_lesson_write_access_for_current_user") < block.index("service.get_lesson_by_id")
    for block in sync_routes:
        assert "iter_sync_lesson_ids" in block
        assert "require_lesson_write_access_for_current_user" in block


def test_lesson_authorization_no_longer_swallows_unexpected_repository_errors():
    source = _source(LESSON_AUTH)
    tree = ast.parse(source)
    lines = source.splitlines()
    owner_block = ""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "lesson_owner_learner_id":
            owner_block = "\n".join(lines[node.lineno - 1 : node.end_lineno or node.lineno])
            break

    assert owner_block
    assert "except Exception" not in owner_block
    assert "except (TypeError, AttributeError, RuntimeError, ValueError)" in owner_block
