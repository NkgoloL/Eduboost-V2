from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from app.services.lesson_authorization import iter_sync_lesson_ids


ROOT = Path(__file__).resolve().parents[2]
LESSONS_ROUTER = ROOT / "app/api_v2_routers/lessons.py"
MARKER_READ = "# code_611_630_lesson_read_authz"
MARKER_WRITE = "# code_611_630_lesson_write_authz"
MARKER_SYNC = "# code_611_630_lesson_sync_authz"


def src() -> str:
    return LESSONS_ROUTER.read_text(encoding="utf-8")


def tree() -> ast.Module:
    return ast.parse(src())


def args(node):
    return [arg.arg for arg in node.args.args + node.args.kwonlyargs]


def block(node):
    lines = src().splitlines()
    return "\n".join(lines[node.lineno - 1:(node.end_lineno or node.lineno)])


def test_lessons_router_imports_authorization_helper():
    text = src()
    assert "app.services.lesson_authorization" in text
    assert "require_lesson_read_access_for_current_user" in text
    assert "require_lesson_write_access_for_current_user" in text


def test_lesson_read_routes_enforce_owner_read_authorization():
    candidates = []
    for node in ast.walk(tree()):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            a = args(node)
            name = node.name.lower()
            if "lesson_id" in a and (name.startswith("get_") or name.startswith("read_")) and "complete" not in name:
                candidates.append(node)
    assert candidates, "Expected at least one lesson read route with lesson_id"
    for node in candidates:
        assert MARKER_READ in block(node)
        assert "require_lesson_read_access_for_current_user" in block(node)


def test_lesson_complete_routes_enforce_owner_write_authorization():
    candidates = []
    for node in ast.walk(tree()):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            a = args(node)
            name = node.name.lower()
            if "lesson_id" in a and any(token in name for token in ("complete", "finish", "submit_completion")):
                candidates.append(node)
    assert candidates, "Expected at least one lesson completion route with lesson_id"
    for node in candidates:
        assert MARKER_WRITE in block(node)
        assert "require_lesson_write_access_for_current_user" in block(node)


def test_lesson_sync_routes_validate_every_lesson_id_before_mutation():
    candidates = [
        node for node in ast.walk(tree())
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and "sync" in node.name.lower()
    ]
    assert candidates, "Expected at least one lesson sync route"
    for node in candidates:
        text = block(node)
        assert MARKER_SYNC in text
        assert "iter_sync_lesson_ids" in text
        assert "require_lesson_write_access_for_current_user" in text


@dataclass
class Event:
    lesson_id: str


@dataclass
class Payload:
    events: list[Event]


def test_iter_sync_lesson_ids_extracts_nested_dict_and_object_payloads():
    assert iter_sync_lesson_ids({"events": [{"lesson_id": "a"}, {"nested": {"lessonId": "b"}}]}) == ["a", "b"]
    assert iter_sync_lesson_ids(Payload(events=[Event(lesson_id="c")])) == ["c"]
