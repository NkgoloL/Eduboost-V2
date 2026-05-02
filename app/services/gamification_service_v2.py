from __future__ import annotations

from typing import Any

from app.services.audit_service import AuditService


class GamificationServiceV2:
    def __init__(self, repository: Any | None = None) -> None:
        self.repository = repository or _EmptyGamificationRepository()

    async def get_profile(self, learner_id: str) -> dict:
        learner, badge_rows = await self.repository.get_profile_rows(learner_id)
        if learner is None:
            raise ValueError("Learner not found")
        total_xp = int(getattr(learner, "total_xp", getattr(learner, "xp", 0)))
        level = total_xp // 100 + 1
        badges = [
            {
                "badge_key": getattr(badge, "badge_key", ""),
                "name": getattr(badge, "name", ""),
                "earned_at": getattr(learner_badge, "earned_at", None),
            }
            for learner_badge, badge in badge_rows
        ]
        await AuditService().log_event("GAMIFICATION_PROFILE_READ", {}, learner_id)
        return {
            "learner_id": str(getattr(learner, "learner_id", learner_id)),
            "total_xp": total_xp,
            "streak_days": getattr(learner, "streak_days", 0),
            "level": level,
            "badges": badges,
        }

    async def leaderboard(self, limit: int = 10) -> list[dict]:
        rows = await self.repository.get_leaderboard_rows(limit=limit)
        return [
            {
                "learner_id": str(getattr(row, "learner_id", "")),
                "total_xp": int(getattr(row, "total_xp", getattr(row, "xp", 0))),
                "streak_days": getattr(row, "streak_days", 0),
            }
            for row in rows
        ]


class _EmptyGamificationRepository:
    async def get_profile_rows(self, learner_id: str):
        return None, []

    async def get_leaderboard_rows(self, limit: int = 10):
        return []
