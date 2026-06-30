import subprocess
import sys
from pathlib import Path
def test_cleanup_runs():
    result=subprocess.run([sys.executable,"scripts/remove_proven_dead_backend_consolidation_artifacts.py"],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    assert result.returncode==0
    assert Path("docs/release/post_migration_cleanup_report.md").exists()
