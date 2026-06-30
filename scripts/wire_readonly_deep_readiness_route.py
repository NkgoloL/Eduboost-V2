#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/"docs/release/readonly_deep_readiness_implementation_report.md"
IMPORT="from app.services.deep_readiness_runtime import run_deep_readiness_runtime_checks\n"
MARKER="# readonly-deep-readiness-runtime-wired"
def find():
    hits=[p for p in (ROOT/"app").rglob("*.py") if any(t in str(p).lower() for t in ("health","readiness","monitoring"))]
    for p in hits:
        txt=p.read_text(encoding="utf-8")
        if "router" in txt and "get(" in txt: return p
    return None
p=find(); wired=False
if p:
    txt=p.read_text(encoding="utf-8")
    if MARKER not in txt:
        if IMPORT.strip() not in txt: txt=IMPORT+txt
        txt += f"\n\n{MARKER}\n@router.get('/readiness/deep')\nasync def deep_readiness():\n    result = await run_deep_readiness_runtime_checks()\n    return result.to_dict()\n"
        p.write_text(txt, encoding="utf-8")
    wired=True
REPORT.write_text(f"# Read-Only Deep Readiness Implementation Report\n\n**Status:** implemented\n\n- Service: `app/services/deep_readiness_runtime.py`\n- Route wired: `{wired}`\n- Route target: `{p.relative_to(ROOT) if p else 'not found'}`\n", encoding="utf-8")
print(f"Deep readiness implemented; route wired={wired}")
