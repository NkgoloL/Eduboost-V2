#!/usr/bin/env python3
import json
from scripts._subprocess import run
import os
from pathlib import Path

os.chdir(Path(__file__).resolve().parents[1])

# Generate baseline
result = run(
    ['detect-secrets', 'scan', '--all-files', '.'],
    capture_output=True,
    text=True
)

with open('.secrets.baseline', 'w') as f:
    f.write(result.stdout)

# Verify
with open('.secrets.baseline') as f:
    d = json.load(f)

print('plugins:', len(d.get('plugins_used', [])))
print('results:', len(d.get('results', {})))
print('version:', d.get('version'))
print('ok')