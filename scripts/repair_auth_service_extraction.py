#!/usr/bin/env python3
from __future__ import annotations

import ast
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "app/api_v2_routers/auth.py"
IMPORT_LINE = "from app.api_v2_deps.auth_service import AuthApplicationService, get_auth_application_service\n"
REPORT = ROOT / "docs/release/auth_service_extraction_repair_report.md"
BLOCKER = ROOT / "docs/release/auth_service_extraction_repair_blockers.md"

REPOSITORY_NAMES = (
    "UserRepository",
    "GuardianRepository",
    "LearnerRepository",
    "ConsentRepository",
    "AuditRepository",
    "RefreshTokenRepository",
    "PasswordResetRepository",
)

REPO_ATTRS = {
    "UserRepository": "user_repo",
    "GuardianRepository": "guardian_repo",
    "LearnerRepository": "learner_repo",
    "ConsentRepository": "consent_repo",
    "AuditRepository": "audit_repo",
    "RefreshTokenRepository": "refresh_token_repo",
    "PasswordResetRepository": "password_reset_repo",
}


def _write_blocker(message: str) -> None:
    BLOCKER.write_text(
        "\n".join(
            [
                "# Auth Service Extraction Repair Blocker",
                "",
                f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
                "",
                message,
                "",
            ]
        ),
        encoding="utf-8",
    )


def _ensure_import(text: str, import_line: str) -> str:
    module = import_line.split(" import ", 1)[0].replace("from ", "")
    if import_line.strip() in text or module in text:
        return text

    lines = text.splitlines(keepends=True)
    insert_at = 0
    if lines and lines[0].startswith('"""'):
        insert_at = 1
        while insert_at < len(lines) and '"""' not in lines[insert_at]:
            insert_at += 1
        insert_at = min(insert_at + 1, len(lines))

    # Do not add future annotations to auth.py. If present, leave the user's
    # explicit fix intact elsewhere; this script will later fail the invariant.
    while insert_at < len(lines) and (lines[insert_at].startswith("import ") or lines[insert_at].startswith("from ")):
        insert_at += 1

    lines.insert(insert_at, import_line)
    return "".join(lines)


def _replace_repository_constructors(text: str) -> str:
    for repo_name, attr in REPO_ATTRS.items():
        text = re.sub(rf"\b{repo_name}\(\s*(?:db|session|database)\s*\)", f"auth_service.{attr}", text)
        text = re.sub(rf"\b{repo_name}\(\s*\)", f"auth_service.{attr}", text)
    return text


def _remove_repository_import_symbols(text: str) -> str:
    lines = []
    for line in text.splitlines(keepends=True):
        if not line.strip().startswith("from app.repositories"):
            lines.append(line)
            continue

        if not any(name in line for name in REPOSITORY_NAMES):
            lines.append(line)
            continue

        before, names_text = line.split("import", 1)
        kept = [
            name.strip()
            for name in names_text.split(",")
            if name.strip() and name.strip() not in REPOSITORY_NAMES
        ]
        if kept:
            lines.append(before + "import " + ", ".join(kept) + "\n")
    return "".join(lines)


def _function_needs_auth_service(block: str) -> bool:
    return "auth_service." in block


def _patch_function_signatures(text: str) -> str:
    tree = ast.parse(text)
    lines = text.splitlines()
    insertions: list[tuple[int, str]] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or not node.body:
            continue

        block = "\n".join(lines[node.lineno - 1:(node.end_lineno or node.lineno)])
        if not _function_needs_auth_service(block):
            continue

        args = [arg.arg for arg in node.args.args + node.args.kwonlyargs]
        if "auth_service" in args:
            continue

        param = "auth_service: AuthApplicationService = Depends(get_auth_application_service)"
        header_start = node.lineno - 1
        body_start = node.body[0].lineno - 1

        if body_start == header_start + 1:
            lines[header_start] = re.sub(r"\)\s*(->[^:]+)?:", rf", {param})\1:", lines[header_start], count=1)
            continue

        for idx in range(body_start - 1, header_start - 1, -1):
            if lines[idx].strip().endswith(":"):
                indent = re.match(r"^(\s*)", lines[idx]).group(1)
                # Existing multiline params normally end with comma before close.
                insertions.append((idx, f"{indent}    {param},"))
                break

    for idx, line in sorted(insertions, reverse=True):
        lines[idx:idx] = [line]

    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def _remove_auth_import_linter_allowances() -> list[str]:
    path = ROOT / ".importlinter"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    original = text
    lines = []
    removed = []
    for line in text.splitlines(keepends=True):
        if "app.api_v2_routers.auth" in line and "app.repositories" in line:
            removed.append(line.strip())
            continue
        lines.append(line)
    text = "".join(lines)
    if text != original:
        path.write_text(text, encoding="utf-8")
    return removed


def main() -> int:
    if not AUTH.exists():
        _write_blocker("Missing app/api_v2_routers/auth.py")
        return 1

    text = AUTH.read_text(encoding="utf-8")
    original = text

    text = _ensure_import(text, IMPORT_LINE)
    text = _replace_repository_constructors(text)
    text = _patch_function_signatures(text)
    text = _remove_repository_import_symbols(text)

    ast.parse(text)

    remaining_constructors = [name for name in REPOSITORY_NAMES if f"{name}(" in text]
    remaining_imports = [line.strip() for line in text.splitlines() if line.strip().startswith("from app.repositories")]

    if remaining_constructors or remaining_imports:
        _write_blocker(
            "Repository boundary not fully closed.\n\n"
            f"Remaining constructors: {remaining_constructors}\n\n"
            f"Remaining repository imports: {remaining_imports}\n"
        )
        print("Auth repository boundary blockers remain; see blocker report.")
        return 1

    if "from __future__ import annotations" in text:
        _write_blocker("auth.py still contains `from __future__ import annotations`, which can reintroduce FastAPI/Pydantic forward-ref failures.")
        print("auth.py still contains future annotations.")
        return 1

    if text != original:
        AUTH.write_text(text, encoding="utf-8")

    removed_allowances = _remove_auth_import_linter_allowances()

    REPORT.write_text(
        "\n".join(
            [
                "# Auth Service Extraction Repair Report",
                "",
                f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
                "",
                "**Status:** implemented",
                "",
                "## Implemented",
                "",
                "- Added `app/services/auth_application_service.py`.",
                "- Added `app/api_v2_deps/auth_service.py`.",
                "- Replaced direct auth router repository constructors with `auth_service.<repo>` handles.",
                "- Removed direct `app.repositories` imports from `app/api_v2_routers/auth.py`.",
                "- Preserved `auth.py` eager route model evaluation by rejecting future annotations.",
                "",
                "## Import-linter allowances removed",
                "",
                *(f"- `{item}`" for item in removed_allowances),
                "",
                "## Remaining debt",
                "",
                "- Move auth business logic from router into AuthApplicationService methods in smaller semantic slices.",
                "- Add HTTP integration tests for register/login/refresh/dev-session with dependency overrides.",
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
