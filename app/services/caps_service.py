"""CAPS Alignment Service — validates content against South African curriculum standards."""

from __future__ import annotations

import re
from typing import Any

class CAPSService:
    """Provides validation rules for CAPS (Curriculum and Assessment Policy Statement)."""

    GRADE_TOPICS = {
        4: {
            "MATH": ["Whole numbers", "Addition and subtraction", "Common fractions", "Length"],
            "NS": ["Living and non-living things", "Structure of plants and animals", "Matter and materials"],
        },
        5: {
            "MATH": ["Whole numbers", "Multiplication and division", "Area and perimeter"],
            "NS": ["Plants and animals on Earth", "Skeletons", "Food chains"],
        },
        # Expanded as needed for Grade 4-7
    }

    @classmethod
    def validate_lesson_alignment(cls, grade_level: int, subject_code: str, topic: str, content: dict[str, Any]) -> dict[str, Any]:
        """Verify if the generated lesson matches CAPS expectations for the grade/subject."""
        issues = []
        
        # 1. Topic Match (Basic check)
        valid_topics = cls.GRADE_TOPICS.get(grade_level, {}).get(subject_code.upper(), [])
        topic_found = any(vt.lower() in topic.lower() for vt in valid_topics)
        if valid_topics and not topic_found:
            issues.append(f"Topic '{topic}' may not be standard for Grade {grade_level} {subject_code}.")

        # 2. Reading Level (Heuristic: Average word length/sentence complexity)
        # Grade 4-7 should avoid overly complex academic jargon without definitions.
        text_blob = str(content.get("story_hook", "")) + str(content.get("worked_example", ""))
        words = text_blob.split()
        if words:
            avg_len = sum(len(w) for w in words) / len(words)
            if avg_len > 7 and grade_level < 6:
                issues.append("Language complexity may be too high for Grade 4-5.")

        # 3. Cultural Context (SA-specific markers)
        sa_markers = ["rand", "R", "ubuntu", "braai", "safari", "protea", "springbok", "limpopo", "gauteng"]
        has_sa_context = any(m.lower() in text_blob.lower() for m in sa_markers)
        if not has_sa_context:
            issues.append("Lesson lacks explicit South African cultural context.")

        return {
            "is_aligned": len(issues) == 0,
            "issues": issues,
            "grade_level": grade_level,
            "subject_code": subject_code,
        }
