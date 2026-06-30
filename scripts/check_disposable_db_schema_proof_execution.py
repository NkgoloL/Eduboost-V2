#!/usr/bin/env python3
from pathlib import Path
r=Path("docs/release/disposable_db_schema_proof_execution_report.md")
assert r.exists(), "report missing"
txt=r.read_text(encoding="utf-8")
assert "Status:** executed" in txt or "Status:** pending-real-disposable-db" in txt
print("PASS disposable DB schema proof execution status present")
