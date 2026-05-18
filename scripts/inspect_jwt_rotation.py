#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECURITY = ROOT / "app/core/security.py"
AUTH_ROUTER = ROOT / "app/api_v2_routers/auth.py"
OUT_JSON = ROOT / "docs/security/jwt_rotation_introspection.json"
OUT_MD = ROOT / "docs/security/jwt_rotation_introspection.md"


def function_names(path: Path) -> list[str]:
    if not path.exists():
        return []
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return sorted(node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)))


def main() -> int:
    security_text = SECURITY.read_text(encoding="utf-8") if SECURITY.exists() else ""
    auth_text = AUTH_ROUTER.read_text(encoding="utf-8") if AUTH_ROUTER.exists() else ""
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "security_exists": SECURITY.exists(),
        "auth_router_exists": AUTH_ROUTER.exists(),
        "security_functions": function_names(SECURITY),
        "jwt_encode_count_security": security_text.count("jwt.encode("),
        "jwt_decode_count_security": security_text.count("jwt.decode("),
        "jwt_keyring_imported_security": "app.services.jwt_keyring" in security_text,
        "jwt_keyring_imported_auth": "app.services.jwt_keyring" in auth_text,
        "kid_header_reference_count": security_text.count("current_jwt_headers") + auth_text.count("current_jwt_headers"),
        "decode_keyring_reference_count": security_text.count("decode_jwt_with_keyring") + auth_text.count("decode_jwt_with_keyring"),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text(
        "\n".join([
            "# JWT Rotation Introspection",
            "",
            f"Generated at: `{payload['generated_at']}`",
            "",
            "| Check | Value |",
            "|---|---|",
            f"| security.py exists | {payload['security_exists']} |",
            f"| auth.py exists | {payload['auth_router_exists']} |",
            f"| jwt.encode count in security.py | {payload['jwt_encode_count_security']} |",
            f"| jwt.decode count in security.py | {payload['jwt_decode_count_security']} |",
            f"| jwt keyring imported in security.py | {payload['jwt_keyring_imported_security']} |",
            f"| kid header references | {payload['kid_header_reference_count']} |",
            f"| decode keyring references | {payload['decode_keyring_reference_count']} |",
            "",
        ]),
        encoding="utf-8",
    )
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
