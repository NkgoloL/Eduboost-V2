from __future__ import annotations

from collections import defaultdict
from uuid import UUID

from app.repositories.mastery_repository import MasteryRepository
from app.modules.progress.learning_velocity_service import LearningVelocityService


class ProgressTimelineService:
    def __init__(self, mastery_repository: MasteryRepository) -> None:
        self.repo = mastery_repository
        self.velocity = LearningVelocityService()

    async def get_topic_progress_timeline(self, learner_id: str | UUID, caps_ref: str) -> list[dict]:
        rows = await self.repo.get_snapshots_for_learner_topic(learner_id, caps_ref)
        return [
            {"snapshot_at": row.snapshot_at.isoformat(), "mastery_score": row.mastery_score, "mastery_label": row.mastery_label, "trigger": row.trigger}
            for row in rows
        ]

    async def get_subject_mastery_summary(self, learner_id: str | UUID, subject: str | None = None, grade: int | None = None) -> dict:
        rows = await self.repo.list_topic_mastery_by_learner(learner_id)
        groups: dict[str, list] = defaultdict(list)
        for row in rows:
            if subject and subject not in row.caps_ref:
                continue
            groups[row.caps_ref.split('.')[1] if '.' in row.caps_ref else 'unknown'].append(row)
        summaries = []
        for key, values in groups.items():
            avg = sum(float(v.mastery_score) for v in values) / len(values)
            summaries.append({"subject_code": key, "topic_count": len(values), "average_mastery": round(avg, 4)})
        return {"learner_id": str(learner_id), "subjects": summaries, "next_best_activities": self.velocity.next_best_activities(rows)}
