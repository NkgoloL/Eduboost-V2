### ✅ Reconstruction Script (Python)

```python
#!/usr/bin/env python3
"""
rebuild_from_md.py
Reconstructs a project tree from a Markdown bundle.
"""

import os
import re
import sys
from pathlib import Path

FILE_HEADER = re.compile(r'^## FILE:\s+(.+)$')

def rebuild(md_path):
    current_file = None
    buffer = []

    with open(md_path, "r", encoding="utf-8") as f:
        for line in f:
            header = FILE_HEADER.match(line.strip())
            if header:
                if current_file:
                    write_file(current_file, buffer)
                current_file = header.group(1)
                buffer = []
            else:
                buffer.append(line)

        if current_file:
            write_file(current_file, buffer)

def write_file(path, lines):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "".join(lines)

    # Strip surrounding code fences if present
    content = re.sub(r'^```.*?\n', '', content, flags=re.DOTALL)
    content = re.sub(r'\n```$', '', content)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

    print(f"[OK] {path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: rebuild_from_md.py <project.md>")
        sys.exit(1)
    rebuild(sys.argv[1])