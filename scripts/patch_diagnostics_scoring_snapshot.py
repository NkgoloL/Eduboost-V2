#!/usr/bin/env python3
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "app/modules/diagnostics/diagnostic_session_service.py"
REPORT = ROOT / "docs/release/diagnostics_scoring_snapshot_repair_report.md"
IMPORT_LINE = (
    "from app.services.diagnostic_scoring_snapshot import "
    "diagnostic_item_from_response, diagnostic_response_snapshot\n"
)


def main() -> int:
    source = TARGET.read_text(encoding="utf-8")
    original = source

    if "diagnostic_item_from_response" not in source:
        anchor = "from app.modules.progress.mastery_model import compute_mastery_score, label_for_score\n"
        if anchor not in source:
            raise RuntimeError("cannot locate diagnostic session service import anchor")
        source = source.replace(anchor, anchor + IMPORT_LINE)

    old_append = 'snap.responses.append({"item_id": item_id, "correct": correct, "response": response})'
    new_append = (
        'snap.responses.append({**diagnostic_response_snapshot(item, item_id=item_id), '
        '"correct": correct, "response": response})'
    )
    if old_append in source:
        source = source.replace(old_append, new_append)

    old_responses = 'responses = [(item, bool(row["correct"])) for row in snap.responses]'
    new_responses = (
        'responses = [(diagnostic_item_from_response(row, fallback_item=item), bool(row["correct"])) '
        'for row in snap.responses]'
    )
    if old_responses in source:
        source = source.replace(old_responses, new_responses)

    if old_responses in source or old_append in source:
        raise RuntimeError("diagnostic scoring snapshot patch did not replace stale current-item scoring path")

    if "diagnostic_response_snapshot(item, item_id=item_id)" not in source:
        raise RuntimeError("diagnostic response snapshot append not present after patch")
    if "diagnostic_item_from_response(row, fallback_item=item)" not in source:
        raise RuntimeError("diagnostic historical item reconstruction not present after patch")

    ast.parse(source)
    if source != original:
        TARGET.write_text(source, encoding="utf-8")

    REPORT.write_text(
        "\n".join(
            [
                "# Diagnostics Scoring Snapshot Repair Report",
                "",
                "**Status:** implemented",
                "",
                "- Diagnostic responses now persist per-response scoring parameters.",
                "- Historical IRT recalculation rebuilds item objects from each response snapshot.",
                "- The current item object is no longer reused for all historical responses.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
