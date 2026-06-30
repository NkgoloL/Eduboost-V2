#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/"docs/release/post_migration_cleanup_report.md"
removed=[]; skipped=[]
for p in sorted((ROOT/"docs/release").glob("*noop*.md")) + sorted((ROOT/"docs/release").glob("*draft*.md")):
    name=p.name.lower()
    if any(x in name for x in ("audit","consent","runtime","schema","readiness","evidence","report")):
        skipped.append(f"{p.relative_to(ROOT)}: active/protected"); continue
    refs="\n".join(q.read_text(encoding="utf-8",errors="ignore") for q in list((ROOT/"app").rglob("*.py"))+list((ROOT/"tests").rglob("*.py")))
    if p.stem in refs:
        skipped.append(f"{p.relative_to(ROOT)}: referenced"); continue
    p.unlink(); removed.append(str(p.relative_to(ROOT)))
REPORT.write_text("# Post-Migration Cleanup Report\n\n**Status:** executed\n\n## Removed\n"+"\n".join(f"- `{x}`" for x in removed)+"\n\n## Skipped\n"+"\n".join(f"- {x}" for x in skipped)+"\n\nNo DB tables or history were deleted.\n",encoding="utf-8")
print(f"Removed {len(removed)}; skipped {len(skipped)}")
