#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
txt=(ROOT/"app/services/deep_readiness_runtime.py").read_text(encoding="utf-8").lower()
for tok in ["insert ","update ","delete ","drop ","truncate ","alter table"]:
    assert tok not in txt, f"write-like SQL token present: {tok}"
assert (ROOT/"docs/release/readonly_deep_readiness_implementation_report.md").exists()
print("PASS read-only deep readiness runtime")
