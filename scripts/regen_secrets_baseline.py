#!/usr/bin/env python3
import json
import subprocess
import os

os.chdir('/home/nkgolol/Dev/Development/Eduboost-V2')

# Generate baseline
result = subprocess.run(
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