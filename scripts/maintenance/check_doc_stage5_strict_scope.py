import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts._subprocess import run


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    args = sys.argv[1:]
    if "--root" in args:
        idx = args.index("--root")
        if idx + 1 < len(args):
            root = Path(args[idx + 1]).resolve()
    command = [sys.executable, str(root / "scripts/maintenance/check_doc_stage3_strict_scope.py"), "--root", str(root), "--scope", "docs/documentation/stage_5_strict_scope.json"]
    proc = run(command)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
