from __future__ import annotations

from typing import Any


class DiagnosticServiceV2:
    def __init__(self, learner_repository: Any, quota_service: Any, diagnostic_repository: Any) -> None:
        self.learner_repository = learner_repository
        self.quota_service = quota_service
        self.diagnostic_repository = diagnostic_repository

    async def run_diagnostic(self, learner_id: str, subject_code: str) -> dict:
        learner = await self.learner_repository.get_by_id(learner_id)
        if learner is None:
            raise ValueError("Learner not found")
        cache_key = f"diagnostic:{learner_id}:{subject_code}"
        cached = await self.quota_service.get_cached(cache_key)
        if cached:
            return cached
        session = await self.diagnostic_repository.create_session(learner_id=learner_id, subject_code=subject_code)
        return {"session_id": getattr(session, "session_id", None), "learner_id": learner_id, "subject_code": subject_code}
