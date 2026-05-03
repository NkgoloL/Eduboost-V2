-- EduBoost SA — Phase 2 Migration
-- Adds: lessons, assessments, reports, badges, diagnostic items
-- Run: docker exec -i eduboost-postgres psql -U eduboost_user -d eduboost < scripts/db_migration_phase2.sql

BEGIN;

-- ============================================================================
-- LESSONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS lessons (
    lesson_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    subject_code VARCHAR(20) NOT NULL,
    grade_level SMALLINT NOT NULL CHECK (grade_level BETWEEN 0 AND 7),
    unit VARCHAR(50),
    topic VARCHAR(100),
    content TEXT NOT NULL,
    content_modality VARCHAR(20) DEFAULT 'text',  -- text, video, interactive
    duration_minutes SMALLINT DEFAULT 15,
    difficulty_level FLOAT DEFAULT 0.5,
    learning_objectives JSONB DEFAULT '[]',
    prerequisites JSONB DEFAULT '[]',
    is_cap_aligned BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_lessons_subject_grade ON lessons(subject_code, grade_level);
CREATE INDEX IF NOT EXISTS ix_lessons_topic ON lessons(topic);

-- ============================================================================
-- ASSESSMENTS / TESTS
-- ============================================================================
CREATE TABLE IF NOT EXISTS assessments (
    assessment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    subject_code VARCHAR(20) NOT NULL,
    grade_level SMALLINT NOT NULL CHECK (grade_level BETWEEN 0 AND 7),
    assessment_type VARCHAR(30) NOT NULL,  -- quiz, test, exam, diagnostic
    total_marks INTEGER DEFAULT 0,
    time_limit_minutes SMALLINT,
    passing_score FLOAT DEFAULT 0.5,
    questions JSONB NOT NULL,  -- Array of question objects
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS assessment_attempts (
    attempt_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    learner_id UUID NOT NULL REFERENCES learners(learner_id) ON DELETE CASCADE,
    assessment_id UUID NOT NULL REFERENCES assessments(assessment_id) ON DELETE CASCADE,
    score FLOAT,
    marks_obtained INTEGER,
    time_taken_seconds INTEGER,
    responses JSONB DEFAULT '[]',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_assessments_subject_grade ON assessments(subject_code, grade_level);
CREATE INDEX IF NOT EXISTS ix_assessment_attempts_learner ON assessment_attempts(learner_id);
CREATE INDEX IF NOT EXISTS ix_assessment_attempts_assessment ON assessment_attempts(assessment_id);

-- ============================================================================
-- REPORTS
-- ============================================================================
CREATE TABLE IF NOT EXISTS reports (
    report_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    learner_id UUID NOT NULL REFERENCES learners(learner_id) ON DELETE CASCADE,
    report_type VARCHAR(30) NOT NULL,  -- progress, diagnostic, weekly, monthly, parent
    title VARCHAR(200) NOT NULL,
    content JSONB NOT NULL,
    summary TEXT,
    generated_by VARCHAR(50) DEFAULT 'SYSTEM',  -- SYSTEM, AI, ALGORITHM
    is_shared BOOLEAN DEFAULT FALSE,
    shared_with_guardian BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_reports_learner ON reports(learner_id);
CREATE INDEX IF NOT EXISTS ix_reports_type ON reports(report_type);

-- ============================================================================
-- BADGES
-- ============================================================================
CREATE TABLE IF NOT EXISTS badges (
    badge_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    badge_key VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon_url VARCHAR(200),
    xp_value INTEGER DEFAULT 0,
    grade_band VARCHAR(20),  -- R-3, 4-7, ALL
    badge_type VARCHAR(30),  -- streak, mastery, milestone, discovery, achievement
    threshold INTEGER,  -- e.g., 7 for 7-day streak
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS learner_badges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    learner_id UUID NOT NULL REFERENCES learners(learner_id) ON DELETE CASCADE,
    badge_id UUID NOT NULL REFERENCES badges(badge_id) ON DELETE CASCADE,
    earned_at TIMESTAMPTZ DEFAULT NOW(),
    evidence JSONB,
    UNIQUE(learner_id, badge_id)
);

CREATE INDEX IF NOT EXISTS ix_learner_badges_learner ON learner_badges(learner_id);

-- ============================================================================
-- DIAGNOSTIC SESSIONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS diagnostic_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    learner_id UUID NOT NULL REFERENCES learners(learner_id) ON DELETE CASCADE,
    subject_code VARCHAR(20) NOT NULL,
    grade_level SMALLINT NOT NULL CHECK (grade_level BETWEEN 0 AND 7),
    status VARCHAR(20) DEFAULT 'in_progress',  -- in_progress, completed, abandoned
    theta_estimate FLOAT,  -- IRT ability estimate
    standard_error FLOAT,
    items_administered INTEGER DEFAULT 0,
    items_total INTEGER DEFAULT 20,
    final_mastery_score FLOAT,
    knowledge_gaps JSONB DEFAULT '[]',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS diagnostic_responses (
    response_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES diagnostic_sessions(session_id) ON DELETE CASCADE,
    item_id VARCHAR(50) NOT NULL,
    learner_response TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    time_taken_ms INTEGER,
    theta_before FLOAT,
    theta_after FLOAT,
    sem_before FLOAT,
    sem_after FLOAT,
    information_gain FLOAT,
    responded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_diagnostic_sessions_learner ON diagnostic_sessions(learner_id);
CREATE INDEX IF NOT EXISTS ix_diagnostic_responses_session ON diagnostic_responses(session_id);

-- ============================================================================
-- ITEM BANK (IRT Diagnostic Items)
-- ============================================================================
CREATE TABLE IF NOT EXISTS item_bank (
    item_id VARCHAR(50) PRIMARY KEY,
    subject_code VARCHAR(20) NOT NULL,
    grade_level SMALLINT NOT NULL CHECK (grade_level BETWEEN 0 AND 7),
    concept_code VARCHAR(50),
    difficulty FLOAT NOT NULL,
    discrimination FLOAT NOT NULL,
    guessing FLOAT DEFAULT 0.25,
    content TEXT NOT NULL,
    options JSONB,  -- For multiple choice
    correct_answer TEXT,
    rubric TEXT,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    calibrated_at TIMESTAMPTZ,
    calibration_sample_size INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS ix_item_bank_subject_grade ON item_bank(subject_code, grade_level);
CREATE INDEX IF NOT EXISTS ix_item_bank_concept ON item_bank(concept_code);

-- ============================================================================
-- PARENT ACCOUNTS
-- ============================================================================
CREATE TABLE IF NOT EXISTS parent_accounts (
    parent_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email_encrypted TEXT NOT NULL,
    password_hash VARCHAR(200),
    full_name_encrypted TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    is_verified BOOLEAN DEFAULT FALSE,
    last_login_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS parent_learner_links (
    link_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parent_id UUID NOT NULL REFERENCES parent_accounts(parent_id) ON DELETE CASCADE,
    learner_id UUID NOT NULL REFERENCES learners(learner_id) ON DELETE CASCADE,
    relationship VARCHAR(20) DEFAULT 'guardian',  -- guardian, parent, grandparent
    is_verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(parent_id, learner_id)
);

CREATE INDEX IF NOT EXISTS ix_parent_learner_links_parent ON parent_learner_links(parent_id);
CREATE INDEX IF NOT EXISTS ix_parent_learner_links_learner ON parent_learner_links(learner_id);

-- ============================================================================
-- AUDIT EVENTS
-- ============================================================================
CREATE TABLE IF NOT EXISTS audit_events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(50) NOT NULL,
    pillar VARCHAR(30),
    actor_id VARCHAR(100),
    learner_id UUID,
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    details JSONB,
    request_id VARCHAR(100),
    ip_address_hash VARCHAR(64),
    occurred_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_audit_events_learner ON audit_events(learner_id);
CREATE INDEX IF NOT EXISTS ix_audit_events_occurred ON audit_events(occurred_at);
CREATE INDEX IF NOT EXISTS ix_audit_events_type ON audit_events(event_type);

COMMIT;