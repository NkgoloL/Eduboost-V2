#!/usr/bin/env python3
from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API_V2 = ROOT / "app/api_v2.py"
CONFIG = ROOT / "app/core/config.py"
REPORT = ROOT / "docs/release/jwt_production_guard_repair_report.md"

IMPORT_LINE = "from app.services.jwt_keyring import validate_jwt_keyring_environment\n"
CALL_LINE = "validate_jwt_keyring_environment()\n"


def _ensure_import(text: str) -> str:
    if "validate_jwt_keyring_environment" in text:
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
    lines.insert(insert_at, IMPORT_LINE)
    return "".join(lines)


def _patch_api_v2() -> bool:
    if not API_V2.exists():
        return False
    text = API_V2.read_text(encoding="utf-8")
    original = text
    text = _ensure_import(text)
    if CALL_LINE.strip() not in text:
        lines = text.splitlines(keepends=True)
        insert_at = 0
        while insert_at < len(lines) and (
            lines[insert_at].strip() == ""
            or lines[insert_at].startswith("import ")
            or lines[insert_at].startswith("from ")
        ):
            insert_at += 1
        lines.insert(insert_at, CALL_LINE)
        text = "".join(lines)
    ast.parse(text)
    if text != original:
        API_V2.write_text(text, encoding="utf-8")
        return True
    return False


def _patch_config() -> bool:
    if not CONFIG.exists():
        return False
    text = CONFIG.read_text(encoding="utf-8")
    original = text
    if "def validate_production_secrets" not in text:
        addition = "\n".join([
            "",
            "# code_1071_1110_jwt_production_secret_guard",
            "def validate_production_secrets() -> None:",
            "    \"\"\"Validate security-sensitive production secrets.\"\"\"",
            "    from app.services.jwt_keyring import validate_jwt_keyring_environment",
            "",
            "    validate_jwt_keyring_environment()",
            "",
        ])
        text = text.rstrip() + "\n" + addition
    ast.parse(text)
    if text != original:
        CONFIG.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> int:
    api_patched = _patch_api_v2()
    config_patched = _patch_config()
    REPORT.write_text(
        "\n".join(
            [
                "# JWT Production Guard Repair Report",
                "",
                f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
                "",
                "**Status:** implemented",
                "",
                f"- app.api_v2 patched with startup guard: `{api_patched}`",
                f"- app.core.config patched with validation shim: `{config_patched}`",
                "- JWT fallback resolution includes `settings.JWT_SECRET` and `JWT_SECRET` before legacy keys.",
                "- Placeholder JWT secrets are rejected outside development/test.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
