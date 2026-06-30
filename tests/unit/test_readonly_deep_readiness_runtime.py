import asyncio
from app.services.deep_readiness_runtime import run_deep_readiness_runtime_checks
class R:
    def scalar(self): return 1
class S:
    def __init__(self): self.statements=[]
    async def execute(self, statement): self.statements.append(str(statement)); return R()
def test_deep_readiness_sql_is_read_only():
    async def run():
        s=S(); result=await run_deep_readiness_runtime_checks(db_session=s, required_tables=("users",))
        assert result.status=="pass"; joined=" ".join(s.statements).lower()
        assert "select" in joined and "insert" not in joined and "update" not in joined and "delete" not in joined
    asyncio.run(run())
