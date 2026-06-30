#!/usr/bin/env python3
from __future__ import annotations
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/"docs/release/disposable_db_schema_proof_execution_report.md"
def safe(url):
    low=url.lower()
    if not url: return False,"DATABASE_URL is not set"
    if any(x in low for x in ("<",">","user:pass","example")): return False,"DATABASE_URL contains placeholders"
    if any(x in low for x in ("prod","production","amazonaws.com","azure.com","render.com")): return False,"DATABASE_URL looks production-like"
    if "test" not in low and "disposable" not in low: return False,"DATABASE_URL must be test/disposable"
    return True,"safe disposable DB URL shape"
def run(cmd):
    r=subprocess.run(cmd,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=False)
    return r.returncode,r.stdout
url=os.getenv("DATABASE_URL",""); ok,reason=safe(url)
lines=["# Disposable DB Schema Proof Execution Report","",f"Generated: `{datetime.now(timezone.utc).isoformat()}`","",f"Safety: `{reason}`",""]
if not ok:
    lines+=["**Status:** pending-real-disposable-db",""]
    REPORT.write_text("\n".join(lines),encoding="utf-8"); print(reason); raise SystemExit(0)
cmds=[["python3","scripts/run_disposable_schema_drift_proof.py","--database-url",url],["python3","scripts/check_schema_drift_contract.py"]]
overall=0; lines+=["**Status:** executed","","| Command | Code |","|---|---:|"]
for cmd in cmds:
    code,out=run(cmd); overall=max(overall,code); lines.append(f"| `{' '.join(cmd).replace(url,'<DATABASE_URL>')}` | {code} |"); lines+=["","```text",out.rstrip(),"```"]
REPORT.write_text("\n".join(lines),encoding="utf-8"); print(f"Wrote {REPORT}"); raise SystemExit(overall)
