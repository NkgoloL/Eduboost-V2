#!/usr/bin/env python3
from __future__ import annotations
import ast
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MARKER="# runtime-consent-facade-ready"
IMPORT="from app.services.runtime_consent_facade import emit_consent_runtime_event\n"
REPORT=ROOT/"docs/release/real_consent_runtime_repair_report.md"

def choose():
    prefs=["app/services/consent_service.py","app/services/parental_consent_service.py","app/services/popia_data_rights_service.py"]
    for rel in prefs:
        if (ROOT/rel).exists(): return ROOT/rel
    hits=[p for p in (ROOT/"app").rglob("*.py") if "consent" in str(p).lower()]
    if not hits: raise SystemExit("No consent module found to repair.")
    return hits[0]

def main():
    p=choose(); txt=p.read_text(encoding="utf-8")
    if MARKER not in txt:
        if IMPORT.strip() not in txt:
            lines=txt.splitlines(True); i=1 if lines and lines[0].startswith("from __future__") else 0
            while i<len(lines) and (lines[i].startswith("import ") or lines[i].startswith("from ")): i+=1
            lines.insert(i, IMPORT); txt="".join(lines)
        tree=ast.parse(txt); classes=[n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        if not classes: raise SystemExit(f"No class found in consent target {p}")
        c=classes[0]; indent=" "*(c.col_offset+4)
        method=["",f"{indent}{MARKER}",f"{indent}async def _emit_runtime_consent_audit(self, *, action: str, learner_id: str, actor_id: str | None = None, metadata: dict | None = None):",f"{indent}    repo = getattr(self, 'audit_repository', None) or getattr(self, 'audit_repo', None)",f"{indent}    return await emit_consent_runtime_event(action=action, learner_id=str(learner_id), actor_id=actor_id, audit_repository=repo, metadata=metadata or {{}})"]
        lines=txt.splitlines(); lines[(c.end_lineno or len(lines)):(c.end_lineno or len(lines))]=method; txt="\n".join(lines)+"\n"
        p.write_text(txt, encoding="utf-8")
    REPORT.write_text(f"# Real Consent Runtime Repair Report\n\n**Status:** implemented\n\n- Target: `{p.relative_to(ROOT)}`\n- Facade: `app/services/runtime_consent_facade.py`\n", encoding="utf-8")
    print(f"Patched consent runtime seam: {p.relative_to(ROOT)}")
if __name__=="__main__": main()
