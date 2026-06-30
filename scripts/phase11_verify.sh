#!/bin/bash
cd ~/Dev/Development/Eduboost-V2
source .venv/bin/activate 2>/dev/null
python -c "from app.api_v2 import app; print('import ok, routes:', len(app.routes))"
echo "---FILES CHANGED---"
git status --short | wc -l
echo "---F821 RECHECK---"
ruff check app tests scripts --select F821
echo "---LINT-IMPORTS---"
lint-imports 2>&1 | tail -8
