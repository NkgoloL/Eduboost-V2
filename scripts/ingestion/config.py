"""
EduBoost SA — Ingestion System Configuration
=============================================
Source registry, CAPS curriculum taxonomy, HuggingFace dataset catalogue,
and authoritative international→CAPS mapping tables.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ─── CAPS Taxonomy ───────────────────────────────────────────────────────────

class CAPSPhase(str, Enum):
    FOUNDATION    = "foundation"    # Grades 1–3
    INTERMEDIATE  = "intermediate"  # Grades 4–6
    SENIOR        = "senior"        # Grades 7–9
    FET           = "fet"           # Grades 10–12


class CAPSSubject(str, Enum):
    MATHEMATICS           = "mathematics"
    MATHEMATICAL_LITERACY = "mathematical_literacy"
    ENGLISH_HOME          = "english_home_language"
    ENGLISH_FAL           = "english_first_additional_language"
    AFRIKAANS_HOME        = "afrikaans_home_language"
    AFRIKAANS_FAL         = "afrikaans_first_additional_language"
    ZULU_HOME             = "isizulu_home_language"
    XHOSA_HOME            = "isixhosa_home_language"
    NATURAL_SCIENCES      = "natural_sciences"
    LIFE_SCIENCES         = "life_sciences"
    PHYSICAL_SCIENCES     = "physical_sciences"
    SOCIAL_SCIENCES       = "social_sciences"
    HISTORY               = "history"
    GEOGRAPHY             = "geography"
    LIFE_ORIENTATION      = "life_orientation"
    TECHNOLOGY            = "technology"
    EMS                   = "economic_management_sciences"
    ACCOUNTING            = "accounting"
    ECONOMICS             = "economics"
    BUSINESS_STUDIES      = "business_studies"
    CREATIVE_ARTS         = "creative_arts"
    PHYSICAL_EDUCATION    = "physical_education"


GRADE_TO_PHASE: dict[int, CAPSPhase] = {
    1: CAPSPhase.FOUNDATION,   2: CAPSPhase.FOUNDATION,   3: CAPSPhase.FOUNDATION,
    4: CAPSPhase.INTERMEDIATE, 5: CAPSPhase.INTERMEDIATE, 6: CAPSPhase.INTERMEDIATE,
    7: CAPSPhase.SENIOR,       8: CAPSPhase.SENIOR,       9: CAPSPhase.SENIOR,
    10: CAPSPhase.FET,         11: CAPSPhase.FET,         12: CAPSPhase.FET,
}

# CAPS Mathematics topic codes by phase
CAPS_MATHS_TOPICS: dict[CAPSPhase, dict[str, str]] = {
    CAPSPhase.FOUNDATION: {
        "NOR": "Numbers, Operations and Relationships",
        "PFA": "Patterns, Functions and Algebra",
        "SS":  "Space and Shape",
        "M":   "Measurement",
        "DH":  "Data Handling",
    },
    CAPSPhase.INTERMEDIATE: {
        "NOR": "Numbers, Operations and Relationships",
        "PFA": "Patterns, Functions and Algebra",
        "SS":  "Space and Shape",
        "M":   "Measurement",
        "DH":  "Data Handling",
    },
    CAPSPhase.SENIOR: {
        "NOR": "Numbers, Operations and Relationships",
        "PFA": "Patterns, Functions and Algebra",
        "SSM": "Space, Shape and Measurement",
        "DH":  "Data Handling",
    },
    CAPSPhase.FET: {
        "F":   "Functions",
        "NPS": "Number Patterns, Sequences and Series",
        "FGD": "Finance, Growth and Decay",
        "A":   "Algebra",
        "DC":  "Differential Calculus",
        "P":   "Probability",
        "EG":  "Euclidean Geometry and Measurement",
        "ST":  "Statistics",
        "AG":  "Analytical Geometry",
        "T":   "Trigonometry",
    },
}

# CAPS Natural Sciences / Life Sciences topic codes
CAPS_SCIENCE_TOPICS: dict[CAPSPhase, dict[str, str]] = {
    CAPSPhase.INTERMEDIATE: {
        "LL":  "Life and Living",
        "MM":  "Matter and Materials",
        "EC":  "Energy and Change",
        "PEB": "Planet Earth and Beyond",
    },
    CAPSPhase.SENIOR: {
        "LL":  "Life and Living",
        "MM":  "Matter and Materials",
        "EC":  "Energy and Change",
        "PEB": "Planet Earth and Beyond",
    },
    CAPSPhase.FET: {
        # Life Sciences
        "BA":  "Biodiversity and Classification",
        "CE":  "Cell Biology and Ecology",
        "HH":  "Human Health",
        "GE":  "Genetics and Inheritance",
        "EV":  "Evolution",
        # Physical Sciences
        "M":   "Mechanics",
        "W":   "Waves, Sound and Light",
        "EC":  "Electricity and Magnetism",
        "CH":  "Chemical Systems",
        "CR":  "Chemical Reactions",
        "MR":  "Matter and Materials",
    },
}


# ─── Source Definitions ───────────────────────────────────────────────────────

@dataclass
class SourceConfig:
    id:                   str
    name:                 str
    base_url:             str
    robots_txt_url:       str
    rate_limit_rps:       float          # requests per second
    license:              str   = "unknown"
    jurisdiction:         str   = "global"
    api_base:             str | None = None
    requires_playwright:  bool  = False
    enabled:              bool  = True
    grade_range:          tuple[int, int] = (1, 12)
    extra:                dict[str, Any] = field(default_factory=dict)


SOURCES: dict[str, SourceConfig] = {

    # ── Global Open Platforms ────────────────────────────────────────────────
    "khan_academy": SourceConfig(
        id             = "khan_academy",
        name           = "Khan Academy",
        base_url       = "https://www.khanacademy.org",
        api_base       = "https://www.khanacademy.org/api/v1",
        rate_limit_rps = 0.5,
        robots_txt_url = "https://www.khanacademy.org/robots.txt",
        license        = "CC BY-NC-SA 4.0",
        grade_range    = (1, 12),
        extra          = {
            "topic_tree_url": "https://www.khanacademy.org/api/v1/topictree",
            "content_kinds": ["Exercise", "Article", "Video"],
        },
    ),
    "openstax": SourceConfig(
        id             = "openstax",
        name           = "OpenStax",
        base_url       = "https://openstax.org",
        api_base       = "https://openstax.org/api/v2",
        rate_limit_rps = 1.0,
        robots_txt_url = "https://openstax.org/robots.txt",
        license        = "CC BY 4.0",
        grade_range    = (6, 12),
        extra          = {
            "books_url": "https://openstax.org/api/v2/books",
            "rex_base":  "https://openstax.org/books",
        },
    ),
    "ck12": SourceConfig(
        id             = "ck12",
        name           = "CK-12 Foundation",
        base_url       = "https://www.ck12.org",
        api_base       = "https://api.ck12.org/api/v1",
        rate_limit_rps = 0.5,
        robots_txt_url = "https://www.ck12.org/robots.txt",
        license        = "CC BY-NC 3.0",
        grade_range    = (1, 12),
        extra          = {
            "subject_url": "https://api.ck12.org/api/v1/subject/",
            "search_url":  "https://api.ck12.org/api/v1/search/",
        },
    ),
    "bbc_bitesize": SourceConfig(
        id                  = "bbc_bitesize",
        name                = "BBC Bitesize",
        base_url            = "https://www.bbc.co.uk/bitesize",
        rate_limit_rps      = 0.3,
        robots_txt_url      = "https://www.bbc.co.uk/robots.txt",
        requires_playwright = True,
        license             = "BBC Educational (Non-Commercial)",
        jurisdiction        = "uk",
        grade_range         = (1, 12),
    ),
    "commonlit": SourceConfig(
        id             = "commonlit",
        name           = "CommonLit (ELA Passages)",
        base_url       = "https://www.commonlit.org",
        rate_limit_rps = 0.3,
        robots_txt_url = "https://www.commonlit.org/robots.txt",
        license        = "CC BY-NC-SA 4.0",
        jurisdiction   = "us",
        grade_range    = (3, 12),
    ),
    "libretexts": SourceConfig(
        id             = "libretexts",
        name           = "LibreTexts",
        base_url       = "https://libretexts.org",
        api_base       = "https://api.libretexts.org",
        rate_limit_rps = 0.5,
        robots_txt_url = "https://libretexts.org/robots.txt",
        license        = "CC BY 4.0",
        grade_range    = (9, 12),
    ),

    # ── South African Specific ───────────────────────────────────────────────
    "siyavula": SourceConfig(
        id             = "siyavula",
        name           = "Siyavula Open Textbooks",
        base_url       = "https://www.siyavula.com",
        rate_limit_rps = 0.5,
        robots_txt_url = "https://www.siyavula.com/robots.txt",
        license        = "CC BY 4.0",
        jurisdiction   = "za",
        grade_range    = (7, 12),
        extra          = {
            "books": {
                "maths-gr7": "https://www.siyavula.com/read/maths/grade-7",
                "maths-gr8": "https://www.siyavula.com/read/maths/grade-8",
                "maths-gr9": "https://www.siyavula.com/read/maths/grade-9",
                "maths-gr10": "https://www.siyavula.com/read/maths/grade-10",
                "maths-gr11": "https://www.siyavula.com/read/maths/grade-11",
                "maths-gr12": "https://www.siyavula.com/read/maths/grade-12",
                "science-gr10": "https://www.siyavula.com/read/science/grade-10",
                "science-gr11": "https://www.siyavula.com/read/science/grade-11",
                "science-gr12": "https://www.siyavula.com/read/science/grade-12",
            }
        },
    ),
    "dbe": SourceConfig(
        id             = "dbe",
        name           = "DBE South Africa (Dept. of Basic Education)",
        base_url       = "https://www.education.gov.za",
        rate_limit_rps = 0.2,
        robots_txt_url = "https://www.education.gov.za/robots.txt",
        license        = "Government Open License (ZA)",
        jurisdiction   = "za",
        grade_range    = (1, 12),
        extra          = {
            "curriculum_url": "https://www.education.gov.za/Curriculum/CurriculumAssessmentPolicyStatements(CAPS).aspx",
            "mind_the_gap":   "https://www.education.gov.za/Curriculum/LearningandTeachingSupportMaterials(LTSM)/MindtheGapStudyGuides/tabid/670/Default.aspx",
        },
    ),
    "wced": SourceConfig(
        id             = "wced",
        name           = "Western Cape Education Department",
        base_url       = "https://wcedonline.wced.school.za",
        rate_limit_rps = 0.2,
        robots_txt_url = "https://wcedonline.wced.school.za/robots.txt",
        license        = "Government Open License (ZA)",
        jurisdiction   = "za",
        grade_range    = (1, 12),
    ),
}

# ─── HuggingFace Open Datasets Catalogue ─────────────────────────────────────

HF_DATASETS: list[dict[str, Any]] = [
    # ── Assessment / QA Benchmarks ──────────────────────────────────────────
    {
        "id": "arc",
        "hf_id": "allenai/ai2_arc",
        "subsets": ["ARC-Easy", "ARC-Challenge"],
        "grade_range": (3, 9),
        "subjects": ["natural_sciences"],
        "license": "CC BY-SA 4.0",
        "description": "AI2 Reasoning Challenge — grade-school science MCQs",
        "splits": ["train", "validation", "test"],
    },
    {
        "id": "mmlu",
        "hf_id": "cais/mmlu",
        "subsets": [
            "elementary_mathematics", "high_school_mathematics",
            "high_school_physics", "high_school_chemistry",
            "high_school_biology", "high_school_geography",
            "high_school_history", "world_history",
            "high_school_english", "high_school_european_history",
            "high_school_government_and_politics",
        ],
        "grade_range": (9, 12),
        "subjects": "multi",
        "license": "MIT",
        "description": "Massive Multitask Language Understanding — HS/college level",
        "splits": ["test"],
    },
    {
        "id": "sciq",
        "hf_id": "sciq",
        "subsets": None,
        "grade_range": (4, 9),
        "subjects": ["natural_sciences"],
        "license": "CC BY-NC 3.0",
        "description": "Science QA dataset with support paragraphs",
        "splits": ["train", "validation", "test"],
    },
    {
        "id": "openbookqa",
        "hf_id": "allenai/openbookqa",
        "subsets": ["main"],
        "grade_range": (4, 8),
        "subjects": ["natural_sciences"],
        "license": "Apache 2.0",
        "description": "Open book-style elementary science questions",
        "splits": ["train", "validation", "test"],
    },
    {
        "id": "gsm8k",
        "hf_id": "openai/gsm8k",
        "subsets": ["main", "socratic"],
        "grade_range": (3, 8),
        "subjects": ["mathematics"],
        "license": "MIT",
        "description": "Grade-school math word problems with chain-of-thought solutions",
        "splits": ["train", "test"],
    },
    {
        "id": "math",
        "hf_id": "lighteval/MATH",
        "subsets": [
            "algebra", "counting_and_probability", "geometry",
            "intermediate_algebra", "number_theory",
            "prealgebra", "precalculus",
        ],
        "grade_range": (7, 12),
        "subjects": ["mathematics"],
        "license": "MIT",
        "description": "Competition math with full step-by-step solutions",
        "splits": ["train", "test"],
    },
    {
        "id": "mathqa",
        "hf_id": "math_qa",
        "subsets": None,
        "grade_range": (7, 12),
        "subjects": ["mathematics"],
        "license": "Apache 2.0",
        "description": "Math word problems with answer derivation chains",
        "splits": ["train", "validation", "test"],
    },
    # ── Reading / ELA ────────────────────────────────────────────────────────
    {
        "id": "race",
        "hf_id": "ehovy/race",
        "subsets": ["middle", "high"],
        "grade_range": (6, 12),
        "subjects": ["english_home_language"],
        "license": "MIT",
        "description": "Reading comprehension passages from Chinese English exams",
        "splits": ["train", "validation", "test"],
    },
    {
        "id": "squad",
        "hf_id": "rajpurkar/squad",
        "subsets": None,
        "grade_range": (6, 12),
        "subjects": ["english_home_language"],
        "license": "CC BY-SA 4.0",
        "description": "Stanford QA on Wikipedia passages — extractive reading comp.",
        "splits": ["train", "validation"],
    },
    # ── Social Sciences / History / Geography ────────────────────────────────
    {
        "id": "triviaqa",
        "hf_id": "mandarjoshi/trivia_qa",
        "subsets": ["rc", "unfiltered"],
        "grade_range": (7, 12),
        "subjects": ["history", "geography", "social_sciences"],
        "license": "Apache 2.0",
        "description": "Trivia QA with evidence documents (history, science, culture)",
        "splits": ["train", "validation"],
    },
    {
        "id": "natural_questions",
        "hf_id": "google-research-datasets/natural_questions",
        "subsets": None,
        "grade_range": (7, 12),
        "subjects": "multi",
        "license": "Apache 2.0",
        "description": "Real Google search questions with long-form Wikipedia answers",
        "splits": ["train", "validation"],
    },
    # ── South African Specific ───────────────────────────────────────────────
    {
        "id": "afriqa",
        "hf_id": "masakhane/afriqa",
        "subsets": ["zul", "xho", "afr"],
        "grade_range": (4, 12),
        "subjects": "multi",
        "license": "Apache 2.0",
        "description": "African QA dataset including Zulu, Xhosa, Afrikaans",
        "splits": ["train", "test"],
    },
    {
        "id": "nchlt",
        "hf_id": "nchlt",
        "subsets": ["afr", "zul", "xho", "sot", "tsn", "ven"],
        "grade_range": (1, 12),
        "subjects": ["english_fal", "afrikaans_home_language"],
        "license": "CC BY 4.0",
        "description": "NCHLT South African language corpora",
        "splits": ["train"],
    },
]

# ─── International → CAPS Subject Mapping ────────────────────────────────────

SUBJECT_NORMALISATION: dict[str, str] = {
    # Mathematics variants
    "math": "mathematics", "maths": "mathematics",
    "elementary mathematics": "mathematics",
    "arithmetic": "mathematics",
    "algebra": "mathematics", "geometry": "mathematics",
    "trigonometry": "mathematics", "calculus": "mathematics",
    "statistics": "mathematics", "number theory": "mathematics",
    "precalculus": "mathematics", "prealgebra": "mathematics",
    "mathematical literacy": "mathematical_literacy",
    "numeracy": "mathematics",

    # Sciences
    "science": "natural_sciences",
    "natural science": "natural_sciences",
    "natural sciences": "natural_sciences",
    "biology": "life_sciences",
    "life science": "life_sciences",
    "life sciences": "life_sciences",
    "physics": "physical_sciences",
    "chemistry": "physical_sciences",
    "physical science": "physical_sciences",
    "physical sciences": "physical_sciences",
    "earth science": "natural_sciences",
    "environmental science": "natural_sciences",

    # Humanities
    "english": "english_home_language",
    "english language arts": "english_home_language",
    "ela": "english_home_language",
    "reading": "english_home_language",
    "writing": "english_home_language",
    "literature": "english_home_language",
    "history": "history",
    "world history": "history",
    "us history": "history",
    "european history": "history",
    "african history": "history",
    "geography": "geography",
    "social studies": "social_sciences",
    "civics": "life_orientation",
    "economics": "economics",
    "business": "business_studies",
    "accounting": "accounting",

    # Other
    "computer science": "technology",
    "information technology": "technology",
    "physical education": "physical_education",
    "art": "creative_arts",
    "music": "creative_arts",
    "drama": "creative_arts",
    "life skills": "life_orientation",
    "health": "life_orientation",
}

# ─── Khan Academy Topic → CAPS Mapping ───────────────────────────────────────

KA_TOPIC_TO_CAPS: dict[str, dict[str, Any]] = {
    # Foundation Phase Mathematics
    "early-math":           {"subject": "mathematics", "topic_code": "NOR", "grades": [1, 2, 3]},
    "cc-kindergarten-math": {"subject": "mathematics", "topic_code": "NOR", "grades": [1]},
    "cc-1st-grade-math":    {"subject": "mathematics", "topic_code": "NOR", "grades": [1]},
    "cc-2nd-grade-math":    {"subject": "mathematics", "topic_code": "NOR", "grades": [2]},
    "cc-3rd-grade-math":    {"subject": "mathematics", "topic_code": "NOR", "grades": [3]},
    "cc-4th-grade-math":    {"subject": "mathematics", "topic_code": "NOR", "grades": [4]},
    "cc-5th-grade-math":    {"subject": "mathematics", "topic_code": "NOR", "grades": [5]},
    "cc-6th-grade-math":    {"subject": "mathematics", "topic_code": "NOR", "grades": [6]},
    "cc-7th-grade-math":    {"subject": "mathematics", "topic_code": "PFA", "grades": [7]},
    "cc-8th-grade-math":    {"subject": "mathematics", "topic_code": "PFA", "grades": [8]},
    # FET Mathematics
    "algebra-basics":       {"subject": "mathematics", "topic_code": "PFA",  "grades": [8, 9]},
    "algebra":              {"subject": "mathematics", "topic_code": "PFA",  "grades": [10, 11]},
    "algebra2":             {"subject": "mathematics", "topic_code": "A",    "grades": [11, 12]},
    "geometry":             {"subject": "mathematics", "topic_code": "EG",   "grades": [10, 11, 12]},
    "trigonometry":         {"subject": "mathematics", "topic_code": "T",    "grades": [10, 11, 12]},
    "precalculus":          {"subject": "mathematics", "topic_code": "F",    "grades": [11, 12]},
    "differential-calculus":{"subject": "mathematics", "topic_code": "DC",   "grades": [12]},
    "statistics-probability":{"subject": "mathematics","topic_code": "ST",   "grades": [10, 11, 12]},
    # Sciences
    "biology":              {"subject": "life_sciences",     "topic_code": "LL",  "grades": [10, 11, 12]},
    "high-school-biology":  {"subject": "life_sciences",     "topic_code": "CE",  "grades": [10, 11, 12]},
    "chemistry":            {"subject": "physical_sciences", "topic_code": "CH",  "grades": [10, 11, 12]},
    "physics":              {"subject": "physical_sciences", "topic_code": "M",   "grades": [10, 11, 12]},
    "cosmology-and-astronomy":{"subject": "natural_sciences","topic_code": "PEB", "grades": [8, 9]},
    "earth-science":        {"subject": "natural_sciences",  "topic_code": "PEB", "grades": [7, 8, 9]},
    # Humanities
    "grammar":              {"subject": "english_home_language", "topic_code": "LB",  "grades": [4, 5, 6, 7, 8, 9]},
    "reading-and-language-arts":{"subject": "english_home_language","topic_code": "RC","grades": list(range(1,13))},
    "world-history":        {"subject": "history",    "topic_code": "WH",  "grades": [8, 9, 10, 11, 12]},
    "us-history":           {"subject": "history",    "topic_code": "WH",  "grades": [9, 10, 11]},
    "ap-world-history":     {"subject": "history",    "topic_code": "WH",  "grades": [11, 12]},
    "microeconomics":       {"subject": "economics",  "topic_code": "ME",  "grades": [10, 11, 12]},
    "macroeconomics":       {"subject": "economics",  "topic_code": "MA",  "grades": [10, 11, 12]},
    "personal-finance":     {"subject": "economics",  "topic_code": "EMS", "grades": [8, 9, 10]},
}

# ─── Common Core Standard Prefix → CAPS Mapping ──────────────────────────────

CC_TO_CAPS: dict[str, dict[str, Any]] = {
    # Math – Operations & Algebraic Thinking
    "1.OA": {"subject": "mathematics", "topic_code": "NOR",  "grade": 1},
    "2.OA": {"subject": "mathematics", "topic_code": "NOR",  "grade": 2},
    "3.OA": {"subject": "mathematics", "topic_code": "NOR",  "grade": 3},
    "4.OA": {"subject": "mathematics", "topic_code": "NOR",  "grade": 4},
    "5.OA": {"subject": "mathematics", "topic_code": "PFA",  "grade": 5},
    # Math – Number & Base Ten
    "K.NBT": {"subject": "mathematics", "topic_code": "NOR",  "grade": 1},
    "1.NBT": {"subject": "mathematics", "topic_code": "NOR",  "grade": 1},
    "2.NBT": {"subject": "mathematics", "topic_code": "NOR",  "grade": 2},
    "3.NBT": {"subject": "mathematics", "topic_code": "NOR",  "grade": 3},
    "4.NBT": {"subject": "mathematics", "topic_code": "NOR",  "grade": 4},
    "5.NBT": {"subject": "mathematics", "topic_code": "NOR",  "grade": 5},
    # Math – Fractions
    "3.NF": {"subject": "mathematics", "topic_code": "NOR",  "grade": 3},
    "4.NF": {"subject": "mathematics", "topic_code": "NOR",  "grade": 4},
    "5.NF": {"subject": "mathematics", "topic_code": "NOR",  "grade": 5},
    # Math – Geometry
    "K.G":  {"subject": "mathematics", "topic_code": "SS",   "grade": 1},
    "1.G":  {"subject": "mathematics", "topic_code": "SS",   "grade": 1},
    "2.G":  {"subject": "mathematics", "topic_code": "SS",   "grade": 2},
    "3.G":  {"subject": "mathematics", "topic_code": "SS",   "grade": 3},
    "4.G":  {"subject": "mathematics", "topic_code": "SS",   "grade": 4},
    "5.G":  {"subject": "mathematics", "topic_code": "SS",   "grade": 5},
    "6.G":  {"subject": "mathematics", "topic_code": "SSM",  "grade": 6},
    "7.G":  {"subject": "mathematics", "topic_code": "SSM",  "grade": 7},
    "8.G":  {"subject": "mathematics", "topic_code": "SSM",  "grade": 8},
    # Math – High School
    "HSA":  {"subject": "mathematics", "topic_code": "A",    "grade": 10},
    "HSF":  {"subject": "mathematics", "topic_code": "F",    "grade": 10},
    "HSG":  {"subject": "mathematics", "topic_code": "EG",   "grade": 10},
    "HSS":  {"subject": "mathematics", "topic_code": "ST",   "grade": 11},
    "HSN":  {"subject": "mathematics", "topic_code": "NPS",  "grade": 11},
    # Science – NGSS approximate mapping
    "K-LS":  {"subject": "natural_sciences", "topic_code": "LL",  "grade": 1},
    "K-PS":  {"subject": "natural_sciences", "topic_code": "EC",  "grade": 1},
    "1-LS":  {"subject": "natural_sciences", "topic_code": "LL",  "grade": 1},
    "2-LS":  {"subject": "natural_sciences", "topic_code": "LL",  "grade": 2},
    "3-LS":  {"subject": "natural_sciences", "topic_code": "LL",  "grade": 3},
    "4-ESS": {"subject": "natural_sciences", "topic_code": "PEB", "grade": 4},
    "5-ESS": {"subject": "natural_sciences", "topic_code": "PEB", "grade": 5},
    "MS-LS": {"subject": "natural_sciences", "topic_code": "LL",  "grade": 7},
    "MS-PS": {"subject": "natural_sciences", "topic_code": "EC",  "grade": 7},
    "MS-ESS":{"subject": "natural_sciences", "topic_code": "PEB", "grade": 7},
    "HS-LS": {"subject": "life_sciences",     "topic_code": "CE",  "grade": 10},
    "HS-PS": {"subject": "physical_sciences", "topic_code": "M",   "grade": 10},
    "HS-ESS":{"subject": "natural_sciences",  "topic_code": "PEB", "grade": 11},
}

# ─── Runtime defaults ─────────────────────────────────────────────────────────

DEFAULT_GRADES      = list(range(1, 13))
DEFAULT_LANGUAGE    = "en"
RAW_TABLE           = "ingestion_raw"
CONTENT_TABLE       = "curriculum_content"
STANDARDS_TABLE     = "curriculum_standards"
JOBS_TABLE          = "ingestion_jobs"
REDIS_QUEUE_KEY     = "ingestion:job_queue"
REDIS_PROGRESS_KEY  = "ingestion:progress:{job_id}"
EXPORT_DIR          = "data/exports"
RAW_STORE_DIR       = "data/raw"
