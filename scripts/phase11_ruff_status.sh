#!/bin/bash
cd ~/Dev/Development/Eduboost-V2
source .venv/bin/activate 2>/dev/null
echo "==== CURRENT STATE ===="
ruff check app tests scripts --statistics 2>&1 | tail -30
echo ""
echo "==== F401 by file (top 15) ===="
ruff check app tests scripts --select F401 --output-format=concise 2>&1 | awk -F: '{print $1}' | sort | uniq -c | sort -rn | head -15
echo ""
echo "==== F841 by file ===="
ruff check app tests scripts --select F841 --output-format=concise 2>&1 | awk -F: '{print $1}' | sort | uniq -c | sort -rn | head -10
echo ""
echo "==== E402 by file (top 10) ===="
ruff check app tests scripts --select E402 --output-format=concise 2>&1 | awk -F: '{print $1}' | sort | uniq -c | sort -rn | head -10
