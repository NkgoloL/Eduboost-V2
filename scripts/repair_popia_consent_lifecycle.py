#!/usr/bin/env python3
from __future__ import annotations

import ast
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "app/api_v2_routers/popia.py"
DEPRECATED_SERVICE = ROOT / "app/services/consent_service.py"
REPORT = ROOT / "docs/release/popia_consent_lifecycle_repair_report.md"
BLOCKER = ROOT / "docs/release/popia_consent_lifecycle_repair_blockers.md"

MARKER = "# code_591_610_popia_consent_lifecycle_repair"
LIFECYCLE_NAME_TOKENS = ("grant_consent", "deny_consent", "withdraw_consent", "renew_consent")
CURRENT_USER_CANDIDATES = [
    "app.core.security",
    "app.core.dependencies",
    "app.security.dependencies",
    "app.modules.auth.dependencies",
    "app.api_v2_routers.auth",
]
LEARNER_WRITE_CANDIDATES = [
    ("app.core.authorization", "require_learner_write_for_current_user"),
    ("app.core.authorization", "require_learner_write"),
    ("app.security.dependencies", "require_learner_write_for_current_user"),
    ("app.security.dependencies", "require_learner_write"),
    ("app.core.dependencies", "require_learner_write_for_current_user"),
    ("app.core.dependencies", "require_learner_write"),
]


def _write_blocker(message: str) -> None:
    BLOCKER.write_text(
        "\n".join([
            "# POPIA Consent Lifecycle Repair Blocker",
            "",
            f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
            "",
            message,
            "",
        ]),
        encoding="utf-8",
    )


def _path_for_module(module: str) -> Path:
    return ROOT / (module.replace(".", "/") + ".py")


def _module_has_symbol(module: str, symbol: str) -> bool:
    path = _path_for_module(module)
    if not path.exists():
        return False
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == symbol:
            return True
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == symbol:
                    return True
    return False


def _find_get_current_user() -> str:
    for module in CURRENT_USER_CANDIDATES:
        if _module_has_symbol(module, "get_current_user"):
            return module
    for path in (ROOT / "app").rglob("*.py"):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "get_current_user":
                return ".".join(path.relative_to(ROOT).with_suffix("").parts)
    raise RuntimeError("Could not locate get_current_user in app. Add/confirm the auth dependency before running this repair.")


def _find_learner_write_symbol() -> tuple[str, str]:
    for module, symbol in LEARNER_WRITE_CANDIDATES:
        if _module_has_symbol(module, symbol):
            return module, symbol
    for path in (ROOT / "app").rglob("*.py"):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in {
                "require_learner_write_for_current_user",
                "require_learner_write",
            }:
                return ".".join(path.relative_to(ROOT).with_suffix("").parts), node.name
    raise RuntimeError("Could not locate require_learner_write_for_current_user or require_learner_write in app.")


def _ensure_import(text: str, import_line: str) -> str:
    if import_line.strip() in text:
        return text
    lines = text.splitlines(keepends=True)
    insert_at = 0
    if lines and lines[0].startswith('"""'):
        insert_at = 1
        while insert_at < len(lines) and '"""' not in lines[insert_at]:
            insert_at += 1
        insert_at = min(insert_at + 1, len(lines))
    if insert_at < len(lines) and lines[insert_at].startswith("from __future__"):
        insert_at += 1
    while insert_at < len(lines) and (
        lines[insert_at].startswith("import ") or lines[insert_at].startswith("from ")
    ):
        insert_at += 1
    lines.insert(insert_at, import_line if import_line.endswith("\n") else import_line + "\n")
    return "".join(lines)


def _replace_deprecated_service_import(text: str) -> str:
    return text.replace(
        "from app.services.consent_service import ConsentService",
        "from app.modules.consent.service import ConsentService",
    )


