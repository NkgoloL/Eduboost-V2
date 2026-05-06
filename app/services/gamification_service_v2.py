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
        total_xp = int(_read_field(learner, "total_xp", _read_field(learner, "xp", 0)))
        level = total_xp // 100 + 1
        badges = [
            {
                "badge_key": _read_field(badge, "badge_key", ""),
                "name": _read_field(badge, "name", ""),
                "earned_at": _read_field(learner_badge, "earned_at", None),
            }
            for learner_badge, badge in badge_rows
        ]
        await AuditService().log_event("GAMIFICATION_PROFILE_READ", {}, learner_id)
        return {
            "learner_id": str(_read_field(learner, "learner_id", _read_field(learner, "id", learner_id))),
            "total_xp": total_xp,
            "streak_days": _read_field(learner, "streak_days", 0),
            "level": level,
            "badges": badges,
        }

    async def leaderboard(self, limit: int = 10) -> list[dict]:
        rows = await self.repository.get_leaderboard_rows(limit=limit)
        return [
            {
                "learner_id": str(_read_field(row, "learner_id", _read_field(row, "id", ""))),
                "total_xp": int(_read_field(row, "total_xp", _read_field(row, "xp", 0))),
                "streak_days": _read_field(row, "streak_days", 0),
            }
            for row in rows
        ]


def _read_field(source: Any, field: str, default: Any = None) -> Any:
    if isinstance(source, dict):
        return source.get(field, default)
    return getattr(source, field, default)


class _EmptyGamificationRepository:
    async def get_profile_rows(self, learner_id: str):
        return None, []

    async def get_leaderboard_rows(self, limit: int = 10):
        return []
