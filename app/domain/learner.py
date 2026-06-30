from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Learner:
    id: str
    guardian_id: str
    display_name: str
    grade: int


__all__ = ["Learner"]
