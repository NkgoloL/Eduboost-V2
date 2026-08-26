# Table and Field Data Inventory (TSR-7.1)

## Overview
This inventory maps all database tables in EduBoost V2 across data classification, purpose, retention rules, and legal basis under POPIA.

## Data Classification Categories
1. **Personal Information (PI) / POPIA Special Personal Information:**
   - `learner_profiles`, `guardians`, `parental_consents`, `consent_records`, `privacy_settings`
   - Lawful Basis: Parental Consent (POPIA §35) & Contractual performance.
2. **Audit & Compliance Ledgers:**
   - `audit_events`, `data_export_requests`, `erasure_requests`, `restriction_requests`, `correction_requests`
   - Lawful Basis: Legal obligation & accountability (POPIA §8, §22).
3. **Pedagogical & Curriculum Content (Non-PII):**
   - `diagnostic_items`, `lessons`, `content_scopes`, `runtime_kg_nodes`, `runtime_kg_edges`, `assessment_blueprints`
   - Treatment: Content hashing, versioning, public educational assets.
4. **Learning Analytics & Progress:**
   - `topic_mastery`, `learner_kg_node_states`, `study_plans`, `practice_sessions`
   - Treatment: Pseudonymized via learner ID; subject to POPIA erasure and export workflows.
