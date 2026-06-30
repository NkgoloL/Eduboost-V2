#!/bin/bash
# Phase 11 — Ruff automated burn-down
# Runs successive ruff --fix passes scoped to safe categories
set -e
cd ~/Dev/Development/Eduboost-V2
source .venv/bin/activate 2>/dev/null

echo "==== BASELINE ===="
ruff check app tests scripts --statistics 2>&1 | tail -30

echo ""
echo "==== PASS 1: Safe fixes (F401, F541, F811, F841, E711, E712, E713, E401, W291/W292/W293) ===="
ruff check app tests scripts --select F401,F541,F811,F841,E711,E712,E713,E401,W291,W292,W293 --fix 2>&1 | tail -5

echo ""
echo "==== PASS 2: SIM rules (safe ones) ===="
ruff check app tests scripts --select SIM101,SIM102,SIM117,SIM118,SIM201,SIM210,SIM211 --fix 2>&1 | tail -5

echo ""
echo "==== AFTER AUTO-FIX ===="
ruff check app tests scripts --statistics 2>&1 | tail -30
