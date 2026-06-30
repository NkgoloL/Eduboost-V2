import asyncio
from app.services.runtime_audit_facade import record_runtime_audit_event

class Sink:
    def __init__(self): self.events=[]
    async def record(self, **kw): self.events.append(kw); return {"ok": True}

def test_runtime_audit_facade_records():
    async def run():
        s=Sink()
        r=await record_runtime_audit_event(s, action="consent.granted", candidate_name="consent_audit_events", actor_id="a", learner_id="l", resource_type="learner_consent")
        assert r.resource_id=="l"
        assert s.events[0]["payload"]["runtime_audit_facade"] is True
    asyncio.run(run())
