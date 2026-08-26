#!/usr/bin/env python3
from __future__ import annotations

import argparse
import filecmp
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts._subprocess import run


OUTPUTS = [
    "docs/generated/documentation_inventory.json",
    "docs/generated/documentation_inventory.csv",
    "docs/generated/documentation_findings.csv",
]


def run_inventory(root: Path, outputs: list[str]) -> int:
    cmd = [
        sys.executable,
        "scripts/maintenance/audit_documentation_inventory.py",
        "--root",
        ".",
        "--out-json",
        outputs[0],
        "--out-csv",
        outputs[1],
        "--out-findings",
        outputs[2],
    ]
    proc = run(cmd, cwd=root)
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify committed documentation inventory is deterministic and reproducible.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--update", action="store_true", help="Regenerate committed inventory outputs in place.")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    if args.update:
        return run_inventory(root, OUTPUTS)

    missing = [rel for rel in OUTPUTS if not (root / rel).exists()]
    if missing:
        print("Missing committed inventory output(s):")
        for rel in missing:
            print(f"  - {rel}")
        return 1

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        temp_outputs = [str(tmp_dir / "documentation_inventory.json"), str(tmp_dir / "documentation_inventory.csv"), str(tmp_dir / "documentation_findings.csv")]
        rc = run_inventory(root, temp_outputs)
        if rc != 0:
            return rc
        diffs = []
        for committed, generated in zip(OUTPUTS, temp_outputs):
            if not filecmp.cmp(root / committed, generated, shallow=False):
                diffs.append(committed)
        if diffs:
            print("Documentation inventory is not reproducible. Regenerate with:")
            print("  python3 scripts/maintenance/check_doc_inventory_reproducible.py --root . --update")
            print("Changed output(s):")
            for rel in diffs:
                print(f"  - {rel}")
            return 1

    print("Documentation inventory reproducibility check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
