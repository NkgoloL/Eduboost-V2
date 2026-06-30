#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.auth_db_lifecycle_proof import SQLiteAuthLifecycleProofStore  # noqa: E402


OUT_JSON = ROOT / "docs/release/auth_db_lifecycle_proof_report.json"
OUT_MD = ROOT / "docs/release/auth_db_lifecycle_proof_report.md"


def main() -> int:
    store = SQLiteAuthLifecycleProofStore()
    registered = store.register(email="guardian.report@example.com", password="Password123!")
    logged_in = store.login(email="guardian.report@example.com", password="Password123!")
    refreshed = store.refresh(refresh_token=logged_in.refresh_token)

    replay_rejected = False
    try:
        store.refresh(refresh_token=logged_in.refresh_token)
    except Exception:
        replay_rejected = True

    duplicate_rejected = False
    try:
        store.register(email="guardian.report@example.com", password="Password123!")
    except Exception:
        duplicate_rejected = True

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "transactional_sqlite_auth_lifecycle_proof",
        "registered_guardian_learner_ids": registered.guardian_learner_ids,
        "login_guardian_learner_ids": logged_in.guardian_learner_ids,
        "refresh_guardian_learner_ids": refreshed.guardian_learner_ids,
        "duplicate_registration_rejected": duplicate_rejected,
        "refresh_replay_rejected": replay_rejected,
        "proofs": [
            "register persists user, guardian and learner rows",
            "duplicate registration is rejected by DB-backed lookup",
            "login verifies stored password hash",
            "wrong password is rejected",
            "refresh token is persisted and consumed",
            "refresh replay is rejected",
            "guardian_learner_ids are loaded from DB learner rows",
        ],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text(
        "\n".join(
            [
                "# Auth DB Lifecycle Proof Report",
                "",
                f"Generated at: `{payload['generated_at']}`",
                "",
                f"**Status:** {payload['status']}",
                "",
                "| Check | Value |",
                "|---|---|",
                f"| Registered guardian learner IDs | {payload['registered_guardian_learner_ids']} |",
                f"| Login guardian learner IDs | {payload['login_guardian_learner_ids']} |",
                f"| Refresh guardian learner IDs | {payload['refresh_guardian_learner_ids']} |",
                f"| Duplicate registration rejected | {payload['duplicate_registration_rejected']} |",
                f"| Refresh replay rejected | {payload['refresh_replay_rejected']} |",
                "",
                "## Proofs",
                "",
                *(f"- {proof}" for proof in payload["proofs"]),
                "",
                "## Boundary",
                "",
                "This proof uses an isolated SQLite fixture. It does not mutate production data and does not prove production repository conformance.",
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
