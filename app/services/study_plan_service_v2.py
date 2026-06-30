from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.services.audit_service import AuditService


class StudyPlanServiceV2:
    def __init__(self, learner_repository: Any | None = None, study_plan_repository: Any | None = None) -> None:
        self.learner_repository = learner_repository or _MissingLearnerRepository()
        self.study_plan_repository = study_plan_repository or _MemoryStudyPlanRepository()

    async def generate_plan(self, learner_id: str, gap_ratio: float = 0.4) -> dict:
        learner = await self.learner_repository.get_by_id(learner_id)
        if learner is None:
            raise ValueError("Learner not found")
        mastery = await self.study_plan_repository.get_subject_mastery(learner_id)
        weak = sorted(mastery, key=lambda m: m.get("mastery_score", 1.0))[:2]
        week_focus = "Balanced revision and grade-level progress"
        if weak:
            week_focus = "Focus on " + ", ".join(item.get("subject_code", "subject") for item in weak)
        learner_grade = getattr(learner, "grade", None) or getattr(learner, "grade_level", None)
        schedule = _build_schedule(weak, learner_grade=learner_grade)
        plan = await self.study_plan_repository.create(
            learner_id=learner_id,
            schedule=schedule,
            gap_ratio=gap_ratio if weak else min(gap_ratio, 0.2),
            week_focus=week_focus,
        )
        await AuditService().log_event("STUDY_PLAN_CREATED", {"week_focus": week_focus}, learner_id)
        return {
            **plan,
            "schedule": schedule,
            "days": schedule,
            "week_focus": week_focus,
        }

    async def list_plans(self, learner_id: str) -> list[dict]:
        learner = await self.learner_repository.get_by_id(learner_id)
        if learner is None:
            raise ValueError("Learner not found")
        return await self.study_plan_repository.list_for_learner(learner_id)


class _MissingLearnerRepository:
    async def get_by_id(self, learner_id: str):
        return None


class _MemoryStudyPlanRepository:
    async def get_subject_mastery(self, learner_id: str):
        return []

    async def create(self, **kwargs):
        return {"plan_id": "local-plan", **kwargs}

    async def list_for_learner(self, learner_id: str):
        return []


_REPO_ROOT = Path(__file__).resolve().parents[2]
_LAUNCH_TEMPLATE_PATH = _REPO_ROOT / "data" / "generated" / "study_plans" / "grade4_maths_launch_templates.json"


def _load_launch_template() -> dict | None:
    if not _LAUNCH_TEMPLATE_PATH.exists():
        return None
    try:
        return json.loads(_LAUNCH_TEMPLATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None


def _weak_caps_refs(weak: list[dict]) -> set[str]:
    refs: set[str] = set()
    for row in weak:
        for gap in row.get("knowledge_gaps") or []:
            if isinstance(gap, str) and gap.count(".") >= 3:
                refs.add(gap)
            elif isinstance(gap, dict):
                ref = gap.get("caps_ref") or gap.get("caps_reference")
                if ref:
                    refs.add(str(ref))
    return refs


def _template_lookup(template: dict) -> dict[str, dict]:
    return {entry["caps_ref"]: entry for entry in template.get("topic_sequence", [])}


def _build_template_schedule(weak: list[dict], learner_grade: int | None) -> dict[str, list[dict]] | None:
    if learner_grade not in {4, None}:
        return None
    template = _load_launch_template()
    if not template:
        return None
    topics = _template_lookup(template)
    weak_refs = _weak_caps_refs(weak)
    days = {"Mon": [], "Tue": [], "Wed": [], "Thu": [], "Fri": [], "Sat": [], "Sun": []}
    for slot in template.get("weekly_template", []):
        ref = slot["caps_ref"]
        topic = topics.get(ref, {})
        priority = "gap-fill" if not weak_refs or ref in weak_refs else "curriculum"
        days.setdefault(slot["day"], []).append({
            "label": topic.get("topic", ref),
            "type": priority,
            "caps_ref": ref,
            "subject": "Mathematics",
            "topic": topic.get("topic", ref),
            "activity_type": slot.get("activity_type", "lesson"),
            "lesson_variant": slot.get("lesson_variant", "standard"),
            "assessment_blueprint_id": slot.get("assessment_blueprint_id"),
            "lesson_href": f"/lesson?caps_ref={ref}",
        })
    return days


def _build_schedule(weak: list[dict], learner_grade: int | None = None) -> dict[str, list[dict]]:
    template_schedule = _build_template_schedule(weak, learner_grade)
    if template_schedule:
        return template_schedule

    gap_subjects = [item.get("subject_code", "General Review") for item in weak if item.get("subject_code")]
    if not gap_subjects:
        gap_subjects = ["English", "Mathematics"]

    weekday_topics = [
        {"label": f"{gap_subjects[0]} Review", "emoji": "📘", "type": "curriculum"},
        {"label": f"{gap_subjects[-1]} Practice", "emoji": "📝", "type": "gap-fill"},
        {"label": "Reading and Reflection", "emoji": "📖", "type": "curriculum"},
        {"label": "Problem Solving", "emoji": "🧠", "type": "gap-fill"},
        {"label": "Weekly Challenge", "emoji": "🏆", "type": "curriculum"},
    ]

    return {
        "Mon": [weekday_topics[0]],
        "Tue": [weekday_topics[1]],
        "Wed": [weekday_topics[2]],
        "Thu": [weekday_topics[3]],
        "Fri": [weekday_topics[4]],
        "Sat": [],
        "Sun": [],
    }
