from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
POPIA_ROUTER = ROOT / "app/api_v2_routers/popia.py"
LEGACY_SERVICE = ROOT / "app/services/consent_service.py"

LIFECYCLE_TOKENS = ("grant_consent", "deny_consent", "withdraw_consent", "renew_consent")


def _source() -> str:
    return POPIA_ROUTER.read_text(encoding="utf-8")


def _tree() -> ast.Module:
    return ast.parse(_source())


def _lifecycle_functions() -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [
        node
        for node in ast.walk(_tree())
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and any(token in node.name for token in LIFECYCLE_TOKENS)
    ]


def _block(node: ast.AST) -> str:
    lines = _source().splitlines()
    return "\n".join(lines[node.lineno - 1:(node.end_lineno or node.lineno)])


def test_popia_router_uses_canonical_consent_service_not_deprecated_service():
    src = _source()
    assert "app.services.consent_service" not in src
    assert "app.modules.consent.service" in src
    assert "get_canonical_consent_service" in src


def test_popia_router_has_no_generated_actor_uuid_dependency():
    src = _source()
    assert "Depends(lambda: uuid.uuid4())" not in src
    assert "uuid.uuid4()" not in "\n".join(_block(node) for node in _lifecycle_functions())


def test_popia_lifecycle_routes_use_authenticated_current_user():
    functions = _lifecycle_functions()
    assert len(functions) == 4, f"Expected 4 lifecycle functions, found {len(functions)}"
    for node in functions:
        args = [arg.arg for arg in node.args.args + node.args.kwonlyargs]
        assert "current_user" in args, f"{node.name} must depend on current_user"
        block = _block(node)
        assert "_authenticated_actor_id(current_user)" in block, f"{node.name} must derive actor from current_user"


def test_popia_lifecycle_routes_enforce_learner_write():
    for node in _lifecycle_functions():
        block = _block(node)
        assert "_enforce_popia_learner_write(current_user, body.learner_id)" in block, (
            f"{node.name} must enforce learner write access before lifecycle mutation"
        )


def test_legacy_consent_service_is_marked_deprecated_without_import_warning():
    if not LEGACY_SERVICE.exists():
        return
    src = LEGACY_SERVICE.read_text(encoding="utf-8")
    assert "DEPRECATED: This asyncpg-style consent service is no longer wired to FastAPI v2 routers." in src
    assert "warnings.warn(" not in src[:800], "Do not emit import-time DeprecationWarning"
