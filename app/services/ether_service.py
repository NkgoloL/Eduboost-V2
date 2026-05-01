"""V2 Ether service for psychological archetypes and onboarding."""

from __future__ import annotations

import uuid
from typing import Literal

from pydantic import BaseModel

from app.services.audit_service import AuditService

Archetype = Literal["Keter", "Chokhmah", "Binah", "Chesed", "Gevurah", "Tiferet", "Netzach", "Hod", "Yesod", "Malkuth"]


class OnboardingResponse(BaseModel):
    learner_id: str
    responses: list[int]  # 1-5 scale for 5 questions


class ArchetypeProfile(BaseModel):
    learner_id: str
    archetype: Archetype
    tone_modifier: str


class EtherService:
    """Manages the 'Ether' pillar: psychological profiling and tone adaptation."""

    def __init__(self) -> None:
        self.audit = AuditService()

    async def get_onboarding_questions(self) -> list[dict]:
        """Return the 5-question cold-start visual onboarding questions."""
        return [
            {"id": 1, "question": "Do you prefer pictures or words?", "options": ["Pictures", "Words"]},
            {"id": 2, "question": "How do you feel about math?", "options": ["Love it", "It's okay", "Hate it"]},
            {"id": 3, "question": "Do you like challenges?", "options": ["Yes, please!", "Sometimes", "Not really"]},
            {"id": 4, "question": "What is your favorite subject?", "options": ["Math", "Science", "Languages", "Arts"]},
            {"id": 5, "question": "How do you like to learn?", "options": ["Watching", "Doing", "Listening", "Reading"]},
        ]

    async def determine_archetype(self, onboarding: OnboardingResponse) -> ArchetypeProfile:
        """Map onboarding responses to a psychological archetype (V2 baseline)."""
        # Simplified mapping logic for V2 baseline
        score = sum(onboarding.responses)
        if score > 20:
            archetype = "Keter"
            tone = "Inspirational and visionary"
        elif score > 15:
            archetype = "Tiferet"
            tone = "Balanced and harmonious"
        else:
            archetype = "Yesod"
            tone = "Foundational and supportive"

        profile = ArchetypeProfile(
            learner_id=onboarding.learner_id,
            archetype=archetype,
            tone_modifier=tone,
        )

        await self.audit.log_event(
            event_type="ARCHETYPE_DETERMINED",
            learner_id=onboarding.learner_id,
            payload={"archetype": archetype, "score": score},
        )
        return profile
