"""Deterministic executive-service compatibility layer."""

from __future__ import annotations


class ExecutiveService:
    async def generate_progress_summary(
        self,
        pseudonym_id: str,
        top_gaps: list[str],
        lessons_completed: int,
    ) -> str:
        focus = ", ".join(top_gaps) if top_gaps else "core skills"
        return (
            f"Learner {pseudonym_id} completed {lessons_completed} lesson(s) recently. "
            f"Recommended focus: {focus}."
        )


__all__ = ["ExecutiveService"]
