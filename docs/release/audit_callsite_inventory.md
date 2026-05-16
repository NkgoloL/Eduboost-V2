# Audit Call-Site Inventory

This inventory supports audit repository consolidation. It is diagnostic only.

| Path | Line | Category | Text |
|---|---:|---|---|
| `alembic/versions/0001_v2_consolidated_schema.py` | 18 | audit_logs_table | `8. audit_logs — Append-only audit trail (immutable)` |
| `alembic/versions/0001_v2_consolidated_schema.py` | 190 | audit_logs_table | `"audit_logs",` |
| `alembic/versions/0001_v2_consolidated_schema.py` | 199 | audit_logs_table | `op.create_index("ix_audit_event_created", "audit_logs", ["event_type", "created_at"])` |
| `alembic/versions/0001_v2_consolidated_schema.py` | 201 | audit_logs_table | `# Append-only trigger on audit_logs (prevent UPDATE/DELETE)` |
| `alembic/versions/0001_v2_consolidated_schema.py` | 206 | audit_logs_table | `RAISE EXCEPTION 'audit_logs is append-only. UPDATE and DELETE are prohibited.';` |
| `alembic/versions/0001_v2_consolidated_schema.py` | 212 | audit_logs_table | `BEFORE UPDATE ON audit_logs` |
| `alembic/versions/0001_v2_consolidated_schema.py` | 217 | audit_logs_table | `BEFORE DELETE ON audit_logs` |
| `alembic/versions/0001_v2_consolidated_schema.py` | 238 | audit_logs_table | `# Drop audit_logs triggers first` |
| `alembic/versions/0001_v2_consolidated_schema.py` | 239 | audit_logs_table | `op.execute("DROP TRIGGER IF EXISTS trg_audit_logs_no_delete ON audit_logs;")` |
| `alembic/versions/0001_v2_consolidated_schema.py` | 240 | audit_logs_table | `op.execute("DROP TRIGGER IF EXISTS trg_audit_logs_no_update ON audit_logs;")` |
| `alembic/versions/0001_v2_consolidated_schema.py` | 245 | audit_logs_table | `op.drop_table("audit_logs")` |
| `alembic/versions/0005_seed_irt_items.py` | 110 | audit_append_call | `rows.append(` |
| `alembic/versions/0006_v2_audit_events.py` | 6 | audit_events_table | `Creates the audit_events table with:` |
| `alembic/versions/0006_v2_audit_events.py` | 30 | audit_events_table | `# ─── Create audit_events table ────────────────────────────────────────────` |
| `alembic/versions/0006_v2_audit_events.py` | 32 | audit_events_table | `"audit_events",` |
| `alembic/versions/0006_v2_audit_events.py` | 77 | audit_events_table | `"audit_events",` |
| `alembic/versions/0006_v2_audit_events.py` | 83 | audit_events_table | `"audit_events",` |
| `alembic/versions/0006_v2_audit_events.py` | 88 | audit_events_table | `"audit_events",` |
| `alembic/versions/0006_v2_audit_events.py` | 94 | audit_events_table | `"audit_events",` |
| `alembic/versions/0006_v2_audit_events.py` | 107 | audit_events_table | `AS ON UPDATE TO audit_events` |
| `alembic/versions/0006_v2_audit_events.py` | 115 | audit_events_table | `AS ON DELETE TO audit_events` |
| `alembic/versions/0006_v2_audit_events.py` | 123 | audit_events_table | `COMMENT ON TABLE audit_events IS` |
| `alembic/versions/0006_v2_audit_events.py` | 133 | audit_events_table | `op.execute("DROP RULE IF EXISTS audit_events_no_update ON audit_events;")` |
| `alembic/versions/0006_v2_audit_events.py` | 134 | audit_events_table | `op.execute("DROP RULE IF EXISTS audit_events_no_delete ON audit_events;")` |
| `alembic/versions/0006_v2_audit_events.py` | 135 | audit_events_table | `op.drop_index("idx_audit_events_ts", table_name="audit_events")` |
| `alembic/versions/0006_v2_audit_events.py` | 136 | audit_events_table | `op.drop_index("idx_audit_events_resource", table_name="audit_events")` |
| `alembic/versions/0006_v2_audit_events.py` | 137 | audit_events_table | `op.drop_index("idx_audit_events_type", table_name="audit_events")` |
| `alembic/versions/0006_v2_audit_events.py` | 138 | audit_events_table | `op.drop_index("idx_audit_events_actor", table_name="audit_events")` |
| `alembic/versions/0006_v2_audit_events.py` | 139 | audit_events_table | `op.drop_table("audit_events")` |
| `alembic/versions/0007_caps_irt_item_bank.py` | 74 | audit_append_call | `rows.append(` |
| `alembic/versions/20260507_1200_popia_consent_audit_hardening.py` | 37 | audit_events_table | `op.add_column("audit_events", sa.Column("previous_event_hash", sa.String(length=64), nullable=True))` |
| `alembic/versions/20260507_1200_popia_consent_audit_hardening.py` | 38 | audit_events_table | `op.add_column("audit_events", sa.Column("event_hash", sa.String(length=64), nullable=False, server_default=""))` |
| `alembic/versions/20260507_1200_popia_consent_audit_hardening.py` | 39 | audit_events_table | `op.add_column("audit_events", sa.Column("hmac_signature", sa.String(length=64), nullable=False, server_default=""))` |
| `alembic/versions/20260507_1200_popia_consent_audit_hardening.py` | 40 | audit_events_table | `op.create_index("idx_audit_events_hash", "audit_events", ["event_hash"])` |
| `alembic/versions/20260507_1200_popia_consent_audit_hardening.py` | 44 | audit_events_table | `op.drop_index("idx_audit_events_hash", table_name="audit_events")` |
| `alembic/versions/20260507_1200_popia_consent_audit_hardening.py` | 45 | audit_events_table | `op.drop_column("audit_events", "hmac_signature")` |
| `alembic/versions/20260507_1200_popia_consent_audit_hardening.py` | 46 | audit_events_table | `op.drop_column("audit_events", "event_hash")` |
| `alembic/versions/20260507_1200_popia_consent_audit_hardening.py` | 47 | audit_events_table | `op.drop_column("audit_events", "previous_event_hash")` |
| `alembic/versions/20260507_1330_database_integrity_constraints.py` | 121 | audit_events_table | `"audit_events",` |
| `alembic/versions/20260507_1330_database_integrity_constraints.py` | 126 | audit_events_table | `"audit_events",` |
| `alembic/versions/20260507_1330_database_integrity_constraints.py` | 131 | audit_events_table | `"audit_events",` |
| `alembic/versions/20260507_1330_database_integrity_constraints.py` | 136 | audit_events_table | `"audit_events",` |
| `alembic/versions/20260507_1330_database_integrity_constraints.py` | 210 | audit_events_table | `op.drop_constraint("ck_audit_events_previous_hash_hex64", "audit_events", type_="check")` |
| `alembic/versions/20260507_1330_database_integrity_constraints.py` | 211 | audit_events_table | `op.drop_constraint("ck_audit_events_hmac_hex64_or_bootstrap", "audit_events", type_="check")` |
| `alembic/versions/20260507_1330_database_integrity_constraints.py` | 212 | audit_events_table | `op.drop_constraint("ck_audit_events_hash_hex64_or_bootstrap", "audit_events", type_="check")` |
| `alembic/versions/20260507_1330_database_integrity_constraints.py` | 213 | audit_events_table | `op.drop_constraint("ck_audit_events_event_type_not_blank", "audit_events", type_="check")` |
| `alembic/versions/20260510_0300_popia_consent_audit_dsr.py` | 4 | audit_events_table | `Sets up row-level trigger to prevent UPDATE/DELETE on audit_events.` |
| `alembic/versions/20260510_0300_popia_consent_audit_dsr.py` | 18 | audit_events_table | `# NOTE: The audit_events table and its append-only rules are` |
| `alembic/versions/20260510_0300_popia_consent_audit_dsr.py` | 23 | audit_events_table | `# Row-level trigger: prevent UPDATE/DELETE on audit_events (§4.5)` |
| `alembic/versions/20260510_0300_popia_consent_audit_dsr.py` | 29 | audit_events_table | `RAISE EXCEPTION 'audit_events is append-only – modifications are forbidden';` |
| `alembic/versions/20260510_0300_popia_consent_audit_dsr.py` | 35 | audit_events_table | `BEFORE UPDATE OR DELETE ON audit_events` |
| `alembic/versions/20260510_0300_popia_consent_audit_dsr.py` | 115 | audit_events_table | `# §4.5 – revoke UPDATE/DELETE from app role on audit_events` |
| `alembic/versions/20260510_0300_popia_consent_audit_dsr.py` | 118 | audit_events_table | `op.execute("REVOKE UPDATE, DELETE ON audit_events FROM eduboost_app;")` |
| `alembic/versions/20260510_0300_popia_consent_audit_dsr.py` | 122 | audit_events_table | `op.execute("DROP TRIGGER IF EXISTS trg_audit_events_immutable ON audit_events;")` |
| `alembic/versions/20260510_0300_popia_consent_audit_dsr.py` | 127 | audit_events_table | `"consent_records", "audit_events",` |
| `alembic/versions/20260516_0100_remove_base_sentinel.py` | 4 | audit_events_table | `Fix split migration state: remove 'base' sentinel + ensure audit_events exists.` |
| `alembic/versions/20260516_0100_remove_base_sentinel.py` | 14 | audit_events_table | `2. Migration ``0006_v2_audit_events.py`` (which creates the ``audit_events``` |
| `alembic/versions/20260516_0100_remove_base_sentinel.py` | 36 | audit_events_table | `# ── Fix 2: Ensure audit_events exists (migration 0006 may have been skipped) ─` |
| `alembic/versions/20260516_0100_remove_base_sentinel.py` | 38 | audit_events_table | `CREATE TABLE IF NOT EXISTS audit_events (` |
| `alembic/versions/20260516_0100_remove_base_sentinel.py` | 51 | audit_events_table | `ON audit_events (actor_id)` |
| `alembic/versions/20260516_0100_remove_base_sentinel.py` | 56 | audit_events_table | `ON audit_events (event_type)` |
| `alembic/versions/20260516_0100_remove_base_sentinel.py` | 60 | audit_events_table | `ON audit_events (resource_id)` |
| `alembic/versions/20260516_0100_remove_base_sentinel.py` | 65 | audit_events_table | `ON audit_events (created_at DESC)` |
| `alembic/versions/20260516_0100_remove_base_sentinel.py` | 69 | audit_events_table | `op.execute("DROP RULE IF EXISTS audit_events_no_update ON audit_events")` |
| `alembic/versions/20260516_0100_remove_base_sentinel.py` | 72 | audit_events_table | `AS ON UPDATE TO audit_events DO INSTEAD NOTHING` |
| `alembic/versions/20260516_0100_remove_base_sentinel.py` | 74 | audit_events_table | `op.execute("DROP RULE IF EXISTS audit_events_no_delete ON audit_events")` |
| `alembic/versions/20260516_0100_remove_base_sentinel.py` | 77 | audit_events_table | `AS ON DELETE TO audit_events DO INSTEAD NOTHING` |
| `alembic/versions/20260516_0100_remove_base_sentinel.py` | 85 | audit_events_table | `RAISE EXCEPTION 'audit_events is append-only – modifications are forbidden';` |
| `alembic/versions/20260516_0100_remove_base_sentinel.py` | 89 | audit_events_table | `op.execute("DROP TRIGGER IF EXISTS trg_audit_events_immutable ON audit_events")` |
| `alembic/versions/20260516_0100_remove_base_sentinel.py` | 92 | audit_events_table | `BEFORE UPDATE OR DELETE ON audit_events` |
| `alembic/versions/20260516_0100_remove_base_sentinel.py` | 97 | audit_events_table | `COMMENT ON TABLE audit_events IS` |
| `alembic/versions/_deprecated/0001_five_pillar_schema.py` | 6 | audit_log_identifier | `- audit_log: append-only trigger` |
| `alembic/versions/_deprecated/0001_five_pillar_schema.py` | 143 | audit_log_identifier | `"audit_log",` |
| `alembic/versions/_deprecated/0001_five_pillar_schema.py` | 155 | audit_log_identifier | `"audit_log",` |
| `alembic/versions/_deprecated/0001_five_pillar_schema.py` | 161 | audit_log_identifier | `"audit_log",` |
| `alembic/versions/_deprecated/0001_five_pillar_schema.py` | 165 | audit_log_identifier | `# Append-only trigger for audit_log` |
| `alembic/versions/_deprecated/0001_five_pillar_schema.py` | 170 | audit_log_identifier | `RAISE EXCEPTION 'audit_log is append-only. UPDATE and DELETE are prohibited.';` |
| `alembic/versions/_deprecated/0001_five_pillar_schema.py` | 177 | audit_log_identifier | `BEFORE UPDATE ON audit_log` |
| `alembic/versions/_deprecated/0001_five_pillar_schema.py` | 183 | audit_log_identifier | `BEFORE DELETE ON audit_log` |
| `alembic/versions/_deprecated/0001_five_pillar_schema.py` | 303 | audit_log_identifier | `"audit_log", "constitutional_violations",` |
| `alembic/versions/_deprecated/0001_initial_consolidated_schema.py` | 173 | audit_log_identifier | `# ── audit_log ─────────────────────────────────────────────────────────` |
| `alembic/versions/_deprecated/0001_initial_consolidated_schema.py` | 175 | audit_log_identifier | `"audit_log",` |
| `alembic/versions/_deprecated/0001_initial_consolidated_schema.py` | 194 | audit_log_identifier | `op.create_index("ix_audit_log_action", "audit_log", ["action"])` |
| `alembic/versions/_deprecated/0001_initial_consolidated_schema.py` | 195 | audit_log_identifier | `op.create_index("ix_audit_log_actor_id", "audit_log", ["actor_id"])` |
| `alembic/versions/_deprecated/0001_initial_consolidated_schema.py` | 196 | audit_log_identifier | `op.create_index("ix_audit_log_created_at", "audit_log", ["created_at"])` |
| `alembic/versions/_deprecated/0001_initial_consolidated_schema.py` | 221 | audit_log_identifier | `op.drop_table("audit_log")` |
| `alembic/versions/_deprecated/0001_phase2_baseline.py` | 231 | audit_events_table | `"audit_events",` |
| `alembic/versions/_deprecated/0001_phase2_baseline.py` | 244 | audit_events_table | `op.create_index("ix_audit_events_learner", "audit_events", ["learner_id"])` |
| `alembic/versions/_deprecated/0001_phase2_baseline.py` | 245 | audit_events_table | `op.create_index("ix_audit_events_occurred", "audit_events", ["occurred_at"])` |
| `alembic/versions/_deprecated/0001_phase2_baseline.py` | 246 | audit_events_table | `op.create_index("ix_audit_events_type", "audit_events", ["event_type"])` |
| `alembic/versions/_deprecated/0001_phase2_baseline.py` | 250 | audit_events_table | `op.drop_table("audit_events")` |
| `alembic/versions/_deprecated/0001_schema_from_technical_report.py` | 125 | audit_events_table | `# ── audit_events ─────────────────────────────────────────────────────────` |
| `alembic/versions/_deprecated/0001_schema_from_technical_report.py` | 127 | audit_events_table | `"audit_events",` |
| `alembic/versions/_deprecated/0001_schema_from_technical_report.py` | 138 | audit_events_table | `op.create_index("ix_audit_events_actor_id", "audit_events", ["actor_id"])` |
| `alembic/versions/_deprecated/0001_schema_from_technical_report.py` | 139 | audit_events_table | `op.create_index("ix_audit_events_resource", "audit_events", ["resource_type", "resource_id"])` |
| `alembic/versions/_deprecated/0001_schema_from_technical_report.py` | 140 | audit_events_table | `op.create_index("ix_audit_events_created_at", "audit_events", ["created_at"])` |
| `alembic/versions/_deprecated/0001_schema_from_technical_report.py` | 183 | audit_events_table | `"audit_events",` |
| `app/api_v2_routers/0005_irt_seed.py` | 41 | audit_append_call | `_ITEMS.append(_make(0, "Mathematics", "Number Sense", q, opts, c, a, b))` |
| `app/api_v2_routers/0005_irt_seed.py` | 58 | audit_append_call | `_ITEMS.append(_make(1, "Mathematics", "Operations", q, opts, c, a, b))` |
| `app/api_v2_routers/0005_irt_seed.py` | 73 | audit_append_call | `_ITEMS.append(_make(2, "Mathematics", "Operations & Measurement", q, opts, c, a, b))` |
| `app/api_v2_routers/0005_irt_seed.py` | 88 | audit_append_call | `_ITEMS.append(_make(3, "Mathematics", "Multiplication & Fractions", q, opts, c, a, b))` |
| `app/api_v2_routers/0005_irt_seed.py` | 103 | audit_append_call | `_ITEMS.append(_make(4, "Mathematics", "Fractions & Decimals", q, opts, c, a, b))` |
| `app/api_v2_routers/0005_irt_seed.py` | 118 | audit_append_call | `_ITEMS.append(_make(5, "Mathematics", "Ratios & Integers", q, opts, c, a, b))` |
| `app/api_v2_routers/0005_irt_seed.py` | 133 | audit_append_call | `_ITEMS.append(_make(6, "Mathematics", "Algebra & Geometry", q, opts, c, a, b))` |
| `app/api_v2_routers/0005_irt_seed.py` | 148 | audit_append_call | `_ITEMS.append(_make(7, "Mathematics", "Algebra & Trigonometry", q, opts, c, a, b))` |
| `app/api_v2_routers/0005_irt_seed.py` | 170 | audit_append_call | `_ITEMS.append(_make(grade, "English", "Language", q, opts, c, a, b))` |
| `app/api_v2_routers/0005_irt_seed.py` | 188 | audit_append_call | `_ITEMS.append(_make(grade, "Natural Sciences", "Science", q, opts, c, a, b))` |
| `app/api_v2_routers/auth.py` | 182 | audit_append_call | `learner_ids.append(str(learner.id))` |
| `app/api_v2_routers/billing.py` | 44 | audit_record_call | `await audit.record("STRIPE_WEBHOOK", payload=result)` |
| `app/api_v2_routers/consent.py` | 47 | audit_log_identifier | `# AuditLog emission is handled inside ConsentService.grant().` |
| `app/api_v2_routers/consent.py` | 80 | audit_log_identifier | `# AuditLog emission is handled inside ConsentService.revoke().` |
| `app/api_v2_routers/gamification.py` | 62 | audit_record_call | `await FourthEstateService(db).record(` |
| `app/api_v2_routers/learners.py` | 151 | audit_record_call | `await audit.record(` |
| `app/api_v2_routers/parents.py` | 77 | audit_append_call | `dashboard_learners.append(` |
| `app/api_v2_routers/parents.py` | 157 | audit_append_call | `response_learners.append(` |
| `app/api_v2_routers/parents.py` | 204 | audit_append_call | `exports.append(` |
| `app/api_v2_routers/parents.py` | 286 | audit_record_call | `await FourthEstateService(db).record(` |
| `app/api_v2_routers/popia.py` | 38 | audit_repository | `from app.repositories.repositories import AuditRepository, ConsentRepository, LearnerRepository` |
| `app/api_v2_routers/popia.py` | 42 | audit_repository | `return ConsentService(ConsentRepository(db), AuditRepository(db))` |
| `app/core/audit.py` | 11 | audit_repository | `from app.repositories.repositories import AuditRepository` |
| `app/core/audit.py` | 23 | audit_repository | `self._repo = AuditRepository(db)` |
| `app/core/audit.py` | 62 | audit_record_call | `await self.record(` |
| `app/core/audit.py` | 70 | audit_record_call | `await self.record(` |
| `app/core/audit.py` | 78 | audit_record_call | `await self.record(` |
| `app/core/audit.py` | 87 | audit_record_call | `await self.record(` |
| `app/core/audit.py` | 95 | audit_record_call | `await self.record(` |
| `app/core/audit.py` | 103 | audit_record_call | `await self.record(` |
| `app/core/audit.py` | 111 | audit_record_call | `await self.record(event.lower(), actor_id=actor_id, payload=detail or {})` |
| `app/core/audit.py` | 114 | audit_record_call | `await self.record(` |
| `app/core/audit.py` | 122 | audit_record_call | `await self.record(` |
| `app/core/database.py` | 75 | audit_events_table | `await conn.execute(text("DROP RULE IF EXISTS audit_events_no_update ON audit_events"))` |
| `app/core/database.py` | 76 | audit_events_table | `await conn.execute(text("DROP RULE IF EXISTS audit_events_no_delete ON audit_events"))` |
| `app/core/database.py` | 81 | audit_events_table | `ON UPDATE TO audit_events` |
| `app/core/database.py` | 90 | audit_events_table | `ON DELETE TO audit_events` |
| `app/core/database.py` | 135 | audit_append_call | `conn.info.setdefault("query_start_time", []).append(time.time())` |
| `app/core/exceptions.py` | 113 | audit_append_call | `field_errors.append(` |
| `app/core/health.py` | 86 | audit_append_call | `missing.append("JWT_SECRET_KEY")` |
| `app/core/health.py` | 89 | audit_append_call | `missing.append("JWT_SECRET")` |
| `app/core/health.py` | 92 | audit_append_call | `missing.append(name)` |
| `app/core/health.py` | 139 | audit_events_table | `await session.execute(text("SELECT 1 FROM audit_events LIMIT 1"))` |
| `app/core/llm_gateway.py` | 597 | audit_append_call | `positions.append((start, label, start + len(needle)))` |
| `app/core/password.py` | 87 | audit_append_call | `errors.append(f"Password must be at least {_MIN_LENGTH} characters.")` |
| `app/core/password.py` | 90 | audit_append_call | `errors.append("Password must contain at least one uppercase letter.")` |
| `app/core/password.py` | 93 | audit_append_call | `errors.append("Password must contain at least one lowercase letter.")` |
| `app/core/password.py` | 96 | audit_append_call | `errors.append("Password must contain at least one digit.")` |
| `app/core/password.py` | 99 | audit_append_call | `errors.append("Password must contain at least one special character.")` |
| `app/core/password.py` | 102 | audit_append_call | `errors.append("Password is too common. Please choose a more unique password.")` |
| `app/core/password_policy.py` | 70 | audit_append_call | `errors.append("must not contain common password words or EduBoost-specific terms")` |
| `app/core/password_policy.py` | 79 | audit_append_call | `errors.append(f"must be at least {policy.min_length} characters")` |
| `app/core/password_policy.py` | 81 | audit_append_call | `errors.append("must contain at least one uppercase letter")` |
| `app/core/password_policy.py` | 83 | audit_append_call | `errors.append("must contain at least one lowercase letter")` |
| `app/core/password_policy.py` | 85 | audit_append_call | `errors.append("must contain at least one number")` |
| `app/core/password_policy.py` | 87 | audit_append_call | `errors.append("must contain at least one symbol")` |
| `app/core/refresh_tokens.py` | 137 | audit_append_call | `sessions.append({"jti": jti, "family_id": family_id, "ttl_seconds": ttl})` |
| `app/core/stripe_client.py` | 67 | audit_record_call | `await self._event_repo.record(event["id"], event["type"], dict(event))` |
| `app/domain/entities.py` | 18 | audit_log_identifier | `class AuditLog:` |
| `app/frontend/node_modules/combined-stream/Readme.md` | 27 | audit_append_call | `combinedStream.append(fs.createReadStream('file1.txt'));` |
| `app/frontend/node_modules/combined-stream/Readme.md` | 28 | audit_append_call | `combinedStream.append(fs.createReadStream('file2.txt'));` |
| `app/frontend/node_modules/combined-stream/Readme.md` | 42 | audit_append_call | `combinedStream.append(fs.createReadStream('file1.txt'));` |
| `app/frontend/node_modules/combined-stream/Readme.md` | 43 | audit_append_call | `combinedStream.append(fs.createReadStream('file2.txt'));` |
| `app/frontend/node_modules/combined-stream/Readme.md` | 58 | audit_append_call | `combinedStream.append(function(next) {` |
| `app/frontend/node_modules/combined-stream/Readme.md` | 61 | audit_append_call | `combinedStream.append(function(next) {` |
| `app/frontend/node_modules/combined-stream/Readme.md` | 95 | audit_append_call | `### combinedStream.append(stream)` |
| `app/frontend/node_modules/flatted/python/flatted.py` | 46 | audit_append_call | `input.append(value)` |
| `app/frontend/node_modules/flatted/python/flatted.py` | 48 | audit_append_call | `known.key.append(value)` |
| `app/frontend/node_modules/flatted/python/flatted.py` | 49 | audit_append_call | `known.value.append(index)` |
| `app/frontend/node_modules/flatted/python/flatted.py` | 70 | audit_append_call | `parsed.append(tmp)` |
| `app/frontend/node_modules/flatted/python/flatted.py` | 71 | audit_append_call | `lazy.append([output, key])` |
| `app/frontend/node_modules/flatted/python/flatted.py` | 81 | audit_append_call | `output.append(_relate(known, input, val))` |
| `app/frontend/node_modules/flatted/python/flatted.py` | 112 | audit_append_call | `wrapped.append(_wrap(value))` |
| `app/frontend/node_modules/flatted/python/flatted.py` | 117 | audit_append_call | `input.append(value.value)` |
| `app/frontend/node_modules/flatted/python/flatted.py` | 119 | audit_append_call | `input.append(value)` |
| `app/frontend/node_modules/flatted/python/flatted.py` | 142 | audit_append_call | `output.append(_transform(known, input, input[i]))` |
| `app/frontend/node_modules/form-data/README.md` | 32 | audit_append_call | `form.append('my_field', 'my value');` |
| `app/frontend/node_modules/form-data/README.md` | 33 | audit_append_call | `form.append('my_buffer', new Buffer(10));` |
| `app/frontend/node_modules/form-data/README.md` | 34 | audit_append_call | `form.append('my_file', fs.createReadStream('/foo/bar.jpg'));` |
| `app/frontend/node_modules/form-data/README.md` | 46 | audit_append_call | `form.append('my_field', 'my value');` |
| `app/frontend/node_modules/form-data/README.md` | 47 | audit_append_call | `form.append('my_buffer', new Buffer(10));` |
| `app/frontend/node_modules/form-data/README.md` | 48 | audit_append_call | `form.append('my_logo', response);` |
| `app/frontend/node_modules/form-data/README.md` | 60 | audit_append_call | `form.append('my_field', 'my value');` |
| `app/frontend/node_modules/form-data/README.md` | 61 | audit_append_call | `form.append('my_buffer', new Buffer(10));` |
| `app/frontend/node_modules/form-data/README.md` | 62 | audit_append_call | `form.append('my_logo', request('http://nodejs.org/images/logo.png'));` |
| `app/frontend/node_modules/form-data/README.md` | 85 | audit_append_call | `form.append('my_field', 'my value');` |
| `app/frontend/node_modules/form-data/README.md` | 86 | audit_append_call | `form.append('my_buffer', /* something big */);` |
| `app/frontend/node_modules/form-data/README.md` | 131 | audit_append_call | `form.append('my_buffer', buffer, options);` |
| `app/frontend/node_modules/form-data/README.md` | 147 | audit_append_call | `form.append('file', stdout, {` |
| `app/frontend/node_modules/form-data/README.md` | 204 | audit_append_call | `form.append('my_string', 'my value');` |
| `app/frontend/node_modules/form-data/README.md` | 205 | audit_append_call | `form.append('my_integer', 1);` |
| `app/frontend/node_modules/form-data/README.md` | 206 | audit_append_call | `form.append('my_boolean', true);` |
| `app/frontend/node_modules/form-data/README.md` | 207 | audit_append_call | `form.append('my_buffer', new Buffer(10));` |
| `app/frontend/node_modules/form-data/README.md` | 208 | audit_append_call | `form.append('my_array_as_json', JSON.stringify(['bird', 'cute']));` |
| `app/frontend/node_modules/form-data/README.md` | 214 | audit_append_call | `form.append('my_file', fs.createReadStream('/foo/bar.jpg'), 'bar.jpg');` |
| `app/frontend/node_modules/form-data/README.md` | 217 | audit_append_call | `form.append('my_file', fs.createReadStream('/foo/bar.jpg'), { filename: 'bar.jpg', contentType: 'image/jpeg', knownLength: 19806 });` |
| `app/frontend/node_modules/form-data/README.md` | 239 | audit_append_call | `form.append('my_buffer', Buffer.from([0x4a,0x42,0x20,0x52,0x6f,0x63,0x6b,0x73]));` |
| `app/frontend/node_modules/form-data/README.md` | 240 | audit_append_call | `form.append('my_file', fs.readFileSync('/foo/bar.jpg'));` |
| `app/frontend/node_modules/form-data/README.md` | 274 | audit_append_call | `form.append('my_string', 'Hello World');` |
| `app/frontend/node_modules/form-data/README.md` | 314 | audit_append_call | `form.append('a', 1);` |
| `app/frontend/node_modules/form-data/README.md` | 331 | audit_append_call | `form.append('image', stream);` |
| `app/frontend/node_modules/jsdom/README.md` | 69 | audit_append_call | `<script>document.getElementById("content").append(document.createElement("hr"));</script>` |
| `app/frontend/node_modules/jsdom/README.md` | 81 | audit_append_call | `<script>document.getElementById("content").append(document.createElement("hr"));</script>` |
| `app/frontend/node_modules/jsdom/README.md` | 99 | audit_append_call | `<script>document.getElementById("content").append(document.createElement("hr"));</script>` |
| `app/frontend/node_modules/jsdom/README.md` | 103 | audit_append_call | `dom.window.eval('document.getElementById("content").append(document.createElement("p"));');` |
| `app/frontend/node_modules/magic-string/README.md` | 52 | audit_append_call | `s.prepend('var ').append(';'); // most methods are chainable` |
| `app/frontend/node_modules/magic-string/README.md` | 101 | audit_append_call | `### s.append( content )` |
| `app/frontend/node_modules/magic-string/README.md` | 296 | audit_append_call | `.append('}());');` |
| `app/frontend/node_modules/postcss-selector-parser/API.md` | 520 | audit_append_call | `### `container.prepend(node)` & `container.append(node)`` |
| `app/frontend/node_modules/postcss-selector-parser/API.md` | 527 | audit_append_call | `selector.append(id);` |
| `app/models/__init__.py` | 239 | audit_events_table | `__tablename__ = "audit_events"` |
| `app/models/__init__.py` | 585 | audit_log_identifier | `class AuditLog(Base):` |
| `app/models/__init__.py` | 586 | audit_logs_table | `__tablename__ = "audit_logs"` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 74 | audit_append_call | `issues.append("beta launch decision must be documented in docs/adr/")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 76 | audit_append_call | `issues.append("beta launch architecture must be documented in docs/beta_launch/")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 87 | audit_append_call | `issues.append(f"{name} is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 104 | audit_append_call | `issues.append("scope_id is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 106 | audit_append_call | `issues.append("product scope description is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 108 | audit_append_call | `issues.append("product scope owner is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 110 | audit_append_call | `issues.append("product scope evidence path must live under docs/beta_launch/")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 112 | audit_append_call | `issues.append("billing must be explicitly excluded or disabled for beta unless approved")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 114 | audit_append_call | `issues.append("excluded beta scope must be explicitly marked as exclusion")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 131 | audit_append_call | `issues.append("criterion_id is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 133 | audit_append_call | `issues.append("acceptance criterion name is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 135 | audit_append_call | `issues.append("staging acceptance evidence path must be controlled")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 137 | audit_append_call | `issues.append("staging acceptance owner is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 139 | audit_append_call | `issues.append(f"{self.criterion_id} blocks beta launch")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 141 | audit_append_call | `issues.append("waived staging acceptance criterion requires waiver path")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 157 | audit_append_call | `issues.append("entry criterion_id is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 159 | audit_append_call | `issues.append("entry criterion description is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 161 | audit_append_call | `issues.append("entry criterion evidence path must be controlled")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 163 | audit_append_call | `issues.append("entry criterion owner is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 165 | audit_append_call | `issues.append(f"{self.criterion_id} required entry criterion is not met")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 182 | audit_append_call | `issues.append("exit criterion_id is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 184 | audit_append_call | `issues.append("exit criterion description is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 186 | audit_append_call | `issues.append("exit criterion metric name is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 188 | audit_append_call | `issues.append("exit criterion threshold is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 190 | audit_append_call | `issues.append("exit criterion owner is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 192 | audit_append_call | `issues.append("exit criterion evidence path must be controlled")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 211 | audit_append_call | `issues.append("cohort_id is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 213 | audit_append_call | `issues.append("max_learners must be positive")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 215 | audit_append_call | `issues.append("max_guardians must be positive")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 217 | audit_append_call | `issues.append("allowed grades are required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 219 | audit_append_call | `issues.append("allowed grades must be South African school grades 1-12")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 221 | audit_append_call | `issues.append("allowed subjects are required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 223 | audit_append_call | `issues.append("beta cohort requires consent")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 225 | audit_append_call | `issues.append("beta cohort requires support channel readiness")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 227 | audit_append_call | `issues.append("beta cohort requires rollback support")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 243 | audit_append_call | `issues.append("feedback channel is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 245 | audit_append_call | `issues.append("feedback triage SLA must be positive")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 247 | audit_append_call | `issues.append(f"{self.severity.value} feedback requires escalation")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 249 | audit_append_call | `issues.append("feedback owner is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 251 | audit_append_call | `issues.append("feedback evidence path must live under docs/beta_launch/")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 269 | audit_append_call | `issues.append("known issue_id is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 271 | audit_append_call | `issues.append("known issue summary is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 273 | audit_append_call | `issues.append("known issue owner is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 275 | audit_append_call | `issues.append("high/critical known issues must block beta or be explicitly accepted")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 277 | audit_append_call | `issues.append("accepted beta known issue requires workaround")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 279 | audit_append_call | `issues.append("known issue evidence path must live under docs/beta_launch/")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 299 | audit_append_call | `issues.append("launch readiness review_id is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 301 | audit_append_call | `issues.append("launch readiness review requires approvers")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 310 | audit_append_call | `issues.append(f"{name} must be reviewed")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 312 | audit_append_call | `issues.append("general availability requires separate production launch approval")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 314 | audit_append_call | `issues.append("launch readiness evidence path must live under docs/beta_launch/")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 350 | audit_append_call | `issues.append(f"{issue.issue_id} blocks beta launch")` |
| `app/modules/billing/production_readiness_contracts.py` | 64 | audit_append_call | `issues.append("billing provider decision must be documented in docs/adr/")` |
| `app/modules/billing/production_readiness_contracts.py` | 66 | audit_append_call | `issues.append("billing architecture must be documented in docs/billing/")` |
| `app/modules/billing/production_readiness_contracts.py` | 68 | audit_append_call | `issues.append("application must not store raw card data")` |
| `app/modules/billing/production_readiness_contracts.py` | 70 | audit_append_call | `issues.append("webhook signature verification is mandatory")` |
| `app/modules/billing/production_readiness_contracts.py` | 72 | audit_append_call | `issues.append("webhook idempotency is mandatory")` |
| `app/modules/billing/production_readiness_contracts.py` | 97 | audit_append_call | `issues.append("trial length cannot be negative")` |
| `app/modules/billing/production_readiness_contracts.py` | 99 | audit_append_call | `issues.append("payment failure grace period cannot be negative")` |
| `app/modules/billing/production_readiness_contracts.py` | 101 | audit_append_call | `issues.append("data access after cancellation cannot be negative")` |
| `app/modules/billing/production_readiness_contracts.py` | 103 | audit_append_call | `issues.append("cancellation policy is required")` |
| `app/modules/billing/production_readiness_contracts.py` | 105 | audit_append_call | `issues.append("refund policy is required")` |
| `app/modules/billing/production_readiness_contracts.py` | 107 | audit_append_call | `issues.append("invoice support is required")` |
| `app/modules/billing/production_readiness_contracts.py` | 109 | audit_append_call | `issues.append("receipt support is required")` |
| `app/modules/billing/production_readiness_contracts.py` | 165 | audit_append_call | `issues.append("account_id is required")` |
| `app/modules/billing/production_readiness_contracts.py` | 167 | audit_append_call | `issues.append("paid plans require provider_subscription_id")` |
| `app/modules/billing/production_readiness_contracts.py` | 169 | audit_append_call | `issues.append("sponsored learner plan requires sponsor account")` |
| `app/modules/billing/production_readiness_contracts.py` | 171 | audit_append_call | `issues.append("school plan requires school account")` |
| `app/modules/billing/production_readiness_contracts.py` | 173 | audit_append_call | `issues.append("expired subscriptions require period end")` |
| `app/modules/billing/production_readiness_contracts.py` | 236 | audit_log_identifier | `audit_log: list[str] = field(default_factory=list)` |
| `app/modules/billing/production_readiness_contracts.py` | 243 | audit_append_call | `self.audit_log.append(f"duplicate:{event_id}:{event_type}")` |
| `app/modules/billing/production_readiness_contracts.py` | 243 | audit_log_identifier | `self.audit_log.append(f"duplicate:{event_id}:{event_type}")` |
| `app/modules/billing/production_readiness_contracts.py` | 246 | audit_append_call | `self.audit_log.append(f"processed:{event_id}:{event_type}:{created_at_timestamp}")` |
| `app/modules/billing/production_readiness_contracts.py` | 246 | audit_log_identifier | `self.audit_log.append(f"processed:{event_id}:{event_type}:{created_at_timestamp}")` |
| `app/modules/billing/production_readiness_contracts.py` | 250 | audit_append_call | `self.dead_letter.append(f"{event_id}:{reason}")` |
| `app/modules/billing/production_readiness_contracts.py` | 261 | audit_append_call | `issues.append("max_attempts must be at least 1")` |
| `app/modules/billing/production_readiness_contracts.py` | 263 | audit_append_call | `issues.append("backoff schedule is required")` |
| `app/modules/billing/production_readiness_contracts.py` | 265 | audit_append_call | `issues.append("backoff values must be positive")` |
| `app/modules/billing/production_readiness_contracts.py` | 283 | audit_append_call | `issues.append("event_id is required")` |
| `app/modules/billing/production_readiness_contracts.py` | 285 | audit_append_call | `issues.append("account_id is required")` |
| `app/modules/billing/production_readiness_contracts.py` | 287 | audit_append_call | `issues.append("occurred_at_utc must be timezone-aware")` |
| `app/modules/billing/production_readiness_contracts.py` | 289 | audit_append_call | `issues.append("request_id is required")` |
| `app/modules/billing/production_readiness_contracts.py` | 291 | audit_append_call | `issues.append("idempotency_key is required")` |
| `app/modules/billing/production_readiness_contracts.py` | 293 | audit_append_call | `issues.append("raw provider payloads must not be retained without redaction")` |
| `app/modules/consent/service.py` | 6 | audit_repository | `:class:`~app.repositories.audit_repository.AuditRepository` or the` |
| `app/modules/consent/service.py` | 28 | audit_repository | `from app.repositories.audit_repository import AuditRepository` |
| `app/modules/consent/service.py` | 37 | audit_repository | `audit trail via :class:`~app.repositories.audit_repository.AuditRepository`` |
| `app/modules/consent/service.py` | 56 | audit_repository | `audit_repo: AuditRepository \| None = None,` |
| `app/modules/consent/service.py` | 65 | audit_repository | `audit_repo: Optional :class:`~app.repositories.audit_repository.AuditRepository`` |
| `app/modules/consent/service.py` | 83 | audit_repository | `audit_repo = AuditRepository(db)` |
| `app/modules/consent/service.py` | 146 | audit_log_identifier | `# AuditLog / fourth_estate coverage is written via _append_audit below.` |
| `app/modules/consent/service.py` | 184 | audit_log_identifier | `# AuditLog / fourth_estate coverage is written via _append_audit below.` |
| `app/modules/consent/service.py` | 250 | audit_log_identifier | `# AuditLog / fourth_estate coverage is written via _append_audit below.` |
| `app/modules/consent/service.py` | 304 | audit_repository | `Tries :class:`~app.repositories.audit_repository.AuditRepository`` |
| `app/modules/consent/service.py` | 316 | audit_append_call | `await self._audit_repo.append(` |
| `app/modules/consent/service.py` | 324 | audit_record_call | `await FourthEstateService(self._db).record(` |
| `app/modules/deployment/production_readiness_contracts.py` | 101 | audit_append_call | `issues.append("infrastructure provider is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 103 | audit_append_call | `issues.append("container registry is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 105 | audit_append_call | `issues.append("deployment platform is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 107 | audit_append_call | `issues.append("infrastructure decision must be documented in docs/adr/")` |
| `app/modules/deployment/production_readiness_contracts.py` | 109 | audit_append_call | `issues.append("deployment architecture must be documented in docs/deployment/")` |
| `app/modules/deployment/production_readiness_contracts.py` | 111 | audit_append_call | `issues.append("infrastructure-as-code is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 113 | audit_append_call | `issues.append("manual production approval is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 115 | audit_append_call | `issues.append("environment separation is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 132 | audit_append_call | `issues.append(f"{self.stage.value} command is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 134 | audit_append_call | `issues.append(f"{self.stage.value} production check must block deploy")` |
| `app/modules/deployment/production_readiness_contracts.py` | 136 | audit_append_call | `issues.append("security scan must run for PRs")` |
| `app/modules/deployment/production_readiness_contracts.py` | 138 | audit_append_call | `issues.append("migration check must run before staging")` |
| `app/modules/deployment/production_readiness_contracts.py` | 157 | audit_append_call | `issues.append("dockerfile path is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 159 | audit_append_call | `issues.append("container must run as non-root user")` |
| `app/modules/deployment/production_readiness_contracts.py` | 161 | audit_append_call | `issues.append("base image pinning is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 163 | audit_append_call | `issues.append("container healthcheck is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 165 | audit_append_call | `issues.append("multi-stage build is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 167 | audit_append_call | `issues.append("dependency lockfile is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 169 | audit_append_call | `issues.append("container vulnerability scan is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 171 | audit_append_call | `issues.append("SBOM generation is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 191 | audit_append_call | `issues.append(f"{self.environment.value} missing required variable {variable}")` |
| `app/modules/deployment/production_readiness_contracts.py` | 193 | audit_append_call | `issues.append(f"{self.environment.value} secrets must be externalized")` |
| `app/modules/deployment/production_readiness_contracts.py` | 195 | audit_append_call | `issues.append("production debug must be disabled")` |
| `app/modules/deployment/production_readiness_contracts.py` | 197 | audit_append_call | `issues.append("production TLS is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 199 | audit_append_call | `issues.append("database migrations must be controlled")` |
| `app/modules/deployment/production_readiness_contracts.py` | 201 | audit_append_call | `issues.append(f"{self.environment.value} observability is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 204 | audit_append_call | `issues.append(f"forbidden variable {variable} cannot be required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 223 | audit_append_call | `issues.append("deployment gate name is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 225 | audit_append_call | `issues.append("deployment gate requires checks")` |
| `app/modules/deployment/production_readiness_contracts.py` | 227 | audit_append_call | `issues.append("production deployment gate requires manual approval")` |
| `app/modules/deployment/production_readiness_contracts.py` | 229 | audit_append_call | `issues.append("production strategy must preserve manual approval")` |
| `app/modules/deployment/production_readiness_contracts.py` | 231 | audit_append_call | `issues.append("rollback plan is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 233 | audit_append_call | `issues.append("smoke test is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 235 | audit_append_call | `issues.append("release notes are required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 237 | audit_append_call | `issues.append("deployment gate owner is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 254 | audit_append_call | `issues.append("rollback command must be documented")` |
| `app/modules/deployment/production_readiness_contracts.py` | 256 | audit_append_call | `issues.append("database rollback policy must be documented")` |
| `app/modules/deployment/production_readiness_contracts.py` | 258 | audit_append_call | `issues.append("feature flag rollback support is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 260 | audit_append_call | `issues.append("previous image must be retained")` |
| `app/modules/deployment/production_readiness_contracts.py` | 262 | audit_append_call | `issues.append("post-rollback smoke test is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 264 | audit_append_call | `issues.append("rollback incident record is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 281 | audit_append_call | `issues.append("git_sha must be lowercase hex")` |
| `app/modules/deployment/production_readiness_contracts.py` | 283 | audit_append_call | `issues.append("image_digest must be sha256")` |
| `app/modules/deployment/production_readiness_contracts.py` | 291 | audit_append_call | `issues.append(f"{name} is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 293 | audit_append_call | `issues.append("generated_at_utc is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 309 | audit_append_call | `issues.append(f"missing required environment variable {variable}")` |
| `app/modules/deployment/production_readiness_contracts.py` | 312 | audit_append_call | `issues.append(f"secret-like variable {key} has placeholder value")` |
| `app/modules/deployment/production_readiness_contracts.py` | 314 | audit_append_call | `issues.append("production manifest must set ENVIRONMENT=production")` |
| `app/modules/diagnostics/diagnostic_session_service.py` | 68 | audit_append_call | `snap.served_item_ids.append(item_id)` |
| `app/modules/diagnostics/diagnostic_session_service.py` | 77 | audit_append_call | `snap.responses.append({"item_id": item_id, "correct": correct, "response": response})` |
| `app/modules/diagnostics/diagnostic_session_service.py` | 84 | audit_append_call | `snap.gap_topics.append(caps_ref)` |
| `app/modules/diagnostics/diagnostic_session_service.py` | 87 | audit_append_call | `snap.misconception_tags.append(tag)` |
| `app/modules/diagnostics/irt_engine.py` | 256 | audit_append_call | `grid.append(round(value, 4))` |
| `app/modules/diagnostics/irt_engine.py` | 268 | audit_append_call | `posterior_weights.append(prior * likelihood)` |
| `app/modules/diagnostics/irt_engine.py` | 497 | audit_append_call | `weights.append(prior * likelihood)` |
| `app/modules/diagnostics/irt_engine.py` | 602 | audit_append_call | `state.responses.append((str(item.item_id), is_correct))` |
| `app/modules/diagnostics/irt_engine.py` | 644 | audit_append_call | `proxies.append((last_item, correct))` |
| `app/modules/diagnostics/irt_engine.py` | 646 | audit_append_call | `proxies.append((_ItemProxy(), correct))` |
| `app/modules/diagnostics/irt_engine.py` | 740 | audit_append_call | `grid.append(round(value, 4))` |
| `app/modules/diagnostics/irt_engine.py` | 752 | audit_append_call | `weights.append(prior * likelihood)` |
| `app/modules/diagnostics/item_validator.py` | 179 | audit_append_call | `errors.append(exc)` |
| `app/modules/diagnostics/item_validator.py` | 250 | audit_append_call | `text_fields.append((f"option_{opt.get('label')}", opt.get("text", "")))` |
| `app/modules/diagnostics/production_readiness_contracts.py` | 77 | audit_append_call | `failures.append(f"{field_name} is required")` |
| `app/modules/diagnostics/production_readiness_contracts.py` | 79 | audit_append_call | `failures.append("grade must be between 0 and 12")` |
| `app/modules/diagnostics/production_readiness_contracts.py` | 81 | audit_append_call | `failures.append("difficulty must be in [-4.0, 4.0]")` |
| `app/modules/diagnostics/production_readiness_contracts.py` | 83 | audit_append_call | `failures.append("discrimination must be in [0.1, 4.0]")` |
| `app/modules/diagnostics/production_readiness_contracts.py` | 85 | audit_append_call | `failures.append("at least one distractor is required")` |
| `app/modules/diagnostics/production_readiness_contracts.py` | 87 | audit_append_call | `failures.append("correct answer must not appear as a distractor")` |
| `app/modules/diagnostics/production_readiness_contracts.py` | 89 | audit_append_call | `failures.append("max_exposure must be positive")` |
| `app/modules/diagnostics/production_readiness_contracts.py` | 91 | audit_append_call | `failures.append("exposure_count must be non-negative")` |
| `app/modules/diagnostics/production_readiness_contracts.py` | 188 | audit_append_call | `failures.append(` |
| `app/modules/diagnostics/quality_scorer.py` | 179 | audit_append_call | `texts.append(opt.get("text", ""))` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 23 | audit_logs_table | `AUDIT_LOGS = "audit_logs"` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 70 | audit_append_call | `issues.append("database backup provider is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 72 | audit_append_call | `issues.append("object backup provider is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 74 | audit_append_call | `issues.append("backup storage provider is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 76 | audit_append_call | `issues.append("backup provider decision must be documented in docs/adr/")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 78 | audit_append_call | `issues.append("backup architecture must be documented in docs/disaster_recovery/")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 80 | audit_append_call | `issues.append("backup encryption at rest is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 82 | audit_append_call | `issues.append("backup encryption in transit is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 84 | audit_append_call | `issues.append("cross-region backup copy is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 86 | audit_append_call | `issues.append("immutable retention is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 104 | audit_append_call | `issues.append(f"{self.scope.value} retention must be positive")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 106 | audit_append_call | `issues.append(f"{self.scope.value} critical backups must be hourly or daily")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 108 | audit_append_call | `issues.append("database backups require point-in-time recovery")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 110 | audit_append_call | `issues.append(f"{self.scope.value} backups must be encrypted")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 112 | audit_append_call | `issues.append(f"{self.scope.value} backups require integrity checks")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 114 | audit_append_call | `issues.append(f"{self.scope.value} backup owner is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 130 | audit_append_call | `issues.append("service is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 132 | audit_append_call | `issues.append("RPO cannot be negative")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 134 | audit_append_call | `issues.append("RTO cannot be negative")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 136 | audit_append_call | `issues.append("critical services require RPO <= 60 minutes")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 138 | audit_append_call | `issues.append("critical services require RTO <= 240 minutes")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 140 | audit_append_call | `issues.append("recovery owner is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 142 | audit_append_call | `issues.append("escalation route is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 162 | audit_append_call | `issues.append("manifest_id is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 164 | audit_append_call | `issues.append("backup_id is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 166 | audit_append_call | `issues.append("created_at_utc must be timezone-aware")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 168 | audit_append_call | `issues.append("source_environment is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 170 | audit_append_call | `issues.append("storage_location is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 172 | audit_append_call | `issues.append("checksum_sha256 must be 64 lowercase hex characters")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 174 | audit_append_call | `issues.append("backup manifest entry must be encrypted")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 176 | audit_append_call | `issues.append("retention_expires_at_utc must be timezone-aware")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 178 | audit_append_call | `issues.append("retention expiry must be after creation time")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 196 | audit_append_call | `issues.append("restore runbook must live under docs/disaster_recovery/runbooks/")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 198 | audit_append_call | `issues.append("pre-restore checks are required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 200 | audit_append_call | `issues.append("restore steps are required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 202 | audit_append_call | `issues.append("post-restore validation is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 204 | audit_append_call | `issues.append("rollback steps are required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 206 | audit_append_call | `issues.append("restore runbook owner is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 228 | audit_append_call | `issues.append("drill_id is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 230 | audit_append_call | `issues.append("drill timestamps must be timezone-aware")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 232 | audit_append_call | `issues.append("drill completion must be after start")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 234 | audit_append_call | `issues.append("observed RPO cannot be negative")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 236 | audit_append_call | `issues.append("observed RTO cannot be negative")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 238 | audit_append_call | `issues.append("passing restore drill requires checksum verification")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 240 | audit_append_call | `issues.append("passing restore drill requires application smoke test")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 242 | audit_append_call | `issues.append("passing restore drill requires data integrity test")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 244 | audit_append_call | `issues.append("restore drill evidence must live under docs/disaster_recovery/evidence/")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 263 | audit_append_call | `issues.append("plan_id is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 271 | audit_append_call | `issues.append(f"{name} is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 273 | audit_append_call | `issues.append("escalation matrix must be documented in docs/disaster_recovery/")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 275 | audit_append_call | `issues.append("business continuity plan must be documented in docs/disaster_recovery/")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 277 | audit_append_call | `issues.append("annual DR test is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 279 | audit_append_call | `issues.append("post-incident review is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 75 | audit_append_call | `issues.append("documentation governance decision must be documented in docs/adr/")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 77 | audit_append_call | `issues.append("documentation architecture must be documented in docs/documentation/")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 87 | audit_append_call | `issues.append(f"{name} is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 106 | audit_append_call | `issues.append("documentation path must live under docs/")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 108 | audit_append_call | `issues.append("documentation title is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 110 | audit_append_call | `issues.append("documentation owner is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 112 | audit_append_call | `issues.append("review interval must be positive")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 114 | audit_append_call | `issues.append(f"{self.path} is stale")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 116 | audit_append_call | `issues.append("superseded documentation must identify replacement or successor")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 118 | audit_append_call | `issues.append("active operator/security/privacy docs must identify source-of-truth status")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 138 | audit_append_call | `issues.append("ADR ID must follow ADR-### format")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 140 | audit_append_call | `issues.append("ADR path must live under docs/adr/")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 142 | audit_append_call | `issues.append("ADR title is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 144 | audit_append_call | `issues.append("ADR owner is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 146 | audit_append_call | `issues.append("accepted ADR requires decision section")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 148 | audit_append_call | `issues.append("ADR context section is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 150 | audit_append_call | `issues.append("ADR consequences section is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 152 | audit_append_call | `issues.append("superseded ADR must identify successor")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 170 | audit_append_call | `issues.append("claim_id is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 172 | audit_append_call | `issues.append("claim_text is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 174 | audit_append_call | `issues.append("claim owner is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 176 | audit_append_call | `issues.append("verified claims require evidence paths")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 179 | audit_append_call | `issues.append("claim evidence path must be controlled")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 181 | audit_append_call | `issues.append("external/manual/legal/security claims require external dependency note")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 183 | audit_append_call | `issues.append("production claims must be verified or clearly excluded")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 185 | audit_append_call | `issues.append("unsupported claims are not allowed in production readiness evidence")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 201 | audit_append_call | `issues.append("claim discipline rule_id is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 203 | audit_append_call | `issues.append("claim discipline description is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 205 | audit_append_call | `issues.append("prohibited phrases are required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 207 | audit_append_call | `issues.append("required boundary phrase is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 209 | audit_append_call | `issues.append("claim discipline path scope is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 211 | audit_append_call | `issues.append("claim discipline violations must block release")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 229 | audit_append_call | `issues.append("release note entry_id is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 231 | audit_append_call | `issues.append("release note summary is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 233 | audit_append_call | `issues.append("release note evidence path must be controlled")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 235 | audit_append_call | `issues.append("breaking changes must use breaking_change release note type")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 237 | audit_append_call | `issues.append("migration-required notes must be breaking_change or operations")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 239 | audit_append_call | `issues.append("release note owner is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 256 | audit_append_call | `issues.append("stale documentation finding_id is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 258 | audit_append_call | `issues.append("stale documentation path must live under docs/")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 260 | audit_append_call | `issues.append("days_stale cannot be negative")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 262 | audit_append_call | `issues.append("stale documentation owner is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 264 | audit_append_call | `issues.append("stale documentation severity is invalid")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 266 | audit_append_call | `issues.append("stale documentation action is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 268 | audit_append_call | `issues.append("release_blocker stale docs must block release")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 287 | audit_append_call | `issues.append("documentation review gate_id is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 289 | audit_append_call | `issues.append("documentation review gate requires docs")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 291 | audit_append_call | `issues.append("documentation review gate requires ADRs")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 294 | audit_append_call | `issues.append("required documentation must live under docs/")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 297 | audit_append_call | `issues.append("required ADRs must live under docs/adr/")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 299 | audit_append_call | `issues.append("claim review is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 301 | audit_append_call | `issues.append("stale documentation review is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 303 | audit_append_call | `issues.append("release notes are required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 305 | audit_append_call | `issues.append("documentation review gate owner is required")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 307 | audit_append_call | `issues.append("documentation review gate must block release")` |
| `app/modules/documentation_governance/production_readiness_contracts.py` | 331 | audit_append_call | `issues.append(f"{claim.claim_id} contains unbounded production claim")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 89 | audit_append_call | `issues.append("final release-blocker decision must be documented in docs/adr/")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 91 | audit_append_call | `issues.append("release-blocker architecture must be documented in docs/release_blockers/")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 102 | audit_append_call | `issues.append(f"{name} is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 123 | audit_append_call | `issues.append("blocker_id must follow RB-### format")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 125 | audit_append_call | `issues.append("release blocker title is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 127 | audit_append_call | `issues.append("release blocker owner is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 129 | audit_append_call | `issues.append("release blocker evidence path must be controlled")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 131 | audit_append_call | `issues.append("closed blockers require closure evidence")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 133 | audit_append_call | `issues.append("closure evidence path must be controlled")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 135 | audit_append_call | `issues.append("waived blockers require waiver evidence")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 137 | audit_append_call | `issues.append("waiver evidence must live under docs/release_blockers/")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 139 | audit_append_call | `issues.append("external pending blockers require external dependency note")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 141 | audit_append_call | `issues.append("critical/release-blocker items cannot remain open")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 143 | audit_append_call | `issues.append("release-blocker severity cannot be waived by default")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 145 | audit_append_call | `issues.append(f"{self.blocker_id} still blocks launch")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 162 | audit_append_call | `issues.append("domain checklist path must live under docs/")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 164 | audit_append_call | `issues.append("domain check command is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 166 | audit_append_call | `issues.append("domain summary owner is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 168 | audit_append_call | `issues.append(f"{self.domain.value} release evidence is incomplete")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 170 | audit_append_call | `issues.append("external/manual domain requires manual dependency")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 187 | audit_append_call | `issues.append("waiver rule_id is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 189 | audit_append_call | `issues.append("release-blocker severity cannot be waived")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 191 | audit_append_call | `issues.append("waiver requires approvers")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 193 | audit_append_call | `issues.append("waiver expiry must be between 1 and 30 days")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 195 | audit_append_call | `issues.append("waiver requires compensating controls")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 197 | audit_append_call | `issues.append("waiver rule evidence path must live under docs/release_blockers/")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 215 | audit_append_call | `issues.append("dependency_id must follow EXT-### format")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 217 | audit_append_call | `issues.append("external dependency description is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 219 | audit_append_call | `issues.append("external dependency owner is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 221 | audit_append_call | `issues.append("external system is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 223 | audit_append_call | `issues.append("verification method is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 225 | audit_append_call | `issues.append("external dependency evidence path must live under docs/release_blockers/")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 227 | audit_append_call | `issues.append(f"{self.dependency_id} required external dependency is not closed")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 248 | audit_append_call | `issues.append("final go/no-go checklist_id is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 250 | audit_append_call | `issues.append("final go/no-go approvers are required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 252 | audit_append_call | `issues.append("release owner approval is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 254 | audit_append_call | `issues.append("required domains are required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 256 | audit_append_call | `issues.append("blocker register path must live under docs/release_blockers/")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 258 | audit_append_call | `issues.append("evidence bundle path must be controlled")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 267 | audit_append_call | `issues.append(f"{name} must be reviewed")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 269 | audit_append_call | `issues.append("GO decision must include external/manual dependency review")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 287 | audit_append_call | `issues.append("closure_id must follow CLOSE-### format")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 289 | audit_append_call | `issues.append("blocker_id must follow RB-### format")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 291 | audit_append_call | `issues.append("closed_by is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 293 | audit_append_call | `issues.append("evidence_checksum must be 64 lowercase hex")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 295 | audit_append_call | `issues.append("closure evidence path must be controlled")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 297 | audit_append_call | `issues.append("residual risk summary is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 347 | audit_append_call | `issues.append(f"checklist GO conflicts with computed {decision.value}")` |
| `app/modules/lessons/adaptive_remediation.py` | 159 | audit_append_call | `resolved_strategies.append(strategy)` |
| `app/modules/lessons/adaptive_remediation.py` | 162 | audit_append_call | `unrecognised_tags.append(tag)` |
| `app/modules/lessons/adaptive_remediation.py` | 163 | audit_append_call | `resolved_strategies.append(RemediationStrategy.RE_EXPLAIN)` |
| `app/modules/lessons/answer_key_verifier.py` | 107 | audit_append_call | `stripped.append(clean)` |
| `app/modules/lessons/answer_key_verifier.py` | 249 | audit_append_call | `disagreements.append({` |
| `app/modules/lessons/answer_key_verifier.py` | 257 | audit_append_call | `disagreements.append({` |
| `app/modules/lessons/answer_key_verifier.py` | 335 | audit_append_call | `results.append(` |
| `app/modules/lessons/caps_topic_map_service.py` | 159 | audit_append_call | `self._maps.append(topic_map)` |
| `app/modules/lessons/caps_topic_map_service.py` | 201 | audit_append_call | `subtopics.append(` |
| `app/modules/lessons/caps_topic_map_service.py` | 211 | audit_append_call | `topics.append(` |
| `app/modules/lessons/caps_topic_map_service.py` | 219 | audit_append_call | `terms.append(` |
| `app/modules/lessons/lesson_coverage_router.py` | 99 | audit_append_call | `rows.append({` |
| `app/modules/lessons/lesson_coverage_router.py` | 108 | audit_append_call | `rows.append({` |
| `app/modules/lessons/lesson_coverage_router.py` | 154 | audit_append_call | `per_ref.append(CapsRefCoverage(` |
| `app/modules/lessons/lesson_generator.py` | 464 | audit_append_call | `disagreements.append(` |
| `app/modules/lessons/lesson_review_router.py` | 88 | audit_append_call | `reasons.append(f"Quality score {score} is below the {QUALITY_SCORE_REVIEW_THRESHOLD} threshold.")` |
| `app/modules/lessons/lesson_review_router.py` | 90 | audit_append_call | `reasons.append("Answer key has not been independently verified.")` |
| `app/modules/lessons/lesson_review_router.py` | 92 | audit_append_call | `reasons.append("Safety classifier flagged content as requiring human review.")` |
| `app/modules/lessons/lesson_validator.py` | 127 | audit_append_call | `failures.append(` |
| `app/modules/lessons/lesson_validator.py` | 134 | audit_append_call | `failures.append(` |
| `app/modules/lessons/lesson_validator.py` | 146 | audit_append_call | `failures.append("FAIL: " + msg)` |
| `app/modules/lessons/lesson_validator.py` | 148 | audit_append_call | `warnings.append("WARN: " + msg + " (queued for human review)")` |
| `app/modules/lessons/lesson_validator.py` | 152 | audit_append_call | `failures.append(` |
| `app/modules/lessons/lesson_validator.py` | 160 | audit_append_call | `failures.append(` |
| `app/modules/lessons/lesson_validator.py` | 168 | audit_append_call | `warnings.append(` |
| `app/modules/lessons/lesson_validator.py` | 180 | audit_append_call | `failures.append(` |
| `app/modules/lessons/lesson_validator.py` | 222 | audit_append_call | `questions.append(qq)` |
| `app/modules/lessons/lesson_validator.py` | 236 | audit_append_call | `examples.append(ee)` |
| `app/modules/lessons/lesson_validator.py` | 313 | audit_append_call | `texts_to_scan.append((f"worked_examples[{i}].question", ex.question))` |
| `app/modules/lessons/lesson_validator.py` | 314 | audit_append_call | `texts_to_scan.append(` |
| `app/modules/lessons/lesson_validator.py` | 318 | audit_append_call | `texts_to_scan.append((f"practice_questions[{q.question_id}]", q.question_text))` |
| `app/modules/lessons/lesson_validator.py` | 320 | audit_append_call | `texts_to_scan.append(` |
| `app/modules/lessons/lesson_validator.py` | 328 | audit_append_call | `failures.append(` |
| `app/modules/lessons/lesson_validator.py` | 337 | audit_append_call | `failures.append(` |
| `app/modules/lessons/lesson_validator.py` | 371 | audit_append_call | `rules.append("caps_ref_resolves")` |
| `app/modules/lessons/lesson_validator.py` | 373 | audit_append_call | `rules.append("answer_key_verified")` |
| `app/modules/lessons/lesson_validator.py` | 375 | audit_append_call | `rules.append("explanation_non_empty")` |
| `app/modules/lessons/lesson_validator.py` | 377 | audit_append_call | `rules.append("schema_valid")` |
| `app/modules/lessons/lesson_validator.py` | 378 | audit_append_call | `rules.append(failure)` |
| `app/modules/lessons/llm_gateway.py` | 146 | audit_append_call | `messages.append({"role": "system", "content": system})` |
| `app/modules/lessons/llm_gateway.py` | 147 | audit_append_call | `messages.append({"role": "user", "content": prompt})` |
| `app/modules/lessons/llm_gateway_v2.py` | 160 | audit_append_call | `messages.append({"role": "system", "content": system})` |
| `app/modules/lessons/llm_gateway_v2.py` | 161 | audit_append_call | `messages.append({"role": "user", "content": prompt})` |
| `app/modules/lessons/llm_gateway_v2.py` | 270 | audit_append_call | `self._providers.append((` |
| `app/modules/lessons/llm_gateway_v2.py` | 276 | audit_append_call | `self._providers.append((` |
| `app/modules/lessons/llm_gateway_v2.py` | 391 | audit_append_call | `self._token_log.append(entry)` |
| `app/modules/lessons/teacher_insight_mode.py` | 184 | audit_append_call | `tag_to_learners.setdefault(tag, []).append(record.learner_id)` |
| `app/modules/lessons/teacher_insight_mode.py` | 220 | audit_append_call | `groups.append(` |
| `app/modules/lessons/teacher_insight_mode.py` | 393 | audit_append_call | `clusters.append(` |
| `app/modules/notifications/production_readiness_contracts.py` | 83 | audit_append_call | `issues.append("communication provider decision must be documented in docs/adr/")` |
| `app/modules/notifications/production_readiness_contracts.py` | 85 | audit_append_call | `issues.append("notification architecture must be documented in docs/notifications/")` |
| `app/modules/notifications/production_readiness_contracts.py` | 94 | audit_append_call | `issues.append(f"{name} is required")` |
| `app/modules/notifications/production_readiness_contracts.py` | 96 | audit_append_call | `issues.append("provider webhook signature verification is required")` |
| `app/modules/notifications/production_readiness_contracts.py` | 98 | audit_append_call | `issues.append("provider webhook idempotency is required")` |
| `app/modules/notifications/production_readiness_contracts.py` | 100 | audit_append_call | `issues.append("bounce and complaint handling is required")` |
| `app/modules/notifications/production_readiness_contracts.py` | 134 | audit_append_call | `issues.append("daily rate limit must be positive")` |
| `app/modules/notifications/production_readiness_contracts.py` | 136 | audit_append_call | `issues.append("hourly rate limit must be positive")` |
| `app/modules/notifications/production_readiness_contracts.py` | 138 | audit_append_call | `issues.append("hourly rate limit cannot exceed daily rate limit")` |
| `app/modules/notifications/production_readiness_contracts.py` | 140 | audit_append_call | `issues.append("marketing preference must be explicitly modeled")` |
| `app/modules/notifications/production_readiness_contracts.py` | 142 | audit_append_call | `issues.append("marketing unsubscribe is required")` |
| `app/modules/notifications/production_readiness_contracts.py` | 144 | audit_append_call | `issues.append("notification audit logging is required")` |
| `app/modules/notifications/production_readiness_contracts.py` | 146 | audit_append_call | `issues.append("notification idempotency is required")` |
| `app/modules/notifications/production_readiness_contracts.py` | 148 | audit_append_call | `issues.append("direct learner SMS is prohibited by default")` |
| `app/modules/notifications/production_readiness_contracts.py` | 150 | audit_append_call | `issues.append("direct learner WhatsApp is prohibited by default")` |
| `app/modules/notifications/production_readiness_contracts.py` | 171 | audit_append_call | `issues.append("template_id is required")` |
| `app/modules/notifications/production_readiness_contracts.py` | 173 | audit_append_call | `issues.append("template version is required")` |
| `app/modules/notifications/production_readiness_contracts.py` | 175 | audit_append_call | `issues.append("at least one channel is required")` |
| `app/modules/notifications/production_readiness_contracts.py` | 177 | audit_append_call | `issues.append("learner billing or marketing templates are prohibited")` |
| `app/modules/notifications/production_readiness_contracts.py` | 181 | audit_append_call | `issues.append(f"template variable {variable!r} missing from required_variables")` |
| `app/modules/notifications/production_readiness_contracts.py` | 183 | audit_append_call | `issues.append("SMS templates cannot allow HTML")` |
| `app/modules/notifications/production_readiness_contracts.py` | 185 | audit_append_call | `issues.append("template review is required")` |
| `app/modules/notifications/production_readiness_contracts.py` | 206 | audit_append_call | `issues.append("recipient_id is required")` |
| `app/modules/notifications/production_readiness_contracts.py` | 208 | audit_append_call | `issues.append("learner billing and marketing notifications are prohibited")` |
| `app/modules/notifications/production_readiness_contracts.py` | 210 | audit_append_call | `issues.append("direct learner SMS or WhatsApp delivery is prohibited by default")` |
| `app/modules/notifications/production_readiness_contracts.py` | 212 | audit_append_call | `issues.append("template_id is required")` |
| `app/modules/notifications/production_readiness_contracts.py` | 214 | audit_append_call | `issues.append("template_version is required")` |
| `app/modules/notifications/production_readiness_contracts.py` | 216 | audit_append_call | `issues.append("request_id is required")` |
| `app/modules/notifications/production_readiness_contracts.py` | 218 | audit_append_call | `issues.append("idempotency_key is required")` |
| `app/modules/notifications/production_readiness_contracts.py` | 220 | audit_append_call | `issues.append("scheduled_at_utc must be timezone-aware")` |
| `app/modules/notifications/production_readiness_contracts.py` | 253 | audit_log_identifier | `audit_log: list[str] = field(default_factory=list)` |
| `app/modules/notifications/production_readiness_contracts.py` | 261 | audit_append_call | `self.audit_log.append(f"duplicate:{request.idempotency_key}:{request.purpose.value}")` |
| `app/modules/notifications/production_readiness_contracts.py` | 261 | audit_log_identifier | `self.audit_log.append(f"duplicate:{request.idempotency_key}:{request.purpose.value}")` |
| `app/modules/notifications/production_readiness_contracts.py` | 264 | audit_append_call | `self.audit_log.append(f"queued:{request.idempotency_key}:{request.channel.value}:{request.purpose.value}")` |
| `app/modules/notifications/production_readiness_contracts.py` | 264 | audit_log_identifier | `self.audit_log.append(f"queued:{request.idempotency_key}:{request.channel.value}:{request.purpose.value}")` |
| `app/modules/notifications/production_readiness_contracts.py` | 268 | audit_append_call | `self.dead_letter.append(f"{idempotency_key}:{reason}")` |
| `app/modules/notifications/production_readiness_contracts.py` | 279 | audit_append_call | `issues.append("max_attempts must be at least 1")` |
| `app/modules/notifications/production_readiness_contracts.py` | 281 | audit_append_call | `issues.append("backoff schedule is required")` |
| `app/modules/notifications/production_readiness_contracts.py` | 283 | audit_append_call | `issues.append("backoff values must be positive")` |
| `app/modules/notifications/production_readiness_contracts.py` | 304 | audit_append_call | `issues.append("event_id is required")` |
| `app/modules/notifications/production_readiness_contracts.py` | 306 | audit_append_call | `issues.append("recipient_id is required")` |
| `app/modules/notifications/production_readiness_contracts.py` | 308 | audit_append_call | `issues.append("request_id is required")` |
| `app/modules/notifications/production_readiness_contracts.py` | 310 | audit_append_call | `issues.append("idempotency_key is required")` |
| `app/modules/notifications/production_readiness_contracts.py` | 312 | audit_append_call | `issues.append("occurred_at_utc must be timezone-aware")` |
| `app/modules/notifications/production_readiness_contracts.py` | 314 | audit_append_call | `issues.append("raw provider payloads must not be retained without redaction")` |
| `app/modules/observability/production_readiness_contracts.py` | 82 | audit_append_call | `issues.append("observability provider decision must be documented in docs/adr/")` |
| `app/modules/observability/production_readiness_contracts.py` | 84 | audit_append_call | `issues.append("observability architecture must be documented in docs/observability/")` |
| `app/modules/observability/production_readiness_contracts.py` | 93 | audit_append_call | `issues.append(f"{name} is required")` |
| `app/modules/observability/production_readiness_contracts.py` | 95 | audit_append_call | `issues.append("OpenTelemetry instrumentation is required")` |
| `app/modules/observability/production_readiness_contracts.py` | 97 | audit_append_call | `issues.append("PII redaction is required")` |
| `app/modules/observability/production_readiness_contracts.py` | 99 | audit_append_call | `issues.append("telemetry retention policy is required")` |
| `app/modules/observability/production_readiness_contracts.py` | 116 | audit_append_call | `issues.append("metric name is required")` |
| `app/modules/observability/production_readiness_contracts.py` | 118 | audit_append_call | `issues.append("metric name must be lowercase prometheus-style text")` |
| `app/modules/observability/production_readiness_contracts.py` | 120 | audit_append_call | `issues.append("metric description is required")` |
| `app/modules/observability/production_readiness_contracts.py` | 122 | audit_append_call | `issues.append("metric unit is required")` |
| `app/modules/observability/production_readiness_contracts.py` | 124 | audit_append_call | `issues.append("metric labels must include environment")` |
| `app/modules/observability/production_readiness_contracts.py` | 126 | audit_append_call | `issues.append("metric labels must include service")` |
| `app/modules/observability/production_readiness_contracts.py` | 128 | audit_append_call | `issues.append("metric must be PII safe")` |
| `app/modules/observability/production_readiness_contracts.py` | 144 | audit_append_call | `issues.append("log event name is required")` |
| `app/modules/observability/production_readiness_contracts.py` | 147 | audit_append_call | `issues.append(f"log event missing required correlation field {field}")` |
| `app/modules/observability/production_readiness_contracts.py` | 149 | audit_append_call | `issues.append("log redaction is required")` |
| `app/modules/observability/production_readiness_contracts.py` | 152 | audit_append_call | `issues.append(f"prohibited field {prohibited} cannot be required")` |
| `app/modules/observability/production_readiness_contracts.py` | 154 | audit_append_call | `issues.append("sample log message must not contain PII")` |
| `app/modules/observability/production_readiness_contracts.py` | 171 | audit_append_call | `issues.append("span name is required")` |
| `app/modules/observability/production_readiness_contracts.py` | 173 | audit_append_call | `issues.append("span attributes must include service")` |
| `app/modules/observability/production_readiness_contracts.py` | 175 | audit_append_call | `issues.append("span attributes must include environment")` |
| `app/modules/observability/production_readiness_contracts.py` | 177 | audit_append_call | `issues.append("request_id propagation is required")` |
| `app/modules/observability/production_readiness_contracts.py` | 179 | audit_append_call | `issues.append("trace_id propagation is required")` |
| `app/modules/observability/production_readiness_contracts.py` | 181 | audit_append_call | `issues.append("error sampling is required")` |
| `app/modules/observability/production_readiness_contracts.py` | 183 | audit_append_call | `issues.append("trace attributes must be PII safe")` |
| `app/modules/observability/production_readiness_contracts.py` | 200 | audit_append_call | `issues.append("SLO name is required")` |
| `app/modules/observability/production_readiness_contracts.py` | 202 | audit_append_call | `issues.append("SLO target must be between 0 and 100")` |
| `app/modules/observability/production_readiness_contracts.py` | 204 | audit_append_call | `issues.append("production SLO target must be at least 90 percent")` |
| `app/modules/observability/production_readiness_contracts.py` | 206 | audit_append_call | `issues.append("SLO window is required")` |
| `app/modules/observability/production_readiness_contracts.py` | 208 | audit_append_call | `issues.append("SLI metric is required")` |
| `app/modules/observability/production_readiness_contracts.py` | 210 | audit_append_call | `issues.append("burn-rate alerts are required")` |
| `app/modules/observability/production_readiness_contracts.py` | 228 | audit_append_call | `issues.append("alert name is required")` |
| `app/modules/observability/production_readiness_contracts.py` | 230 | audit_append_call | `issues.append("alert expression is required")` |
| `app/modules/observability/production_readiness_contracts.py` | 232 | audit_append_call | `issues.append("alert runbook must live under docs/observability/runbooks/")` |
| `app/modules/observability/production_readiness_contracts.py` | 234 | audit_append_call | `issues.append("critical/page alerts require paging")` |
| `app/modules/observability/production_readiness_contracts.py` | 236 | audit_append_call | `issues.append("alert deduplication key is required")` |
| `app/modules/observability/production_readiness_contracts.py` | 254 | audit_append_call | `issues.append("dashboard name is required")` |
| `app/modules/observability/production_readiness_contracts.py` | 256 | audit_append_call | `issues.append("dashboard must include panels")` |
| `app/modules/observability/production_readiness_contracts.py` | 258 | audit_append_call | `issues.append("dashboard must link runbooks")` |
| `app/modules/observability/production_readiness_contracts.py` | 260 | audit_append_call | `issues.append("dashboard must include SLO panels")` |
| `app/modules/observability/production_readiness_contracts.py` | 262 | audit_append_call | `issues.append("dashboard must include error panels")` |
| `app/modules/observability/production_readiness_contracts.py` | 264 | audit_append_call | `issues.append("dashboard must include latency panels")` |
| `app/modules/observability/production_readiness_contracts.py` | 266 | audit_append_call | `issues.append("dashboard must include traffic panels")` |
| `app/modules/observability/production_readiness_contracts.py` | 283 | audit_append_call | `issues.append("metrics retention must be positive")` |
| `app/modules/observability/production_readiness_contracts.py` | 285 | audit_append_call | `issues.append("logs retention must be positive")` |
| `app/modules/observability/production_readiness_contracts.py` | 287 | audit_append_call | `issues.append("traces retention must be positive")` |
| `app/modules/observability/production_readiness_contracts.py` | 289 | audit_append_call | `issues.append("audit logs retention must be at least regular logs retention")` |
| `app/modules/observability/production_readiness_contracts.py` | 291 | audit_append_call | `issues.append("PII redaction is required")` |
| `app/modules/observability/production_readiness_contracts.py` | 293 | audit_append_call | `issues.append("telemetry deletion workflow is required")` |
| `app/modules/observability/production_readiness_contracts.py` | 295 | audit_append_call | `issues.append("telemetry export workflow is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 80 | audit_append_call | `issues.append("operations support decision must be documented in docs/adr/")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 82 | audit_append_call | `issues.append("operations support architecture must be documented in docs/operations_support/")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 93 | audit_append_call | `issues.append(f"{name} is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 111 | audit_append_call | `issues.append("incident response time must be positive")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 113 | audit_append_call | `issues.append("incident update interval must be positive")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 115 | audit_append_call | `issues.append(f"{self.severity.value} requires incident commander")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 117 | audit_append_call | `issues.append("sev1 requires status update")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 119 | audit_append_call | `issues.append("major or critical customer impact must block release")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 137 | audit_append_call | `issues.append("policy_id is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 139 | audit_append_call | `issues.append("primary and secondary roles must differ")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 141 | audit_append_call | `issues.append("escalation minutes must be positive")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 143 | audit_append_call | `issues.append("coverage hours are required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 145 | audit_append_call | `issues.append("backup on-call is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 147 | audit_append_call | `issues.append("on-call handoff is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 149 | audit_append_call | `issues.append("on-call evidence path must live under docs/operations_support/")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 168 | audit_append_call | `issues.append("operational runbook must live under docs/operations_support/runbooks/")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 170 | audit_append_call | `issues.append("runbook scenario is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 172 | audit_append_call | `issues.append("detection steps are required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 174 | audit_append_call | `issues.append("triage steps are required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 176 | audit_append_call | `issues.append("mitigation steps are required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 178 | audit_append_call | `issues.append("recovery steps are required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 180 | audit_append_call | `issues.append("verification steps are required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 182 | audit_append_call | `issues.append("rollback criteria are required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 198 | audit_append_call | `issues.append("first response minutes must be positive")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 200 | audit_append_call | `issues.append("target resolution hours must be positive")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 202 | audit_append_call | `issues.append(f"{self.priority.value} support requires escalation")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 204 | audit_append_call | `issues.append("p0 first response must be <= 30 minutes")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 206 | audit_append_call | `issues.append("p1 first response must be <= 120 minutes")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 223 | audit_append_call | `issues.append("template_id is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 225 | audit_append_call | `issues.append("status communication channels are required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 227 | audit_append_call | `issues.append("status communication audience is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 229 | audit_append_call | `issues.append("status update interval must be positive")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 231 | audit_append_call | `issues.append(f"{self.severity.value} status communication requires status page")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 234 | audit_append_call | `issues.append(f"status communication missing required field {field}")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 253 | audit_append_call | `issues.append("incident_id is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 255 | audit_append_call | `issues.append("detected_at_utc must be timezone-aware")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 257 | audit_append_call | `issues.append("resolved/reviewed incidents require root cause summary")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 259 | audit_append_call | `issues.append("incident evidence must live under docs/operations_support/incidents/")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 261 | audit_append_call | `issues.append("sev1/sev2 incidents require post-incident review")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 279 | audit_append_call | `issues.append("review_id is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 281 | audit_append_call | `issues.append("incident_id is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 283 | audit_append_call | `issues.append("post-incident review must be completed")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 285 | audit_append_call | `issues.append("root cause must be documented")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 287 | audit_append_call | `issues.append("incident timeline must be documented")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 289 | audit_append_call | `issues.append("corrective actions are required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 291 | audit_append_call | `issues.append("post-incident review evidence must live under docs/operations_support/post_incident_reviews/")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 310 | audit_append_call | `issues.append("operational handover checklist must live under docs/operations_support/")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 312 | audit_append_call | `issues.append("release owner is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 314 | audit_append_call | `issues.append("support owner is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 324 | audit_append_call | `issues.append(f"{name} must be true")` |
| `app/modules/practice/router.py` | 62 | audit_append_call | `session["responses"].append(body.model_dump(mode="json"))` |
| `app/modules/progress/learning_velocity_service.py` | 41 | audit_append_call | `ranked.append({"caps_ref": caps_ref, "activity": activity, "mastery_score": score, "priority": priority})` |
| `app/modules/progress/progress_timeline_service.py` | 28 | audit_append_call | `groups[row.caps_ref.split('.')[1] if '.' in row.caps_ref else 'unknown'].append(row)` |
| `app/modules/progress/progress_timeline_service.py` | 32 | audit_append_call | `summaries.append({"subject_code": key, "topic_count": len(values), "average_mastery": round(avg, 4)})` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 79 | audit_append_call | `issues.append("testing strategy decision must be documented in docs/adr/")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 81 | audit_append_call | `issues.append("testing architecture must be documented in docs/testing/")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 93 | audit_append_call | `issues.append(f"{name} is required")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 111 | audit_append_call | `issues.append(f"{self.layer.value} test command is required")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 113 | audit_append_call | `issues.append(f"{self.layer.value} test owner is required")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 115 | audit_append_call | `issues.append(f"{self.layer.value} production tests must also gate staging")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 117 | audit_append_call | `issues.append(f"{self.layer.value} PR tests must be deterministic")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 119 | audit_append_call | `issues.append(f"{self.layer.value} tests require evidence artifact path")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 121 | audit_append_call | `issues.append(f"{self.layer.value} artifact path must be controlled")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 137 | audit_append_call | `issues.append("minimum line coverage must be between 0 and 100")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 139 | audit_append_call | `issues.append("minimum branch coverage must be between 0 and 100")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 141 | audit_append_call | `issues.append("production line coverage threshold must be at least 70 percent")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 143 | audit_append_call | `issues.append("coverage measured path is required")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 145 | audit_append_call | `issues.append("coverage ratchet is required")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 147 | audit_append_call | `issues.append("unit coverage waiver is not allowed by default")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 165 | audit_append_call | `issues.append("quality gate name is required")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 167 | audit_append_call | `issues.append("quality gate requires at least one test layer")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 169 | audit_append_call | `issues.append("quality gate requires evidence")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 171 | audit_append_call | `issues.append("production quality gate requires manual approval")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 173 | audit_append_call | `issues.append("quality gate waiver policy must live under docs/testing/")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 175 | audit_append_call | `issues.append("beta and production quality gates must block release")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 177 | audit_append_call | `issues.append("quality gate owner is required")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 195 | audit_append_call | `issues.append("evidence_id is required")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 197 | audit_append_call | `issues.append("evidence path must be controlled")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 199 | audit_append_call | `issues.append("generated_by is required")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 201 | audit_append_call | `issues.append("git_sha must be lowercase hex")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 203 | audit_append_call | `issues.append("checksum_sha256 must be 64 lowercase hex characters")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 205 | audit_append_call | `issues.append("beta and production evidence must be retained")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 221 | audit_append_call | `issues.append(f"{self.severity.value} defects must block release")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 223 | audit_append_call | `issues.append(f"{self.severity.value} defects require owner")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 225 | audit_append_call | `issues.append(f"{self.severity.value} defects require fix or waiver")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 227 | audit_append_call | `issues.append("release blockers allowed for production must be zero")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 229 | audit_append_call | `issues.append("defect SLA must be positive")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 247 | audit_append_call | `issues.append("release checklist must live under docs/testing/")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 249 | audit_append_call | `issues.append("release checklist requires approvers")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 251 | audit_append_call | `issues.append("release evidence bundle is required")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 253 | audit_append_call | `issues.append("known issues review is required")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 255 | audit_append_call | `issues.append("rollback review is required")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 257 | audit_append_call | `issues.append("smoke test is required")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 259 | audit_append_call | `issues.append("beta and production signoff is required")` |
| `app/modules/quality_gates/production_readiness_contracts.py` | 285 | audit_append_call | `issues.append(f"missing {evidence_type.value} for {stage.value}")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 85 | audit_append_call | `issues.append("roadmap governance decision must be documented in docs/adr/")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 87 | audit_append_call | `issues.append("roadmap architecture must be documented in docs/roadmap/")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 98 | audit_append_call | `issues.append(f"{name} is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 116 | audit_append_call | `issues.append("boundary_id is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 118 | audit_append_call | `issues.append("baseline boundary title is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 120 | audit_append_call | `issues.append("baseline boundary rationale is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 122 | audit_append_call | `issues.append("baseline boundary evidence path must be controlled")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 124 | audit_append_call | `issues.append("baseline boundary owner is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 126 | audit_append_call | `issues.append("external/manual boundary requires manual dependency")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 147 | audit_append_call | `issues.append("roadmap_id must follow RM-### format")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 149 | audit_append_call | `issues.append("roadmap item title is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 151 | audit_append_call | `issues.append("roadmap owner is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 153 | audit_append_call | `issues.append("roadmap rationale is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 155 | audit_append_call | `issues.append("roadmap expected outcome is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 157 | audit_append_call | `issues.append("P0/P1 items cannot be parked")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 159 | audit_append_call | `issues.append("in-progress items must be now or next")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 161 | audit_append_call | `issues.append("roadmap evidence path must live under docs/roadmap/")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 163 | audit_append_call | `issues.append("now/next roadmap items require target quarter")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 182 | audit_append_call | `issues.append("deferred_id must follow DEF-### format")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 184 | audit_append_call | `issues.append("deferred title is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 186 | audit_append_call | `issues.append("deferred reason is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 188 | audit_append_call | `issues.append("unblock condition is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 190 | audit_append_call | `issues.append("deferred scope owner is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 192 | audit_append_call | `issues.append("risk if deferred is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 194 | audit_append_call | `issues.append("deferred scope evidence path must live under docs/roadmap/")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 196 | audit_append_call | `issues.append("deferred scope review date is stale")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 214 | audit_append_call | `issues.append("dependency_id must follow DEP-### format")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 216 | audit_append_call | `issues.append("source_roadmap_id must follow RM-### format")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 218 | audit_append_call | `issues.append("dependency description is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 220 | audit_append_call | `issues.append("dependency owner is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 222 | audit_append_call | `issues.append("external dependencies require mitigation")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 224 | audit_append_call | `issues.append("roadmap dependency evidence path must live under docs/roadmap/")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 241 | audit_append_call | `issues.append("criterion_id must follow GRAD-### format")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 243 | audit_append_call | `issues.append("roadmap_id must follow RM-### format")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 245 | audit_append_call | `issues.append("graduation metric name is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 247 | audit_append_call | `issues.append("graduation threshold is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 249 | audit_append_call | `issues.append("graduation evidence path must be controlled")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 251 | audit_append_call | `issues.append("graduation criterion owner is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 253 | audit_append_call | `issues.append("GA-required graduation criterion must define metric")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 270 | audit_append_call | `issues.append("cadence_id is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 272 | audit_append_call | `issues.append("roadmap review frequency must be positive")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 274 | audit_append_call | `issues.append("roadmap review cadence must be at least quarterly")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 276 | audit_append_call | `issues.append("roadmap review owner is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 278 | audit_append_call | `issues.append("roadmap review requires inputs")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 280 | audit_append_call | `issues.append("roadmap review requires outputs")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 282 | audit_append_call | `issues.append("roadmap review evidence path must live under docs/roadmap/")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 284 | audit_append_call | `issues.append("roadmap review must block uncontrolled scope expansion")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 303 | audit_append_call | `issues.append("risk_id must follow RISK-### format")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 305 | audit_append_call | `issues.append("risk title is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 307 | audit_append_call | `issues.append("risk impact is invalid")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 309 | audit_append_call | `issues.append("risk likelihood is invalid")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 311 | audit_append_call | `issues.append("risk owner is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 313 | audit_append_call | `issues.append("risk mitigation is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 315 | audit_append_call | `issues.append("risk evidence path must live under docs/roadmap/")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 317 | audit_append_call | `issues.append("critical post-baseline risk must block GA")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 353 | audit_append_call | `issues.append(f"{dependency.dependency_id} references unknown roadmap item")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 98 | audit_append_call | `issues.append("security posture decision must be documented in docs/adr/")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 100 | audit_append_call | `issues.append("security architecture must be documented in docs/security/")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 111 | audit_append_call | `issues.append(f"{name} is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 130 | audit_append_call | `issues.append("threat_id is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 132 | audit_append_call | `issues.append("asset is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 134 | audit_append_call | `issues.append("abuse case is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 136 | audit_append_call | `issues.append("control summary is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 138 | audit_append_call | `issues.append("high or critical residual threat risk must be remediated or formally accepted")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 140 | audit_append_call | `issues.append("threat owner is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 142 | audit_append_call | `issues.append("threat model review is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 160 | audit_append_call | `issues.append("control_id is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 162 | audit_append_call | `issues.append("control name is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 164 | audit_append_call | `issues.append("control description is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 166 | audit_append_call | `issues.append(f"{self.control_id} is required but not implemented")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 168 | audit_append_call | `issues.append("security evidence path must be controlled")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 170 | audit_append_call | `issues.append("security control owner is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 172 | audit_append_call | `issues.append(f"{self.control_id} production-blocking control must be implemented or verified")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 188 | audit_append_call | `issues.append("vulnerability max age must be positive")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 190 | audit_append_call | `issues.append(f"{self.severity.value} vulnerabilities must block release")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 192 | audit_append_call | `issues.append(f"{self.severity.value} vulnerabilities require owner")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 194 | audit_append_call | `issues.append(f"{self.severity.value} vulnerabilities require fix or accepted risk")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 196 | audit_append_call | `issues.append(f"{self.severity.value} vulnerabilities require CVE or finding ID")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 214 | audit_append_call | `issues.append(f"{self.test_type.value} command is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 216 | audit_append_call | `issues.append(f"{self.test_type.value} production security test must also gate staging")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 222 | audit_append_call | `issues.append(f"{self.test_type.value} must run for PRs")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 224 | audit_append_call | `issues.append(f"{self.test_type.value} artifact path must be controlled")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 226 | audit_append_call | `issues.append(f"{self.test_type.value} owner is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 228 | audit_append_call | `issues.append(f"{self.test_type.value} production security test must block release")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 245 | audit_append_call | `issues.append("secret hygiene rule_id is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 247 | audit_append_call | `issues.append("secret hygiene description is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 249 | audit_append_call | `issues.append("secret hygiene pattern name is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 251 | audit_append_call | `issues.append("secret hygiene path scope is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 253 | audit_append_call | `issues.append("secret exposure must block commit or merge")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 255 | audit_append_call | `issues.append("secret exposure requires rotation")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 257 | audit_append_call | `issues.append("secret hygiene evidence path must be controlled")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 275 | audit_append_call | `issues.append("supply-chain control_id is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 277 | audit_append_call | `issues.append("dependency lockfile is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 279 | audit_append_call | `issues.append("SBOM is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 281 | audit_append_call | `issues.append("artifact provenance is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 283 | audit_append_call | `issues.append("dependency review is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 285 | audit_append_call | `issues.append("license review is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 287 | audit_append_call | `issues.append("signed artifact or digest pinning is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 289 | audit_append_call | `issues.append("supply-chain owner is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 307 | audit_append_call | `issues.append("security incident runbook must live under docs/security/runbooks/")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 309 | audit_append_call | `issues.append("security incident triage owner is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 311 | audit_append_call | `issues.append("containment steps are required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 313 | audit_append_call | `issues.append("eradication steps are required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 315 | audit_append_call | `issues.append("recovery steps are required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 317 | audit_append_call | `issues.append("notification steps are required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 319 | audit_append_call | `issues.append("post-incident review is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 337 | audit_append_call | `issues.append("risk_id is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 339 | audit_append_call | `issues.append("critical risks cannot be accepted for production by default")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 341 | audit_append_call | `issues.append("risk acceptance reason is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 343 | audit_append_call | `issues.append("risk owner is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 345 | audit_append_call | `issues.append("risk approver is required")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 347 | audit_append_call | `issues.append("risk acceptance expiry must be between 1 and 90 days")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 349 | audit_append_call | `issues.append("risk acceptance requires compensating controls")` |
| `app/modules/security_posture/production_readiness_contracts.py` | 351 | audit_append_call | `issues.append("risk acceptance evidence must live under docs/security/")` |
| `app/repositories/__init__.py` | 4 | audit_repository | `from app.repositories.audit_repository import AuditRepository` |
| `app/repositories/__init__.py` | 14 | audit_repository | `"AuditRepository",` |
| `app/repositories/audit_compat.py` | 73 | audit_record_call | `return await _maybe_await(self.repository.record(**canonical))` |
| `app/repositories/audit_compat.py` | 75 | audit_append_call | `return await _maybe_await(self.repository.append(**canonical))` |
| `app/repositories/audit_compat.py` | 84 | audit_record_call | `return await self.record(**kwargs)` |
| `app/repositories/audit_repository.py` | 75 | audit_repository | `class AuditRepository:` |
| `app/repositories/audit_repository.py` | 149 | audit_events_table | `INSERT INTO audit_events (` |
| `app/repositories/audit_repository.py` | 219 | audit_events_table | `INSERT INTO audit_events (` |
| `app/repositories/audit_repository.py` | 257 | audit_events_table | `SELECT * FROM audit_events` |
| `app/repositories/audit_repository.py` | 263 | audit_append_call | `args.append(event_type)` |
| `app/repositories/audit_repository.py` | 279 | audit_events_table | `SELECT * FROM audit_events` |
| `app/repositories/audit_repository.py` | 285 | audit_append_call | `args.append(event_type)` |
| `app/repositories/audit_repository.py` | 317 | audit_events_table | `FROM audit_events` |
| `app/repositories/audit_repository.py` | 356 | audit_append_call | `errors.append(f"[{eid}] event_hash mismatch")` |
| `app/repositories/audit_repository.py` | 358 | audit_append_call | `errors.append(f"[{eid}] HMAC mismatch")` |
| `app/repositories/audit_repository.py` | 360 | audit_append_call | `errors.append(` |
| `app/repositories/audit_repository.py` | 389 | audit_events_table | `SELECT event_hash FROM audit_events` |
| `app/repositories/diagnostic_session_repository.py` | 56 | audit_append_call | `items.append(response)` |
| `app/repositories/item_bank_repository.py` | 127 | audit_append_call | `heatmap.append(` |
| `app/repositories/repositories.py` | 13 | audit_log_identifier | `AuditLog,` |
| `app/repositories/repositories.py` | 313 | audit_repository | `class AuditRepository:` |
| `app/repositories/repositories.py` | 324 | audit_log_identifier | `) -> AuditLog:` |
| `app/repositories/repositories.py` | 325 | audit_log_identifier | `entry = AuditLog(` |
| `app/security/dependencies.py` | 34 | audit_append_call | `roles.append(Role(raw_role))` |
| `app/services/audit_service.py` | 21 | audit_append_call | `row = await self.repository.append(` |
| `app/services/consent_service.py` | 18 | audit_repository | `from app.repositories.audit_repository import AuditRepository` |
| `app/services/consent_service.py` | 26 | audit_repository | `audit_repo: AuditRepository,` |
| `app/services/consent_service.py` | 55 | audit_record_call | `await self._audit.record(` |
| `app/services/consent_service.py` | 91 | audit_record_call | `await self._audit.record(` |
| `app/services/consent_service.py` | 111 | audit_record_call | `await self._audit.record(` |
| `app/services/consent_service.py` | 132 | audit_record_call | `await self._audit.record(` |
| `app/services/consent_service.py` | 151 | audit_record_call | `await self._audit.record(` |
| `app/services/consent_service.py` | 191 | audit_record_call | `await self._audit.record(` |
| `app/services/consent_service.py` | 200 | audit_append_call | `flagged.append(saved)` |
| `app/services/content_safety/lesson_contracts.py` | 99 | audit_append_call | `reasons.append("topic missing")` |
| `app/services/content_safety/lesson_contracts.py` | 101 | audit_append_call | `reasons.append("CAPS alignment invalid")` |
| `app/services/content_safety/lesson_contracts.py` | 103 | audit_append_call | `reasons.append("unsafe content")` |
| `app/services/content_safety/lesson_contracts.py` | 113 | audit_append_call | `reasons.append("PII detected")` |
| `app/services/content_safety/lesson_contracts.py` | 115 | audit_append_call | `reasons.append("explanation missing")` |
| `app/services/content_safety/lesson_contracts.py` | 117 | audit_append_call | `reasons.append("answer key missing or inconsistent")` |
| `app/services/content_safety/lesson_contracts.py` | 119 | audit_append_call | `reasons.append("low alignment confidence")` |
| `app/services/content_safety/lesson_contracts.py` | 121 | audit_append_call | `reasons.append("low quality score")` |
| `app/services/curriculum/coverage.py` | 34 | audit_append_call | `gaps.append(` |
| `app/services/data_subject_rights_service.py` | 25 | audit_repository | `from app.repositories.audit_repository import AuditRepository` |
| `app/services/data_subject_rights_service.py` | 32 | audit_repository | `audit_repo: AuditRepository,` |
| `app/services/data_subject_rights_service.py` | 61 | audit_record_call | `await self._audit.record(` |
| `app/services/data_subject_rights_service.py` | 106 | audit_record_call | `await self._audit.record(` |
| `app/services/data_subject_rights_service.py` | 138 | audit_record_call | `await self._audit.record(` |
| `app/services/data_subject_rights_service.py` | 180 | audit_events_table | `Deletes learner PII but PRESERVES audit_events rows (anonymised).` |
| `app/services/data_subject_rights_service.py` | 200 | audit_events_table | `UPDATE audit_events` |
| `app/services/data_subject_rights_service.py` | 229 | audit_record_call | `await self._audit.record(` |
| `app/services/diagnostic_safety.py` | 30 | audit_append_call | `reasons.append(caps.reason)` |
| `app/services/diagnostic_safety.py` | 32 | audit_append_call | `reasons.append("difficulty must be finite and between -4 and 4")` |
| `app/services/diagnostic_safety.py` | 34 | audit_append_call | `reasons.append("discrimination must be finite and between 0 and 4")` |
| `app/services/diagnostic_safety.py` | 36 | audit_append_call | `reasons.append("distractors must be mutually distinct")` |
| `app/services/diagnostic_safety.py` | 38 | audit_append_call | `reasons.append("approved items require an explanation")` |
| `app/services/lesson_context_builder.py` | 217 | audit_append_call | `parts.append(f"({subtopic})")` |
| `app/services/lesson_context_builder.py` | 221 | audit_append_call | `parts.append(f"with emphasis on correcting: {tags_str}")` |
| `app/services/lesson_context_builder.py` | 231 | audit_append_call | `parts.append(severity_hints.get(severity, ""))` |
| `app/services/llm/gateway.py` | 147 | audit_append_call | `providers.append((self.development_fallback, "development_fallback"))` |
| `app/services/llm/gateway.py` | 154 | audit_append_call | `failures.append(f"{provider.provider_name}:{health.reason}")` |
| `app/services/llm/gateway.py` | 186 | audit_append_call | `failures.append(f"{provider.provider_name}:{exc}")` |
| `app/services/pii_sweep.py` | 105 | audit_append_call | `self.findings.append(finding)` |
| `app/services/pii_sweep.py` | 250 | audit_append_call | `all_findings.append({` |
| `app/services/popia_service.py` | 22 | audit_repository | `from app.repositories.audit_repository import AuditRepository` |
| `app/services/popia_service.py` | 55 | audit_repository | `self.audit = AuditRepository(db)` |
| `app/services/popia_service.py` | 84 | audit_append_call | `await self.audit.append(` |
| `app/services/popia_service.py` | 132 | audit_append_call | `await self.audit.append(` |
| `app/services/popia_service.py` | 156 | audit_append_call | `await self.audit.append(` |
| `app/services/popia_service.py` | 183 | audit_append_call | `await self.audit.append(` |
| `app/services/popia_service.py` | 202 | audit_append_call | `await self.audit.append(` |
| `scripts/archive/db_migration_phase2.sql` | 205 | audit_events_table | `CREATE TABLE IF NOT EXISTS audit_events (` |
| `scripts/archive/db_migration_phase2.sql` | 219 | audit_events_table | `CREATE INDEX IF NOT EXISTS ix_audit_events_learner ON audit_events(learner_id);` |
| `scripts/archive/db_migration_phase2.sql` | 220 | audit_events_table | `CREATE INDEX IF NOT EXISTS ix_audit_events_occurred ON audit_events(occurred_at);` |
| `scripts/archive/db_migration_phase2.sql` | 221 | audit_events_table | `CREATE INDEX IF NOT EXISTS ix_audit_events_type ON audit_events(event_type);` |
| `scripts/audit_router_thinness.py` | 126 | audit_append_call | `report.violations.append(` |
| `scripts/audit_router_thinness.py` | 137 | audit_append_call | `report.violations.append(` |
| `scripts/audit_router_thinness.py` | 151 | audit_append_call | `report.violations.append(` |
| `scripts/audit_router_thinness.py` | 173 | audit_append_call | `report.violations.append(` |
| `scripts/build_corrective_caps_v2.py` | 111 | audit_append_call | `records.append(` |
| `scripts/build_corrective_caps_v2.py` | 132 | audit_append_call | `records.append(` |
| `scripts/build_corrective_caps_v2.py` | 153 | audit_append_call | `records.append(` |
| `scripts/build_corrective_caps_v2.py` | 170 | audit_append_call | `records.append(` |
| `scripts/build_corrective_caps_v2.py` | 202 | audit_append_call | `unique.append(record)` |
| `scripts/build_focused_caps_dataset.py` | 115 | audit_append_call | `records.append(` |
| `scripts/build_focused_caps_dataset.py` | 152 | audit_append_call | `focused.append(` |
| `scripts/build_focused_caps_dataset.py` | 175 | audit_append_call | `deduped.append(record)` |
| `scripts/build_guardrails_dataset.py` | 66 | audit_append_call | `records.append(` |
| `scripts/build_release_evidence.py` | 52 | audit_append_call | `artifacts.append({"path": relative, "sha256": sha256(path), "bytes": path.stat().st_size})` |
| `scripts/capture_migration_evidence.py` | 101 | audit_append_call | `commands.append((name, [sys.executable, script]))` |
| `scripts/capture_migration_evidence.py` | 104 | audit_append_call | `commands.append(("alembic_downgrade_minus_one", ["alembic", "downgrade", "-1"]))` |
| `scripts/capture_migration_evidence.py` | 105 | audit_append_call | `commands.append(("alembic_upgrade_head_after_downgrade", ["alembic", "upgrade", "head"]))` |
| `scripts/capture_migration_evidence.py` | 163 | audit_append_call | `lines.append(` |
| `scripts/check_active_consent_route_order.py` | 57 | audit_append_call | `results.append(OrderResult(target, False, f"missing {CONSENT_MARKER}"))` |
| `scripts/check_active_consent_route_order.py` | 64 | audit_append_call | `results.append(OrderResult(target, True, "active consent present; no local object-auth marker in function"))` |
| `scripts/check_active_consent_route_order.py` | 68 | audit_append_call | `results.append(` |
| `scripts/check_active_consent_route_sources.py` | 52 | audit_append_call | `results.append(` |
| `scripts/check_active_consent_route_sources.py` | 60 | audit_append_call | `results.append(` |
| `scripts/check_ai_fixture_coverage_matrix.py` | 47 | audit_append_call | `results.append(` |
| `scripts/check_ai_fixture_coverage_matrix.py` | 54 | audit_append_call | `results.append(` |
| `scripts/check_ai_fixture_coverage_matrix.py` | 63 | audit_append_call | `results.append(` |
| `scripts/check_ai_llm_safety_caps_production_readiness.py` | 160 | audit_append_call | `results.append(CheckResult(path.exists(), f"required file exists: {rel_path}" if path.exists() else f"missing required file: {rel_path}"))` |
| `scripts/check_ai_llm_safety_caps_production_readiness.py` | 165 | audit_append_call | `results.append(CheckResult(snippet in text, f"{rel_path} contains {snippet!r}" if snippet in text else f"{rel_path} missing {snippet!r}"))` |
| `scripts/check_ai_output_schema_contract.py` | 42 | audit_append_call | `results.append(` |
| `scripts/check_ai_prompt_input_contract.py` | 38 | audit_append_call | `results.append(` |
| `scripts/check_ai_prompt_secret_leakage.py` | 68 | audit_append_call | `literals.append((getattr(node, "lineno", 0), node.value))` |
| `scripts/check_ai_prompt_secret_leakage.py` | 73 | audit_append_call | `text_parts.append(value.value)` |
| `scripts/check_ai_prompt_secret_leakage.py` | 75 | audit_append_call | `literals.append((getattr(node, "lineno", 0), "".join(text_parts)))` |
| `scripts/check_ai_prompt_secret_leakage.py` | 96 | audit_append_call | `results.append(` |
| `scripts/check_ai_prompt_secret_leakage.py` | 106 | audit_append_call | `results.append(` |
| `scripts/check_ai_prompt_surface_inventory.py` | 37 | audit_append_call | `results.append(` |
| `scripts/check_ai_refusal_fixtures.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_ai_refusal_fixtures.py` | 63 | audit_append_call | `results.append(` |
| `scripts/check_ai_refusal_fixtures.py` | 70 | audit_append_call | `results.append(` |
| `scripts/check_ai_refusal_fixtures.py` | 85 | audit_append_call | `results.append(RefusalFixtureResult(str(DOC.relative_to(REPO_ROOT)), DOC.exists(), "doc present" if DOC.exists() else "doc missing"))` |
| `scripts/check_ai_refusal_fixtures.py` | 87 | audit_append_call | `results.append(RefusalFixtureResult(str(DOC.relative_to(REPO_ROOT)), snippet in doc_text, f"contains {snippet!r}" if snippet in doc_text else f"missing {snippet!r}"))` |
| `scripts/check_ai_safety_boundary_contract.py` | 35 | audit_append_call | `results.append(` |
| `scripts/check_api_envelope_error_contract.py` | 91 | audit_append_call | `results.append(EvidenceResult(rel_path, path.exists(), "present" if path.exists() else "missing"))` |
| `scripts/check_api_envelope_error_contract.py` | 97 | audit_append_call | `results.append(` |
| `scripts/check_api_envelope_error_contract.py` | 107 | audit_append_call | `results.append(` |
| `scripts/check_archival_lock_assertion.py` | 51 | audit_append_call | `results.append(` |
| `scripts/check_audit_event_contracts.py` | 33 | audit_log_identifier | `"AuditLog emission is handled inside ConsentService",` |
| `scripts/check_audit_event_contracts.py` | 51 | audit_append_call | `results.append(CheckResult(rel_path, marker, marker in text))` |
| `scripts/check_audit_review_closeout_certificate.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_auth_boundary_evidence.py` | 58 | audit_append_call | `results.append(EvidenceResult(rel_path, path.exists(), "present" if path.exists() else "missing"))` |
| `scripts/check_auth_boundary_evidence.py` | 62 | audit_append_call | `results.append(EvidenceResult(rel_path, snippet in text, f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}"))` |
| `scripts/check_backend_consolidation_dragons.py` | 28 | audit_append_call | `paths.append(path)` |
| `scripts/check_backend_consolidation_dragons.py` | 44 | audit_append_call | `matched_paths.append(str(path.relative_to(REPO_ROOT)))` |
| `scripts/check_backend_consolidation_dragons.py` | 51 | audit_events_table | `"audit_events": _scan(r"\baudit_events\b"),` |
| `scripts/check_backend_consolidation_dragons.py` | 52 | audit_logs_table | `"audit_logs": _scan(r"\baudit_logs\b"),` |
| `scripts/check_backend_consolidation_execution_packet.py` | 54 | audit_append_call | `failures.append(f"missing {path}")` |
| `scripts/check_backend_consolidation_execution_packet.py` | 64 | audit_append_call | `failures.append(f"{path} missing {needle!r}")` |
| `scripts/check_backend_consolidation_execution_packet.py` | 68 | audit_append_call | `failures.append(f"{path} has premature phrase {phrase!r}")` |
| `scripts/check_backend_consolidation_noop_guard.py` | 39 | audit_append_call | `failures.append(f"missing {relative}")` |
| `scripts/check_backend_consolidation_noop_guard.py` | 46 | audit_append_call | `failures.append("pending decision marker missing")` |
| `scripts/check_backend_consolidation_noop_guard.py` | 54 | audit_append_call | `failures.append("retention default safeguards missing")` |
| `scripts/check_backend_consolidation_noop_guard.py` | 58 | audit_append_call | `failures.append(f"forbidden phrase {phrase!r}")` |
| `scripts/check_backend_consolidation_release_guard.py` | 40 | audit_append_call | `failures.append(f"missing {relative}")` |
| `scripts/check_backend_consolidation_release_guard.py` | 49 | audit_append_call | `failures.append("decision record status marker missing")` |
| `scripts/check_backend_consolidation_release_guard.py` | 54 | audit_append_call | `failures.append(f"forbidden phrase {phrase!r}")` |
| `scripts/check_backend_consolidation_terminal_packet.py` | 38 | audit_append_call | `failures.append(f"missing {relative}")` |
| `scripts/check_backend_consolidation_terminal_packet.py` | 48 | audit_append_call | `failures.append(f"packet missing {needle!r}")` |
| `scripts/check_backend_consolidation_terminal_packet.py` | 61 | audit_append_call | `failures.append("command failed: " + " ".join(command))` |
| `scripts/check_backend_runtime_compatibility.py` | 31 | audit_append_call | `failures.append("missing app.repositories.audit_compat")` |
| `scripts/check_backend_runtime_compatibility.py` | 38 | audit_append_call | `failures.append(f"missing audit compat {name}")` |
| `scripts/check_backend_runtime_compatibility.py` | 42 | audit_repository | `repo_cls = getattr(canonical, "AuditRepository", None)` |
| `scripts/check_backend_runtime_compatibility.py` | 44 | audit_repository | `print("- WARN [audit repository] AuditRepository class not found in canonical module")` |
| `scripts/check_backend_runtime_compatibility.py` | 51 | audit_repository | `failures.append("canonical AuditRepository lacks record/append/create")` |
| `scripts/check_backend_runtime_compatibility.py` | 51 | audit_append_call | `failures.append("canonical AuditRepository lacks record/append/create")` |
| `scripts/check_backend_runtime_compatibility.py` | 62 | audit_append_call | `failures.append("missing app.services.consent_compat")` |
| `scripts/check_backend_runtime_compatibility.py` | 69 | audit_append_call | `failures.append(f"missing consent compat {name}")` |
| `scripts/check_backend_runtime_compatibility.py` | 84 | audit_append_call | `failures.append("no consent service module imported")` |
| `scripts/check_backend_runtime_compatibility.py` | 96 | audit_append_call | `failures.append("missing health readiness contract")` |
| `scripts/check_backend_runtime_compatibility.py` | 104 | audit_append_call | `failures.append(f"health contract missing {needle!r}")` |
| `scripts/check_backend_runtime_probe_fixtures.py` | 36 | audit_append_call | `failures.append(f"{event['name']} action mismatch")` |
| `scripts/check_backend_runtime_probe_fixtures.py` | 38 | audit_append_call | `failures.append(f"{event['name']} resource_id mismatch")` |
| `scripts/check_backend_runtime_probe_fixtures.py` | 41 | audit_append_call | `failures.append(f"{event['name']} payload missing {key}")` |
| `scripts/check_backend_runtime_probe_fixtures.py` | 59 | audit_append_call | `failures.append(f"{event['name']} classification mismatch")` |
| `scripts/check_backend_runtime_probe_fixtures.py` | 61 | audit_append_call | `failures.append(f"{event['name']} resource_type mismatch")` |
| `scripts/check_backend_runtime_probe_fixtures.py` | 63 | audit_append_call | `failures.append(f"{event['name']} missing learner_id metadata")` |
| `scripts/check_backend_runtime_probe_fixtures.py` | 82 | audit_append_call | `failures.append("readiness fixture missing required checks: " + ", ".join(missing))` |
| `scripts/check_backend_runtime_probe_fixtures.py` | 86 | audit_append_call | `failures.append("audit_write_probe must be internal_only_disabled_by_default")` |
| `scripts/check_backend_runtime_probe_fixtures.py` | 88 | audit_append_call | `failures.append(f"{check.get('name')} has unsafe/unknown mode {check.get('mode')}")` |
| `scripts/check_backend_runtime_probe_fixtures.py` | 104 | audit_append_call | `failures.append(f"missing {path}")` |
| `scripts/check_backup_restore_disaster_recovery_production_readiness.py` | 145 | audit_append_call | `results.append(` |
| `scripts/check_backup_restore_disaster_recovery_production_readiness.py` | 156 | audit_append_call | `results.append(` |
| `scripts/check_backup_restore_disaster_recovery_production_readiness.py` | 180 | audit_append_call | `results.append(DisasterRecoveryReadinessResult("disaster_recovery_contracts", False, f"contract check failed: {exc}"))` |
| `scripts/check_beta_acceptance_exit_criteria.py` | 53 | audit_append_call | `results.append(` |
| `scripts/check_beta_evidence_consistency.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_beta_evidence_consistency.py` | 71 | audit_append_call | `results.append(` |
| `scripts/check_beta_evidence_consistency.py` | 83 | audit_append_call | `results.append(` |
| `scripts/check_beta_evidence_consistency.py` | 98 | audit_append_call | `results.append(` |
| `scripts/check_beta_evidence_consistency.py` | 113 | audit_append_call | `results.append(` |
| `scripts/check_beta_evidence_consistency.py` | 128 | audit_append_call | `results.append(` |
| `scripts/check_beta_feedback_intake_contract.py` | 53 | audit_append_call | `results.append(` |
| `scripts/check_beta_governance_seal.py` | 53 | audit_append_call | `results.append(BetaGovernanceSealResult(snippet in text, f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}"))` |
| `scripts/check_beta_known_issues_register.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_beta_launch_staging_acceptance_production_readiness.py` | 151 | audit_append_call | `results.append(` |
| `scripts/check_beta_launch_staging_acceptance_production_readiness.py` | 158 | audit_append_call | `results.append(` |
| `scripts/check_beta_launch_staging_acceptance_production_readiness.py` | 185 | audit_append_call | `results.append(BetaLaunchReadinessResult("beta_launch_contracts", False, f"contract check failed: {exc}"))` |
| `scripts/check_beta_monitoring_incident_trigger.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_beta_outcome_report_template.py` | 57 | audit_append_call | `results.append(` |
| `scripts/check_beta_participant_support_handoff.py` | 57 | audit_append_call | `results.append(` |
| `scripts/check_beta_pr_body.py` | 56 | audit_append_call | `results.append(` |
| `scripts/check_beta_pr_body.py` | 65 | audit_append_call | `results.append(` |
| `scripts/check_beta_release_closure_attestation.py` | 46 | audit_append_call | `results.append(` |
| `scripts/check_beta_release_communications_plan.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_beta_release_decision_log.py` | 50 | audit_append_call | `results.append(` |
| `scripts/check_beta_release_evidence_bundle.py` | 57 | audit_append_call | `results.append(` |
| `scripts/check_beta_release_evidence_bundle.py` | 66 | audit_append_call | `results.append(` |
| `scripts/check_beta_release_execution_plan.py` | 53 | audit_append_call | `results.append(` |
| `scripts/check_beta_release_final_checklist.py` | 51 | audit_append_call | `results.append(` |
| `scripts/check_beta_release_final_index.py` | 52 | audit_append_call | `results.append(BetaReleaseFinalIndexResult(snippet in text, f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}"))` |
| `scripts/check_beta_release_freeze_window.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_beta_release_readiness_contract.py` | 52 | audit_append_call | `results.append(` |
| `scripts/check_beta_retrospective_action_register.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_beta_rollback_runbook.py` | 47 | audit_append_call | `results.append(` |
| `scripts/check_beta_signoff_manifest.py` | 51 | audit_append_call | `results.append(` |
| `scripts/check_beta_signoff_manifest.py` | 60 | audit_append_call | `results.append(` |
| `scripts/check_billing_monetization_production_readiness.py` | 150 | audit_append_call | `results.append(` |
| `scripts/check_billing_monetization_production_readiness.py` | 161 | audit_append_call | `results.append(` |
| `scripts/check_billing_monetization_production_readiness.py` | 207 | audit_append_call | `results.append(BillingReadinessResult("billing_contracts", False, f"contract import/check failed: {exc}"))` |
| `scripts/check_branch_handoff_proof_record.py` | 54 | audit_append_call | `results.append(` |
| `scripts/check_branch_sync_rebase_checklist.py` | 43 | audit_append_call | `results.append(` |
| `scripts/check_caps_alignment_contract.py` | 36 | audit_append_call | `results.append(` |
| `scripts/check_caps_learning_proof.py` | 33 | audit_append_call | `results.append(Result("docs/caps/grade4_maths_coverage_matrix.md", snippet in matrix, f"contains {snippet!r}"))` |
| `scripts/check_ci_cd_deployment_production_readiness.py` | 147 | audit_append_call | `results.append(` |
| `scripts/check_ci_cd_deployment_production_readiness.py` | 158 | audit_append_call | `results.append(` |
| `scripts/check_ci_cd_deployment_production_readiness.py` | 183 | audit_append_call | `results.append(DeploymentReadinessResult("deployment_contracts", False, f"contract check failed: {exc}"))` |
| `scripts/check_ci_workflow_consolidation.py` | 45 | audit_append_call | `failures.append(f"missing file {path}")` |
| `scripts/check_ci_workflow_consolidation.py` | 54 | audit_append_call | `failures.append(f"{path} missing {needle!r}")` |
| `scripts/check_cluster_d_ci_evidence.py` | 117 | audit_append_call | `results.append(` |
| `scripts/check_cluster_d_ci_evidence.py` | 130 | audit_append_call | `results.append(` |
| `scripts/check_cluster_e_data_resilience_evidence.py` | 170 | audit_append_call | `results.append(ClusterEResult("file", rel_path, path.exists(), "present" if path.exists() else "missing"))` |
| `scripts/check_cluster_e_data_resilience_evidence.py` | 176 | audit_append_call | `results.append(` |
| `scripts/check_cluster_f_ai_safety_evidence.py` | 184 | audit_append_call | `results.append(ClusterFResult("file", rel_path, path.exists(), "present" if path.exists() else "missing"))` |
| `scripts/check_cluster_f_ai_safety_evidence.py` | 190 | audit_append_call | `results.append(` |
| `scripts/check_cluster_g_frontend_evidence.py` | 246 | audit_append_call | `results.append(ClusterGResult("file", rel_path, path.exists(), "present" if path.exists() else "missing"))` |
| `scripts/check_cluster_g_frontend_evidence.py` | 252 | audit_append_call | `results.append(` |
| `scripts/check_cluster_h_closure.py` | 60 | audit_append_call | `results.append(` |
| `scripts/check_cluster_h_closure.py` | 73 | audit_append_call | `results.append(` |
| `scripts/check_cluster_h_final_closeout_rollup.py` | 59 | audit_append_call | `results.append(` |
| `scripts/check_cluster_h_final_closeout_rollup.py` | 69 | audit_append_call | `results.append(` |
| `scripts/check_cluster_h_release_evidence_checksum_index.py` | 54 | audit_append_call | `results.append(` |
| `scripts/check_cluster_h_release_readiness.py` | 784 | audit_append_call | `results.append(` |
| `scripts/check_cluster_h_release_readiness.py` | 797 | audit_append_call | `results.append(` |
| `scripts/check_cluster_h_terminal_closure_assertion.py` | 48 | audit_append_call | `results.append(ClusterHTerminalClosureAssertionResult(snippet in text, f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}"))` |
| `scripts/check_consent_rejection_audit.py` | 41 | audit_append_call | `results.append(` |
| `scripts/check_database_backup_contract.py` | 44 | audit_append_call | `results.append(` |
| `scripts/check_database_backup_contract.py` | 52 | audit_append_call | `results.append(` |
| `scripts/check_database_backup_integrity.py` | 38 | audit_append_call | `results.append(` |
| `scripts/check_database_backup_integrity.py` | 46 | audit_append_call | `results.append(` |
| `scripts/check_database_persistence_production_readiness.py` | 107 | audit_repository | `"class AuditRepository",` |
| `scripts/check_database_persistence_production_readiness.py` | 127 | audit_append_call | `results.append(Result(rel_path, path.exists(), "present" if path.exists() else "missing"))` |
| `scripts/check_database_persistence_production_readiness.py` | 133 | audit_append_call | `results.append(Result(rel_path, snippet in text, f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}"))` |
| `scripts/check_database_persistence_production_readiness.py` | 138 | audit_append_call | `results.append(Result("app/repositories", keyword in repo_text, f"contains {keyword!r}" if keyword in repo_text else f"missing {keyword!r}"))` |
| `scripts/check_database_resilience_env_matrix.py` | 33 | audit_append_call | `results.append(` |
| `scripts/check_database_restore_integrity.py` | 41 | audit_append_call | `results.append(` |
| `scripts/check_database_restore_integrity.py` | 52 | audit_append_call | `results.append(` |
| `scripts/check_dev_only_endpoint_exposure.py` | 39 | audit_append_call | `results.append(` |
| `scripts/check_diagnostic_generation_safety_contract.py` | 40 | audit_append_call | `results.append(` |
| `scripts/check_diagnostics_assessment_production_readiness.py` | 113 | audit_append_call | `results.append(CheckResult(rel_path, path.exists(), "present" if path.exists() else "missing"))` |
| `scripts/check_diagnostics_assessment_production_readiness.py` | 117 | audit_append_call | `results.append(` |
| `scripts/check_documentation_adrs_claim_discipline_production_readiness.py` | 109 | audit_append_call | `results.append(DocumentationGovernanceReadinessResult(rel_path, path.exists(), "file present" if path.exists() else "file missing"))` |
| `scripts/check_documentation_adrs_claim_discipline_production_readiness.py` | 113 | audit_append_call | `results.append(DocumentationGovernanceReadinessResult(rel_path, snippet in text, f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}"))` |
| `scripts/check_documentation_adrs_claim_discipline_production_readiness.py` | 131 | audit_append_call | `results.append(DocumentationGovernanceReadinessResult("documentation_governance_contracts", False, f"contract check failed: {exc}"))` |
| `scripts/check_environment_security_contract.py` | 41 | audit_append_call | `results.append(` |
| `scripts/check_evidence_archive_completeness_guard.py` | 58 | audit_append_call | `results.append(EvidenceArchiveCompletenessGuardResult(snippet in text, f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}"))` |
| `scripts/check_evidence_freeze_confirmation_record.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_final_acceptance_memo.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_final_acceptance_packet_index.py` | 57 | audit_append_call | `results.append(` |
| `scripts/check_final_archive_accession_record.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_final_audit_handoff_register.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_final_beta_operator_packet.py` | 51 | audit_append_call | `results.append(` |
| `scripts/check_final_closure_manifest.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_final_evidence_noop_execution_assertion.py` | 51 | audit_append_call | `results.append(` |
| `scripts/check_final_merge_signoff_lock.py` | 53 | audit_append_call | `results.append(` |
| `scripts/check_final_pr_handoff_summary.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_final_pr_merge_readiness.py` | 48 | audit_append_call | `results.append(` |
| `scripts/check_final_project_closeout_attestation.py` | 53 | audit_append_call | `results.append(` |
| `scripts/check_final_release_blocker_checklist.py` | 141 | audit_append_call | `results.append(FinalReleaseBlockerResult(rel_path, path.exists(), "file present" if path.exists() else "file missing"))` |
| `scripts/check_final_release_blocker_checklist.py` | 146 | audit_append_call | `results.append(` |
| `scripts/check_final_release_blocker_checklist.py` | 172 | audit_append_call | `results.append(FinalReleaseBlockerResult("final_release_blocker_contracts", False, f"contract check failed: {exc}"))` |
| `scripts/check_final_release_evidence_ledger.py` | 59 | audit_append_call | `results.append(` |
| `scripts/check_final_release_evidence_toc.py` | 48 | audit_append_call | `results.append(` |
| `scripts/check_final_release_handoff_package.py` | 54 | audit_append_call | `results.append(FinalReleaseHandoffPackageResult(snippet in text, f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}"))` |
| `scripts/check_final_release_operator_brief.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_final_release_readiness_rollup.py` | 54 | audit_append_call | `results.append(` |
| `scripts/check_final_release_verification_bundle.py` | 52 | audit_append_call | `results.append(` |
| `scripts/check_final_release_verification_bundle.py` | 66 | audit_append_call | `results.append(` |
| `scripts/check_final_reviewer_disposition_record.py` | 56 | audit_append_call | `results.append(` |
| `scripts/check_final_reviewer_pack_checklist.py` | 52 | audit_append_call | `results.append(` |
| `scripts/check_final_sealed_package_manifest.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_frontend_accessibility_contract.py` | 44 | audit_append_call | `results.append(` |
| `scripts/check_frontend_accessibility_static.py` | 59 | audit_append_call | `results.append(` |
| `scripts/check_frontend_accessibility_static.py` | 68 | audit_append_call | `results.append(` |
| `scripts/check_frontend_accessibility_static.py` | 77 | audit_append_call | `results.append(` |
| `scripts/check_frontend_api_client_inventory.py` | 44 | audit_append_call | `results.append(` |
| `scripts/check_frontend_auth_consent_denial_contract.py` | 43 | audit_append_call | `results.append(` |
| `scripts/check_frontend_build_test_lint_contract.py` | 69 | audit_append_call | `results.append(` |
| `scripts/check_frontend_build_test_lint_contract.py` | 85 | audit_append_call | `results.append(` |
| `scripts/check_frontend_build_test_lint_contract.py` | 98 | audit_append_call | `results.append(` |
| `scripts/check_frontend_build_test_lint_contract.py` | 107 | audit_append_call | `results.append(` |
| `scripts/check_frontend_build_test_lint_contract.py` | 127 | audit_append_call | `results.append(` |
| `scripts/check_frontend_build_test_lint_contract.py` | 136 | audit_append_call | `results.append(` |
| `scripts/check_frontend_e2e_environment_contract.py` | 52 | audit_append_call | `results.append(` |
| `scripts/check_frontend_e2e_environment_contract.py` | 61 | audit_append_call | `results.append(` |
| `scripts/check_frontend_e2e_opt_in_workflow.py` | 94 | audit_append_call | `failures.append(f"MISSING – {description}\n  Pattern: {pattern!r}")` |
| `scripts/check_frontend_e2e_opt_in_workflow.py` | 98 | audit_append_call | `failures.append(f"FORBIDDEN – {description}\n  Pattern: {pattern!r}")` |
| `scripts/check_frontend_e2e_runtime_commands.py` | 50 | audit_append_call | `results.append(` |
| `scripts/check_frontend_e2e_runtime_commands.py` | 59 | audit_append_call | `results.append(` |
| `scripts/check_frontend_journey_fixtures.py` | 54 | audit_append_call | `results.append(` |
| `scripts/check_frontend_journey_fixtures.py` | 62 | audit_append_call | `results.append(` |
| `scripts/check_frontend_journey_fixtures.py` | 70 | audit_append_call | `results.append(` |
| `scripts/check_frontend_journey_fixtures.py` | 85 | audit_append_call | `results.append(` |
| `scripts/check_frontend_journey_fixtures.py` | 96 | audit_append_call | `results.append(` |
| `scripts/check_frontend_mock_api_fixtures.py` | 78 | audit_append_call | `results.append(` |
| `scripts/check_frontend_mock_api_fixtures.py` | 89 | audit_append_call | `results.append(` |
| `scripts/check_frontend_playwright_mock_helpers.py` | 51 | audit_append_call | `results.append(` |
| `scripts/check_frontend_playwright_mock_helpers.py` | 60 | audit_append_call | `results.append(` |
| `scripts/check_frontend_playwright_mocked_specs.py` | 52 | audit_append_call | `results.append(MockedSpecResult(rel_path, path.exists(), "present" if path.exists() else "missing"))` |
| `scripts/check_frontend_playwright_mocked_specs.py` | 58 | audit_append_call | `results.append(` |
| `scripts/check_frontend_playwright_scaffold.py` | 42 | audit_append_call | `results.append(` |
| `scripts/check_frontend_playwright_scaffold.py` | 45 | audit_append_call | `results.append(` |
| `scripts/check_frontend_playwright_scaffold.py` | 50 | audit_append_call | `results.append(` |
| `scripts/check_frontend_playwright_scaffold.py` | 59 | audit_append_call | `results.append(` |
| `scripts/check_frontend_playwright_specs.py` | 51 | audit_append_call | `results.append(` |
| `scripts/check_frontend_playwright_specs.py` | 59 | audit_append_call | `results.append(` |
| `scripts/check_frontend_production_readiness.py` | 201 | audit_append_call | `results.append(` |
| `scripts/check_frontend_production_readiness.py` | 216 | audit_append_call | `results.append(` |
| `scripts/check_frontend_production_readiness.py` | 227 | audit_append_call | `results.append(` |
| `scripts/check_frontend_route_inventory.py` | 41 | audit_append_call | `results.append(` |
| `scripts/check_frontend_runtime_inventory.py` | 44 | audit_append_call | `results.append(` |
| `scripts/check_frozen_scope_variance_register.py` | 50 | audit_append_call | `results.append(` |
| `scripts/check_generated_artifact_hygiene.py` | 57 | audit_append_call | `results.append(` |
| `scripts/check_generated_artifact_hygiene.py` | 66 | audit_append_call | `results.append(` |
| `scripts/check_health_readiness_contract.py` | 56 | audit_append_call | `failures.append(f"missing {path}")` |
| `scripts/check_health_readiness_contract.py` | 66 | audit_append_call | `failures.append(f"{path} missing {needle!r}")` |
| `scripts/check_health_readiness_contract.py` | 75 | audit_append_call | `failures.append(f"{path} unsafe write-like operation")` |
| `scripts/check_incident_response_operations_support_production_readiness.py` | 148 | audit_append_call | `results.append(` |
| `scripts/check_incident_response_operations_support_production_readiness.py` | 159 | audit_append_call | `results.append(` |
| `scripts/check_incident_response_operations_support_production_readiness.py` | 191 | audit_append_call | `results.append(OperationsSupportReadinessResult("operations_support_contracts", False, f"contract check failed: {exc}"))` |
| `scripts/check_learner_vertical_journey_contract.py` | 49 | audit_append_call | `results.append(` |
| `scripts/check_learner_vertical_journey_contract.py` | 54 | audit_append_call | `results.append(` |
| `scripts/check_learner_vertical_journey_contract.py` | 62 | audit_append_call | `results.append(` |
| `scripts/check_learner_vertical_journey_contract.py` | 71 | audit_append_call | `results.append(` |
| `scripts/check_learning_evidence.py` | 74 | audit_append_call | `results.append(EvidenceResult(rel_path, path.exists(), "present" if path.exists() else "missing"))` |
| `scripts/check_learning_evidence.py` | 80 | audit_append_call | `results.append(` |
| `scripts/check_lesson_generation_safety_contract.py` | 41 | audit_append_call | `results.append(` |
| `scripts/check_llm_provider_fallback_contract.py` | 47 | audit_append_call | `results.append(` |
| `scripts/check_llm_provider_fallback_contract.py` | 56 | audit_append_call | `results.append(` |
| `scripts/check_llm_provider_fallback_contract.py` | 65 | audit_append_call | `results.append(` |
| `scripts/check_merge_control_evidence_gate.py` | 53 | audit_append_call | `results.append(` |
| `scripts/check_notifications_communication_production_readiness.py` | 138 | audit_append_call | `results.append(` |
| `scripts/check_notifications_communication_production_readiness.py` | 149 | audit_append_call | `results.append(` |
| `scripts/check_notifications_communication_production_readiness.py` | 204 | audit_append_call | `results.append(NotificationsReadinessResult("notifications_contracts", False, f"contract check failed: {exc}"))` |
| `scripts/check_observability_production_readiness.py` | 158 | audit_append_call | `results.append(` |
| `scripts/check_observability_production_readiness.py` | 169 | audit_append_call | `results.append(` |
| `scripts/check_observability_production_readiness.py` | 199 | audit_append_call | `results.append(ObservabilityReadinessResult("observability_contracts", False, f"contract check failed: {exc}"))` |
| `scripts/check_parent_vertical_journey_contract.py` | 47 | audit_append_call | `results.append(` |
| `scripts/check_parent_vertical_journey_contract.py` | 52 | audit_append_call | `results.append(` |
| `scripts/check_parent_vertical_journey_contract.py` | 60 | audit_append_call | `results.append(` |
| `scripts/check_parent_vertical_journey_contract.py` | 69 | audit_append_call | `results.append(` |
| `scripts/check_persistence_resilience_evidence.py` | 69 | audit_append_call | `results.append(EvidenceResult(rel_path, path.exists(), "present" if path.exists() else "missing"))` |
| `scripts/check_persistence_resilience_evidence.py` | 75 | audit_append_call | `results.append(` |
| `scripts/check_phase2_authorization_closure.py` | 47 | audit_append_call | `failures.append(command)` |
| `scripts/check_phase2_authorization_evidence.py` | 320 | audit_append_call | `results.append(` |
| `scripts/check_phase2_authorization_evidence.py` | 336 | audit_append_call | `results.append(CheckResult("content", rel_path, False, "file missing"))` |
| `scripts/check_phase2_authorization_evidence.py` | 341 | audit_append_call | `results.append(` |
| `scripts/check_popia_consent_audit_evidence.py` | 209 | audit_append_call | `results.append(CheckResult("file", rel_path, path.exists(), "present" if path.exists() else "missing"))` |
| `scripts/check_popia_consent_audit_evidence.py` | 215 | audit_append_call | `results.append(` |
| `scripts/check_popia_consent_boundary_matrix.py` | 31 | audit_append_call | `results.append(CheckResult("active_consent_required_count", bool(active), f"{len(active)} active routes"))` |
| `scripts/check_popia_consent_boundary_matrix.py` | 32 | audit_append_call | `results.append(CheckResult("rights_exercise_count", bool(rights), f"{len(rights)} rights routes"))` |
| `scripts/check_popia_consent_boundary_matrix.py` | 33 | audit_append_call | `results.append(CheckResult("catalog_boundary_count", bool(catalog), f"{len(catalog)} catalog routes"))` |
| `scripts/check_popia_consent_boundary_matrix.py` | 36 | audit_append_call | `results.append(` |
| `scripts/check_popia_consent_boundary_matrix.py` | 45 | audit_append_call | `results.append(` |
| `scripts/check_popia_consent_boundary_matrix.py` | 64 | audit_append_call | `results.append(CheckResult(f"{key[0]}::{key[1]}", key in present, "expected active-consent route"))` |
| `scripts/check_popia_legal_evidence.py` | 34 | audit_append_call | `results.append(Result("docs/legal/legal_documents_index.md", snippet.lower() in text.lower(), f"contains {snippet!r}"))` |
| `scripts/check_post_beta_evidence_archive_manifest.py` | 59 | audit_append_call | `results.append(` |
| `scripts/check_post_closeout_custody_register.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_post_closeout_evidence_access_policy.py` | 50 | audit_append_call | `results.append(` |
| `scripts/check_post_closeout_maintenance_boundary.py` | 49 | audit_append_call | `results.append(` |
| `scripts/check_post_deploy_staging_smoke_checklist.py` | 51 | audit_append_call | `results.append(` |
| `scripts/check_post_merge_evidence_continuity_note.py` | 51 | audit_append_call | `results.append(` |
| `scripts/check_post_merge_release_handoff.py` | 52 | audit_append_call | `results.append(` |
| `scripts/check_post_terminal_audit_readiness.py` | 50 | audit_append_call | `results.append(PostTerminalAuditReadinessResult(snippet in text, f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}"))` |
| `scripts/check_pr002r_evidence.py` | 104 | audit_append_call | `results.append(` |
| `scripts/check_pr002r_evidence.py` | 122 | audit_append_call | `results.append(` |
| `scripts/check_pr002r_evidence.py` | 134 | audit_append_call | `results.append(` |
| `scripts/check_pr002r_evidence.py` | 155 | audit_append_call | `lines.append(f"- {status} [{result.kind}] {result.path}: {result.message}")` |
| `scripts/check_pr_closeout_evidence_checklist.py` | 47 | audit_append_call | `results.append(` |
| `scripts/check_pr_merge_evidence_summary.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_pr_ready_final_closure_certificate.py` | 53 | audit_append_call | `results.append(` |
| `scripts/check_privacy_boundary_evidence.py` | 66 | audit_append_call | `results.append(` |
| `scripts/check_privacy_boundary_evidence.py` | 74 | audit_append_call | `results.append(` |
| `scripts/check_production_restore_approval.py` | 43 | audit_append_call | `results.append(` |
| `scripts/check_production_restore_approval.py` | 52 | audit_append_call | `results.append(` |
| `scripts/check_production_restore_approval.py` | 61 | audit_append_call | `results.append(` |
| `scripts/check_production_secret_placeholders.py` | 41 | audit_append_call | `results.append(` |
| `scripts/check_production_secret_placeholders.py` | 50 | audit_append_call | `results.append(` |
| `scripts/check_project_release_closure_index.py` | 46 | audit_append_call | `results.append(` |
| `scripts/check_release_approval_workflow_contract.py` | 59 | audit_append_call | `results.append(` |
| `scripts/check_release_approval_workflow_contract.py` | 68 | audit_append_call | `results.append(` |
| `scripts/check_release_artifact_retention_contract.py` | 46 | audit_append_call | `results.append(` |
| `scripts/check_release_audit_trail_index.py` | 47 | audit_append_call | `results.append(` |
| `scripts/check_release_candidate_tag_manifest.py` | 52 | audit_append_call | `results.append(` |
| `scripts/check_release_candidate_tag_manifest.py` | 61 | audit_append_call | `results.append(` |
| `scripts/check_release_change_control_exception_log.py` | 49 | audit_append_call | `results.append(` |
| `scripts/check_release_evidence_artifacts.py` | 56 | audit_append_call | `results.append(` |
| `scripts/check_release_evidence_artifacts.py` | 68 | audit_append_call | `results.append(` |
| `scripts/check_release_evidence_artifacts.py` | 80 | audit_append_call | `results.append(` |
| `scripts/check_release_evidence_index.py` | 41 | audit_append_call | `failures.append(f"missing file {path}")` |
| `scripts/check_release_evidence_index.py` | 50 | audit_append_call | `failures.append(f"{path} missing {needle!r}")` |
| `scripts/check_release_evidence_retention_finalization.py` | 53 | audit_append_call | `results.append(` |
| `scripts/check_release_handoff_freeze_assertion.py` | 50 | audit_append_call | `results.append(` |
| `scripts/check_release_owner_accountability.py` | 52 | audit_append_call | `results.append(` |
| `scripts/check_release_owner_execution_guardrail.py` | 50 | audit_append_call | `results.append(` |
| `scripts/check_release_owner_post_closeout_decision_record.py` | 54 | audit_append_call | `results.append(` |
| `scripts/check_release_record_closure_ledger.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_release_state_snapshot.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_release_state_snapshot.py` | 64 | audit_append_call | `results.append(` |
| `scripts/check_remediation_safety_contract.py` | 41 | audit_append_call | `results.append(` |
| `scripts/check_reviewer_decision_capture_template.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_roadmap_after_production_readiness_baseline.py` | 156 | audit_append_call | `results.append(RoadmapReadinessResult(rel_path, path.exists(), "file present" if path.exists() else "file missing"))` |
| `scripts/check_roadmap_after_production_readiness_baseline.py` | 161 | audit_append_call | `results.append(` |
| `scripts/check_roadmap_after_production_readiness_baseline.py` | 187 | audit_append_call | `results.append(RoadmapReadinessResult("roadmap_contracts", False, f"contract check failed: {exc}"))` |
| `scripts/check_route_alias_matrix.py` | 73 | audit_append_call | `lines.append(f"{row.method.upper()} {row.canonical_path} -- baseline exception; review before release")` |
| `scripts/check_runtime_entrypoints.py` | 124 | audit_append_call | `results.append(check_entrypoint(spec, canonical=index == 0))` |
| `scripts/check_runtime_entrypoints.py` | 154 | audit_append_call | `lines.append(f"- {status} {result.spec}")` |
| `scripts/check_runtime_entrypoints.py` | 157 | audit_append_call | `lines.append(f"  title: {result.title}")` |
| `scripts/check_runtime_entrypoints.py` | 159 | audit_append_call | `lines.append(f"  version: {result.version}")` |
| `scripts/check_runtime_entrypoints.py` | 161 | audit_append_call | `lines.append(f"  route_count: {result.route_count}")` |
| `scripts/check_runtime_entrypoints.py` | 163 | audit_append_call | `lines.append(f"  missing_routes: {', '.join(result.missing_routes)}")` |
| `scripts/check_runtime_entrypoints.py` | 165 | audit_append_call | `lines.append(f"  missing_prefixes: {', '.join(result.missing_prefixes)}")` |
| `scripts/check_runtime_entrypoints.py` | 167 | audit_append_call | `lines.append(f"  error: {result.error}")` |
| `scripts/check_runtime_release_evidence.py` | 73 | audit_append_call | `failures.append(f"missing file {path}")` |
| `scripts/check_runtime_release_evidence.py` | 83 | audit_append_call | `failures.append(f"{path} missing {needle!r}")` |
| `scripts/check_runtime_release_evidence.py` | 95 | audit_append_call | `failures.append(f"{path} pending status removed")` |
| `scripts/check_schema_drift_contract.py` | 27 | audit_append_call | `failures.append(f"missing {path}")` |
| `scripts/check_schema_drift_contract.py` | 41 | audit_append_call | `failures.append("compare_orm_tables_to_database.py failed without DB")` |
| `scripts/check_sealed_evidence_access_handoff.py` | 54 | audit_append_call | `results.append(` |
| `scripts/check_sealed_reviewer_closeout_packet.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_security_posture_threat_modeling_production_readiness.py` | 172 | audit_append_call | `results.append(` |
| `scripts/check_security_posture_threat_modeling_production_readiness.py` | 183 | audit_append_call | `results.append(` |
| `scripts/check_security_posture_threat_modeling_production_readiness.py` | 211 | audit_append_call | `results.append(SecurityPostureReadinessResult("security_posture_contracts", False, f"contract check failed: {exc}"))` |
| `scripts/check_staging_release_gate.py` | 45 | audit_append_call | `results.append(StagingGateResult("file", str(DOC.relative_to(REPO_ROOT)), DOC.exists(), "present" if DOC.exists() else "missing"))` |
| `scripts/check_staging_release_gate.py` | 48 | audit_append_call | `results.append(` |
| `scripts/check_staging_release_gate.py` | 59 | audit_append_call | `results.append(` |
| `scripts/check_staging_smoke_evidence_manifest.py` | 49 | audit_append_call | `results.append(` |
| `scripts/check_staging_smoke_evidence_manifest.py` | 58 | audit_append_call | `results.append(` |
| `scripts/check_terminal_evidence_retrieval_guide.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_terminal_evidence_seal.py` | 61 | audit_append_call | `results.append(` |
| `scripts/check_terminal_handoff_closure_note.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_terminal_pr_evidence_index.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_terminal_review_index.py` | 54 | audit_append_call | `results.append(` |
| `scripts/check_test_environment.py` | 105 | audit_append_call | `failures.append(result.name)` |
| `scripts/check_testing_release_quality_gates_production_readiness.py` | 141 | audit_append_call | `results.append(` |
| `scripts/check_testing_release_quality_gates_production_readiness.py` | 152 | audit_append_call | `results.append(` |
| `scripts/check_testing_release_quality_gates_production_readiness.py` | 177 | audit_append_call | `results.append(QualityGateReadinessResult("quality_gate_contracts", False, f"contract check failed: {exc}"))` |
| `scripts/check_warning_cleanup.py` | 36 | audit_append_call | `failures.append("pytest.ini norecursedirs missing: " + ", ".join(sorted(missing)))` |
| `scripts/check_warning_cleanup.py` | 45 | audit_append_call | `failures.append(f"{repo_test} _mock_session block {idx} lacks synchronous add MagicMock")` |
| `scripts/check_warning_cleanup.py` | 49 | audit_append_call | `failures.append(f"missing {repo_test}")` |
| `scripts/check_warning_cleanup.py` | 55 | audit_append_call | `failures.append(f"{register} missing or incomplete")` |
| `scripts/ci/ci_lesson_bank_check.py` | 169 | audit_append_call | `results.append(result)` |
| `scripts/ci/ci_lesson_bank_check.py` | 218 | audit_append_call | `violations.append(violation)` |
| `scripts/deduplicate_makefile_targets.py` | 64 | audit_append_call | `occurrences[m.group(1)].append(i)` |
| `scripts/deduplicate_makefile_targets.py` | 89 | audit_append_call | `block.append(i)` |
| `scripts/deduplicate_makefile_targets.py` | 149 | audit_append_call | `new_lines.append(phony_line)` |
| `scripts/deduplicate_makefile_targets.py` | 152 | audit_append_call | `new_lines.append(line)` |
| `scripts/evaluate_pedagogy.py` | 88 | audit_append_call | `cases.append(BenchmarkCase(**record))` |
| `scripts/evaluate_pedagogy.py` | 171 | audit_append_call | `case_results.append(result)` |
| `scripts/generate_ai_prompt_surface_inventory.py` | 49 | audit_append_call | `surfaces.append(PromptSurface(str(path.relative_to(REPO_ROOT)), markers))` |
| `scripts/generate_ai_prompt_surface_inventory.py` | 76 | audit_append_call | `lines.append("\| _none found_ \| _none_ \|")` |
| `scripts/generate_ai_prompt_surface_inventory.py` | 79 | audit_append_call | `lines.append(f"\| `{surface.path}` \| `{', '.join(surface.markers)}` \|")` |
| `scripts/generate_audit_callsite_inventory.py` | 42 | audit_append_call | `files.append(path)` |
| `scripts/generate_audit_callsite_inventory.py` | 57 | audit_append_call | `rows.append(` |
| `scripts/generate_audit_callsite_inventory.py` | 79 | audit_append_call | `output.append(f"\| `{row.path}` \| {row.line} \| {row.category} \| `{text}` \|")` |
| `scripts/generate_audit_callsite_inventory.py` | 89 | audit_logs_table | `"- [ ] Identify any `audit_logs` data-retention requirement.",` |
| `scripts/generate_backend_consolidation_evidence_manifest.py` | 62 | audit_append_call | `rows.append(ManifestRow(relative, True, path.stat().st_size, _sha256(path)))` |
| `scripts/generate_backend_consolidation_evidence_manifest.py` | 64 | audit_append_call | `rows.append(ManifestRow(relative, False, 0, ""))` |
| `scripts/generate_backend_consolidation_evidence_manifest.py` | 80 | audit_append_call | `lines.append(` |
| `scripts/generate_backend_consolidation_execution_report.py` | 48 | audit_append_call | `rows.append((name, code, " ".join(command), output))` |
| `scripts/generate_backend_consolidation_execution_report.py` | 60 | audit_append_call | `lines.append(f"\| {name} \| {code} \| `{command}` \|")` |
| `scripts/generate_backend_consolidation_readiness_report.py` | 42 | audit_append_call | `rows.append((name, code, " ".join(command), output))` |
| `scripts/generate_backend_consolidation_readiness_report.py` | 52 | audit_append_call | `lines.append(f"\| {name} \| {code} \| `{command}` \|")` |
| `scripts/generate_backend_consolidation_report.py` | 47 | audit_append_call | `rows.append((name, code, " ".join(command), output))` |
| `scripts/generate_backend_consolidation_report.py` | 59 | audit_append_call | `lines.append(f"\| {name} \| {code} \| `{command}` \|")` |
| `scripts/generate_backend_consolidation_terminal_report.py` | 49 | audit_append_call | `rows.append((name, code, " ".join(command), output))` |
| `scripts/generate_backend_consolidation_terminal_report.py` | 60 | audit_append_call | `lines.append(f"\| {name} \| {code} \| `{command}` \|")` |
| `scripts/generate_backend_deletion_candidate_inventory.py` | 13 | audit_logs_table | `("legacy_audit", re.compile(r"audit_logs\|AuditLog\|legacy audit", re.IGNORECASE)),` |
| `scripts/generate_backend_deletion_candidate_inventory.py` | 13 | audit_log_identifier | `("legacy_audit", re.compile(r"audit_logs\|AuditLog\|legacy audit", re.IGNORECASE)),` |
| `scripts/generate_backend_deletion_candidate_inventory.py` | 15 | audit_repository | `("duplicate_repository", re.compile(r"class\s+\w*Repository\|AuditRepository\|ConsentRepository")),` |
| `scripts/generate_backend_deletion_candidate_inventory.py` | 34 | audit_append_call | `files.append(path)` |
| `scripts/generate_backend_deletion_candidate_inventory.py` | 47 | audit_append_call | `candidates.append(Candidate(str(path.relative_to(REPO_ROOT)), line_number, category, line.strip()[:220]))` |
| `scripts/generate_backend_deletion_candidate_inventory.py` | 61 | audit_append_call | `lines.append(f"\| `{candidate.path}` \| {candidate.line} \| {candidate.category} \| `{text}` \| TODO \| no \|")` |
| `scripts/generate_backend_runtime_compatibility_report.py` | 48 | audit_append_call | `rows.append((name, code, " ".join(command), output))` |
| `scripts/generate_backend_runtime_compatibility_report.py` | 60 | audit_append_call | `lines.append(f"\| {name} \| {code} \| `{command}` \|")` |
| `scripts/generate_backend_runtime_probe_report.py` | 48 | audit_append_call | `rows.append((name, code, " ".join(command), output))` |
| `scripts/generate_backend_runtime_probe_report.py` | 59 | audit_append_call | `lines.append(f"\| {name} \| {code} \| `{command}` \|")` |
| `scripts/generate_beta_release_evidence_bundle.py` | 71 | audit_append_call | `lines.append(f"\| {artifact.category} \| `{artifact.path}` \| `{present}` \|")` |
| `scripts/generate_beta_signoff_manifest.py` | 69 | audit_append_call | `lines.append(f"\| {area.name} \| {area.evidence} \| _pending_ \| _pending_ \|")` |
| `scripts/generate_beta_signoff_manifest.py` | 79 | audit_append_call | `lines.append(f"- `{rel_path}`")` |
| `scripts/generate_consent_callsite_inventory.py` | 44 | audit_append_call | `files.append(path)` |
| `scripts/generate_consent_callsite_inventory.py` | 59 | audit_append_call | `rows.append(` |
| `scripts/generate_consent_callsite_inventory.py` | 81 | audit_append_call | `output.append(f"\| `{row.path}` \| {row.line} \| {row.category} \| `{text}` \|")` |
| `scripts/generate_consent_gate_inventory.py` | 63 | audit_append_call | `rows.append(` |
| `scripts/generate_consent_gate_inventory.py` | 73 | audit_append_call | `rows.append(` |
| `scripts/generate_consent_gate_inventory.py` | 97 | audit_append_call | `lines.append(` |
| `scripts/generate_dep_graph.py` | 61 | audit_append_call | `imports.append(alias.name)` |
| `scripts/generate_dep_graph.py` | 64 | audit_append_call | `imports.append(node.module)` |
| `scripts/generate_dep_graph.py` | 70 | audit_append_call | `imports.append(resolved)` |
| `scripts/generate_dep_graph.py` | 99 | audit_append_call | `lines.append(f'    {src_id}["{src_label}"] --> {tgt_id}["{tgt_label}"]')` |
| `scripts/generate_dep_graph.py` | 111 | audit_append_call | `lines.append(f'    "{source}" -> "{target}";')` |
| `scripts/generate_dep_graph.py` | 112 | audit_append_call | `lines.append("}")` |
| `scripts/generate_frontend_api_client_inventory.py` | 73 | audit_append_call | `surfaces.append(` |
| `scripts/generate_frontend_api_client_inventory.py` | 110 | audit_append_call | `lines.append("\| _none found_ \| _none_ \| _none_ \|")` |
| `scripts/generate_frontend_api_client_inventory.py` | 115 | audit_append_call | `lines.append(f"\| `{surface.path}` \| `{api_text}` \| `{domain_text}` \|")` |
| `scripts/generate_frontend_route_inventory.py` | 73 | audit_append_call | `surfaces.append(` |
| `scripts/generate_frontend_route_inventory.py` | 108 | audit_append_call | `lines.append("\| _none found_ \| _none_ \| _none_ \|")` |
| `scripts/generate_frontend_route_inventory.py` | 113 | audit_append_call | `lines.append(f"\| `{surface.path}` \| `{route_text}` \| `{journey_text}` \|")` |
| `scripts/generate_frontend_runtime_inventory.py` | 65 | audit_append_call | `packages.append(package)` |
| `scripts/generate_frontend_runtime_inventory.py` | 98 | audit_append_call | `lines.append(f"- {area}")` |
| `scripts/generate_frontend_runtime_inventory.py` | 128 | audit_append_call | `lines.append("\| _none_ \| _none_ \|")` |
| `scripts/generate_frontend_runtime_inventory.py` | 132 | audit_append_call | `lines.append(f"\| `{name}` \| `{safe_command}` \|")` |
| `scripts/generate_frontend_runtime_inventory.py` | 133 | audit_append_call | `lines.append("")` |
| `scripts/generate_grade4_item_batch.py` | 168 | audit_append_call | `batch.append(` |
| `scripts/generate_grade4_item_batch.py` | 252 | audit_append_call | `batch.append(` |
| `scripts/generate_grade4_item_batch.py` | 335 | audit_append_call | `batch.append(` |
| `scripts/generate_items.py` | 234 | audit_append_call | `seed["items"].append(item)` |
| `scripts/generate_learner_authz_matrix.py` | 126 | audit_append_call | `rows.append(` |
| `scripts/generate_learner_authz_matrix.py` | 160 | audit_append_call | `lines.append(` |
| `scripts/generate_learner_authz_matrix.py` | 168 | audit_append_call | `lines.append(f"- `{row.router}` `{row.method} {row.path}` via `{row.function}`")` |
| `scripts/generate_phase2_authorization_closure_report.py` | 71 | audit_append_call | `lines.append(f"- `{rel_path}` — {status}")` |
| `scripts/generate_phase2_authorization_closure_report.py` | 100 | audit_append_call | `lines.append(f"- `{rel_path}` — {status}")` |
| `scripts/generate_phase2_authorization_closure_report.py` | 114 | audit_append_call | `lines.append("Status: **not closed** — missing learner authorization markers remain.")` |
| `scripts/generate_phase2_authorization_closure_report.py` | 115 | audit_append_call | `lines.append("")` |
| `scripts/generate_phase2_authorization_closure_report.py` | 117 | audit_append_call | `lines.append(f"- `{row.router}` `{row.method} {row.path}` via `{row.function}`")` |
| `scripts/generate_phase2_authorization_closure_report.py` | 119 | audit_append_call | `lines.append("Status: **closure-ready** — no unallowlisted learner-scoped route is missing an authorization marker.")` |
| `scripts/generate_phase2_authorization_closure_report.py` | 131 | audit_append_call | `lines.append("")` |
| `scripts/generate_popia_consent_boundary_matrix.py` | 79 | audit_append_call | `routes.append((func.attr.upper(), route))` |
| `scripts/generate_popia_consent_boundary_matrix.py` | 120 | audit_append_call | `rows.append(BoundaryRow(path.name, node.name, route, method, decision, marker))` |
| `scripts/generate_popia_consent_boundary_matrix.py` | 125 | audit_append_call | `rows.append(BoundaryRow(router, function, "source-evidence", "SOURCE", decision, marker))` |
| `scripts/generate_popia_consent_boundary_matrix.py` | 142 | audit_append_call | `lines.append(f"- `{decision}`: {counts[decision]}")` |
| `scripts/generate_popia_consent_boundary_matrix.py` | 151 | audit_append_call | `lines.append(f"\| `{row.router}` \| `{row.method}` \| `{row.route}` \| `{row.function}` \| `{row.decision}` \| `{row.marker}` \|")` |
| `scripts/generate_release_evidence_manifest.py` | 69 | audit_append_call | `lines.append(f"\| {item.name} \| `{item.command}` \| pending \|")` |
| `scripts/generate_release_state_snapshot.py` | 69 | audit_append_call | `lines.append(f"\| `{rel_path}` \| `{present}` \|")` |
| `scripts/generate_route_alias_matrix.py` | 47 | audit_append_call | `rows.append(` |
| `scripts/generate_route_alias_matrix.py` | 72 | audit_append_call | `rendered.append(f"\| {row.method} \| `{row.canonical_path}` \| `{row.alias_path}` \| {status} \| {row.note} \|")` |
| `scripts/generate_route_alias_matrix.py` | 74 | audit_append_call | `rendered.append("")` |
| `scripts/generate_route_inventory.py` | 94 | audit_append_call | `rows.append((path, methods, name, include_in_schema, endpoint))` |
| `scripts/generate_route_inventory.py` | 99 | audit_append_call | `rows.append((path, methods, name, "no", endpoint))` |
| `scripts/generate_route_inventory.py` | 125 | audit_append_call | `missing.append(expected_prefix)` |
| `scripts/generate_route_inventory.py` | 164 | audit_append_call | `lines.append(f"\| `{route}` \| {status} \|")` |
| `scripts/generate_route_inventory.py` | 182 | audit_append_call | `lines.append(f"\| `{prefix}` \| `{fragment}` \| {status} \|")` |
| `scripts/generate_route_inventory.py` | 195 | audit_append_call | `lines.append(f"- `{prefix}`")` |
| `scripts/generate_route_inventory.py` | 212 | audit_append_call | `lines.append(` |
| `scripts/generate_route_inventory.py` | 216 | audit_append_call | `lines.append("")` |
| `scripts/generate_staging_smoke_evidence_manifest.py` | 63 | audit_append_call | `lines.append(f"\| {entry.name} \| `{entry.command}` \|")` |
| `scripts/inspect_learner_routes.py` | 106 | audit_append_call | `candidates.append(` |
| `scripts/inspect_learner_routes.py` | 128 | audit_append_call | `references.append(` |
| `scripts/inspect_learner_routes.py` | 156 | audit_append_call | `lines.append(` |
| `scripts/inspect_learner_routes.py` | 161 | audit_append_call | `lines.append("\| — \| — \| — \| — \| — \| no route candidates found \|")` |
| `scripts/inspect_learner_routes.py` | 175 | audit_append_call | `lines.append(f"\| `{reference.file}` \| {reference.line} \| `{safe_text}` \|")` |
| `scripts/inspect_learner_routes.py` | 178 | audit_append_call | `lines.append(f"\| — \| — \| `{len(references) - 200} additional references omitted` \|")` |
| `scripts/integrate_patch.py` | 59 | audit_append_call | `staged_conflicts.append(target)` |
| `scripts/integrate_patch.py` | 64 | audit_append_call | `moved.append(dest_file)` |
| `scripts/inventory_services.py` | 92 | audit_append_call | `found_duplicates.append((dup_path, canonical_rel))` |
| `scripts/lessons/generate_lessons.py` | 150 | audit_append_call | `result.errors.append(msg)` |
| `scripts/lessons/generate_lessons.py` | 157 | audit_append_call | `result.errors.append(msg)` |
| `scripts/lessons/generate_lessons.py` | 164 | audit_append_call | `result.errors.append(msg)` |
| `scripts/lessons/generate_lessons.py` | 227 | audit_append_call | `results.append(result)` |
| `scripts/lessons/validate_lessons.py` | 185 | audit_append_call | `failed_lessons.append((lesson_id, caps_ref, result))` |
| `scripts/maintenance/audit_todo_backlog.py` | 17 | audit_append_call | `paths.append(str(rel))` |
| `scripts/maintenance/audit_todo_backlog.py` | 34 | audit_append_call | `hits.append(rel)` |
| `scripts/maintenance/audit_todo_backlog.py` | 52 | audit_append_call | `tasks.append({'id':f'TODO-{idx:03d}','line':lineno,'section':section,'subsection':subsection,'todo_checked':'x' if m.group(1)=='x' else '', 'priority':m.group(2),'task':m.group(3).strip()})` |
| `scripts/maintenance/audit_todo_backlog.py` | 70 | audit_append_call | `RULES.append((marker.lower(),paths,status,note))` |
| `scripts/maintenance/audit_todo_backlog.py` | 333 | audit_append_call | `rows.append({**t,'repo_status':st,'owner':owner,'evidence_paths':'; '.join(ev),'audit_note':note,'pr_bucket':pr_bucket(t,st),'rank_score':rank(t,st)})` |
| `scripts/maintenance/audit_todo_backlog.py` | 340 | audit_append_call | `for st in ['Done','Partial','Missing','Blocked','Human-decision']: md.append(f'\| {st} \| {counts[st]} \|')` |
| `scripts/maintenance/audit_todo_backlog.py` | 344 | audit_append_call | `md.append(f"\| {p} \| {sum(r['repo_status']=='Done' for r in sub)} \| {sum(r['repo_status']=='Partial' for r in sub)} \| {sum(r['repo_status']=='Missing' for r in sub)} \| {sum(r['repo_status']=='Blocked' for r in sub)} \| {su` |
| `scripts/maintenance/audit_todo_backlog.py` | 347 | audit_append_call | `md.append(f"\| {i} \| {r['id']} \| {r['priority']} \| {r['repo_status']} \| {r['owner']} \| {r['task'].replace('\|','\\\|')} \| {(r['evidence_paths'] or '—').replace('\|','\\\|')} \|")` |
| `scripts/maintenance/audit_todo_backlog.py` | 348 | audit_append_call | `md.append('\n## PR-sized backlog buckets\n')` |
| `scripts/maintenance/audit_todo_backlog.py` | 350 | audit_append_call | `for r in sorted(rows,key=lambda r:(-r['rank_score'],r['id'])): by_pr[r['pr_bucket']].append(r)` |
| `scripts/maintenance/audit_todo_backlog.py` | 355 | audit_append_call | `md.append(f'\n### {bucket}\n')` |
| `scripts/maintenance/audit_todo_backlog.py` | 356 | audit_append_call | `md.append(f"Open items: {len(open_items)} — Partial {c['Partial']}, Missing {c['Missing']}, Blocked {c['Blocked']}, Human-decision {c['Human-decision']}.\n")` |
| `scripts/maintenance/audit_todo_backlog.py` | 357 | audit_append_call | `md.append('\| ID \| Priority \| Status \| Task \| Evidence \|\n\|---\|---\|---\|---\|---\|')` |
| `scripts/maintenance/audit_todo_backlog.py` | 358 | audit_append_call | `for r in open_items[:18]: md.append(f"\| {r['id']} \| {r['priority']} \| {r['repo_status']} \| {r['task'].replace('\|','\\\|')} \| {(r['evidence_paths'] or '—').replace('\|','\\\|')} \|")` |
| `scripts/maintenance/audit_todo_backlog.py` | 359 | audit_append_call | `if len(open_items)>18: md.append(f'\n_Additional items in CSV: {len(open_items)-18}._\n')` |
| `scripts/maintenance/audit_todo_backlog.py` | 365 | audit_append_call | `cp.append(f'{i}. **{b}** — {len(oi)} open, {crit} critical.')` |
| `scripts/maintenance/audit_todo_backlog.py` | 368 | audit_append_call | `cp.append(f"\| {r['id']} \| {r['priority']} \| {r['repo_status']} \| {r['task'].replace('\|','\\\|')} \|")` |
| `scripts/maintenance/audit_todo_backlog.py` | 373 | audit_append_call | `for r in first: fb.append(f"\| {r['id']} \| {r['priority']} \| {r['repo_status']} \| {r['task'].replace('\|','\\\|')} \| {(r['evidence_paths'] or '—').replace('\|','\\\|')} \|")` |
| `scripts/popia_sweep.py` | 113 | audit_append_call | `self.issues.append(issue)` |
| `scripts/popia_sweep.py` | 133 | audit_append_call | `files.append(path)` |
| `scripts/popia_sweep.py` | 230 | audit_append_call | `decorator_names.append(decorator.attr)` |
| `scripts/popia_sweep.py` | 232 | audit_append_call | `decorator_names.append(decorator.id)` |
| `scripts/popia_sweep.py` | 300 | audit_log_identifier | `kw in func_source for kw in ["audit_log", "fourth_estate", "AuditLog", "log_action"]` |
| `scripts/popia_sweep.py` | 377 | audit_append_call | `by_severity.setdefault(issue.severity, []).append(issue)` |
| `scripts/populate_md_with_pdfs.py` | 42 | audit_append_call | `matched_pdfs.append(pdf)` |
| `scripts/prepare_training_data.py` | 59 | audit_append_call | `pairs.append({` |
| `scripts/prepare_training_data.py` | 65 | audit_append_call | `pairs.append({` |
| `scripts/prepare_training_data.py` | 71 | audit_append_call | `pairs.append({` |
| `scripts/prepare_training_data.py` | 77 | audit_append_call | `pairs.append({` |
| `scripts/prepare_training_data.py` | 83 | audit_append_call | `pairs.append({` |
| `scripts/prepare_training_data.py` | 105 | audit_append_call | `pairs.append({` |
| `scripts/prepare_training_data.py` | 117 | audit_append_call | `pairs.append({` |
| `scripts/prepare_training_data.py` | 125 | audit_append_call | `pairs.append({` |
| `scripts/refresh_current_state_doc.py` | 341 | audit_append_call | `results.append(r)` |
| `scripts/rename_metaphor_layers.py` | 85 | audit_append_call | `hits.append((path, lineno, match.group(0).lower(), line.rstrip()))` |
| `scripts/run_database_backup.py` | 37 | audit_append_call | `results.append(` |
| `scripts/run_database_backup.py` | 60 | audit_append_call | `lines.append(f"- `{name}`")` |
| `scripts/run_database_restore.py` | 36 | audit_append_call | `results.append(` |
| `scripts/run_database_restore.py` | 86 | audit_append_call | `results.append(validate_target_environment(args.target_environment, args.allow_production_target))` |
| `scripts/run_staging_smoke.py` | 187 | audit_append_call | `rows.append(` |
| `scripts/scrape_caps.py` | 168 | audit_append_call | `docs.append(doc)` |
| `scripts/scrape_caps.py` | 205 | audit_append_call | `self._anchor_text.append(data)` |
| `scripts/scrape_caps.py` | 207 | audit_append_call | `self._cell_text.append(data)` |
| `scripts/scrape_caps.py` | 209 | audit_append_call | `self._heading_text.append(data)` |
| `scripts/scrape_caps.py` | 215 | audit_append_call | `self.links.append((self._href, " ".join(self._anchor_text).strip(), context_title))` |
| `scripts/scrape_caps.py` | 225 | audit_append_call | `self._row_cells.append(cell)` |
| `scripts/scrape_caps.py` | 260 | audit_append_call | `docs.append(doc)` |
| `scripts/scrape_caps.py` | 354 | audit_append_call | `documents.append(doc)` |
| `scripts/scrape_caps.py` | 395 | audit_append_call | `parts.append(page.get_text("text"))` |
| `scripts/scrape_caps.py` | 481 | audit_append_call | `records.append(record)` |
| `scripts/scrape_teaching_materials.py` | 41 | audit_append_call | `links.append({"url": full_url, "text": text})` |
| `scripts/seed_item_bank.py` | 99 | audit_append_call | `failing.append({"item": item, "errors": errors})` |
| `scripts/seed_item_bank.py` | 109 | audit_append_call | `passing.append(item)` |
| `scripts/staging_smoke.py` | 61 | audit_append_call | `results.append({"path": check.path, "status": status, "passed": passed})` |
| `scripts/sync_caps_r2.py` | 58 | audit_append_call | `items.append(SyncItem(path, f"{prefix.rstrip('/')}/{rel}"))` |
| `scripts/sync_caps_r2.py` | 95 | audit_append_call | `synced.append({"local_path": str(item.local_path), "key": item.key})` |
| `scripts/sync_caps_r2.py` | 112 | audit_append_call | `synced.append({"local_path": str(local_path), "key": key})` |
| `scripts/sync_git_to_redmine.py` | 15 | audit_events_table | `"fourth estate": 5, "estate": 5, "audit_events": 5,` |
| `scripts/train_qlora.py` | 41 | audit_append_call | `records.append(json.loads(line))` |
| `scripts/validate_ai_output_fixtures.py` | 50 | audit_append_call | `results.append(` |
| `scripts/validate_ai_output_fixtures.py` | 58 | audit_append_call | `results.append(` |
| `scripts/validate_ai_output_fixtures.py` | 67 | audit_append_call | `results.append(` |
| `scripts/validate_ai_output_fixtures.py` | 101 | audit_append_call | `results.append(` |
| `scripts/validate_ai_output_fixtures.py` | 122 | audit_append_call | `results.append(` |
| `scripts/validate_ai_output_fixtures.py` | 149 | audit_append_call | `results.append(FixtureValidationResult(path.name, False, f"unsupported type {output_type!r}"))` |
| `scripts/validate_ai_output_fixtures.py` | 159 | audit_append_call | `results.append(FixtureValidationResult(fixture, False, "fixture missing"))` |
| `scripts/validate_item_bank.py` | 185 | audit_append_call | `failure_log.append({` |
| `scripts/validate_runtime_env.py` | 58 | audit_append_call | `errors.append(f"{name} is required for {args.env}")` |
| `scripts/validate_runtime_env.py` | 61 | audit_append_call | `errors.append(f"{name} contains a placeholder/dev value")` |
| `scripts/validate_runtime_env.py` | 66 | audit_append_call | `errors.append("JWT_SECRET must be at least 32 characters")` |
| `scripts/validate_runtime_env.py` | 69 | audit_append_call | `errors.append("ALLOWED_ORIGINS must not contain wildcard origins in staging/production")` |
| `scripts/validate_runtime_env.py` | 71 | audit_append_call | `errors.append("at least one external provider secret should be configured or explicitly mocked")` |
| `scripts/validate_schema_integrity.py` | 28 | audit_events_table | `"audit_events",` |
| `scripts/validate_schema_integrity.py` | 52 | audit_events_table | `"audit_events": {"idx_audit_events_ts", "idx_audit_events_actor", "idx_audit_events_hash"},` |
| `scripts/validate_schema_integrity.py` | 67 | audit_events_table | `"audit_events": {` |
| `scripts/validate_schema_integrity.py` | 90 | audit_append_call | `errors.append(f"missing ORM tables: {sorted(missing_tables)}")` |
| `scripts/validate_schema_integrity.py` | 96 | audit_append_call | `errors.append(f"{table_name}: missing primary key")` |
| `scripts/validate_schema_integrity.py` | 97 | audit_events_table | `if table_name not in {"audit_events"} and "created_at" not in table.c:` |
| `scripts/validate_schema_integrity.py` | 98 | audit_append_call | `errors.append(f"{table_name}: missing created_at timestamp")` |
| `scripts/validate_schema_integrity.py` | 102 | audit_append_call | `errors.append(f"{table_name}: expected at least one foreign key")` |
| `scripts/validate_schema_integrity.py` | 110 | audit_append_call | `errors.append(f"{table_name}: missing indexes {sorted(missing)}")` |
| `scripts/validate_schema_integrity.py` | 118 | audit_append_call | `errors.append(f"{table_name}: missing constraints {sorted(missing)}")` |
| `scripts/verify_audit_chain.py` | 5 | audit_events_table | `Walks the audit_events table and checks hash/HMAC integrity.` |
| `scripts/verify_audit_chain.py` | 28 | audit_repository | `from app.repositories.audit_repository import AuditRepository, configure_hmac_secret` |
| `scripts/verify_audit_chain.py` | 40 | audit_repository | `repo = AuditRepository(pool)` |
| `scripts/verify_migration_graph.py` | 69 | audit_append_call | `migrations.append(Migration(file=file, revision=str(revision), down_revisions=down_revisions))` |
| `scripts/verify_migration_graph.py` | 82 | audit_append_call | `errors.append(f"duplicate revision id: {migration.revision}")` |
| `scripts/verify_migration_graph.py` | 88 | audit_append_call | `errors.append(` |
| `scripts/verify_migration_graph.py` | 92 | audit_append_call | `errors.append(` |
| `scripts/verify_migration_graph.py` | 100 | audit_append_call | `bases.append(migration.revision)` |
| `scripts/verify_migration_graph.py` | 102 | audit_append_call | `children.setdefault(down_revision, []).append(migration.revision)` |
| `scripts/verify_migration_graph.py` | 106 | audit_append_call | `errors.append(f"expected exactly one base revision, found {bases}")` |
| `scripts/verify_migration_graph.py` | 108 | audit_append_call | `errors.append(f"expected exactly one head revision, found {heads}")` |
| `tests/ci/test_item_bank_ci_jobs.py` | 181 | audit_append_call | `failures.append(f"{item.get('item_id', '?')}: missing {missing}")` |
| `tests/ci/test_item_bank_ci_jobs.py` | 185 | audit_append_call | `failures.append(` |
| `tests/ci/test_item_bank_ci_jobs.py` | 254 | audit_append_call | `latencies.append(lat)` |
| `tests/integration/conftest.py` | 60 | audit_append_call | `results.append(await self._incr_immediate(*args))` |
| `tests/integration/conftest.py` | 62 | audit_append_call | `results.append(await self._expire_immediate(*args))` |
| `tests/integration/conftest.py` | 68 | audit_append_call | `self._queue.append(("incr", (key,)))` |
| `tests/integration/conftest.py` | 79 | audit_append_call | `self._queue.append(("expire", (key, seconds)))` |
| `tests/integration/test_audit_immutability.py` | 12 | audit_events_table | `Verify that audit_events cannot be updated or deleted due to DB rules.` |
| `tests/integration/test_audit_immutability.py` | 34 | audit_events_table | `"UPDATE audit_events SET payload = '{\"key\": \"tampered\"}' "` |
| `tests/integration/test_audit_immutability.py` | 43 | audit_events_table | `text("SELECT payload FROM audit_events WHERE id = :id"),` |
| `tests/integration/test_audit_immutability.py` | 58 | audit_events_table | `text("DELETE FROM audit_events WHERE id = :id"),` |
| `tests/integration/test_audit_immutability.py` | 65 | audit_events_table | `text("SELECT COUNT(*) FROM audit_events WHERE id = :id"),` |
| `tests/integration/test_diagnostic_session.py` | 91 | audit_append_call | `items.append(_make_item(difficulty_b=b, caps_ref=caps_ref))` |
| `tests/integration/test_diagnostic_session.py` | 194 | audit_append_call | `served_item_ids.append(item.item_id)` |
| `tests/integration/test_diagnostic_session.py` | 250 | audit_append_call | `served_ids.append(item.item_id)` |
| `tests/integration/test_lesson_sync.py` | 42 | audit_append_call | `calls.append(("complete", lesson_id, None))` |
| `tests/integration/test_lesson_sync.py` | 45 | audit_append_call | `calls.append(("feedback", lesson_id, score))` |
| `tests/integration/test_stripe_webhooks.py` | 32 | audit_append_call | `calls.append(guardian_id)` |
| `tests/legacy/integration/test_api_contracts.py` | 114 | audit_events_table | `assert "audit_events" in payload` |
| `tests/legacy/integration/test_five_pillar_pipeline.py` | 121 | audit_append_call | `captured_calls.append({"args": args, "kwargs": kwargs})` |
| `tests/legacy/integration/test_lesson_api.py` | 59 | audit_append_call | `captured_prompts.append({"system": system, "user": user})` |
| `tests/legacy/popia/test_popia_compliance.py` | 240 | audit_log_identifier | `from app.models import AuditLog` |
| `tests/legacy/popia/test_popia_compliance.py` | 242 | audit_log_identifier | `log = AuditLog()` |
| `tests/legacy/unit/test_irt_benchmarks.py` | 27 | audit_append_call | `session.responses.append(Response(item.item_id, is_correct, 5000))` |
| `tests/legacy/unit/test_irt_benchmarks.py` | 43 | audit_append_call | `bank.append(Item(` |
| `tests/legacy/unit/test_irt_benchmarks.py` | 57 | audit_append_call | `estimates.append(est)` |
| `tests/legacy/unit/test_irt_benchmarks.py` | 61 | audit_append_call | `results.append((true_theta, avg_est, error))` |
| `tests/legacy/unit/test_profiler.py` | 21 | audit_append_call | `events.append({` |
| `tests/test_entrypoints.py` | 94 | audit_append_call | `missing.append(f"{prefix}{fragment}")` |
| `tests/unit/modules/lessons/test_lesson_generation_perf.py` | 184 | audit_append_call | `latencies.append(elapsed)` |
| `tests/unit/modules/lessons/test_lesson_generation_perf.py` | 229 | audit_append_call | `latencies.append(elapsed * 1000)  # convert to ms` |
| `tests/unit/modules/lessons/test_lesson_generation_perf.py` | 270 | audit_append_call | `latencies.append((time.perf_counter() - start) * 1000)` |
| `tests/unit/test_api_v2_router_contract.py` | 46 | audit_append_call | `missing.append(f"{router_name}:{expected_prefix}")` |
| `tests/unit/test_audit_callsite_inventory_and_adapter.py` | 44 | audit_append_call | `self.calls.append(kwargs)` |
| `tests/unit/test_audit_callsite_inventory_and_adapter.py` | 50 | audit_append_call | `result = await adapter.append(action="x", resource_id="r1")` |
| `tests/unit/test_audit_integrity.py` | 15 | audit_repository | `AuditRepository,` |
| `tests/unit/test_audit_repository.py` | 4 | audit_repository | `Task 23: AuditRepository unit tests` |
| `tests/unit/test_audit_repository.py` | 8 | audit_events_table | `- UPDATE on audit_events is a no-op (PostgreSQL RULE)` |
| `tests/unit/test_audit_repository.py` | 9 | audit_events_table | `- DELETE on audit_events is a no-op (PostgreSQL RULE)` |
| `tests/unit/test_audit_repository.py` | 25 | audit_repository | `from app.repositories.audit_repository import AuditRepository` |
| `tests/unit/test_audit_repository.py` | 33 | audit_repository | `repo = AuditRepository(db_session)` |
| `tests/unit/test_audit_repository.py` | 37 | audit_append_call | `event = await repo.append(` |
| `tests/unit/test_audit_repository.py` | 53 | audit_repository | `repo = AuditRepository(db_session)` |
| `tests/unit/test_audit_repository.py` | 54 | audit_append_call | `event = await repo.append(` |
| `tests/unit/test_audit_repository.py` | 64 | audit_repository | `repo = AuditRepository(db_session)` |
| `tests/unit/test_audit_repository.py` | 65 | audit_append_call | `event = await repo.append(` |
| `tests/unit/test_audit_repository.py` | 74 | audit_repository | `repo = AuditRepository(db_session)` |
| `tests/unit/test_audit_repository.py` | 76 | audit_append_call | `await repo.append(event_type="", payload={})` |
| `tests/unit/test_audit_repository.py` | 81 | audit_repository | `repo = AuditRepository(db_session)` |
| `tests/unit/test_audit_repository.py` | 84 | audit_append_call | `await repo.append(` |
| `tests/unit/test_audit_repository.py` | 90 | audit_append_call | `await repo.append(` |
| `tests/unit/test_audit_repository.py` | 96 | audit_append_call | `await repo.append(` |
| `tests/unit/test_audit_repository.py` | 110 | audit_repository | `repo = AuditRepository(db_session)` |
| `tests/unit/test_audit_repository.py` | 111 | audit_append_call | `event = await repo.append(` |
| `tests/unit/test_audit_repository.py` | 118 | audit_events_table | `text("UPDATE audit_events SET event_type = 'tampered' WHERE id = :id"),` |
| `tests/unit/test_audit_repository.py` | 129 | audit_events_table | `"UPDATE on audit_events must be a no-op due to PostgreSQL RULE"` |
| `tests/unit/test_audit_repository.py` | 138 | audit_repository | `repo = AuditRepository(db_session)` |
| `tests/unit/test_audit_repository.py` | 139 | audit_append_call | `event = await repo.append(` |
| `tests/unit/test_audit_repository.py` | 146 | audit_events_table | `text("DELETE FROM audit_events WHERE id = :id"),` |
| `tests/unit/test_audit_repository.py` | 157 | audit_events_table | `"DELETE on audit_events must be a no-op due to PostgreSQL RULE"` |
| `tests/unit/test_audit_repository.py` | 165 | audit_repository | `repo = AuditRepository(db_session)` |
| `tests/unit/test_audit_repository.py` | 169 | audit_append_call | `await repo.append("consent.granted", payload={}, resource_id=resource_id)` |
| `tests/unit/test_audit_repository.py` | 170 | audit_append_call | `await repo.append("consent.revoked", payload={}, resource_id=resource_id)` |
| `tests/unit/test_audit_repository.py` | 171 | audit_append_call | `await repo.append("consent.granted", payload={}, resource_id=other_resource_id)` |
| `tests/unit/test_audit_repository.py` | 179 | audit_repository | `repo = AuditRepository(db_session)` |
| `tests/unit/test_audit_repository.py` | 182 | audit_append_call | `await repo.append("consent.granted", payload={}, resource_id=resource_id)` |
| `tests/unit/test_audit_repository.py` | 183 | audit_append_call | `await repo.append("consent.revoked", payload={}, resource_id=resource_id)` |
| `tests/unit/test_audit_repository.py` | 191 | audit_repository | `repo = AuditRepository(db_session)` |
| `tests/unit/test_audit_repository.py` | 194 | audit_append_call | `await repo.append("consent.granted", payload={}, actor_id=actor_id)` |
| `tests/unit/test_audit_repository.py` | 195 | audit_append_call | `await repo.append("consent.revoked", payload={}, actor_id=actor_id)` |
| `tests/unit/test_billing_monetization_production_readiness.py` | 69 | audit_log_identifier | `assert "processed:evt_1:invoice.created:1" in store.audit_log` |
| `tests/unit/test_billing_monetization_production_readiness.py` | 70 | audit_log_identifier | `assert "duplicate:evt_1:invoice.created" in store.audit_log` |
| `tests/unit/test_consent_policy.py` | 75 | audit_append_call | `self.events.append(kwargs)` |
| `tests/unit/test_no_raw_dict_responses.py` | 74 | audit_append_call | `violations.append(` |
| `tests/unit/test_v2_services.py` | 6 | audit_log_identifier | `from app.domain.entities import AuditLog, LearnerProfile` |
| `tests/unit/test_v2_services.py` | 35 | audit_log_identifier | `repo.append.return_value = AuditLog(` |
| `tests/unit/test_v2_services_full.py` | 15 | audit_log_identifier | `from app.domain.entities import LearnerProfile, AuditLog` |
| `tests/unit/test_v2_services_full.py` | 29 | audit_log_identifier | `def _audit_log(event_type: str = "TEST") -> AuditLog:` |
| `tests/unit/test_v2_services_full.py` | 30 | audit_log_identifier | `return AuditLog(event_id=str(uuid.uuid4()), learner_id=LEARNER_ID, event_type=event_type,` |
| `tests/unit/test_v2_services_full.py` | 285 | audit_append_call | `learners.append(m)` |

## Review checklist

- [ ] Confirm canonical append-only audit table.
- [ ] Confirm all security/POPIA-sensitive actions emit canonical audit events.
- [ ] Identify legacy `append` call sites that need adapter migration.
- [ ] Identify any `audit_logs` data-retention requirement.
- [ ] Delete legacy audit code only after adapter migration and full-suite evidence.