def _replace_generated_actor_dependencies(text: str) -> str:
    text = re.sub(
        r"actor_id\s*:\s*[^=,\n]+=\s*Depends\(\s*lambda\s*:\s*uuid\.uuid4\(\)\s*\)",
        "current_user = Depends(get_current_user)",
        text,
    )
    text = re.sub(
        r"actor_id\s*=\s*Depends\(\s*lambda\s*:\s*uuid\.uuid4\(\)\s*\)",
        "current_user = Depends(get_current_user)",
        text,
    )
    text = re.sub(
        r"actor_id\s*:\s*[^=,\n]+=\s*Depends\(\s*get_current_user\s*\)",
        "current_user = Depends(get_current_user)",
        text,
    )
    return text


def _insert_helper_block(text: str) -> str:
    if MARKER in text:
        return text

    helper = f"""
{MARKER}
def _authenticated_actor_id(current_user):
    # Return stable authenticated actor identity for POPIA audit events.
    if isinstance(current_user, dict):
        for key in ("id", "user_id", "sub"):
            value = current_user.get(key)
            if value:
                return value
    for attr in ("id", "user_id", "sub"):
        value = getattr(current_user, attr, None)
        if value:
            return value
    raise HTTPException(status_code=401, detail="Authenticated actor id is unavailable")


async def _enforce_popia_learner_write(current_user, learner_id):
    # Enforce learner write access while tolerating sync/async dependency helpers.
    try:
        result = require_learner_write_for_current_user(current_user, learner_id)
    except TypeError:
        try:
            result = require_learner_write_for_current_user(learner_id, current_user)
        except TypeError:
            result = require_learner_write_for_current_user(current_user=current_user, learner_id=learner_id)
    if inspect.isawaitable(result):
        return await result
    return result


def get_canonical_consent_service(db: AsyncSession = Depends(get_db)) -> ConsentService:
    # Construct the canonical SQLAlchemy-compatible consent service for FastAPI v2.
    params = inspect.signature(ConsentService).parameters
    if "session" in params:
        return ConsentService(session=db)
    if "db" in params:
        return ConsentService(db=db)
    if "consent_repository" in params or "consent_repo" in params:
        repo = ConsentRepository(db)
        if "consent_repository" in params:
            return ConsentService(consent_repository=repo)
        return ConsentService(consent_repo=repo)
    try:
        return ConsentService(db)
    except TypeError as exc:
        raise RuntimeError(
            "Cannot construct canonical ConsentService from AsyncSession. "
            "Align app.modules.consent.service.ConsentService constructor before using POPIA lifecycle routes."
        ) from exc

"""
    index = text.find("@router.")
    if index != -1:
        return text[:index] + helper + text[index:]
    return text.rstrip() + "\n\n" + helper


def _function_blocks(tree: ast.Module) -> list[ast.AsyncFunctionDef | ast.FunctionDef]:
    blocks = []
    for node in tree.body:
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)) and any(token in node.name for token in LIFECYCLE_NAME_TOKENS):
            blocks.append(node)
    return blocks


def _inject_authorization(text: str) -> str:
    tree = ast.parse(text)
    lines = text.splitlines()
    insertions: list[tuple[int, str]] = []

    for node in _function_blocks(tree):
        start = node.lineno
        end = node.end_lineno or node.lineno
        block = "\n".join(lines[start - 1:end])
        if "_enforce_popia_learner_write" in block and "_authenticated_actor_id" in block:
            continue

        if not node.body:
            continue

        arg_names = [arg.arg for arg in node.args.args + node.args.kwonlyargs]
        if "current_user" not in arg_names:
            raise RuntimeError(
                f"{node.name} does not have current_user dependency after generated actor replacement. "
                "Manual signature repair is required."
            )

        first = node.body[0]
        if isinstance(first, ast.Expr) and isinstance(getattr(first, "value", None), ast.Constant) and isinstance(first.value.value, str):
            insertion_line = (first.end_lineno or first.lineno)
        else:
            insertion_line = first.lineno - 1

        indent_match = re.match(r"^(\s*)", lines[first.lineno - 1])
        indent = indent_match.group(1) if indent_match else "    "
        snippet = (
            f"{indent}await _enforce_popia_learner_write(current_user, body.learner_id)\n"
            f"{indent}actor_id = _authenticated_actor_id(current_user)\n"
        )
        insertions.append((insertion_line, snippet))

    for line_no, snippet in sorted(insertions, reverse=True):
        lines[line_no:line_no] = snippet.rstrip("\n").splitlines()
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def _replace_consent_service_dependency(text: str) -> str:
    return re.sub(
        r":\s*ConsentService\s*=\s*Depends\([^)]*\)",
        ": ConsentService = Depends(get_canonical_consent_service)",
        text,
    )


