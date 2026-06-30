#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

BLOCK_START = "# BEGIN EDUBOOST DOCS HOUSEKEEPING TARGETS"
BLOCK_END = "# END EDUBOOST DOCS HOUSEKEEPING TARGETS"
BLOCK = f"""
{BLOCK_START}
.PHONY: docs-housekeeping-check docs-housekeeping-refresh docs-housekeeping-inventory docs-housekeeping-inventory-check docs-housekeeping-ratchet-check docs-housekeeping-strict-check docs-metadata-check docs-source-of-truth-check docs-links-check docs-links-full-check docs-claim-discipline-check docs-adr-number-check docs-stale-term-check docs-housekeeping-baseline-refresh

docs-housekeeping-check: docs-housekeeping-inventory-check docs-source-of-truth-check docs-metadata-check docs-claim-discipline-check docs-links-check docs-housekeeping-ratchet-check docs-adr-number-check docs-stale-term-check

docs-housekeeping-inventory:
	$(PYTHON) scripts/maintenance/audit_documentation_inventory.py --root . --out-json docs/generated/documentation_inventory.json --out-csv docs/generated/documentation_inventory.csv --out-findings docs/generated/documentation_findings.csv

docs-housekeeping-refresh: docs-housekeeping-inventory

docs-housekeeping-inventory-check:
	$(PYTHON) scripts/maintenance/check_doc_inventory_reproducible.py --root .

docs-housekeeping-ratchet-check:
	$(PYTHON) scripts/maintenance/check_doc_housekeeping_ratchet.py --root .

docs-source-of-truth-check:
	$(PYTHON) scripts/maintenance/check_doc_source_of_truth.py --root .

docs-metadata-check:
	$(PYTHON) scripts/maintenance/check_doc_metadata.py --root . --canonical-only

docs-links-check:
	$(PYTHON) scripts/maintenance/check_doc_links.py --root . --changed-only

docs-links-full-check:
	$(PYTHON) scripts/maintenance/check_doc_links.py --root .

docs-claim-discipline-check:
	$(PYTHON) scripts/maintenance/check_doc_truth_claims.py --root . --canonical-only

docs-adr-number-check:
	$(PYTHON) scripts/maintenance/check_doc_adr_numbers.py --root .

docs-stale-term-check:
	$(PYTHON) scripts/maintenance/check_doc_stale_terms.py --root .

docs-housekeeping-baseline-refresh: docs-housekeeping-refresh
	$(PYTHON) scripts/maintenance/update_doc_housekeeping_baseline.py --root .
	$(PYTHON) scripts/maintenance/check_doc_adr_numbers.py --root . --update
	$(PYTHON) scripts/maintenance/check_doc_stale_terms.py --root . --update

docs-housekeeping-strict-check: docs-source-of-truth-check docs-housekeeping-inventory-check
	$(PYTHON) scripts/maintenance/check_doc_metadata.py --root . --strict-legacy
	$(PYTHON) scripts/maintenance/check_doc_truth_claims.py --root . --strict-legacy
	$(PYTHON) scripts/maintenance/check_doc_links.py --root .
	$(PYTHON) scripts/maintenance/check_doc_adr_numbers.py --root . --strict
	$(PYTHON) scripts/maintenance/check_doc_stale_terms.py --root . --strict
{BLOCK_END}
""".lstrip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch Makefile with Stage 2 docs housekeeping targets.")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    makefile = root / "Makefile"
    if not makefile.exists():
        makefile.write_text("SHELL := /bin/bash\nPYTHON ?= python3\n\n" + BLOCK, encoding="utf-8")
        print("Created Makefile with Stage 2 docs housekeeping targets.")
        return 0
    text = makefile.read_text(encoding="utf-8")
    if BLOCK_START in text and BLOCK_END in text:
        before = text.split(BLOCK_START, 1)[0]
        after = text.split(BLOCK_END, 1)[1]
        makefile.write_text(before.rstrip() + "\n\n" + BLOCK + after, encoding="utf-8")
        print("Updated docs housekeeping target block in Makefile for Stage 2.")
    else:
        makefile.write_text(text.rstrip() + "\n\n" + BLOCK, encoding="utf-8")
        print("Appended Stage 2 docs housekeeping target block to Makefile.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
