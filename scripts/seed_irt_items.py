"""Seed initial IRT-calibrated CAPS items into the database."""

import asyncio
import uuid
import json
from sqlalchemy import text
from app.api.core.database import AsyncSessionFactory

# Sample CAPS-aligned questions for Grade 4 Mathematics
GRADE_4_MATH_QUESTIONS = [
    {
        "question_id": "q4m_001",
        "question_text": "What is 456 + 123?",
        "options": ["579", "589", "569", "578"],
        "correct_answer": "579",
        "difficulty": -1.5, # Easy
        "marks": 1,
        "caps_topic": "Whole numbers: Addition"
    },
    {
        "question_id": "q4m_002",
        "question_text": "Which of these is a common fraction?",
        "options": ["1/2", "0.5", "50%", "2"],
        "correct_answer": "1/2",
        "difficulty": 0.0, # Medium
        "marks": 2,
        "caps_topic": "Common fractions"
    },
    {
        "question_id": "q4m_003",
        "question_text": "If a rectangle has a length of 5cm and width of 3cm, what is its perimeter?",
        "options": ["16cm", "15cm", "8cm", "11cm"],
        "correct_answer": "16cm",
        "difficulty": 1.2, # Hard
        "marks": 3,
        "caps_topic": "Length: Perimeter"
    }
]

async def seed_irt_items():
    async with AsyncSessionFactory() as session:
        print("Seeding IRT Items...")
        
        assessment_id = str(uuid.uuid4())
        
        await session.execute(
            text(
                "INSERT INTO assessments (assessment_id, title, subject_code, grade_level, assessment_type, total_marks, questions, is_active) "
                "VALUES (:id, :title, :subject, :grade, :type, :marks, :questions, :active)"
            ),
            {
                "id": assessment_id,
                "title": "Grade 4 Mathematics: Baseline IRT Assessment",
                "subject": "MATH",
                "grade": 4,
                "type": "diagnostic",
                "marks": 6,
                "questions": json.dumps(GRADE_4_MATH_QUESTIONS),
                "active": True
            }
        )
        await session.commit()
        print(f"Successfully seeded assessment with ID: {assessment_id}")

if __name__ == "__main__":
    asyncio.run(seed_irt_items())
