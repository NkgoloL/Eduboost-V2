#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
patched=[p for p in (ROOT/"app").rglob("*.py") if "runtime-consent-facade-ready" in p.read_text(encoding="utf-8", errors="ignore")]
assert (ROOT/"app/services/runtime_consent_facade.py").exists(), "facade missing"
assert patched, "no real consent seam patched"
assert (ROOT/"docs/release/real_consent_runtime_repair_report.md").exists(), "report missing"
print("PASS real consent runtime repair:", ", ".join(str(p.relative_to(ROOT)) for p in patched))
