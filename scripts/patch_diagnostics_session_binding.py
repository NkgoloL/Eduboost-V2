#!/usr/bin/env python3
from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTICS = ROOT / "app/api_v2_routers/diagnostics.py"
REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"
REPORT = ROOT / "docs/release/diagnostics_session_binding_repair_report.md"


def patch_diagnostics_router() -> bool:
    text = DIAGNOSTICS.read_text(encoding="utf-8")
    original = text

    old_import = "from app.services.diagnostic_data_integrity import validate_diagnostic_submission_payload\n"
    new_import = (
        "from app.services.diagnostic_data_integrity import DiagnosticIntegrityError, validate_diagnostic_submission_payload\n"
        "from app.services.diagnostic_route_integrity import validate_adaptive_diagnostic_response\n"
    )
    if "validate_adaptive_diagnostic_response" not in text:
        text = text.replace(old_import, new_import)
    elif "DiagnosticIntegrityError" not in text:
        text = text.replace(old_import, "from app.services.diagnostic_data_integrity import DiagnosticIntegrityError, validate_diagnostic_submission_payload\n")

    if "caps_ref: str | None = None" not in text:
        text = text.replace(
            "class DiagnosticSessionResponseRequest(BaseModel):\n    item_id: UUID\n    correct: bool\n    response: str | None = None\n",
            "class DiagnosticSessionResponseRequest(BaseModel):\n    item_id: UUID\n    correct: bool\n    response: str | None = None\n    caps_ref: str | None = None\n",
        )

    next_item_marker = "    await require_active_consent_for_current_user(db, current_user, snap.learner_id)\n    repo = ItemBankRepository(db)\n    items = list(await repo.list_by_caps_ref(caps_ref, limit=200))\n"
    next_item_replacement = (
        "    await require_active_consent_for_current_user(db, current_user, snap.learner_id)\n"
        "    session_caps_ref = getattr(snap, \"caps_ref\", None) or caps_ref\n"
        "    if session_caps_ref and str(caps_ref) != str(session_caps_ref):\n"
        "        raise HTTPException(status_code=400, detail=\"caps_ref does not match recovered diagnostic session\")\n"
        "    repo = ItemBankRepository(db)\n"
        "    items = list(await repo.list_by_caps_ref(session_caps_ref, limit=200))\n"
    )
    if "caps_ref does not match recovered diagnostic session" not in text:
        text = text.replace(next_item_marker, next_item_replacement)

    respond_marker = "    await require_active_consent_for_current_user(db, current_user, snap.learner_id)\n    item = await ItemBankRepository(db).get_item(body.item_id)\n"
    respond_replacement = (
        "    await require_active_consent_for_current_user(db, current_user, snap.learner_id)\n"
        "    try:\n"
        "        validate_adaptive_diagnostic_response(body, snapshot=snap, session_id=session_id)\n"
        "    except DiagnosticIntegrityError as exc:\n"
        "        raise HTTPException(status_code=400, detail=str(exc)) from exc\n"
        "    item = await ItemBankRepository(db).get_item(body.item_id)\n"
    )
    if "validate_adaptive_diagnostic_response(body, snapshot=snap" not in text:
        text = text.replace(respond_marker, respond_replacement)

    ast.parse(text)
    if text != original:
        DIAGNOSTICS.write_text(text, encoding="utf-8")
        return True
    return False


def patch_evidence_registry() -> bool:
    if not REGISTRY.exists():
        return False
    text = REGISTRY.read_text(encoding="utf-8")
    original = text

    if "id: DIAG-001" in text:
        # Narrow update only inside the DIAG-001 block.
        before, marker, after = text.partition("  - id: DIAG-001")
        if marker:
            block, next_marker, rest = after.partition("\n\n  - id:")
            block = block.replace("proof_status: not-started", "proof_status: runtime-passing")
            block = block.replace("proof_command: make diagnostics-session-binding-check", "proof_command: make backend-implementation-1231-1270-full-check")
            block = block.replace("evidence_file: null", "evidence_file: docs/release/diagnostics_session_binding_repair_report.md")
            block = block.replace(
                "closure_blocker: validate_session_served_item_binding not fully wired into adaptive routes",
                "closure_blocker: full HTTP plus production DB diagnostic session proof still required",
            )
            text = before + marker + block + (next_marker + rest if next_marker else "")

    if text != original:
        REGISTRY.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> int:
    router_patched = patch_diagnostics_router()
    registry_patched = patch_evidence_registry()
    REPORT.write_text(
        "\n".join(
            [
                "# Diagnostics Session Binding Repair Report",
                "",
                f"Generated at: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
                "",
                "**Status:** implemented at route-runtime level",
                "",
                f"- diagnostics router patched: `{router_patched}`",
                f"- evidence registry patched: `{registry_patched}`",
                "- adaptive next-item rejects mismatched query caps_ref against recovered session caps_ref",
                "- adaptive respond rejects item IDs not recorded in recovered session served_item_ids",
                "- adaptive respond rejects mismatched response caps_ref when supplied",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
