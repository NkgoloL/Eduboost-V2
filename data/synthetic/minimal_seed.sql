-- EduBoost local-only synthetic seed data.
-- Contains no real learner or guardian PII.

INSERT INTO guardians (
    id, email_hash, email_encrypted, display_name, role, password_hash,
    subscription_tier, is_active, created_at, updated_at
) VALUES (
    '00000000-0000-4000-8000-000000000001',
    'synthetic_guardian_email_hash_000000000000000000000000000000000000',
    'encrypted:synthetic.guardian@example.test',
    'Synthetic Guardian',
    'parent',
    '$2b$12$syntheticpasswordhashplaceholder00000000000000000000000',
    'free',
    true,
    now(),
    now()
) ON CONFLICT (id) DO NOTHING;

INSERT INTO learner_profiles (
    id, pseudonym_id, guardian_id, display_name, grade, language,
    theta, xp, streak_days, is_deleted, created_at, updated_at
) VALUES (
    '00000000-0000-4000-8000-000000000101',
    '00000000-0000-4000-8000-000000000102',
    '00000000-0000-4000-8000-000000000001',
    'Synthetic Learner',
    4,
    'en',
    0.0,
    0,
    0,
    false,
    now(),
    now()
) ON CONFLICT (id) DO NOTHING;
