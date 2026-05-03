from dataclasses import dataclass

from app.modules.learners.ether_service import EtherService


@dataclass(slots=True)
class OnboardingResponse:
    archetype: str
    description: str


__all__ = ["EtherService", "OnboardingResponse"]
