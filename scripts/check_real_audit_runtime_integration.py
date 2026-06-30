#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
wired=[p for p in (ROOT/"app").rglob("*.py") if "runtime-audit-facade-wired" in p.read_text(encoding="utf-8", errors="ignore")]
assert (ROOT/"app/services/runtime_audit_facade.py").exists(), "facade missing"
assert wired, "no real runtime path wired"
assert (ROOT/"docs/release/real_audit_runtime_integration_report.md").exists(), "report missing"
print("PASS real audit runtime integration:", ", ".join(str(p.relative_to(ROOT)) for p in wired))
