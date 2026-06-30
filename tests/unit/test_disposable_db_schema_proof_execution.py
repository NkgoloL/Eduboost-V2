import subprocess
import sys
from pathlib import Path
def test_pending_without_database_url():
    result=subprocess.run([sys.executable,"scripts/execute_disposable_db_schema_proof.py"],env={},text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    assert result.returncode==0
    assert "pending-real-disposable-db" in Path("docs/release/disposable_db_schema_proof_execution_report.md").read_text()
