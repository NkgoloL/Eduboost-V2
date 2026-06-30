#!/bin/bash
cd ~/Dev/Development/Eduboost-V2
source .venv/bin/activate 2>/dev/null
# Run a quick smoke / collection check first
python -m pytest --collect-only -q 2>&1 | tail -15
