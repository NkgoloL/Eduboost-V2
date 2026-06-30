#!/usr/bin/env python3
from __future__ import annotations

import ast
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECURITY = ROOT / "app/core/security.py"
REPORT = ROOT / "docs/security/jwt_rotation_repair_report.md"
BLOCKER = ROOT / "docs/security/jwt_rotation_repair_blockers.md"
IMPORT_LINE = (
    "from app.services.jwt_keyring import "
    "current_jwt_algorithm, current_jwt_headers, current_jwt_signing_key, decode_jwt_with_keyring\n"
)


def _write_blocker(message: str) -> None:
    BLOCKER.write_text(
        "\n".join([
            "# JWT Rotation Repair Blocker",
            "",
            f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
            "",
            message,
            "",
        ]),
        encoding="utf-8",
    )


def _ensure_import(text: str) -> str:
    if "app.services.jwt_keyring" in text:
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


def _patch_encode_calls(text: str) -> tuple[str, int]:
    pattern = re.compile(
        r"jwt\.encode\(\s*(?P<payload>[^,\n)]+)\s*,\s*(?P<key>[^,\n)]+)\s*,\s*algorithm\s*=\s*(?P<algorithm>[^,\n)]+)\s*\)"
    )
    count = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal count
        if "current_jwt_signing_key" in match.group(0):
            return match.group(0)
        count += 1
        payload = match.group("payload").strip()
        algorithm = match.group("algorithm").strip()
        return (
            f"jwt.encode({payload}, current_jwt_signing_key(), "
            f"algorithm=current_jwt_algorithm({algorithm}), headers=current_jwt_headers())"
        )

    return pattern.sub(repl, text), count


def _patch_decode_calls(text: str) -> tuple[str, int]:
    pattern = re.compile(
        r"jwt\.decode\(\s*(?P<token>[^,\n)]+)\s*,\s*(?P<key>[^,\n)]+)\s*,\s*algorithms\s*=\s*(?P<algorithms>[^)\n]+)\)"
    )
    count = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal count
        if "decode_jwt_with_keyring" in match.group(0):
            return match.group(0)
        count += 1
        token = match.group("token").strip()
        return f"decode_jwt_with_keyring({token})"

    return pattern.sub(repl, text), count


def main() -> int:
    if not SECURITY.exists():
        _write_blocker("Missing `app/core/security.py`; cannot patch JWT rotation.")
        return 1

    text = SECURITY.read_text(encoding="utf-8")
    original = text
    text = _ensure_import(text)
    text, encode_patches = _patch_encode_calls(text)
    text, decode_patches = _patch_decode_calls(text)
    ast.parse(text)
    SECURITY.write_text(text, encoding="utf-8")

    if encode_patches == 0 and "current_jwt_headers" not in original:
        _write_blocker(
            "No recognizable `jwt.encode(payload, secret, algorithm=...)` call found in `app/core/security.py`. "
            "Key-ring helper installed, but token encoding must be patched manually."
        )
        print("No recognizable jwt.encode call found; wrote blocker report.")

    REPORT.write_text(
        "\n".join([
            "# JWT Rotation Repair Report",
            "",
            f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
            "",
            "**Status:** implemented" if encode_patches or "current_jwt_headers" in text else "**Status:** helper-only",
            "",
            f"- Encode call patches: `{encode_patches}`",
            f"- Decode call patches: `{decode_patches}`",
            "- Key-ring helper: `app/services/jwt_keyring.py`",
            "- Current JWTs should include `kid` headers where patched.",
            "",
        ]),
        encoding="utf-8",
    )
    if BLOCKER.exists() and encode_patches:
        BLOCKER.unlink()
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
