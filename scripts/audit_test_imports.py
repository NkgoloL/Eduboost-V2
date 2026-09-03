"""Audit all import statements in tests to verify imported symbols exist."""
from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path


def audit_test_imports(tests_dir: Path) -> list[str]:
    root = tests_dir.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    errors: list[str] = []
    py_files = sorted(tests_dir.rglob("test_*.py"))


    for py_file in py_files:
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        except Exception as e:
            errors.append(f"{py_file}: syntax error parsing AST: {e}")
            continue

        # Collect all nodes that are inside Try handlers (except blocks)
        fallback_import_nodes = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Try):
                for handler in n.handlers:
                    for sub_n in ast.walk(handler):
                        if isinstance(sub_n, ast.ImportFrom):
                            fallback_import_nodes.add(sub_n)

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if not node.module.startswith("app"):
                    continue
                # If this import is inside an except handler fallback, ignore import error
                is_fallback = node in fallback_import_nodes

                try:
                    mod = importlib.import_module(node.module)
                except Exception as e:
                    if not is_fallback:
                        errors.append(f"{py_file}:{node.lineno}: Cannot import module '{node.module}': {e}")
                    continue

                for alias in node.names:
                    symbol_name = alias.name
                    if symbol_name == "*":
                        continue
                    if not hasattr(mod, symbol_name):
                        # Check if it's a submodule
                        submod_name = f"{node.module}.{symbol_name}"
                        try:
                            importlib.import_module(submod_name)
                        except Exception:
                            if not is_fallback:
                                errors.append(
                                    f"{py_file}:{node.lineno}: Symbol '{symbol_name}' does not exist in module '{node.module}'"
                                )

    return errors


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    tests_dir = root / "tests"
    errors = audit_test_imports(tests_dir)
    if errors:
        print(f"FAILED: Found {len(errors)} broken test import(s):")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"SUCCESS: All imports in {tests_dir} verified against active codebase.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