def _mark_deprecated_service() -> None:
    if not DEPRECATED_SERVICE.exists():
        return
    text = DEPRECATED_SERVICE.read_text(encoding="utf-8")
    if "DEPRECATED: This asyncpg-style consent service is no longer wired to FastAPI v2 routers." in text:
        return
    marker = (
        "# DEPRECATED: This asyncpg-style consent service is no longer wired to FastAPI v2 routers.\n"
        "# Canonical consent service: app.modules.consent.service.ConsentService\n"
        "# This file will be removed after all call sites are migrated. See roadmap P0-01.\n"
        "# Do not emit an import-time DeprecationWarning here; tests may run with warnings as errors.\n\n"
    )
    DEPRECATED_SERVICE.write_text(marker + text, encoding="utf-8")


def main() -> int:
    if not ROUTER.exists():
        _write_blocker("Missing `app/api_v2_routers/popia.py`; cannot repair POPIA consent lifecycle.")
        return 1
    if not (ROOT / "app/modules/consent/service.py").exists():
        _write_blocker("Missing canonical `app/modules/consent/service.py`; cannot switch POPIA router.")
        return 1

    try:
        current_user_module = _find_get_current_user()
        learner_write_module, learner_write_symbol = _find_learner_write_symbol()
    except RuntimeError as exc:
        _write_blocker(str(exc))
        print(str(exc))
        return 1

    text = ROUTER.read_text(encoding="utf-8")
    original = text

    text = _replace_deprecated_service_import(text)
    text = _replace_generated_actor_dependencies(text)

    if "Depends(lambda: uuid.uuid4())" in text:
        _write_blocker(
            "Generated UUID dependency remains in `app/api_v2_routers/popia.py` after safe replacement. "
            "Review non-actor usage before continuing."
        )
        print("Generated UUID dependency remains after safe replacement.")
        return 1

    text = _ensure_import(text, "import inspect")
    text = _ensure_import(text, "from fastapi import Depends, HTTPException")
    text = _ensure_import(text, "from sqlalchemy.ext.asyncio import AsyncSession")
    text = _ensure_import(text, "from app.core.database import get_db")
    text = _ensure_import(text, "from app.repositories.consent_repository import ConsentRepository")
    text = _ensure_import(text, f"from {current_user_module} import get_current_user")

    if learner_write_symbol == "require_learner_write_for_current_user":
        text = _ensure_import(text, f"from {learner_write_module} import require_learner_write_for_current_user")
    else:
        text = _ensure_import(text, f"from {learner_write_module} import {learner_write_symbol} as require_learner_write_for_current_user")

    text = _insert_helper_block(text)
    text = _replace_consent_service_dependency(text)
    text = _inject_authorization(text)

    ast.parse(text)

    if text != original:
        ROUTER.write_text(text, encoding="utf-8")

    _mark_deprecated_service()

    REPORT.write_text(
        "\n".join([
            "# POPIA Consent Lifecycle Repair Report",
            "",
            f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
            "",
            "**Status:** implemented",
            "",
            "| Item | Value |",
            "|---|---|",
            f"| Router | `{ROUTER.relative_to(ROOT)}` |",
            "| Deprecated service import removed | true |",
            f"| get_current_user source | `{current_user_module}` |",
            f"| learner-write source | `{learner_write_module}.{learner_write_symbol}` |",
            "| Generated actor UUID dependencies removed | true |",
            "| Canonical ConsentService helper inserted | true |",
            "",
            "## Boundary",
            "",
            "This batch repairs POPIA consent lifecycle wiring and actor/learner-write enforcement only. "
            "Lesson object authorization and auth service extraction are handled by later batches.",
            "",
        ]),
        encoding="utf-8",
    )
    if BLOCKER.exists():
        BLOCKER.unlink()
    print(f"Patched {ROUTER.relative_to(ROOT)}")
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
