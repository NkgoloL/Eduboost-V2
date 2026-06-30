#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.final_gate_classifier import ACCEPTED_AUTH_REFRESH_IDS, registry_findings, release_ready_for, write_refresh  # noqa: E402

REGISTRY = ROOT / "docs/release/evidence_status_registry.yml"


def _block_bounds(text: str, item_id: str) -> tuple[int, int] | None:
    marker = f"  - id: {item_id}"
    start = text.find(marker)
    if start < 0:
        return None
    end = text.find("\n  - id:", start + 1)
    return (start, len(text) if end < 0 else end + 1)


def _set_field(block: str, field: str, value: str) -> str:
    pattern = rf"(?m)^(\s{{4}}{re.escape(field)}:\s*).*$"
    if re.search(pattern, block):
        return re.sub(pattern, rf"\g<1>{value}", block)
    return block.rstrip() + f"\n    {field}: {value}\n"


def patch_registry() -> list[str]:
    text = REGISTRY.read_text(encoding="utf-8") if REGISTRY.exists() else "findings:\n"
    findings = {finding.id: finding for finding in registry_findings()}
    patched_ids: list[str] = []

    for item_id in ACCEPTED_AUTH_REFRESH_IDS:
        finding = findings.get(item_id)
        if finding is None or not release_ready_for(finding.proof_status, finding.closure_blocker):
            continue
        bounds = _block_bounds(text, item_id)
        if bounds is None:
            continue
        start, end = bounds
        block = text[start:end]
        block = _set_field(block, "blocks_beta", "false")
        block = _set_field(block, "closure_blocker", "none")
        text = text[:start] + block + text[end:]
        patched_ids.append(item_id)

    REGISTRY.write_text(text, encoding="utf-8")
    write_refresh()
    return patched_ids


def main() -> int:
    patched = patch_registry()
    print("Patched final gate classifier registry entries: " + (", ".join(patched) or "none"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
