#!/usr/bin/env python3
import os
import asyncio
import asyncpg

CREATE_SQL = '''
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'itemtype') THEN
        CREATE TYPE itemtype AS ENUM ('mcq','short_answer','true_false','fill_blank');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'subjectcode') THEN
        CREATE TYPE subjectcode AS ENUM ('Mathematics','English','isiZulu','Afrikaans','Life Skills','Natural Sciences');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'language') THEN
        CREATE TYPE language AS ENUM ('en','zu','af','xh');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'reviewstatus') THEN
        CREATE TYPE reviewstatus AS ENUM ('draft','ai_generated','human_reviewed','approved','retired');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'itemsource') THEN
        CREATE TYPE itemsource AS ENUM ('llm_generated','human_authored','imported');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'difficultyband') THEN
        CREATE TYPE difficultyband AS ENUM ('easy','moderate','on_level','challenging');
    END IF;
END$$;

CREATE TABLE IF NOT EXISTS diagnostic_items (
    item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    caps_ref VARCHAR(40) NOT NULL,
    grade SMALLINT NOT NULL,
    subject subjectcode NOT NULL,
    term SMALLINT NOT NULL,
    topic VARCHAR(200) NOT NULL,
    subtopic VARCHAR(200) NOT NULL,
    skill VARCHAR(200) NOT NULL,
    stem TEXT NOT NULL,
    answer_key VARCHAR(500) NOT NULL,
    options JSONB,
    explanation TEXT NOT NULL,
    distractor_rationale JSONB,
    misconception_tags TEXT[] DEFAULT '{}',
    item_type itemtype NOT NULL DEFAULT 'mcq',
    language language NOT NULL DEFAULT 'en',
    difficulty_b NUMERIC(6,4) NOT NULL DEFAULT 0.0,
    discrimination_a NUMERIC(6,4) NOT NULL DEFAULT 1.0,
    guessing_c NUMERIC(6,4) NOT NULL DEFAULT 0.25,
    difficulty_band difficultyband NOT NULL DEFAULT 'on_level',
    review_status reviewstatus NOT NULL DEFAULT 'draft',
    reviewer_id UUID NULL,
    reviewed_at timestamptz NULL,
    exposure_count INTEGER NOT NULL DEFAULT 0,
    max_exposure INTEGER NOT NULL DEFAULT 50,
    quality_score NUMERIC(5,4) NULL,
    safety_passed BOOLEAN NOT NULL DEFAULT false,
    source itemsource NOT NULL DEFAULT 'llm_generated',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_diagnostic_items_caps_ref ON diagnostic_items (caps_ref);
CREATE INDEX IF NOT EXISTS ix_diagnostic_items_review_status ON diagnostic_items (review_status);
CREATE INDEX IF NOT EXISTS ix_diagnostic_items_grade_subject_term ON diagnostic_items (grade, subject, term);
CREATE INDEX IF NOT EXISTS ix_diagnostic_items_exposure_cap ON diagnostic_items (exposure_count, max_exposure);
'''


def dsn_from_env():
    db = os.environ.get('DATABASE_URL')
    if not db:
        raise RuntimeError('DATABASE_URL not set')
    if db.startswith('postgresql+asyncpg://'):
        return db.replace('postgresql+asyncpg://','postgresql://',1)
    return db

async def main():
    dsn = dsn_from_env()
    conn = await asyncpg.connect(dsn)
    try:
        await conn.execute(CREATE_SQL)
        print('diagnostic_items schema ensured')
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(main())
