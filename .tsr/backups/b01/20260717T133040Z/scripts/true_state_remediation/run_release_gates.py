from __future__ import annotations
import argparse, sys
from pathlib import Path
from scripts.true_state_remediation.core import CommandSpec, evidence_root, root_from, run_commands

def specs(root: Path):
    py=sys.executable
    existing=root/"scripts/advisory_suites/run_coverage_static_security_green.py"
    coverage=(py,str(existing),"--execute","--require-green") if existing.exists() else ("make","coverage-baseline-stabilisation")
    return [
      CommandSpec("compileall",(py,"-m","compileall","-q","app","tests","scripts","alembic"),600),
      CommandSpec("mcp_stub_isolation",(py,"-m","pytest","-c","pytest.ini","tests/unit/test_etl_mcp_server_startup.py","-q"),600,env={"PYTHONPATH":"."}),
      CommandSpec("test_collection",(py,"-m","pytest","--collect-only","-q"),1800,env={"PYTHONPATH":"."}),
      CommandSpec("execution7_gate_suite",coverage,7200),
      CommandSpec("ruff",(py,"-m","ruff","check","app","tests"),1800),
      CommandSpec("mypy",(py,"-m","mypy","app"),2400),
      CommandSpec("bandit",(py,"-m","bandit","-r","app","scripts","-q"),2400),
      CommandSpec("pip_audit_base",(py,"-m","pip_audit","-r","requirements/base.txt"),1800),
      CommandSpec("pip_audit_dev",(py,"-m","pip_audit","-r","requirements/dev.txt"),1800),
      CommandSpec("frontend_audit",("pnpm","audit","--prod"),1800,cwd="app/frontend"),
      CommandSpec("frontend_quality",("pnpm","run","quality:release"),3600,cwd="app/frontend"),
      CommandSpec("product_gate",(py,"scripts/test_suites/verify_product_gate_execution.py"),1200),
      CommandSpec("product_runtime_gate",(py,"scripts/test_suites/verify_product_runtime_test_gates.py"),1200),
      CommandSpec("execution7_verifier",(py,"scripts/roadmap_reconciliation/verify_prd1100r_runtime_restore_execution_7_coverage_static_security_green.py","--require-green","--json"),1200),
    ]

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); ap.add_argument("--stop-on-failure",action="store_true")
    a=ap.parse_args(); root=root_from(Path(a.repo)); out=evidence_root(root,"B01")/"commands"
    results=run_commands(root,specs(root),out,stop_on_failure=a.stop_on_failure)
    return 0 if all(r["passed"] or not r["required"] for r in results) else 1
if __name__=="__main__": raise SystemExit(main())
