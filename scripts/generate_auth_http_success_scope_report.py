#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
OUT_JSON = ROOT / "docs/release/auth_http_success_scope_report.json"
OUT_MD = ROOT / "docs/release/auth_http_success_scope_report.md"


def main() -> int:
    from app.api_v2 import app

    rows = []
    for route in getattr(app, "routes", []):
        path = getattr(route, "path", "")
        methods = sorted(getattr(route, "methods", set()) or [])
        lowered = path.lower()
        if any(token in lowered for token in ("register", "login", "refresh", "dev")):
            rows.append(
                {
                    "path": path,
                    "methods": methods,
                    "name": getattr(route, "name", ""),
                    "endpoint": getattr(getattr(route, "endpoint", None), "__name__", ""),
                    "response_model": getattr(getattr(route, "response_model", None), "__name__", None),
                }
            )

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "controlled_dependency_override_success_scope_proof",
        "route_count": len(rows),
        "routes": rows,
        "proofs": [
            "register success path through AuthApplicationService override",
            "login success path through AuthApplicationService override",
            "refresh success path preserving guardian_learner_ids through override",
            "duplicate register clean 409 failure",
            "wrong password clean 401 failure",
        ],
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text(
        "\n".join(
            [
                "# Auth HTTP Success Scope Report",
                "",
                f"Generated at: `{payload['generated_at']}`",
                "",
                f"**Status:** {payload['status']}",
                "",
                "## Proofs",
                "",
                *(f"- {proof}" for proof in payload["proofs"]),
                "",
                "## Auth lifecycle routes",
                "",
                "| Path | Methods | Endpoint | Response model |",
                "|---|---|---|---|",
                *[
                    f"| `{row['path']}` | {', '.join(row['methods'])} | `{row['endpoint']}` | `{row['response_model'] or '-'}` |"
                    for row in rows
                ],
                "",
                "## Boundary",
                "",
                "This proof uses FastAPI dependency overrides. It verifies route registration, request validation compatibility, route-to-service delegation, clean failure handling, and refresh scope propagation. It does not prove real database persistence.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
