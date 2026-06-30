#!/bin/bash
cd ~/Dev/Development/Eduboost-V2
source .venv/bin/activate 2>/dev/null
python -m pytest tests/unit -q \
    --deselect tests/unit/modules/diagnostics/test_item_bank_service.py::test_get_coverage_summary_calculates_ratios \
    --no-header 2>&1 | tail -25
