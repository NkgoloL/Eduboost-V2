#!/usr/bin/env python3
from pathlib import Path
r=Path("docs/release/post_migration_cleanup_report.md")
assert r.exists(), "cleanup report missing"
txt=r.read_text(encoding="utf-8").lower()
assert "status:** executed" in txt
assert "no db tables or history were deleted" in txt
print("PASS post-migration cleanup")
