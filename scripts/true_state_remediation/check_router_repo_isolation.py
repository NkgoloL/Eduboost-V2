#!/usr/bin/env python3
import ast
import sys
from pathlib import Path

def is_router_file(path: Path) -> bool:
    """Check if the file is an API router (endpoint handler)."""
    if path.name.startswith("test_"):
        return False
    if "api_v2_routers" in path.parts:
        return True
    if "router" in path.name.lower():
        return True
    return False

def check_file(path: Path) -> list[str]:
    violations = []
    try:
        content = path.read_text(encoding='utf-8')
        tree = ast.parse(content, filename=str(path))
    except Exception as e:
        return [f"Could not parse {path}: {e}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith('app.repositories'):
                    violations.append(f"{path.name}: L{node.lineno} imports {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith('app.repositories'):
                violations.append(f"{path.name}: L{node.lineno} imports from {node.module}")
    return violations

def main():
    # Scan standard router directories
    target_dirs = [Path('app/api_v2_routers'), Path('app/modules')]
    all_violations = []

    for d in target_dirs:
        if d.exists():
            for f in d.rglob('*.py'):
                if is_router_file(f):
                    all_violations.extend(check_file(f))

    if all_violations:
        print(f"FAILED: Found {len(all_violations)} router-to-repository import violations:")
        for v in all_violations:
            print(f"  - {v}")
        sys.exit(1)
    
    print("PASSED: Zero router-to-repository violations found. Service boundary intact.")
    sys.exit(0)

if __name__ == '__main__':
    main()
