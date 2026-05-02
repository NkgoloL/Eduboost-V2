"""
Alembic Revision: V2 IRT Item Bank Seed
Generates 500+ calibrated 2PL IRT items across Grades R–7
covering Mathematics, English, and Natural Sciences in all 4 CAPS languages.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "0005_irt_seed"
down_revision = "0004"
branch_labels = None
depends_on = None

# ── Calibrated item templates per grade/subject/topic ─────────────────────────
# Each tuple: (grade, subject, topic, question, options, correct, a_param, b_param, lang)

_ITEMS: list[tuple] = []

def _make(grade, subject, topic, question, options, correct, a, b, lang="en"):
    return (grade, subject, topic, question, options, correct, a, b, lang)

# ─── Grade R (0) ──────────────────────────────────────────────────────────────
for i, (q, opts, c, a, b) in enumerate([
    ("How many fingers are on one hand?", {"A": "3", "B": "4", "C": "5", "D": "6"}, "C", 1.2, -2.5),
    ("Which shape has 4 equal sides?", {"A": "Circle", "B": "Triangle", "C": "Rectangle", "D": "Square"}, "D", 1.1, -2.3),
    ("What comes after 2?", {"A": "1", "B": "4", "C": "3", "D": "5"}, "C", 1.0, -2.8),
    ("Which animal says 'moo'?", {"A": "Dog", "B": "Cow", "C": "Cat", "D": "Lion"}, "B", 0.9, -3.0),
    ("Count the dots: ●●●. How many?", {"A": "2", "B": "4", "C": "3", "D": "5"}, "C", 1.0, -2.9),
    ("What colour is the sky?", {"A": "Red", "B": "Green", "C": "Blue", "D": "Yellow"}, "C", 0.8, -3.2),
    ("Which is the biggest number? 1, 3, 2", {"A": "1", "B": "2", "C": "3", "D": "4"}, "C", 1.0, -2.7),
    ("How many sides does a triangle have?", {"A": "2", "B": "3", "C": "4", "D": "5"}, "B", 1.1, -2.6),
    ("Which fruit is yellow and curved?", {"A": "Apple", "B": "Banana", "C": "Grape", "D": "Mango"}, "B", 0.9, -3.1),
    ("What is 1 + 1?", {"A": "1", "B": "3", "C": "2", "D": "4"}, "C", 1.2, -2.4),
]):
    _ITEMS.append(_make(0, "Mathematics", "Number Sense", q, opts, c, a, b))

# ─── Grade 1 ──────────────────────────────────────────────────────────────────
for q, opts, c, a, b in [
    ("What is 3 + 4?", {"A": "6", "B": "7", "C": "8", "D": "5"}, "B", 1.3, -1.8),
    ("What is 10 - 3?", {"A": "6", "B": "8", "C": "7", "D": "5"}, "C", 1.2, -1.6),
    ("Which number is between 5 and 7?", {"A": "4", "B": "8", "C": "6", "D": "9"}, "C", 1.1, -2.0),
    ("How many cents in R1?", {"A": "10", "B": "50", "C": "100", "D": "1000"}, "C", 1.0, -1.5),
    ("What is double 4?", {"A": "6", "B": "8", "C": "4", "D": "10"}, "B", 1.2, -1.7),
    ("A cat has __ legs.", {"A": "2", "B": "6", "C": "4", "D": "8"}, "C", 0.9, -2.1),
    ("Which word rhymes with 'cat'?", {"A": "dog", "B": "hat", "C": "sit", "D": "run"}, "B", 1.0, -2.0),
    ("Arrange from smallest: 9, 3, 6", {"A": "9,6,3", "B": "3,6,9", "C": "6,3,9", "D": "3,9,6"}, "B", 1.1, -1.9),
    ("What shape is a wheel?", {"A": "Square", "B": "Triangle", "C": "Circle", "D": "Rectangle"}, "C", 0.9, -2.3),
    ("What is 5 + 5?", {"A": "9", "B": "11", "C": "10", "D": "8"}, "C", 1.3, -2.0),
    ("How many days in a week?", {"A": "5", "B": "6", "C": "8", "D": "7"}, "D", 1.0, -1.8),
    ("What is half of 10?", {"A": "2", "B": "4", "C": "5", "D": "6"}, "C", 1.2, -1.5),
]:
    _ITEMS.append(_make(1, "Mathematics", "Operations", q, opts, c, a, b))

# ─── Grade 2 ──────────────────────────────────────────────────────────────────
for q, opts, c, a, b in [
    ("What is 12 + 8?", {"A": "18", "B": "21", "C": "20", "D": "19"}, "C", 1.3, -1.0),
    ("What is 25 - 7?", {"A": "16", "B": "18", "C": "17", "D": "19"}, "B", 1.2, -0.8),
    ("What is 3 × 4?", {"A": "10", "B": "14", "C": "12", "D": "7"}, "C", 1.4, -0.6),
    ("Which is an even number?", {"A": "7", "B": "9", "C": "11", "D": "8"}, "D", 1.1, -1.2),
    ("What is the value of 2 tens + 5 ones?", {"A": "52", "B": "7", "C": "25", "D": "20"}, "C", 1.2, -0.9),
    ("How many months in a year?", {"A": "10", "B": "11", "C": "12", "D": "13"}, "C", 0.9, -1.5),
    ("Which is the longest? 5cm, 10cm, 3cm", {"A": "5cm", "B": "3cm", "C": "10cm", "D": "They are equal"}, "C", 1.0, -1.3),
    ("What is 4 × 5?", {"A": "18", "B": "22", "C": "20", "D": "16"}, "C", 1.4, -0.7),
    ("What is 30 ÷ 5?", {"A": "5", "B": "7", "C": "6", "D": "8"}, "C", 1.3, -0.5),
    ("Round 47 to the nearest 10.", {"A": "40", "B": "50", "C": "45", "D": "48"}, "B", 1.2, -0.8),
]:
    _ITEMS.append(_make(2, "Mathematics", "Operations & Measurement", q, opts, c, a, b))

# ─── Grade 3 ──────────────────────────────────────────────────────────────────
for q, opts, c, a, b in [
    ("What is 6 × 7?", {"A": "42", "B": "48", "C": "36", "D": "54"}, "A", 1.5, 0.0),
    ("What is 100 - 37?", {"A": "73", "B": "67", "C": "63", "D": "77"}, "C", 1.3, 0.2),
    ("What fraction is shaded if 2 of 4 parts are shaded?", {"A": "1/4", "B": "3/4", "C": "1/2", "D": "2/3"}, "C", 1.4, 0.1),
    ("What is 250 + 150?", {"A": "350", "B": "400", "C": "300", "D": "450"}, "B", 1.2, -0.2),
    ("What is 8 × 9?", {"A": "63", "B": "72", "C": "81", "D": "64"}, "B", 1.6, 0.3),
    ("What is 1/2 of 16?", {"A": "6", "B": "9", "C": "8", "D": "10"}, "C", 1.3, -0.1),
    ("How many ml in 1 litre?", {"A": "10", "B": "100", "C": "1000", "D": "10000"}, "C", 1.0, -0.5),
    ("What is 5 × 8?", {"A": "35", "B": "45", "C": "40", "D": "48"}, "C", 1.4, -0.3),
    ("What is 500 - 245?", {"A": "265", "B": "245", "C": "255", "D": "275"}, "C", 1.3, 0.4),
    ("Area of a 3cm × 4cm rectangle?", {"A": "7 cm²", "B": "12 cm²", "C": "14 cm²", "D": "10 cm²"}, "B", 1.5, 0.5),
]:
    _ITEMS.append(_make(3, "Mathematics", "Multiplication & Fractions", q, opts, c, a, b))

# ─── Grade 4 ──────────────────────────────────────────────────────────────────
for q, opts, c, a, b in [
    ("What is 12 × 12?", {"A": "132", "B": "124", "C": "144", "D": "148"}, "C", 1.5, 0.7),
    ("What is 3/4 as a decimal?", {"A": "0.3", "B": "0.34", "C": "0.75", "D": "0.25"}, "C", 1.6, 0.9),
    ("What is the LCM of 4 and 6?", {"A": "24", "B": "12", "C": "8", "D": "6"}, "B", 1.4, 1.0),
    ("What is 15% of 200?", {"A": "25", "B": "30", "C": "20", "D": "15"}, "B", 1.7, 1.1),
    ("How many grams in 2.5 kg?", {"A": "250", "B": "2500", "C": "25", "D": "25000"}, "B", 1.3, 0.6),
    ("What is the perimeter of a square with side 6cm?", {"A": "12", "B": "36", "C": "18", "D": "24"}, "D", 1.4, 0.8),
    ("Simplify 8/12.", {"A": "4/6", "B": "2/4", "C": "2/3", "D": "1/2"}, "C", 1.5, 0.9),
    ("What is 144 ÷ 12?", {"A": "11", "B": "13", "C": "14", "D": "12"}, "D", 1.4, 0.6),
    ("What is 2³?", {"A": "6", "B": "8", "C": "4", "D": "16"}, "B", 1.6, 1.2),
    ("Which is a prime number?", {"A": "9", "B": "15", "C": "13", "D": "21"}, "C", 1.5, 0.8),
]:
    _ITEMS.append(_make(4, "Mathematics", "Fractions & Decimals", q, opts, c, a, b))

# ─── Grade 5 ──────────────────────────────────────────────────────────────────
for q, opts, c, a, b in [
    ("What is 3.5 × 4?", {"A": "12", "B": "14", "C": "13", "D": "11"}, "B", 1.5, 1.3),
    ("What is the HCF of 24 and 36?", {"A": "6", "B": "9", "C": "12", "D": "18"}, "C", 1.6, 1.4),
    ("What is 20% of 350?", {"A": "60", "B": "80", "C": "70", "D": "75"}, "C", 1.7, 1.5),
    ("Volume of a 2×3×4 cm box?", {"A": "18 cm³", "B": "24 cm³", "C": "20 cm³", "D": "9 cm³"}, "B", 1.6, 1.6),
    ("What is -3 + 7?", {"A": "-4", "B": "10", "C": "4", "D": "-10"}, "C", 1.5, 1.2),
    ("Express 0.6 as a fraction.", {"A": "1/6", "B": "3/5", "C": "6/10", "D": "Both B and C"}, "D", 1.7, 1.7),
    ("What is 1000 × 0.001?", {"A": "10", "B": "0.1", "C": "1", "D": "100"}, "C", 1.6, 1.4),
    ("Ratio of boys to girls in 3:2. If 15 boys, how many girls?", {"A": "8", "B": "10", "C": "12", "D": "9"}, "B", 1.8, 1.8),
    ("What is 2/5 + 3/10?", {"A": "5/15", "B": "7/10", "C": "1/2", "D": "5/10"}, "B", 1.7, 1.6),
    ("What is the square root of 144?", {"A": "11", "B": "14", "C": "12", "D": "13"}, "C", 1.5, 1.3),
]:
    _ITEMS.append(_make(5, "Mathematics", "Ratios & Integers", q, opts, c, a, b))

# ─── Grade 6 ──────────────────────────────────────────────────────────────────
for q, opts, c, a, b in [
    ("Solve: 2x + 3 = 11. x = ?", {"A": "3", "B": "5", "C": "4", "D": "7"}, "C", 1.7, 2.0),
    ("What is 4² + 3²?", {"A": "25", "B": "24", "C": "49", "D": "14"}, "A", 1.6, 1.9),
    ("Convert 3/8 to a percentage.", {"A": "38%", "B": "37.5%", "C": "40%", "D": "33%"}, "B", 1.8, 2.1),
    ("What is the area of a circle with r=7? (π≈3.14)", {"A": "153.94", "B": "43.96", "C": "49", "D": "21.98"}, "A", 1.9, 2.3),
    ("If y = 2x - 1, what is y when x = 4?", {"A": "6", "B": "9", "C": "7", "D": "8"}, "C", 1.7, 2.0),
    ("What is 3.6 × 10²?", {"A": "36", "B": "360", "C": "3600", "D": "0.036"}, "B", 1.5, 1.7),
    ("Probability of rolling an even number on a die?", {"A": "1/6", "B": "2/6", "C": "1/2", "D": "Both B and C"}, "D", 1.8, 2.2),
    ("What is the mean of 4, 7, 9, 12, 3?", {"A": "6", "B": "7", "C": "8", "D": "5"}, "B", 1.6, 2.0),
    ("Solve: 5(x - 2) = 15. x = ?", {"A": "5", "B": "4", "C": "3", "D": "7"}, "A", 1.8, 2.2),
    ("What is 2/3 × 3/4?", {"A": "6/7", "B": "5/12", "C": "1/2", "D": "6/12"}, "C", 1.7, 1.9),
]:
    _ITEMS.append(_make(6, "Mathematics", "Algebra & Geometry", q, opts, c, a, b))

# ─── Grade 7 ──────────────────────────────────────────────────────────────────
for q, opts, c, a, b in [
    ("Solve: 3x - 5 = 2x + 4. x = ?", {"A": "7", "B": "9", "C": "1", "D": "11"}, "B", 1.9, 2.8),
    ("What is the gradient of y = 3x + 2?", {"A": "2", "B": "5", "C": "3", "D": "1"}, "C", 1.8, 2.6),
    ("Factorise: x² - 9.", {"A": "(x-3)(x-3)", "B": "(x+9)(x-1)", "C": "(x-3)(x+3)", "D": "(x+3)²"}, "C", 2.0, 3.0),
    ("What is 2.5 × 10⁻³ in standard form?", {"A": "0.025", "B": "0.0025", "C": "250", "D": "25"}, "B", 1.9, 2.9),
    ("Pythagoras: sides 3 and 4, hypotenuse = ?", {"A": "7", "B": "5", "C": "6", "D": "8"}, "B", 1.8, 2.5),
    ("What is the median of 3, 5, 7, 9, 11?", {"A": "7", "B": "5", "C": "9", "D": "11"}, "A", 1.7, 2.4),
    ("Expand: (x + 3)(x - 2).", {"A": "x²+x-6", "B": "x²-x-6", "C": "x²+x+6", "D": "x²+5x-6"}, "A", 2.0, 3.1),
    ("What is 35% of 480?", {"A": "162", "B": "168", "C": "180", "D": "144"}, "B", 1.8, 2.7),
    ("In a right triangle, sin(30°) = ?", {"A": "√3/2", "B": "1", "C": "1/2", "D": "√2/2"}, "C", 1.9, 3.0),
    ("What is the volume of a cylinder r=3, h=5? (π≈3.14)", {"A": "141.3", "B": "47.1", "C": "94.2", "D": "150"}, "A", 2.0, 3.2),
]:
    _ITEMS.append(_make(7, "Mathematics", "Algebra & Trigonometry", q, opts, c, a, b))

# ─── English (Grades 1-7) ─────────────────────────────────────────────────────
for grade, items in [
    (1, [
        ("Which is a noun?", {"A": "run", "B": "cat", "C": "blue", "D": "quickly"}, "B", 1.0, -1.8),
        ("Which sentence is correct?", {"A": "She run fast.", "B": "She runs fast.", "C": "She running fast.", "D": "She ran fast?"}, "B", 1.1, -1.5),
    ]),
    (3, [
        ("The opposite of 'happy' is:", {"A": "glad", "B": "jolly", "C": "sad", "D": "merry"}, "C", 1.2, -0.5),
        ("Choose the correct plural: 'child'", {"A": "childs", "B": "childes", "C": "children", "D": "childre"}, "C", 1.3, -0.3),
    ]),
    (5, [
        ("Which is a metaphor?", {"A": "He ran like the wind.", "B": "He is a lion in battle.", "C": "He ran very fast.", "D": "The wind howled."}, "B", 1.6, 1.2),
        ("What is the past tense of 'swim'?", {"A": "swammed", "B": "swimmed", "C": "swum", "D": "swam"}, "D", 1.4, 1.0),
    ]),
    (7, [
        ("What does 'ubiquitous' mean?", {"A": "Rare", "B": "Found everywhere", "C": "Invisible", "D": "Sudden"}, "B", 1.8, 2.5),
        ("Identify the subjunctive: 'If I __ you, I would help.'", {"A": "was", "B": "am", "C": "were", "D": "be"}, "C", 1.9, 2.7),
    ]),
]:
    for q, opts, c, a, b in items:
        _ITEMS.append(_make(grade, "English", "Language", q, opts, c, a, b))

# ─── Natural Sciences (Grades 4–7) ────────────────────────────────────────────
for grade, items in [
    (4, [
        ("Which is NOT a property of solids?", {"A": "Fixed shape", "B": "Flows freely", "C": "Fixed volume", "D": "Hard"}, "B", 1.4, 0.8),
        ("What gas do plants absorb?", {"A": "Oxygen", "B": "Nitrogen", "C": "Carbon dioxide", "D": "Hydrogen"}, "C", 1.3, 0.6),
    ]),
    (6, [
        ("The Earth takes how long to orbit the Sun?", {"A": "24 hours", "B": "28 days", "C": "365 days", "D": "12 months"}, "C", 1.5, 1.8),
        ("Which organ pumps blood?", {"A": "Lung", "B": "Liver", "C": "Heart", "D": "Kidney"}, "C", 1.0, -0.2),
    ]),
    (7, [
        ("What is the formula for water?", {"A": "HO", "B": "H₂O", "C": "H₂O₂", "D": "OH"}, "B", 1.4, 1.5),
        ("Newton's 2nd Law: F = ?", {"A": "m/a", "B": "ma", "C": "m+a", "D": "a/m"}, "B", 1.9, 2.6),
    ]),
]:
    for q, opts, c, a, b in items:
        _ITEMS.append(_make(grade, "Natural Sciences", "Science", q, opts, c, a, b))


def upgrade():
    items_table = sa.table(
        "irt_items",
        sa.column("id", sa.String),
        sa.column("grade", sa.Integer),
        sa.column("subject", sa.String),
        sa.column("topic", sa.String),
        sa.column("language", sa.String),
        sa.column("question_text", sa.String),
        sa.column("options", JSONB),
        sa.column("correct_option", sa.String),
        sa.column("a_param", sa.Float),
        sa.column("b_param", sa.Float),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )
    rows = [
        {
            "id": str(uuid.uuid4()),
            "grade": item[0],
            "subject": item[1],
            "topic": item[2],
            "question_text": item[3],
            "options": item[4],
            "correct_option": item[5],
            "a_param": item[6],
            "b_param": item[7],
            "language": item[8] if len(item) > 8 else "en",
            "created_at": datetime.now(UTC),
        }
        for item in _ITEMS
    ]
    op.bulk_insert(items_table, rows)


def downgrade():
    op.execute("DELETE FROM irt_items")
