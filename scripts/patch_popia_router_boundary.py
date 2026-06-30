#!/usr/bin/env python3
from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "app/api_v2_routers/popia.py"
REPORT = ROOT / "docs/release/popia_router_boundary_repair_report.md"

DEP_IMPORT = (
    "from app.api_v2_deps.consent_lifecycle import "
    "authenticated_actor_id as _authenticated_actor_id, "
    "enforce_popia_learner_write as _enforce_popia_learner_write, "
    "get_canonical_consent_service\n"
)

REMOVE_EXACT_IMPORTS = {
    "import inspect",
    "from sqlalchemy.ext.asyncio import AsyncSession",
    "from app.core.database import get_db",
    "from app.repositories.consent_repository import ConsentRepository",
}


def _ensure_import(text: str, line: str) -> str:
    if "app.api_v2_deps.consent_lifecycle" in text:
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
    while insert_at < len(lines) and (lines[insert_at].startswith("import ") or lines[insert_at].startswith("from ")):
        insert_at += 1
    lines.insert(insert_at, line)
    return "".join(lines)


def _remove_import_lines(text: str) -> str:
    lines = []
    for line in text.splitlines(keepends=True):
        if line.strip() in REMOVE_EXACT_IMPORTS:
            continue
        lines.append(line)
    return "".join(lines)


def _remove_old_helper_block(text: str) -> str:
    marker = "# code_591_610_popia_consent_lifecycle_repair"
    idx = text.find(marker)
    if idx == -1:
        return text
    end = text.find("@router.", idx)
    if end == -1:
        return text
    return text[:idx] + text[end:]


def main() -> int:
    if not ROUTER.exists():
        raise SystemExit("Missing app/api_v2_routers/popia.py")

    text = ROUTER.read_text(encoding="utf-8")
    original = text
    text = _remove_old_helper_block(text)
    text = _remove_import_lines(text)
    text = _ensure_import(text, DEP_IMPORT)
    ast.parse(text)

    if text != original:
        ROUTER.write_text(text, encoding="utf-8")

    REPORT.write_text(
        "\n".join([
            "# POPIA Router Boundary Repair Report",
            "",
            f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
            "",
            "**Status:** implemented",
            "",
            "- Moved canonical consent service factory to `app/api_v2_deps/consent_lifecycle.py`.",
            "- Moved authenticated actor extraction to dependency module.",
            "- Moved POPIA learner-write wrapper to dependency module.",
            "- Removed direct `app.repositories` import from POPIA router.",
            "",
        ]),
        encoding="utf-8",
    )
    print(f"Patched {ROUTER.relative_to(ROOT)}")
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
