import asyncio
from app.services.runtime_consent_facade import emit_consent_runtime_event
class Sink:
    def __init__(self): self.events=[]
    async def record(self, **kw): self.events.append(kw); return {"ok": True}
def test_emit_consent_runtime_event_records():
    async def run():
        s=Sink(); r=await emit_consent_runtime_event(action="consent.granted", learner_id="l", actor_id="a", audit_repository=s)
        assert r.operation_type=="write"; assert r.audit_recorded; assert s.events
    asyncio.run(run())
