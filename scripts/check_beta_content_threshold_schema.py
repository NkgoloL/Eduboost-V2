#!/usr/bin/env python3
import json
from pathlib import Path

path = Path("docs/beta/beta_content_threshold_status.json")
assert path.exists(), "missing beta_content_threshold_status.json"
data = json.loads(path.read_text())
for key in ["beta_ready", "approved_items", "required_items", "blockers"]:
    assert key in data, f"missing {key}"
print("PASS beta content threshold evidence schema")
