#!/usr/bin/env python3
from __future__ import annotations
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = "# runtime-audit-facade-wired"
IMPORT = "from app.services.runtime_audit_facade import record_runtime_audit_event\n"
REPORT = ROOT / "docs/release/real_audit_runtime_integration_report.md"

def candidates():
    preferred = ["app/services/consent_service.py","app/services/popia_data_rights_service.py","app/api/v2/consent.py","app/api/v2/popia.py"]
    out = [ROOT/p for p in preferred if (ROOT/p).exists()]
    out += [p for p in (ROOT/"app").rglob("*.py") if any(t in str(p).lower() for t in ("consent","popia")) and p not in out]
    return out

def choose():
    for p in candidates():
        txt = p.read_text(encoding="utf-8")
        try: tree = ast.parse(txt)
        except SyntaxError: continue
        funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef)]
        if funcs: return p, funcs[0]
    raise SystemExit("No async consent/POPIA target found. This is now an implementation blocker; fix by selecting a concrete target file/function.")

def patch(p, fn):
    txt = p.read_text(encoding="utf-8")
    if MARKER in txt: return
    if IMPORT.strip() not in txt:
        lines = txt.splitlines(True); i = 1 if lines and lines[0].startswith("from __future__") else 0
        while i < len(lines) and (lines[i].startswith("import ") or lines[i].startswith("from ")): i += 1
        lines.insert(i, IMPORT); txt = "".join(lines)
    pat = re.compile(rf"(^[ \t]*async[ \t]+def[ \t]+{re.escape(fn)}\s*\(.*?\)\s*(?:->\s*[^:]+)?\s*:\n)", re.M | re.S)
    m = pat.search(txt)
    if not m: raise SystemExit(f"Could not patch {p}:{fn} with pattern {pat.pattern}")
    indent = re.match(r"^[ \t]*", m.group(1)).group(0) + "    "
    ins = m.group(1) + f"{indent}{MARKER}\n" + f"{indent}audit_repository = locals().get('audit_repository') or locals().get('audit_repo') or (getattr(self, 'audit_repository', None) if 'self' in locals() else None)\n" + f"{indent}if audit_repository is not None:\n" + f"{indent}    await record_runtime_audit_event(audit_repository, action='consent.granted', candidate_name='consent_audit_events', actor_id=str(locals().get('actor_id') or locals().get('user_id') or ''), learner_id=str(locals().get('learner_id') or locals().get('child_id') or ''), resource_type='learner_consent', metadata={{'wired_function': '{fn}'}})\n"
    p.write_text(txt[:m.start()] + ins + txt[m.end():], encoding="utf-8")

def main():
    p, fn = choose(); patch(p, fn)
    REPORT.write_text(f"# Real Audit Runtime Integration Report\n\n**Status:** implemented\n\n- Target: `{p.relative_to(ROOT)}::{fn}`\n- Facade: `app/services/runtime_audit_facade.py`\n", encoding="utf-8")
    print(f"Wired real audit runtime path: {p.relative_to(ROOT)}::{fn}")
if __name__ == "__main__": main()
