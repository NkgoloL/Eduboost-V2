#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

BLOCK_START = "# BEGIN EDUBOOST DOCS HOUSEKEEPING TARGETS"
BLOCK_END = "# END EDUBOOST DOCS HOUSEKEEPING TARGETS"
BLOCK = f"""
{BLOCK_START}
.PHONY: docs-housekeeping-check docs-inventory docs-metadata-check docs-source-of-truth-check docs-links-check docs-claim-discipline-check

docs-housekeeping-check: docs-source-of-truth-check docs-metadata-check docs-claim-discipline-check docs-links-check
	$(PYTHON) scripts/maintenance/audit_documentation_inventory.py --root . --out-json docs/generated/documentation_inventory.json --out-csv docs/generated/documentation_inventory.csv --out-findings docs/generated/documentation_findings.csv

docs-inventory:
	$(PYTHON) scripts/maintenance/audit_documentation_inventory.py --root . --out-json docs/generated/documentation_inventory.json --out-csv docs/generated/documentation_inventory.csv --out-findings docs/generated/documentation_findings.csv

docs-source-of-truth-check:
	$(PYTHON) scripts/maintenance/check_doc_source_of_truth.py --root .

docs-metadata-check:
	$(PYTHON) scripts/maintenance/check_doc_metadata.py --root . --canonical-only

docs-links-check:
	$(PYTHON) scripts/maintenance/check_doc_links.py --root . --changed-only

docs-claim-discipline-check:
	$(PYTHON) scripts/maintenance/check_doc_truth_claims.py --root . --canonical-only
{BLOCK_END}
""".lstrip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch Makefile with docs housekeeping targets.")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    makefile = root / "Makefile"
    if not makefile.exists():
        makefile.write_text("SHELL := /bin/bash\nPYTHON ?= python3\n\n" + BLOCK, encoding="utf-8")
        print("Created Makefile with docs housekeeping targets.")
        return 0
    text = makefile.read_text(encoding="utf-8")
    if BLOCK_START in text and BLOCK_END in text:
        before = text.split(BLOCK_START, 1)[0]
        after = text.split(BLOCK_END, 1)[1]
        makefile.write_text(before.rstrip() + "\n\n" + BLOCK + after, encoding="utf-8")
        print("Updated existing docs housekeeping target block in Makefile.")
    else:
        makefile.write_text(text.rstrip() + "\n\n" + BLOCK, encoding="utf-8")
        print("Appended docs housekeeping target block to Makefile.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
