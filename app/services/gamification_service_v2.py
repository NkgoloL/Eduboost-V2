"""V2 gamification service."""

from __future__ import annotations

from app.repositories.gamification_repository import GamificationRepository
from app.services.audit_service import AuditService


class GamificationServiceV2:
    def __init__(self, repository: GamificationRepository | None = None) -> None:
        self.repository = repository or GamificationRepository()

    async def get_profile(self, learner_id: str) -> dict:
        learner, rows = await self.repository.get_profile_rows(learner_id)
        if learner is None:
            raise ValueError("Learner not found")
        profile = {
            "learner_id": str(learner.learner_id),
            "total_xp": learner.total_xp,
            "streak_days": learner.streak_days,
            "level": max(1, (learner.total_xp // 100) + 1),
            "badges": [
                {
                    "badge_key": badge.badge_key,
                    "name": badge.name,
                    "earned_at": learner_badge.earned_at.isoformat() if learner_badge.earned_at else None,
                }
                for learner_badge, badge in rows
            ],
        }
        await AuditService().log_event(
            event_type="GAMIFICATION_PROFILE_READ",
            learner_id=str(learner.learner_id),
            payload={"level": profile["level"], "badge_count": len(profile["badges"])},
        )
        return profile

    async def leaderboard(self, limit: int = 10) -> list[dict]:
        learners = await self.repository.get_leaderboard_rows(limit=limit)
        return [
            {
                "learner_id": str(learner.learner_id),
                "total_xp": learner.total_xp,
                "streak_days": learner.streak_days,
                "level": max(1, (learner.total_xp // 100) + 1),
            }
            for learner in learners
        ]
