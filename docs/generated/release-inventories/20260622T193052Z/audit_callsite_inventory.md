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
| `alembic/versions/20260510_0300_popia_consent_audit_dsr.py` | 122 | audit_events_table | `REVOKE UPDATE, DELETE ON audit_events FROM eduboost_app;` |
| `alembic/versions/20260510_0300_popia_consent_audit_dsr.py` | 129 | audit_events_table | `op.execute("DROP TRIGGER IF EXISTS trg_audit_events_immutable ON audit_events;")` |
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
| `app/api_v2_deps/diagnostic_repositories.py` | 77 | audit_append_call | `failures.append(f"{dotted_path}: {type(exc).__name__}: {exc}")` |
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
| `app/api_v2_routers/auth_extended.py` | 76 | audit_append_call | `_reset_attempts[ip].append(now)` |
| `app/api_v2_routers/auth_extended.py` | 96 | audit_append_call | `errors.append("at least 8 characters")` |
| `app/api_v2_routers/auth_extended.py` | 98 | audit_append_call | `errors.append("one uppercase letter")` |
| `app/api_v2_routers/auth_extended.py` | 100 | audit_append_call | `errors.append("one digit")` |
| `app/api_v2_routers/billing.py` | 44 | audit_record_call | `await audit.record("STRIPE_WEBHOOK", payload=result)` |
| `app/api_v2_routers/consent.py` | 50 | audit_log_identifier | `# AuditLog emission is handled inside ConsentService.grant().` |
| `app/api_v2_routers/consent.py` | 83 | audit_log_identifier | `# AuditLog emission is handled inside ConsentService.revoke().` |
| `app/api_v2_routers/gamification.py` | 63 | audit_record_call | `await FourthEstateService(db).record(` |
| `app/api_v2_routers/learners.py` | 153 | audit_record_call | `await audit.record(` |
| `app/api_v2_routers/parents.py` | 77 | audit_append_call | `dashboard_learners.append(` |
| `app/api_v2_routers/parents.py` | 157 | audit_append_call | `response_learners.append(` |
| `app/api_v2_routers/parents.py` | 204 | audit_append_call | `exports.append(` |
| `app/api_v2_routers/parents.py` | 286 | audit_record_call | `await FourthEstateService(db).record(` |
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
| `app/core/config.py` | 198 | audit_append_call | `qlist.append(("ssl", val))` |
| `app/core/config.py` | 200 | audit_append_call | `qlist.append((k, val))` |
| `app/core/database.py` | 84 | audit_events_table | `await conn.execute(text("DROP RULE IF EXISTS audit_events_no_update ON audit_events"))` |
| `app/core/database.py` | 85 | audit_events_table | `await conn.execute(text("DROP RULE IF EXISTS audit_events_no_delete ON audit_events"))` |
| `app/core/database.py` | 90 | audit_events_table | `ON UPDATE TO audit_events` |
| `app/core/database.py` | 99 | audit_events_table | `ON DELETE TO audit_events` |
| `app/core/database.py` | 144 | audit_append_call | `conn.info.setdefault("query_start_time", []).append(time.time())` |
| `app/core/exceptions.py` | 113 | audit_append_call | `field_errors.append(` |
| `app/core/health.py` | 102 | audit_append_call | `missing.append("JWT_SECRET_KEY")` |
| `app/core/health.py` | 105 | audit_append_call | `missing.append("JWT_SECRET")` |
| `app/core/health.py` | 108 | audit_append_call | `missing.append(name)` |
| `app/core/health.py` | 155 | audit_events_table | `await session.execute(text("SELECT 1 FROM audit_events LIMIT 1"))` |
| `app/core/llm_gateway.py` | 686 | audit_append_call | `positions.append((start, label, start + len(needle)))` |
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
| `app/domain/consent.py` | 69 | audit_log_identifier | `# audit_log` |
| `app/domain/entities.py` | 18 | audit_log_identifier | `class AuditLog:` |
| `app/frontend/node_modules/.pnpm/flatted@3.4.2/node_modules/flatted/python/flatted.py` | 46 | audit_append_call | `input.append(value)` |
| `app/frontend/node_modules/.pnpm/flatted@3.4.2/node_modules/flatted/python/flatted.py` | 48 | audit_append_call | `known.key.append(value)` |
| `app/frontend/node_modules/.pnpm/flatted@3.4.2/node_modules/flatted/python/flatted.py` | 49 | audit_append_call | `known.value.append(index)` |
| `app/frontend/node_modules/.pnpm/flatted@3.4.2/node_modules/flatted/python/flatted.py` | 70 | audit_append_call | `parsed.append(tmp)` |
| `app/frontend/node_modules/.pnpm/flatted@3.4.2/node_modules/flatted/python/flatted.py` | 71 | audit_append_call | `lazy.append([output, key])` |
| `app/frontend/node_modules/.pnpm/flatted@3.4.2/node_modules/flatted/python/flatted.py` | 81 | audit_append_call | `output.append(_relate(known, input, val))` |
| `app/frontend/node_modules/.pnpm/flatted@3.4.2/node_modules/flatted/python/flatted.py` | 112 | audit_append_call | `wrapped.append(_wrap(value))` |
| `app/frontend/node_modules/.pnpm/flatted@3.4.2/node_modules/flatted/python/flatted.py` | 117 | audit_append_call | `input.append(value.value)` |
| `app/frontend/node_modules/.pnpm/flatted@3.4.2/node_modules/flatted/python/flatted.py` | 119 | audit_append_call | `input.append(value)` |
| `app/frontend/node_modules/.pnpm/flatted@3.4.2/node_modules/flatted/python/flatted.py` | 142 | audit_append_call | `output.append(_transform(known, input, input[i]))` |
| `app/frontend/node_modules/.pnpm/jsdom@29.1.1/node_modules/jsdom/README.md` | 69 | audit_append_call | `<script>document.getElementById("content").append(document.createElement("hr"));</script>` |
| `app/frontend/node_modules/.pnpm/jsdom@29.1.1/node_modules/jsdom/README.md` | 81 | audit_append_call | `<script>document.getElementById("content").append(document.createElement("hr"));</script>` |
| `app/frontend/node_modules/.pnpm/jsdom@29.1.1/node_modules/jsdom/README.md` | 99 | audit_append_call | `<script>document.getElementById("content").append(document.createElement("hr"));</script>` |
| `app/frontend/node_modules/.pnpm/jsdom@29.1.1/node_modules/jsdom/README.md` | 103 | audit_append_call | `dom.window.eval('document.getElementById("content").append(document.createElement("p"));');` |
| `app/frontend/node_modules/.pnpm/magic-string@0.30.21/node_modules/magic-string/README.md` | 52 | audit_append_call | `s.prepend('var ').append(';'); // most methods are chainable` |
| `app/frontend/node_modules/.pnpm/magic-string@0.30.21/node_modules/magic-string/README.md` | 101 | audit_append_call | `### s.append( content )` |
| `app/frontend/node_modules/.pnpm/magic-string@0.30.21/node_modules/magic-string/README.md` | 296 | audit_append_call | `.append('}());');` |
| `app/frontend/node_modules/.pnpm/postcss-selector-parser@6.1.2/node_modules/postcss-selector-parser/API.md` | 520 | audit_append_call | `### `container.prepend(node)` & `container.append(node)`` |
| `app/frontend/node_modules/.pnpm/postcss-selector-parser@6.1.2/node_modules/postcss-selector-parser/API.md` | 527 | audit_append_call | `selector.append(id);` |
| `app/models/__init__.py` | 323 | audit_events_table | `__tablename__ = "audit_events"` |
| `app/models/__init__.py` | 699 | audit_log_identifier | `class AuditLog(Base):` |
| `app/models/__init__.py` | 700 | audit_logs_table | `__tablename__ = "audit_logs"` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 71 | audit_append_call | `issues.append("beta launch decision must be documented in docs/adr/")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 73 | audit_append_call | `issues.append("beta launch architecture must be documented in docs/beta_launch/")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 84 | audit_append_call | `issues.append(f"{name} is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 101 | audit_append_call | `issues.append("scope_id is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 103 | audit_append_call | `issues.append("product scope description is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 105 | audit_append_call | `issues.append("product scope owner is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 107 | audit_append_call | `issues.append("product scope evidence path must live under docs/beta_launch/")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 109 | audit_append_call | `issues.append("billing must be explicitly excluded or disabled for beta unless approved")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 111 | audit_append_call | `issues.append("excluded beta scope must be explicitly marked as exclusion")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 128 | audit_append_call | `issues.append("criterion_id is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 130 | audit_append_call | `issues.append("acceptance criterion name is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 132 | audit_append_call | `issues.append("staging acceptance evidence path must be controlled")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 134 | audit_append_call | `issues.append("staging acceptance owner is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 136 | audit_append_call | `issues.append(f"{self.criterion_id} blocks beta launch")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 138 | audit_append_call | `issues.append("waived staging acceptance criterion requires waiver path")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 154 | audit_append_call | `issues.append("entry criterion_id is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 156 | audit_append_call | `issues.append("entry criterion description is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 158 | audit_append_call | `issues.append("entry criterion evidence path must be controlled")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 160 | audit_append_call | `issues.append("entry criterion owner is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 162 | audit_append_call | `issues.append(f"{self.criterion_id} required entry criterion is not met")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 179 | audit_append_call | `issues.append("exit criterion_id is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 181 | audit_append_call | `issues.append("exit criterion description is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 183 | audit_append_call | `issues.append("exit criterion metric name is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 185 | audit_append_call | `issues.append("exit criterion threshold is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 187 | audit_append_call | `issues.append("exit criterion owner is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 189 | audit_append_call | `issues.append("exit criterion evidence path must be controlled")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 208 | audit_append_call | `issues.append("cohort_id is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 210 | audit_append_call | `issues.append("max_learners must be positive")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 212 | audit_append_call | `issues.append("max_guardians must be positive")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 214 | audit_append_call | `issues.append("allowed grades are required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 216 | audit_append_call | `issues.append("allowed grades must be South African school grades 1-12")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 218 | audit_append_call | `issues.append("allowed subjects are required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 220 | audit_append_call | `issues.append("beta cohort requires consent")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 222 | audit_append_call | `issues.append("beta cohort requires support channel readiness")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 224 | audit_append_call | `issues.append("beta cohort requires rollback support")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 240 | audit_append_call | `issues.append("feedback channel is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 242 | audit_append_call | `issues.append("feedback triage SLA must be positive")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 244 | audit_append_call | `issues.append(f"{self.severity.value} feedback requires escalation")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 246 | audit_append_call | `issues.append("feedback owner is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 248 | audit_append_call | `issues.append("feedback evidence path must live under docs/beta_launch/")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 266 | audit_append_call | `issues.append("known issue_id is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 268 | audit_append_call | `issues.append("known issue summary is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 270 | audit_append_call | `issues.append("known issue owner is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 272 | audit_append_call | `issues.append("high/critical known issues must block beta or be explicitly accepted")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 274 | audit_append_call | `issues.append("accepted beta known issue requires workaround")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 276 | audit_append_call | `issues.append("known issue evidence path must live under docs/beta_launch/")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 296 | audit_append_call | `issues.append("launch readiness review_id is required")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 298 | audit_append_call | `issues.append("launch readiness review requires approvers")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 307 | audit_append_call | `issues.append(f"{name} must be reviewed")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 309 | audit_append_call | `issues.append("general availability requires separate production launch approval")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 311 | audit_append_call | `issues.append("launch readiness evidence path must live under docs/beta_launch/")` |
| `app/modules/beta_launch/production_readiness_contracts.py` | 347 | audit_append_call | `issues.append(f"{issue.issue_id} blocks beta launch")` |
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
| `app/modules/consent/service.py` | 29 | audit_repository | `from app.repositories.audit_repository import AuditRepository` |
| `app/modules/consent/service.py` | 43 | audit_repository | `audit trail via :class:`~app.repositories.audit_repository.AuditRepository`` |
| `app/modules/consent/service.py` | 65 | audit_repository | `audit_repo: AuditRepository \| None = None,` |
| `app/modules/consent/service.py` | 75 | audit_repository | `audit_repo: Optional :class:`~app.repositories.audit_repository.AuditRepository`` |
| `app/modules/consent/service.py` | 95 | audit_repository | `audit_repo = AuditRepository(db)` |
| `app/modules/consent/service.py` | 196 | audit_log_identifier | `# AuditLog / fourth_estate coverage is written via _append_audit below.` |
| `app/modules/consent/service.py` | 236 | audit_log_identifier | `# AuditLog / fourth_estate coverage is written via _append_audit below.` |
| `app/modules/consent/service.py` | 315 | audit_log_identifier | `# AuditLog / fourth_estate coverage is written via _append_audit below.` |
| `app/modules/consent/service.py` | 369 | audit_repository | `Tries :class:`~app.repositories.audit_repository.AuditRepository`` |
| `app/modules/consent/service.py` | 381 | audit_append_call | `await self._audit_repo.append(` |
| `app/modules/consent/service.py` | 389 | audit_record_call | `await FourthEstateService(self._db).record(` |
| `app/modules/deployment/production_readiness_contracts.py` | 100 | audit_append_call | `issues.append("infrastructure provider is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 102 | audit_append_call | `issues.append("container registry is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 104 | audit_append_call | `issues.append("deployment platform is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 106 | audit_append_call | `issues.append("infrastructure decision must be documented in docs/adr/")` |
| `app/modules/deployment/production_readiness_contracts.py` | 108 | audit_append_call | `issues.append("deployment architecture must be documented in docs/deployment/")` |
| `app/modules/deployment/production_readiness_contracts.py` | 110 | audit_append_call | `issues.append("infrastructure-as-code is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 112 | audit_append_call | `issues.append("manual production approval is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 114 | audit_append_call | `issues.append("environment separation is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 131 | audit_append_call | `issues.append(f"{self.stage.value} command is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 133 | audit_append_call | `issues.append(f"{self.stage.value} production check must block deploy")` |
| `app/modules/deployment/production_readiness_contracts.py` | 135 | audit_append_call | `issues.append("security scan must run for PRs")` |
| `app/modules/deployment/production_readiness_contracts.py` | 137 | audit_append_call | `issues.append("migration check must run before staging")` |
| `app/modules/deployment/production_readiness_contracts.py` | 156 | audit_append_call | `issues.append("dockerfile path is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 158 | audit_append_call | `issues.append("container must run as non-root user")` |
| `app/modules/deployment/production_readiness_contracts.py` | 160 | audit_append_call | `issues.append("base image pinning is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 162 | audit_append_call | `issues.append("container healthcheck is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 164 | audit_append_call | `issues.append("multi-stage build is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 166 | audit_append_call | `issues.append("dependency lockfile is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 168 | audit_append_call | `issues.append("container vulnerability scan is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 170 | audit_append_call | `issues.append("SBOM generation is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 190 | audit_append_call | `issues.append(f"{self.environment.value} missing required variable {variable}")` |
| `app/modules/deployment/production_readiness_contracts.py` | 192 | audit_append_call | `issues.append(f"{self.environment.value} secrets must be externalized")` |
| `app/modules/deployment/production_readiness_contracts.py` | 194 | audit_append_call | `issues.append("production debug must be disabled")` |
| `app/modules/deployment/production_readiness_contracts.py` | 196 | audit_append_call | `issues.append("production TLS is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 198 | audit_append_call | `issues.append("database migrations must be controlled")` |
| `app/modules/deployment/production_readiness_contracts.py` | 200 | audit_append_call | `issues.append(f"{self.environment.value} observability is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 203 | audit_append_call | `issues.append(f"forbidden variable {variable} cannot be required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 222 | audit_append_call | `issues.append("deployment gate name is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 224 | audit_append_call | `issues.append("deployment gate requires checks")` |
| `app/modules/deployment/production_readiness_contracts.py` | 226 | audit_append_call | `issues.append("production deployment gate requires manual approval")` |
| `app/modules/deployment/production_readiness_contracts.py` | 228 | audit_append_call | `issues.append("production strategy must preserve manual approval")` |
| `app/modules/deployment/production_readiness_contracts.py` | 230 | audit_append_call | `issues.append("rollback plan is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 232 | audit_append_call | `issues.append("smoke test is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 234 | audit_append_call | `issues.append("release notes are required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 236 | audit_append_call | `issues.append("deployment gate owner is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 253 | audit_append_call | `issues.append("rollback command must be documented")` |
| `app/modules/deployment/production_readiness_contracts.py` | 255 | audit_append_call | `issues.append("database rollback policy must be documented")` |
| `app/modules/deployment/production_readiness_contracts.py` | 257 | audit_append_call | `issues.append("feature flag rollback support is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 259 | audit_append_call | `issues.append("previous image must be retained")` |
| `app/modules/deployment/production_readiness_contracts.py` | 261 | audit_append_call | `issues.append("post-rollback smoke test is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 263 | audit_append_call | `issues.append("rollback incident record is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 280 | audit_append_call | `issues.append("git_sha must be lowercase hex")` |
| `app/modules/deployment/production_readiness_contracts.py` | 282 | audit_append_call | `issues.append("image_digest must be sha256")` |
| `app/modules/deployment/production_readiness_contracts.py` | 290 | audit_append_call | `issues.append(f"{name} is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 292 | audit_append_call | `issues.append("generated_at_utc is required")` |
| `app/modules/deployment/production_readiness_contracts.py` | 308 | audit_append_call | `issues.append(f"missing required environment variable {variable}")` |
| `app/modules/deployment/production_readiness_contracts.py` | 311 | audit_append_call | `issues.append(f"secret-like variable {key} has placeholder value")` |
| `app/modules/deployment/production_readiness_contracts.py` | 313 | audit_append_call | `issues.append("production manifest must set ENVIRONMENT=production")` |
| `app/modules/diagnostics/diagnostic_session_service.py` | 69 | audit_append_call | `snap.served_item_ids.append(item_id)` |
| `app/modules/diagnostics/diagnostic_session_service.py` | 78 | audit_append_call | `snap.responses.append({**diagnostic_response_snapshot(item, item_id=item_id), "correct": correct, "response": response})` |
| `app/modules/diagnostics/diagnostic_session_service.py` | 85 | audit_append_call | `snap.gap_topics.append(caps_ref)` |
| `app/modules/diagnostics/diagnostic_session_service.py` | 88 | audit_append_call | `snap.misconception_tags.append(tag)` |
| `app/modules/diagnostics/irt_engine.py` | 256 | audit_append_call | `grid.append(round(value, 4))` |
| `app/modules/diagnostics/irt_engine.py` | 268 | audit_append_call | `posterior_weights.append(prior * likelihood)` |
| `app/modules/diagnostics/irt_engine.py` | 497 | audit_append_call | `weights.append(prior * likelihood)` |
| `app/modules/diagnostics/irt_engine.py` | 602 | audit_append_call | `state.responses.append((str(item.item_id), is_correct))` |
| `app/modules/diagnostics/irt_engine.py` | 644 | audit_append_call | `proxies.append((last_item, correct))` |
| `app/modules/diagnostics/irt_engine.py` | 646 | audit_append_call | `proxies.append((_ItemProxy(), correct))` |
| `app/modules/diagnostics/irt_engine.py` | 740 | audit_append_call | `grid.append(round(value, 4))` |
| `app/modules/diagnostics/irt_engine.py` | 752 | audit_append_call | `weights.append(prior * likelihood)` |
| `app/modules/diagnostics/item_validator.py` | 179 | audit_append_call | `errors.append(exc)` |
| `app/modules/diagnostics/item_validator.py` | 279 | audit_append_call | `text_fields.append((f"option_{opt.get('label')}", opt.get("text", "")))` |
| `app/modules/diagnostics/production_readiness_contracts.py` | 77 | audit_append_call | `failures.append(f"{field_name} is required")` |
| `app/modules/diagnostics/production_readiness_contracts.py` | 79 | audit_append_call | `failures.append("grade must be between 0 and 12")` |
| `app/modules/diagnostics/production_readiness_contracts.py` | 81 | audit_append_call | `failures.append("difficulty must be in [-4.0, 4.0]")` |
| `app/modules/diagnostics/production_readiness_contracts.py` | 83 | audit_append_call | `failures.append("discrimination must be in [0.1, 4.0]")` |
| `app/modules/diagnostics/production_readiness_contracts.py` | 85 | audit_append_call | `failures.append("at least one distractor is required")` |
| `app/modules/diagnostics/production_readiness_contracts.py` | 87 | audit_append_call | `failures.append("correct answer must not appear as a distractor")` |
| `app/modules/diagnostics/production_readiness_contracts.py` | 89 | audit_append_call | `failures.append("max_exposure must be positive")` |
| `app/modules/diagnostics/production_readiness_contracts.py` | 91 | audit_append_call | `failures.append("exposure_count must be non-negative")` |
| `app/modules/diagnostics/production_readiness_contracts.py` | 188 | audit_append_call | `failures.append(` |
| `app/modules/diagnostics/quality_scorer.py` | 226 | audit_append_call | `texts.append(opt.get("text", ""))` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 22 | audit_logs_table | `AUDIT_LOGS = "audit_logs"` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 69 | audit_append_call | `issues.append("database backup provider is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 71 | audit_append_call | `issues.append("object backup provider is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 73 | audit_append_call | `issues.append("backup storage provider is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 75 | audit_append_call | `issues.append("backup provider decision must be documented in docs/adr/")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 77 | audit_append_call | `issues.append("backup architecture must be documented in docs/disaster_recovery/")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 79 | audit_append_call | `issues.append("backup encryption at rest is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 81 | audit_append_call | `issues.append("backup encryption in transit is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 83 | audit_append_call | `issues.append("cross-region backup copy is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 85 | audit_append_call | `issues.append("immutable retention is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 103 | audit_append_call | `issues.append(f"{self.scope.value} retention must be positive")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 105 | audit_append_call | `issues.append(f"{self.scope.value} critical backups must be hourly or daily")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 107 | audit_append_call | `issues.append("database backups require point-in-time recovery")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 109 | audit_append_call | `issues.append(f"{self.scope.value} backups must be encrypted")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 111 | audit_append_call | `issues.append(f"{self.scope.value} backups require integrity checks")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 113 | audit_append_call | `issues.append(f"{self.scope.value} backup owner is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 129 | audit_append_call | `issues.append("service is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 131 | audit_append_call | `issues.append("RPO cannot be negative")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 133 | audit_append_call | `issues.append("RTO cannot be negative")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 135 | audit_append_call | `issues.append("critical services require RPO <= 60 minutes")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 137 | audit_append_call | `issues.append("critical services require RTO <= 240 minutes")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 139 | audit_append_call | `issues.append("recovery owner is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 141 | audit_append_call | `issues.append("escalation route is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 161 | audit_append_call | `issues.append("manifest_id is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 163 | audit_append_call | `issues.append("backup_id is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 165 | audit_append_call | `issues.append("created_at_utc must be timezone-aware")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 167 | audit_append_call | `issues.append("source_environment is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 169 | audit_append_call | `issues.append("storage_location is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 171 | audit_append_call | `issues.append("checksum_sha256 must be 64 lowercase hex characters")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 173 | audit_append_call | `issues.append("backup manifest entry must be encrypted")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 175 | audit_append_call | `issues.append("retention_expires_at_utc must be timezone-aware")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 177 | audit_append_call | `issues.append("retention expiry must be after creation time")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 195 | audit_append_call | `issues.append("restore runbook must live under docs/disaster_recovery/runbooks/")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 197 | audit_append_call | `issues.append("pre-restore checks are required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 199 | audit_append_call | `issues.append("restore steps are required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 201 | audit_append_call | `issues.append("post-restore validation is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 203 | audit_append_call | `issues.append("rollback steps are required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 205 | audit_append_call | `issues.append("restore runbook owner is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 227 | audit_append_call | `issues.append("drill_id is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 229 | audit_append_call | `issues.append("drill timestamps must be timezone-aware")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 231 | audit_append_call | `issues.append("drill completion must be after start")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 233 | audit_append_call | `issues.append("observed RPO cannot be negative")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 235 | audit_append_call | `issues.append("observed RTO cannot be negative")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 237 | audit_append_call | `issues.append("passing restore drill requires checksum verification")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 239 | audit_append_call | `issues.append("passing restore drill requires application smoke test")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 241 | audit_append_call | `issues.append("passing restore drill requires data integrity test")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 243 | audit_append_call | `issues.append("restore drill evidence must live under docs/disaster_recovery/evidence/")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 262 | audit_append_call | `issues.append("plan_id is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 270 | audit_append_call | `issues.append(f"{name} is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 272 | audit_append_call | `issues.append("escalation matrix must be documented in docs/disaster_recovery/")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 274 | audit_append_call | `issues.append("business continuity plan must be documented in docs/disaster_recovery/")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 276 | audit_append_call | `issues.append("annual DR test is required")` |
| `app/modules/disaster_recovery/production_readiness_contracts.py` | 278 | audit_append_call | `issues.append("post-incident review is required")` |
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
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 88 | audit_append_call | `issues.append("final release-blocker decision must be documented in docs/adr/")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 90 | audit_append_call | `issues.append("release-blocker architecture must be documented in docs/release_blockers/")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 101 | audit_append_call | `issues.append(f"{name} is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 122 | audit_append_call | `issues.append("blocker_id must follow RB-### format")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 124 | audit_append_call | `issues.append("release blocker title is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 126 | audit_append_call | `issues.append("release blocker owner is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 128 | audit_append_call | `issues.append("release blocker evidence path must be controlled")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 130 | audit_append_call | `issues.append("closed blockers require closure evidence")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 132 | audit_append_call | `issues.append("closure evidence path must be controlled")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 134 | audit_append_call | `issues.append("waived blockers require waiver evidence")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 136 | audit_append_call | `issues.append("waiver evidence must live under docs/release_blockers/")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 138 | audit_append_call | `issues.append("external pending blockers require external dependency note")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 140 | audit_append_call | `issues.append("critical/release-blocker items cannot remain open")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 142 | audit_append_call | `issues.append("release-blocker severity cannot be waived by default")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 144 | audit_append_call | `issues.append(f"{self.blocker_id} still blocks launch")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 161 | audit_append_call | `issues.append("domain checklist path must live under docs/")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 163 | audit_append_call | `issues.append("domain check command is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 165 | audit_append_call | `issues.append("domain summary owner is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 167 | audit_append_call | `issues.append(f"{self.domain.value} release evidence is incomplete")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 169 | audit_append_call | `issues.append("external/manual domain requires manual dependency")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 186 | audit_append_call | `issues.append("waiver rule_id is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 188 | audit_append_call | `issues.append("release-blocker severity cannot be waived")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 190 | audit_append_call | `issues.append("waiver requires approvers")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 192 | audit_append_call | `issues.append("waiver expiry must be between 1 and 30 days")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 194 | audit_append_call | `issues.append("waiver requires compensating controls")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 196 | audit_append_call | `issues.append("waiver rule evidence path must live under docs/release_blockers/")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 214 | audit_append_call | `issues.append("dependency_id must follow EXT-### format")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 216 | audit_append_call | `issues.append("external dependency description is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 218 | audit_append_call | `issues.append("external dependency owner is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 220 | audit_append_call | `issues.append("external system is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 222 | audit_append_call | `issues.append("verification method is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 224 | audit_append_call | `issues.append("external dependency evidence path must live under docs/release_blockers/")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 226 | audit_append_call | `issues.append(f"{self.dependency_id} required external dependency is not closed")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 247 | audit_append_call | `issues.append("final go/no-go checklist_id is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 249 | audit_append_call | `issues.append("final go/no-go approvers are required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 251 | audit_append_call | `issues.append("release owner approval is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 253 | audit_append_call | `issues.append("required domains are required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 255 | audit_append_call | `issues.append("blocker register path must live under docs/release_blockers/")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 257 | audit_append_call | `issues.append("evidence bundle path must be controlled")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 266 | audit_append_call | `issues.append(f"{name} must be reviewed")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 268 | audit_append_call | `issues.append("GO decision must include external/manual dependency review")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 286 | audit_append_call | `issues.append("closure_id must follow CLOSE-### format")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 288 | audit_append_call | `issues.append("blocker_id must follow RB-### format")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 290 | audit_append_call | `issues.append("closed_by is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 292 | audit_append_call | `issues.append("evidence_checksum must be 64 lowercase hex")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 294 | audit_append_call | `issues.append("closure evidence path must be controlled")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 296 | audit_append_call | `issues.append("residual risk summary is required")` |
| `app/modules/final_release_blockers/production_readiness_contracts.py` | 346 | audit_append_call | `issues.append(f"checklist GO conflicts with computed {decision.value}")` |
| `app/modules/lessons/adaptive_remediation.py` | 159 | audit_append_call | `resolved_strategies.append(strategy)` |
| `app/modules/lessons/adaptive_remediation.py` | 162 | audit_append_call | `unrecognised_tags.append(tag)` |
| `app/modules/lessons/adaptive_remediation.py` | 163 | audit_append_call | `resolved_strategies.append(RemediationStrategy.RE_EXPLAIN)` |
| `app/modules/lessons/answer_key_verifier.py` | 107 | audit_append_call | `stripped.append(clean)` |
| `app/modules/lessons/answer_key_verifier.py` | 249 | audit_append_call | `disagreements.append({` |
| `app/modules/lessons/answer_key_verifier.py` | 257 | audit_append_call | `disagreements.append({` |
| `app/modules/lessons/answer_key_verifier.py` | 335 | audit_append_call | `results.append(` |
| `app/modules/lessons/caps_topic_map_service.py` | 54 | audit_append_call | `paths.append(legacy_launch_map)` |
| `app/modules/lessons/caps_topic_map_service.py` | 171 | audit_append_call | `self._maps.append(topic_map)` |
| `app/modules/lessons/caps_topic_map_service.py` | 213 | audit_append_call | `subtopics.append(` |
| `app/modules/lessons/caps_topic_map_service.py` | 223 | audit_append_call | `topics.append(` |
| `app/modules/lessons/caps_topic_map_service.py` | 231 | audit_append_call | `terms.append(` |
| `app/modules/lessons/caps_topic_map_service.py` | 358 | audit_append_call | `contexts.append(topic_context)` |
| `app/modules/lessons/caps_topic_map_service.py` | 363 | audit_append_call | `contexts.append(subtopic_context)` |
| `app/modules/lessons/lesson_coverage_router.py` | 103 | audit_append_call | `rows.append({` |
| `app/modules/lessons/lesson_coverage_router.py` | 112 | audit_append_call | `rows.append({` |
| `app/modules/lessons/lesson_coverage_router.py` | 163 | audit_append_call | `per_ref.append(CapsRefCoverage(` |
| `app/modules/lessons/lesson_generator.py` | 465 | audit_append_call | `disagreements.append(` |
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
| `app/modules/lessons/llm_gateway.py` | 152 | audit_append_call | `messages.append({"role": "system", "content": system})` |
| `app/modules/lessons/llm_gateway.py` | 153 | audit_append_call | `messages.append({"role": "user", "content": prompt})` |
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
| `app/modules/operations_support/production_readiness_contracts.py` | 79 | audit_append_call | `issues.append("operations support decision must be documented in docs/adr/")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 81 | audit_append_call | `issues.append("operations support architecture must be documented in docs/operations_support/")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 92 | audit_append_call | `issues.append(f"{name} is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 110 | audit_append_call | `issues.append("incident response time must be positive")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 112 | audit_append_call | `issues.append("incident update interval must be positive")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 114 | audit_append_call | `issues.append(f"{self.severity.value} requires incident commander")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 116 | audit_append_call | `issues.append("sev1 requires status update")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 118 | audit_append_call | `issues.append("major or critical customer impact must block release")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 136 | audit_append_call | `issues.append("policy_id is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 138 | audit_append_call | `issues.append("primary and secondary roles must differ")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 140 | audit_append_call | `issues.append("escalation minutes must be positive")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 142 | audit_append_call | `issues.append("coverage hours are required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 144 | audit_append_call | `issues.append("backup on-call is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 146 | audit_append_call | `issues.append("on-call handoff is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 148 | audit_append_call | `issues.append("on-call evidence path must live under docs/operations_support/")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 167 | audit_append_call | `issues.append("operational runbook must live under docs/operations_support/runbooks/")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 169 | audit_append_call | `issues.append("runbook scenario is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 171 | audit_append_call | `issues.append("detection steps are required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 173 | audit_append_call | `issues.append("triage steps are required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 175 | audit_append_call | `issues.append("mitigation steps are required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 177 | audit_append_call | `issues.append("recovery steps are required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 179 | audit_append_call | `issues.append("verification steps are required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 181 | audit_append_call | `issues.append("rollback criteria are required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 197 | audit_append_call | `issues.append("first response minutes must be positive")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 199 | audit_append_call | `issues.append("target resolution hours must be positive")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 201 | audit_append_call | `issues.append(f"{self.priority.value} support requires escalation")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 203 | audit_append_call | `issues.append("p0 first response must be <= 30 minutes")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 205 | audit_append_call | `issues.append("p1 first response must be <= 120 minutes")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 222 | audit_append_call | `issues.append("template_id is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 224 | audit_append_call | `issues.append("status communication channels are required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 226 | audit_append_call | `issues.append("status communication audience is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 228 | audit_append_call | `issues.append("status update interval must be positive")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 230 | audit_append_call | `issues.append(f"{self.severity.value} status communication requires status page")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 233 | audit_append_call | `issues.append(f"status communication missing required field {field}")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 252 | audit_append_call | `issues.append("incident_id is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 254 | audit_append_call | `issues.append("detected_at_utc must be timezone-aware")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 256 | audit_append_call | `issues.append("resolved/reviewed incidents require root cause summary")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 258 | audit_append_call | `issues.append("incident evidence must live under docs/operations_support/incidents/")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 260 | audit_append_call | `issues.append("sev1/sev2 incidents require post-incident review")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 278 | audit_append_call | `issues.append("review_id is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 280 | audit_append_call | `issues.append("incident_id is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 282 | audit_append_call | `issues.append("post-incident review must be completed")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 284 | audit_append_call | `issues.append("root cause must be documented")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 286 | audit_append_call | `issues.append("incident timeline must be documented")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 288 | audit_append_call | `issues.append("corrective actions are required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 290 | audit_append_call | `issues.append("post-incident review evidence must live under docs/operations_support/post_incident_reviews/")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 309 | audit_append_call | `issues.append("operational handover checklist must live under docs/operations_support/")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 311 | audit_append_call | `issues.append("release owner is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 313 | audit_append_call | `issues.append("support owner is required")` |
| `app/modules/operations_support/production_readiness_contracts.py` | 323 | audit_append_call | `issues.append(f"{name} must be true")` |
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
| `app/modules/roadmap/production_readiness_contracts.py` | 84 | audit_append_call | `issues.append("roadmap governance decision must be documented in docs/adr/")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 86 | audit_append_call | `issues.append("roadmap architecture must be documented in docs/roadmap/")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 97 | audit_append_call | `issues.append(f"{name} is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 115 | audit_append_call | `issues.append("boundary_id is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 117 | audit_append_call | `issues.append("baseline boundary title is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 119 | audit_append_call | `issues.append("baseline boundary rationale is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 121 | audit_append_call | `issues.append("baseline boundary evidence path must be controlled")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 123 | audit_append_call | `issues.append("baseline boundary owner is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 125 | audit_append_call | `issues.append("external/manual boundary requires manual dependency")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 146 | audit_append_call | `issues.append("roadmap_id must follow RM-### format")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 148 | audit_append_call | `issues.append("roadmap item title is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 150 | audit_append_call | `issues.append("roadmap owner is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 152 | audit_append_call | `issues.append("roadmap rationale is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 154 | audit_append_call | `issues.append("roadmap expected outcome is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 156 | audit_append_call | `issues.append("P0/P1 items cannot be parked")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 158 | audit_append_call | `issues.append("in-progress items must be now or next")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 160 | audit_append_call | `issues.append("roadmap evidence path must live under docs/roadmap/")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 162 | audit_append_call | `issues.append("now/next roadmap items require target quarter")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 181 | audit_append_call | `issues.append("deferred_id must follow DEF-### format")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 183 | audit_append_call | `issues.append("deferred title is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 185 | audit_append_call | `issues.append("deferred reason is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 187 | audit_append_call | `issues.append("unblock condition is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 189 | audit_append_call | `issues.append("deferred scope owner is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 191 | audit_append_call | `issues.append("risk if deferred is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 193 | audit_append_call | `issues.append("deferred scope evidence path must live under docs/roadmap/")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 195 | audit_append_call | `issues.append("deferred scope review date is stale")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 213 | audit_append_call | `issues.append("dependency_id must follow DEP-### format")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 215 | audit_append_call | `issues.append("source_roadmap_id must follow RM-### format")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 217 | audit_append_call | `issues.append("dependency description is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 219 | audit_append_call | `issues.append("dependency owner is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 221 | audit_append_call | `issues.append("external dependencies require mitigation")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 223 | audit_append_call | `issues.append("roadmap dependency evidence path must live under docs/roadmap/")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 240 | audit_append_call | `issues.append("criterion_id must follow GRAD-### format")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 242 | audit_append_call | `issues.append("roadmap_id must follow RM-### format")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 244 | audit_append_call | `issues.append("graduation metric name is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 246 | audit_append_call | `issues.append("graduation threshold is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 248 | audit_append_call | `issues.append("graduation evidence path must be controlled")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 250 | audit_append_call | `issues.append("graduation criterion owner is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 252 | audit_append_call | `issues.append("GA-required graduation criterion must define metric")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 269 | audit_append_call | `issues.append("cadence_id is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 271 | audit_append_call | `issues.append("roadmap review frequency must be positive")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 273 | audit_append_call | `issues.append("roadmap review cadence must be at least quarterly")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 275 | audit_append_call | `issues.append("roadmap review owner is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 277 | audit_append_call | `issues.append("roadmap review requires inputs")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 279 | audit_append_call | `issues.append("roadmap review requires outputs")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 281 | audit_append_call | `issues.append("roadmap review evidence path must live under docs/roadmap/")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 283 | audit_append_call | `issues.append("roadmap review must block uncontrolled scope expansion")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 302 | audit_append_call | `issues.append("risk_id must follow RISK-### format")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 304 | audit_append_call | `issues.append("risk title is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 306 | audit_append_call | `issues.append("risk impact is invalid")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 308 | audit_append_call | `issues.append("risk likelihood is invalid")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 310 | audit_append_call | `issues.append("risk owner is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 312 | audit_append_call | `issues.append("risk mitigation is required")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 314 | audit_append_call | `issues.append("risk evidence path must live under docs/roadmap/")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 316 | audit_append_call | `issues.append("critical post-baseline risk must block GA")` |
| `app/modules/roadmap/production_readiness_contracts.py` | 352 | audit_append_call | `issues.append(f"{dependency.dependency_id} references unknown roadmap item")` |
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
| `app/repositories/item_bank_repository.py` | 151 | audit_append_call | `heatmap.append(` |
| `app/repositories/repositories.py` | 13 | audit_log_identifier | `AuditLog,` |
| `app/repositories/repositories.py` | 313 | audit_repository | `class AuditRepository:` |
| `app/repositories/repositories.py` | 324 | audit_log_identifier | `) -> AuditLog:` |
| `app/repositories/repositories.py` | 325 | audit_log_identifier | `entry = AuditLog(` |
| `app/security/dependencies.py` | 35 | audit_append_call | `roles.append(Role(raw_role))` |
| `app/services/audit_canonicalization_registry.py` | 46 | audit_logs_table | `current_shape="legacy audit_logs/AuditLog references",` |
| `app/services/audit_canonicalization_registry.py` | 46 | audit_log_identifier | `current_shape="legacy audit_logs/AuditLog references",` |
| `app/services/audit_canonicalization_slice.py` | 71 | audit_record_call | `return await adapter.record(command.to_event_input())` |
| `app/services/audit_migration_orchestrator.py` | 73 | audit_record_call | `return await adapter.record(envelope.to_event_input())` |
| `app/services/audit_service.py` | 21 | audit_append_call | `row = await self.repository.append(` |
| `app/services/auth_application_service.py` | 28 | audit_repository | `"app.repositories.repositories.AuditRepository",` |
| `app/services/auth_application_service.py` | 29 | audit_repository | `"app.repositories.audit_repository.AuditRepository",` |
| `app/services/auth_lifecycle_impl.py` | 106 | audit_append_call | `learner_ids.append(str(learner.id))` |
| `app/services/backend_adapter_wiring_service.py` | 28 | audit_append_call | `self.events.append(kwargs)` |
| `app/services/backend_adapter_wiring_service.py` | 36 | audit_record_call | `response = await adapter.record(` |
| `app/services/backend_adapter_wiring_service.py` | 53 | audit_append_call | `results.append(await record_candidate_payload(repository, payload))` |
| `app/services/backend_consolidation_runtime.py` | 38 | audit_record_call | `return await adapter.record(**event.to_kwargs())` |
| `app/services/backend_consolidation_runtime.py` | 39 | audit_record_call | `return await adapter.record(**event)` |
| `app/services/backend_first_wiring_candidates.py` | 52 | audit_append_call | `candidates.append(` |
| `app/services/backend_runtime_integration_readiness.py` | 58 | audit_append_call | `targets.append(` |
| `app/services/backend_runtime_integration_readiness.py` | 131 | audit_append_call | `results.append(await _run_audit_dry_run(target))` |
| `app/services/backend_runtime_integration_readiness.py` | 133 | audit_append_call | `results.append(_run_consent_dry_run(target))` |
| `app/services/backend_runtime_integration_readiness.py` | 135 | audit_append_call | `results.append(_run_deep_readiness_dry_run(target))` |
| `app/services/backend_runtime_integration_readiness.py` | 137 | audit_append_call | `results.append(` |
| `app/services/backend_runtime_wiring_cases.py` | 55 | audit_append_call | `results.append(` |
| `app/services/backend_runtime_wiring_cases.py` | 80 | audit_append_call | `results.append(` |
| `app/services/backend_runtime_wiring_cases.py` | 97 | audit_append_call | `results.append(` |
| `app/services/backend_runtime_wiring_cases.py` | 112 | audit_append_call | `results.append(` |
| `app/services/consent_runtime_compatibility.py` | 94 | audit_append_call | `required.append(name)` |
| `app/services/consent_service.py` | 24 | audit_repository | `from app.repositories.audit_repository import AuditRepository` |
| `app/services/consent_service.py` | 32 | audit_repository | `audit_repo: AuditRepository,` |
| `app/services/consent_service.py` | 48 | audit_log_identifier | `# audit_log` |
| `app/services/consent_service.py` | 66 | audit_record_call | `await self._audit.record(` |
| `app/services/consent_service.py` | 102 | audit_record_call | `await self._audit.record(` |
| `app/services/consent_service.py` | 122 | audit_record_call | `await self._audit.record(` |
| `app/services/consent_service.py` | 143 | audit_record_call | `await self._audit.record(` |
| `app/services/consent_service.py` | 162 | audit_record_call | `await self._audit.record(` |
| `app/services/consent_service.py` | 202 | audit_record_call | `await self._audit.record(` |
| `app/services/consent_service.py` | 211 | audit_append_call | `flagged.append(saved)` |
| `app/services/content_blueprint_validation.py` | 18 | audit_append_call | `errors.append("Blueprint requires content_json or blueprint_json.")` |
| `app/services/content_blueprint_validation.py` | 21 | audit_append_call | `errors.append("Blueprint may reference only approved diagnostic items: " + ", ".join(sorted(missing)))` |
| `app/services/content_bulk_review.py` | 60 | audit_append_call | `approved.append(transition.artifact_id)` |
| `app/services/content_bulk_review.py` | 71 | audit_append_call | `rejected.append((await self.lifecycle_service.reject_artifact(session, uuid.UUID(str(artifact_id)), reviewer_id, reason)).artifact_id)` |
| `app/services/content_bulk_review.py` | 79 | audit_append_call | `quarantined.append((await self.lifecycle_service.quarantine_artifact(session, uuid.UUID(str(artifact_id)), reviewer_id, reason)).artifact_id)` |
| `app/services/content_factory.py` | 79 | audit_append_call | `errors.append(f"{label}.source_document_id is required.")` |
| `app/services/content_factory.py` | 81 | audit_append_call | `errors.append(f"{label}.source_chunk_id is required.")` |
| `app/services/content_factory.py` | 85 | audit_append_call | `errors.append(` |
| `app/services/content_factory.py` | 91 | audit_append_call | `errors.append(f"{label} has incompatible license_status {license_status}.")` |
| `app/services/content_factory.py` | 95 | audit_append_call | `errors.append(f"{label}.caps_ref {mapping_caps_ref} does not match artifact caps_ref {caps_ref}.")` |
| `app/services/content_factory.py` | 99 | audit_append_call | `errors.append(f"{label}.chunk_quality_score must be at least 0.5.")` |
| `app/services/content_factory.py` | 103 | audit_append_call | `snapshot_inputs.append(` |
| `app/services/content_factory.py` | 113 | audit_append_call | `errors.append(f"Artifact requires at least {min_sources} cited ETL source(s).")` |
| `app/services/content_factory.py` | 138 | audit_append_call | `errors.append("artifact_json must not be empty.")` |
| `app/services/content_factory.py` | 142 | audit_append_call | `errors.append("diagnostic_item artifacts require answer_key.")` |
| `app/services/content_factory.py` | 155 | audit_append_call | `errors.append(f"safety_status must be passed/safe/approved; got {safety_status}.")` |
| `app/services/content_file_artifact_import.py` | 164 | audit_append_call | `errors.append(f"{path_key} path is missing from scope registry.")` |
| `app/services/content_file_artifact_import.py` | 168 | audit_append_call | `errors.append(f"{path_key} file is missing: {rel_path}")` |
| `app/services/content_file_artifact_import.py` | 177 | audit_append_call | `records.append(` |
| `app/services/content_file_artifact_import.py` | 376 | audit_append_call | `layer_ids.setdefault(record.layer, []).append(str(record.artifact_id))` |
| `app/services/content_file_lesson_quality.py` | 87 | audit_append_call | `blockers.append(` |
| `app/services/content_file_promotion_readiness.py` | 76 | audit_append_call | `blockers.append("Scope source material is not generation-ready.")` |
| `app/services/content_file_promotion_readiness.py` | 83 | audit_append_call | `blockers.append(f"Missing {layer} artifact file: {configured or 'not configured'}.")` |
| `app/services/content_file_promotion_readiness.py` | 85 | audit_append_call | `blockers.append(f"{layer} artifact file contains no records.")` |
| `app/services/content_file_promotion_readiness.py` | 93 | audit_append_call | `blockers.append("Scope is still review; activate scope intentionally before learner visibility.")` |
| `app/services/content_file_promotion_readiness.py` | 96 | audit_append_call | `blockers.append("Scope is still in review and requires dev_approved or educator approval before staging unlock.")` |
| `app/services/content_file_promotion_readiness.py` | 100 | audit_append_call | `blockers.append(f"Scope status {scope.status.value} is not production-promotable.")` |
| `app/services/content_file_promotion_readiness.py` | 249 | audit_append_call | `refs.append(topic["caps_ref"])` |
| `app/services/content_file_review_workflow.py` | 131 | audit_append_call | `stage_blockers.append("Review decision is not dev_approved or approved.")` |
| `app/services/content_file_review_workflow.py` | 133 | audit_append_call | `stage_blockers.append("Reviewer ID is pending.")` |
| `app/services/content_file_review_workflow.py` | 135 | audit_append_call | `stage_blockers.append("Review evidence_url is pending.")` |
| `app/services/content_file_review_workflow.py` | 137 | audit_append_call | `stage_blockers.append("Review approved_at timestamp is pending.")` |
| `app/services/content_file_review_workflow.py` | 139 | audit_append_call | `stage_blockers.append("Review packet scope_id does not match request.")` |
| `app/services/content_file_review_workflow.py` | 142 | audit_append_call | `production_blockers.append("Educator approval is required for production.")` |
| `app/services/content_file_review_workflow.py` | 144 | audit_append_call | `production_blockers.append("Legal approval is required for production.")` |
| `app/services/content_file_review_workflow.py` | 146 | audit_append_call | `production_blockers.append("Educator approval evidence_url is pending.")` |
| `app/services/content_file_review_workflow.py` | 148 | audit_append_call | `production_blockers.append("Legal approval evidence_url is pending.")` |
| `app/services/content_file_review_workflow.py` | 152 | audit_append_call | `stage_blockers.append(f"{layer} review packet has no records.")` |
| `app/services/content_file_review_workflow.py` | 154 | audit_append_call | `stage_blockers.append(f"{layer} review packet is missing artifact hash.")` |
| `app/services/content_generation/blueprint_generator.py` | 132 | audit_append_call | `errors.append("Missing caps_ref")` |
| `app/services/content_generation/blueprint_generator.py` | 134 | audit_append_call | `errors.append(f"caps_ref mismatch: expected {caps_ref}, got {payload.get('caps_ref')}")` |
| `app/services/content_generation/blueprint_generator.py` | 137 | audit_append_call | `errors.append("Missing assessment_type")` |
| `app/services/content_generation/blueprint_generator.py` | 140 | audit_append_call | `errors.append("Missing question_mix")` |
| `app/services/content_generation/diagnostic_generator.py` | 11 | audit_append_call | `errors.append("diagnostic item requires an answer key.")` |
| `app/services/content_generation/diagnostic_generator.py` | 14 | audit_append_call | `errors.append("diagnostic item requires at least two options.")` |
| `app/services/content_generation/diagnostic_generator.py` | 16 | audit_append_call | `errors.append("diagnostic item requires exactly one correct answer.")` |
| `app/services/content_generation/diagnostic_generator.py` | 18 | audit_append_call | `errors.append("diagnostic item requires an explanation.")` |
| `app/services/content_generation/diagnostic_generator.py` | 20 | audit_append_call | `errors.append(f"diagnostic item caps_ref {item.caps_ref} does not match task caps_ref {caps_ref}.")` |
| `app/services/content_generation/diagnostic_generator.py` | 22 | audit_append_call | `errors.append("diagnostic item requires source citations.")` |
| `app/services/content_generation/diagnostic_generator.py` | 24 | audit_append_call | `errors.append("diagnostic item duplicates an existing artifact hash.")` |
| `app/services/content_generation/generated_item_contract.py` | 45 | audit_append_call | `issues.append(GeneratedItemQualityIssue(item_id=item_id, caps_ref=caps_ref, field=field, reason=reason))` |
| `app/services/content_generation/generated_item_contract.py` | 93 | audit_append_call | `issues.append(` |
| `app/services/content_generation/generated_lesson_contract.py` | 129 | audit_append_call | `issues.append(GeneratedLessonQualityIssue(lesson_id=lesson_id, caps_ref=caps_ref, field=field, reason=reason))` |
| `app/services/content_generation/lesson_generator.py` | 18 | audit_append_call | `errors.append("lesson requires learning objectives.")` |
| `app/services/content_generation/lesson_generator.py` | 20 | audit_append_call | `errors.append("lesson requires an answer key for practice questions.")` |
| `app/services/content_generation/lesson_generator.py` | 22 | audit_append_call | `errors.append(f"lesson caps_ref {lesson.caps_ref} does not match task caps_ref {caps_ref}.")` |
| `app/services/content_generation/lesson_generator.py` | 24 | audit_append_call | `errors.append("lesson requires source citations.")` |
| `app/services/content_generation/lesson_generator.py` | 26 | audit_append_call | `errors.append("lesson grade must be age appropriate.")` |
| `app/services/content_generation/lesson_generator.py` | 28 | audit_append_call | `errors.append("lesson duplicates an existing artifact hash.")` |
| `app/services/content_generation/scope_lesson_generator.py` | 319 | audit_append_call | `questions.append(` |
| `app/services/content_generation/scope_lesson_generator.py` | 388 | audit_append_call | `citations.append(` |
| `app/services/content_generation/scope_study_plan_generator.py` | 41 | audit_append_call | `topic_sequence.append(` |
| `app/services/content_generation/scope_study_plan_generator.py` | 55 | audit_append_call | `remediation_mappings.append(` |
| `app/services/content_generation/scope_study_plan_generator.py` | 66 | audit_append_call | `extension_mappings.append(` |
| `app/services/content_generation/scope_study_plan_generator.py` | 117 | audit_append_call | `template.append(` |
| `app/services/content_generation/source_context.py` | 53 | audit_append_call | `errors.append(f"source {getattr(source, 'source_document_id', 'unknown')} has status {document_status}.")` |
| `app/services/content_generation/source_context.py` | 56 | audit_append_call | `errors.append(f"source {getattr(source, 'source_document_id', 'unknown')} is not eligible for generation.")` |
| `app/services/content_generation/source_context.py` | 59 | audit_append_call | `errors.append(f"source {getattr(source, 'source_document_id', 'unknown')} has incompatible license {license_status}.")` |
| `app/services/content_generation/source_context.py` | 62 | audit_append_call | `errors.append(f"source {getattr(source, 'source_document_id', 'unknown')} quality is below threshold.")` |
| `app/services/content_generation/source_context.py` | 65 | audit_append_call | `errors.append(f"source {getattr(source, 'source_document_id', 'unknown')} has no chunk id.")` |
| `app/services/content_generation/source_context.py` | 67 | audit_append_call | `chunks.append(` |
| `app/services/content_generation/source_context.py` | 81 | audit_append_call | `errors.append("No approved/indexed/training_ready ETL source chunks are available.")` |
| `app/services/content_generation/study_plan_template_generator.py` | 132 | audit_append_call | `errors.append("Missing caps_ref")` |
| `app/services/content_generation/study_plan_template_generator.py` | 134 | audit_append_call | `errors.append(f"caps_ref mismatch: expected {caps_ref}, got {payload.get('caps_ref')}")` |
| `app/services/content_generation/study_plan_template_generator.py` | 137 | audit_append_call | `errors.append("Missing diagnostic_trigger_conditions")` |
| `app/services/content_generation/study_plan_template_generator.py` | 140 | audit_append_call | `errors.append("Missing estimated_minutes")` |
| `app/services/content_generation/topic_map_source_context.py` | 93 | audit_append_call | `errors.append(f"{caps_ref}: topic map context lacks assessment standards.")` |
| `app/services/content_generation/topic_map_source_context.py` | 97 | audit_append_call | `errors.append(f"{caps_ref}: scope/topic map lacks source document ids.")` |
| `app/services/content_generation/topic_map_source_context.py` | 101 | audit_append_call | `errors.append(f"{caps_ref}: no source text snippets available for lesson generation.")` |
| `app/services/content_generation/topic_map_source_context.py` | 103 | audit_append_call | `errors.append(f"{caps_ref}: source context is too thin for grounded generation.")` |
| `app/services/content_generation/topic_map_source_context.py` | 177 | audit_append_call | `snippets.append(paragraph.strip())` |
| `app/services/content_generation/topic_map_source_context.py` | 214 | audit_append_call | `words.append(cleaned)` |
| `app/services/content_generation_executor.py` | 141 | audit_append_call | `errors.append("Artifact creation failed because a matching artifact hash already exists.")` |
| `app/services/content_generation_executor.py` | 158 | audit_append_call | `artifact_ids.append(artifact.artifact_id)` |
| `app/services/content_generation_planner.py` | 75 | audit_append_call | `skipped.append({"scope_id": scope.scope_id, "caps_ref": layer.caps_ref, "layer": layer.layer, "reason": "coverage_green"})` |
| `app/services/content_generation_planner.py` | 79 | audit_append_call | `skipped.append({"scope_id": scope.scope_id, "caps_ref": layer.caps_ref, "layer": layer.layer, "reason": "missing_source_context", "errors": context.errors})` |
| `app/services/content_generation_planner.py` | 86 | audit_append_call | `skipped.append({"scope_id": scope.scope_id, "caps_ref": layer.caps_ref, "layer": layer.layer, "reason": "duplicate_task"})` |
| `app/services/content_generation_planner.py` | 113 | audit_append_call | `created.append(task.task_id)` |
| `app/services/content_generation_planner.py` | 114 | audit_append_call | `missing_rows.append({"scope_id": scope.scope_id, "caps_ref": layer.caps_ref, "layer": layer.layer, "missing_count": task_missing})` |
| `app/services/content_generation_runs.py` | 69 | audit_append_call | `tasks.append(task)` |
| `app/services/content_generation_runs.py` | 129 | audit_append_call | `retry_tasks.append(retry)` |
| `app/services/content_learner_read_service.py` | 189 | audit_append_call | `items.append(` |
| `app/services/content_learner_read_service.py` | 267 | audit_append_call | `items.append(` |
| `app/services/content_production_promotion_executor.py` | 190 | audit_append_call | `errors.append(f"Failed to promote artifact {staging_artifact.artifact_id}: {str(e)}")` |
| `app/services/content_production_promotion_executor.py` | 284 | audit_append_call | `items.append(` |
| `app/services/content_production_promotion_gate.py` | 145 | audit_append_call | `blockers.append(` |
| `app/services/content_production_promotion_gate.py` | 183 | audit_append_call | `blockers.append(` |
| `app/services/content_production_promotion_gate.py` | 201 | audit_append_call | `blockers.append(` |
| `app/services/content_production_promotion_gate.py` | 212 | audit_append_call | `blockers.append(` |
| `app/services/content_production_promotion_gate.py` | 250 | audit_append_call | `blockers.append(` |
| `app/services/content_production_promotion_gate.py` | 267 | audit_append_call | `blockers.append(` |
| `app/services/content_production_promotion_gate.py` | 284 | audit_append_call | `blockers.append(` |
| `app/services/content_production_promotion_gate.py` | 303 | audit_append_call | `blockers.append(` |
| `app/services/content_production_promotion_gate.py` | 314 | audit_append_call | `blockers.append(` |
| `app/services/content_production_read_verification.py` | 75 | audit_append_call | `errors.append(` |
| `app/services/content_production_read_verification.py` | 89 | audit_append_call | `errors.append(f"Source artifact {prod_artifact.artifact_id} not found")` |
| `app/services/content_production_read_verification.py` | 93 | audit_append_call | `errors.append(` |
| `app/services/content_production_read_verification.py` | 138 | audit_append_call | `errors.append(f"Source artifact {prod_artifact.artifact_id} not found")` |
| `app/services/content_production_read_verification.py` | 142 | audit_append_call | `errors.append(` |
| `app/services/content_review_queue.py` | 101 | audit_append_call | `items.append(self._queue_item(artifact, risk, validation.get(artifact.artifact_id), provenance, assignment))` |
| `app/services/content_review_risk.py` | 32 | audit_append_call | `reasons.append("invalid_provenance")` |
| `app/services/content_review_risk.py` | 35 | audit_append_call | `reasons.append("missing_provenance")` |
| `app/services/content_review_risk.py` | 40 | audit_append_call | `reasons.append("missing_sources")` |
| `app/services/content_review_risk.py` | 45 | audit_append_call | `reasons.append("low_source_quality")` |
| `app/services/content_review_risk.py` | 51 | audit_append_call | `reasons.append("validation_failed")` |
| `app/services/content_review_risk.py` | 55 | audit_append_call | `reasons.append("validation_warnings")` |
| `app/services/content_review_risk.py` | 60 | audit_append_call | `reasons.append("non_deterministic_provider")` |
| `app/services/content_review_risk.py` | 65 | audit_append_call | `reasons.append("high_difficulty")` |
| `app/services/content_review_risk.py` | 70 | audit_append_call | `reasons.append("low_confidence_answer_key")` |
| `app/services/content_review_risk.py` | 74 | audit_append_call | `reasons.append("duplicate_similarity")` |
| `app/services/content_review_risk.py` | 78 | audit_append_call | `reasons.append("new_caps_ref")` |
| `app/services/content_review_risk.py` | 84 | audit_append_call | `reasons.append("stale_source_document")` |
| `app/services/content_reviewer_assignment.py` | 71 | audit_append_call | `assignments.append(await self.assign_artifact(session, artifact_id, reviewer_id, assigned_by, priority=priority))` |
| `app/services/content_safety/lesson_contracts.py` | 99 | audit_append_call | `reasons.append("topic missing")` |
| `app/services/content_safety/lesson_contracts.py` | 101 | audit_append_call | `reasons.append("CAPS alignment invalid")` |
| `app/services/content_safety/lesson_contracts.py` | 103 | audit_append_call | `reasons.append("unsafe content")` |
| `app/services/content_safety/lesson_contracts.py` | 113 | audit_append_call | `reasons.append("PII detected")` |
| `app/services/content_safety/lesson_contracts.py` | 115 | audit_append_call | `reasons.append("explanation missing")` |
| `app/services/content_safety/lesson_contracts.py` | 117 | audit_append_call | `reasons.append("answer key missing or inconsistent")` |
| `app/services/content_safety/lesson_contracts.py` | 119 | audit_append_call | `reasons.append("low alignment confidence")` |
| `app/services/content_safety/lesson_contracts.py` | 121 | audit_append_call | `reasons.append("low quality score")` |
| `app/services/content_seed_promotion.py` | 131 | audit_append_call | `errors.append(f"{caps_ref.caps_ref}:{item.value} coverage is {counts.status.value}.")` |
| `app/services/content_staging_preview_service.py` | 130 | audit_append_call | `artifacts.append(` |
| `app/services/content_staging_preview_service.py` | 219 | audit_append_call | `artifacts.append(` |
| `app/services/content_staging_read_verification.py` | 54 | audit_append_call | `errors.append(f"Missing staging record for seeded artifact {item.artifact_id}")` |
| `app/services/content_staging_read_verification.py` | 57 | audit_append_call | `errors.append(f"Multiple staging records for seeded artifact {item.artifact_id}")` |
| `app/services/content_staging_read_verification.py` | 61 | audit_append_call | `errors.append(f"Staging record for {item.artifact_id} is not active ({artifact.staging_status})")` |
| `app/services/content_staging_read_verification.py` | 63 | audit_append_call | `errors.append(f"Staging record for {item.artifact_id} has mismatched scope {artifact.scope_id}")` |
| `app/services/content_staging_read_verification.py` | 65 | audit_append_call | `errors.append(f"Staging record for {item.artifact_id} has mismatched caps_ref {artifact.caps_ref}")` |
| `app/services/content_staging_read_verification.py` | 67 | audit_append_call | `errors.append(f"Staging record for {item.artifact_id} has mismatched layer {artifact.layer}")` |
| `app/services/content_staging_read_verification.py` | 72 | audit_append_call | `errors.append(f"Source artifact {item.artifact_id} deleted")` |
| `app/services/content_staging_read_verification.py` | 77 | audit_append_call | `errors.append(f"Source artifact {item.artifact_id} status invalid for staging: {source_status}")` |
| `app/services/content_staging_read_verification.py` | 89 | audit_append_call | `errors.append(f"Seeded item count {len(seeded_items)} does not match active staging count {active_count}")` |
| `app/services/content_staging_read_verification.py` | 107 | audit_append_call | `errors.append(f"Staged artifact {artifact.artifact_id} source missing")` |
| `app/services/content_staging_read_verification.py` | 113 | audit_append_call | `errors.append(f"Artifact {artifact.artifact_id} is in staging but status is {source_status}")` |
| `app/services/content_staging_readiness.py` | 160 | audit_append_call | `layers.append(LayerReadinessSummary(layer=layer_name, caps_ref=target.caps_ref, target=int(required), status=StagingReadinessStatus.NOT_CONFIGURED))` |
| `app/services/content_staging_readiness.py` | 168 | audit_append_call | `layers.append(summary)` |
| `app/services/content_staging_readiness.py` | 172 | audit_append_call | `blockers.append(ScopeBlocker(code="missing_targets", severity=BlockerSeverity.BLOCKING, message="Scope has no configured coverage targets."))` |
| `app/services/content_staging_readiness.py` | 252 | audit_append_call | `scopes.append(` |
| `app/services/content_staging_readiness.py` | 284 | audit_append_call | `index[source.artifact_id].append(source)` |
| `app/services/content_staging_readiness.py` | 352 | audit_append_call | `blockers.append(ScopeBlocker(code="target_not_configured", severity=BlockerSeverity.WARNING, **common))` |
| `app/services/content_staging_readiness.py` | 359 | audit_append_call | `blockers.append(ScopeBlocker(code=code, severity=BlockerSeverity.BLOCKING, **common))` |
| `app/services/content_staging_readiness.py` | 361 | audit_append_call | `blockers.append(ScopeBlocker(code="invalid_provenance", severity=BlockerSeverity.BLOCKING, **common))` |
| `app/services/content_staging_readiness.py` | 363 | audit_append_call | `blockers.append(ScopeBlocker(code="invalid_license", severity=BlockerSeverity.BLOCKING, **common))` |
| `app/services/content_staging_readiness.py` | 365 | audit_append_call | `blockers.append(ScopeBlocker(code="low_source_quality", severity=BlockerSeverity.BLOCKING, **common))` |
| `app/services/content_staging_seed_executor.py` | 293 | audit_append_call | `errors.append(f"Constraint violation for artifact {artifact.artifact_id}: {item_integrity_err}")` |
| `app/services/content_staging_seed_executor.py` | 362 | audit_append_call | `items.append(StagingSeedRunResult(` |
| `app/services/content_staging_seed_executor.py` | 451 | audit_append_call | `skipped.append(SkippedArtifact(artifact.artifact_id, "Artifact is pending review"))` |
| `app/services/content_staging_seed_executor.py` | 455 | audit_append_call | `skipped.append(SkippedArtifact(artifact.artifact_id, "Artifact is rejected"))` |
| `app/services/content_staging_seed_executor.py` | 459 | audit_append_call | `skipped.append(SkippedArtifact(artifact.artifact_id, "Artifact is quarantined"))` |
| `app/services/content_staging_seed_executor.py` | 463 | audit_append_call | `skipped.append(SkippedArtifact(artifact.artifact_id, "Artifact validation failed"))` |
| `app/services/content_staging_seed_executor.py` | 467 | audit_append_call | `skipped.append(SkippedArtifact(artifact.artifact_id, f"Artifact status {status_val} is not seedable"))` |
| `app/services/content_staging_seed_executor.py` | 473 | audit_append_call | `skipped.append(SkippedArtifact(artifact.artifact_id, "Invalid provenance"))` |
| `app/services/content_staging_seed_executor.py` | 480 | audit_append_call | `skipped.append(SkippedArtifact(artifact.artifact_id, "Latest validation report missing"))` |
| `app/services/content_staging_seed_executor.py` | 483 | audit_append_call | `skipped.append(SkippedArtifact(artifact.artifact_id, "Latest validation failed"))` |
| `app/services/content_staging_seed_executor.py` | 486 | audit_append_call | `seedable.append(SeedableArtifact(` |
| `app/services/content_template_validation.py` | 18 | audit_append_call | `errors.append("Study plan template requires content_json or template_json.")` |
| `app/services/content_template_validation.py` | 21 | audit_append_call | `errors.append("Study templates may reference only approved lessons or blueprints: " + ", ".join(sorted(missing)))` |
| `app/services/curriculum/coverage.py` | 34 | audit_append_call | `gaps.append(` |
| `app/services/data_subject_rights_service.py` | 39 | audit_repository | `from app.repositories.audit_repository import AuditRepository` |
| `app/services/data_subject_rights_service.py` | 46 | audit_repository | `audit_repo: AuditRepository,` |
| `app/services/data_subject_rights_service.py` | 75 | audit_record_call | `await self._audit.record(` |
| `app/services/data_subject_rights_service.py` | 120 | audit_record_call | `await self._audit.record(` |
| `app/services/data_subject_rights_service.py` | 152 | audit_record_call | `await self._audit.record(` |
| `app/services/data_subject_rights_service.py` | 194 | audit_events_table | `Deletes learner PII but PRESERVES audit_events rows (anonymised).` |
| `app/services/data_subject_rights_service.py` | 213 | audit_events_table | `UPDATE audit_events` |
| `app/services/data_subject_rights_service.py` | 242 | audit_record_call | `await self._audit.record(` |
| `app/services/deep_readiness_runtime.py` | 30 | audit_append_call | `checks.append(DeepReadinessCheckResult("database_connectivity","pass","read-only connectivity check completed"))` |
| `app/services/deep_readiness_runtime.py` | 32 | audit_append_call | `checks.append(DeepReadinessCheckResult("database_connectivity","fail",f"{type(exc).__name__}: {exc}"))` |
| `app/services/deep_readiness_runtime.py` | 35 | audit_append_call | `checks.append(DeepReadinessCheckResult("alembic_revision","pass","read-only Alembic revision query completed"))` |
| `app/services/deep_readiness_runtime.py` | 37 | audit_append_call | `checks.append(DeepReadinessCheckResult("alembic_revision","warn",f"{type(exc).__name__}: {exc}"))` |
| `app/services/deep_readiness_runtime.py` | 41 | audit_append_call | `checks.append(DeepReadinessCheckResult(f"table:{table}","pass","read-only table presence query completed"))` |
| `app/services/deep_readiness_runtime.py` | 43 | audit_append_call | `checks.append(DeepReadinessCheckResult(f"table:{table}","warn",f"{type(exc).__name__}: {exc}"))` |
| `app/services/deep_readiness_runtime.py` | 49 | audit_append_call | `checks.append(DeepReadinessCheckResult("cache_ping","pass","cache ping completed"))` |
| `app/services/diagnostic_data_integrity.py` | 39 | audit_append_call | `found.append(item)` |
| `app/services/diagnostic_data_integrity.py` | 47 | audit_append_call | `found.append(item)` |
| `app/services/diagnostic_data_integrity.py` | 77 | audit_append_call | `duplicates.append(item_id)` |
| `app/services/diagnostic_safety.py` | 30 | audit_append_call | `reasons.append(caps.reason)` |
| `app/services/diagnostic_safety.py` | 32 | audit_append_call | `reasons.append("difficulty must be finite and between -4 and 4")` |
| `app/services/diagnostic_safety.py` | 34 | audit_append_call | `reasons.append("discrimination must be finite and between 0 and 4")` |
| `app/services/diagnostic_safety.py` | 36 | audit_append_call | `reasons.append("distractors must be mutually distinct")` |
| `app/services/diagnostic_safety.py` | 38 | audit_append_call | `reasons.append("approved items require an explanation")` |
| `app/services/etl/etl_pipeline.py` | 497 | audit_append_call | `raw_parts.append(text)` |
| `app/services/etl/etl_pipeline.py` | 507 | audit_append_call | `pages.append({"page_num": pnum, "text": text, "headings": page_headings})` |
| `app/services/etl/etl_pipeline.py` | 525 | audit_append_call | `headings.append(para.text)` |
| `app/services/etl/etl_pipeline.py` | 526 | audit_append_call | `paras.append(para.text)` |
| `app/services/etl/etl_pipeline.py` | 532 | audit_append_call | `tables.append({"headers": rows[0], "rows": rows[1:]})` |
| `app/services/etl/etl_pipeline.py` | 533 | audit_append_call | `pages.append({"page_num": 1, "text": raw_text, "headings": headings})` |
| `app/services/etl/etl_pipeline.py` | 743 | audit_append_call | `chunks.append(DocumentChunk(` |
| `app/services/etl/etl_pipeline.py` | 770 | audit_append_call | `chunks.append(DocumentChunk(` |
| `app/services/etl/etl_pipeline.py` | 787 | audit_append_call | `positions.append((len(text), 0, ""))   # sentinel` |
| `app/services/etl/etl_pipeline.py` | 798 | audit_append_call | `chunks.append(DocumentChunk(` |
| `app/services/etl/etl_pipeline.py` | 823 | audit_append_call | `chunks.append(DocumentChunk(` |
| `app/services/etl/etl_pipeline.py` | 842 | audit_append_call | `chunks.append(DocumentChunk(` |
| `app/services/etl/etl_pipeline.py` | 852 | audit_append_call | `buf.append(para); buf_tokens += t` |
| `app/services/etl/etl_pipeline.py` | 854 | audit_append_call | `chunks.append(DocumentChunk(` |
| `app/services/etl/etl_pipeline.py` | 873 | audit_append_call | `buf.append(word); chars += len(word) + 1` |
| `app/services/etl/etl_pipeline.py` | 875 | audit_append_call | `results.append(" ".join(buf)); buf=[]; chars=0` |
| `app/services/etl/etl_pipeline.py` | 876 | audit_append_call | `if buf: results.append(" ".join(buf))` |
| `app/services/etl/etl_pipeline.py` | 901 | audit_append_call | `issues.append(f"Incomplete metadata: {required_present}/{len(self.REQUIRED_METADATA)} required fields")` |
| `app/services/etl/etl_pipeline.py` | 906 | audit_append_call | `issues.append(f"Extraction failed: {extraction.error}")` |
| `app/services/etl/etl_pipeline.py` | 909 | audit_append_call | `issues.append("Very little text extracted — possible scanned PDF or empty document")` |
| `app/services/etl/etl_pipeline.py` | 922 | audit_append_call | `issues.append("No headings detected — document may lack structure")` |
| `app/services/etl/etl_pipeline.py` | 928 | audit_append_call | `issues.append("No chunks produced — document too short or extraction failed")` |
| `app/services/etl/etl_pipeline.py` | 931 | audit_append_call | `issues.append(f"Very few chunks ({chunk_count}) — document may be incomplete")` |
| `app/services/etl/etl_pipeline.py` | 938 | audit_append_call | `issues.append("Duplicate chunks detected")` |
| `app/services/etl/etl_pipeline.py` | 946 | audit_append_call | `issues.append("License status unknown — confirm before AI use")` |
| `app/services/etl/etl_pipeline.py` | 954 | audit_append_call | `issues.append("License not cleared for training use")` |
| `app/services/etl/etl_pipeline.py` | 1262 | audit_append_call | `if status:        clauses.append("processing_status=?"); params.append(status)` |
| `app/services/etl/etl_pipeline.py` | 1263 | audit_append_call | `if grade:         clauses.append("grade=?");             params.append(grade)` |
| `app/services/etl/etl_pipeline.py` | 1264 | audit_append_call | `if subject:       clauses.append("subject=?");           params.append(subject)` |
| `app/services/etl/etl_pipeline.py` | 1265 | audit_append_call | `if document_type: clauses.append("document_type=?");     params.append(document_type)` |
| `app/services/etl/etl_pipeline_v2.py` | 499 | audit_append_call | `params.append(grade)` |
| `app/services/etl/etl_pipeline_v2.py` | 502 | audit_append_call | `params.append(subject)` |
| `app/services/etl/etl_pipeline_v2.py` | 505 | audit_append_call | `params.append(document_type)` |
| `app/services/etl/etl_pipeline_v2.py` | 525 | audit_append_call | `params.append(grade)` |
| `app/services/etl/etl_pipeline_v2.py` | 528 | audit_append_call | `params.append(subject)` |
| `app/services/etl/etl_pipeline_v2.py` | 531 | audit_append_call | `params.append(document_type)` |
| `app/services/etl/etl_pipeline_v2.py` | 547 | audit_append_call | `results.append(row)` |
| `app/services/etl/etl_pipeline_v2.py` | 625 | audit_append_call | `scored.append({"score": score, **dict(r)})` |
| `app/services/etl/etl_pipeline_v2.py` | 729 | audit_append_call | `examples.append(ex)` |
| `app/services/etl/etl_pipeline_v2.py` | 1054 | audit_append_call | `alerts.append(f"HIGH job failure rate: {jobs['failure_rate']*100:.0f}% in last 24h.")` |
| `app/services/etl/etl_pipeline_v2.py` | 1056 | audit_append_call | `alerts.append(f"{stats['pending_reviews']} documents pending human review.")` |
| `app/services/etl/etl_pipeline_v2.py` | 1058 | audit_append_call | `alerts.append(f"{len(stale)} documents have been stale for >90 days.")` |
| `app/services/etl/etl_pipeline_v2.py` | 1060 | audit_append_call | `alerts.append(f"Low approval rate: {approval_rate*100:.0f}% in last 30 days.")` |
| `app/services/etl/etl_pipeline_v2.py` | 1062 | audit_append_call | `alerts.append(f"{feedback['incorrect_answer']} 'incorrect_answer' reports in last 30 days.")` |
| `app/services/etl/etl_pipeline_v2.py` | 1095 | audit_append_call | `missing.append({"grade": g, "subject": s, "document_type": t})` |
| `app/services/etl/etl_pipeline_v3_additions.py` | 291 | audit_append_call | `set_clauses.append(f"{col}=?")` |
| `app/services/etl/etl_pipeline_v3_additions.py` | 292 | audit_append_call | `params.append(new_val)` |
| `app/services/etl/etl_pipeline_v3_additions.py` | 293 | audit_append_call | `changes.append((col, str(old_doc[col]), str(new_val)))` |
| `app/services/etl/etl_pipeline_v3_additions.py` | 298 | audit_append_call | `set_clauses.append("updated_at=?")` |
| `app/services/etl/etl_pipeline_v3_additions.py` | 342 | audit_append_call | `results.append({"document_id": doc_id, "success": True})` |
| `app/services/etl/etl_pipeline_v3_additions.py` | 345 | audit_append_call | `results.append({"document_id": doc_id, "success": False, "error": str(e)})` |
| `app/services/etl/etl_pipeline_v3_additions.py` | 507 | audit_append_call | `overlapping.append(r["example_id"])` |
| `app/services/first_audit_runtime_wiring.py` | 60 | audit_append_call | `self.events.append(kwargs)` |
| `app/services/first_audit_runtime_wiring.py` | 132 | audit_record_call | `response = await adapter.record(` |
| `app/services/first_deep_readiness_runtime_wiring.py` | 85 | audit_append_call | `selected_checks.append(name)` |
| `app/services/job_dependency_factory.py` | 56 | audit_repository | `audit_repo_cls = _import_symbol("app.repositories.audit_repository.AuditRepository") or _import_symbol("app.repositories.repositories.AuditRepository")` |
| `app/services/jwt_keyring.py` | 167 | audit_append_call | `keys.append(JWTKey(kid=kid, secret=secret, algorithm=algorithm, status=status))` |
| `app/services/lesson_authorization.py` | 185 | audit_append_call | `found.append(item)` |
| `app/services/lesson_authorization.py` | 198 | audit_append_call | `found.append(item)` |
| `app/services/lesson_context_builder.py` | 216 | audit_append_call | `parts.append(f"({subtopic})")` |
| `app/services/lesson_context_builder.py` | 220 | audit_append_call | `parts.append(f"with emphasis on correcting: {tags_str}")` |
| `app/services/lesson_context_builder.py` | 230 | audit_append_call | `parts.append(severity_hints.get(severity, ""))` |
| `app/services/llm/gateway.py` | 147 | audit_append_call | `providers.append((self.development_fallback, "development_fallback"))` |
| `app/services/llm/gateway.py` | 154 | audit_append_call | `failures.append(f"{provider.provider_name}:{health.reason}")` |
| `app/services/llm/gateway.py` | 186 | audit_append_call | `failures.append(f"{provider.provider_name}:{exc}")` |
| `app/services/llm/json_completion.py` | 58 | audit_append_call | `errors.append(f"google: {exc}")` |
| `app/services/llm/json_completion.py` | 63 | audit_append_call | `errors.append(f"groq: {exc}")` |
| `app/services/llm/json_completion.py` | 68 | audit_append_call | `errors.append(f"anthropic: {exc}")` |
| `app/services/pii_sweep.py` | 105 | audit_append_call | `self.findings.append(finding)` |
| `app/services/pii_sweep.py` | 250 | audit_append_call | `all_findings.append({` |
| `app/services/popia_consent_lifecycle_adapter.py` | 169 | audit_append_call | `missing.append(method_name)` |
| `app/services/popia_consent_lifecycle_adapter.py` | 190 | audit_append_call | `positional.append(_value(kwargs, "guardian_id", "parent_id", "actor_id"))` |
| `app/services/popia_consent_lifecycle_adapter.py` | 192 | audit_append_call | `positional.append(kwargs.get("learner_id"))` |
| `app/services/popia_consent_lifecycle_adapter.py` | 194 | audit_append_call | `positional.append(_value(kwargs, "consent_version", "privacy_notice_version"))` |
| `app/services/popia_consent_lifecycle_adapter.py` | 196 | audit_append_call | `positional.append(_value(kwargs, "actor_id", "guardian_id"))` |
| `app/services/popia_service.py` | 36 | audit_repository | `from app.repositories.audit_repository import AuditRepository` |
| `app/services/popia_service.py` | 82 | audit_repository | `self.audit = AuditRepository(db)` |
| `app/services/popia_service.py` | 111 | audit_append_call | `await self.audit.append(` |
| `app/services/popia_service.py` | 187 | audit_append_call | `await self.audit.append(` |
| `app/services/popia_service.py` | 244 | audit_append_call | `await self.audit.append(` |
| `app/services/popia_service.py` | 281 | audit_append_call | `await self.audit.append(` |
| `app/services/popia_service.py` | 300 | audit_append_call | `await self.audit.append(` |
| `app/services/popia_service.py` | 390 | audit_append_call | `await self.audit.append(` |
| `app/services/popia_service.py` | 438 | audit_events_table | `audit_events = await self.db.scalar(` |
| `app/services/popia_service.py` | 441 | audit_events_table | `verification["audit_records_preserved"] = audit_events is not None or method == ERASURE_METHOD_PHYSICAL` |
| `app/services/popia_service.py` | 463 | audit_events_table | `audit_events = list((await self.db.scalars(select(AuditEvent).where(AuditEvent.resource_id == learner_id))).all())` |
| `app/services/popia_service.py` | 633 | audit_events_table | `"audit_events": [` |
| `app/services/popia_service.py` | 644 | audit_events_table | `for row in audit_events` |
| `app/services/popia_service.py` | 664 | audit_events_table | `"audit_events",` |
| `app/services/popia_transactional_lifecycle.py` | 60 | audit_append_call | `missing.append(method_name)` |
| `app/services/runtime_audit_facade.py` | 25 | audit_record_call | `await AuditRepositoryCompatAdapter(repository).record(` |
| `app/services/study_plan_service_v2.py` | 106 | audit_append_call | `days.setdefault(slot["day"], []).append({` |
| `scripts/approval_evidence.py` | 170 | audit_append_call | `blockers.append("decision must be approved/accepted/pass")` |
| `scripts/approval_evidence.py` | 172 | audit_append_call | `blockers.append("approver is pending")` |
| `scripts/approval_evidence.py` | 174 | audit_append_call | `blockers.append("evidence URL is pending or invalid")` |
| `scripts/approval_evidence.py` | 176 | audit_append_call | `blockers.append("date verified is pending")` |
| `scripts/approval_evidence.py` | 178 | audit_append_call | `blockers.append("scope is pending")` |
| `scripts/approval_evidence.py` | 287 | audit_append_call | `lines.append(` |
| `scripts/approval_evidence.py` | 296 | audit_append_call | `lines.append("- None")` |
| `scripts/archive/db_migration_phase2.sql` | 205 | audit_events_table | `CREATE TABLE IF NOT EXISTS audit_events (` |
| `scripts/archive/db_migration_phase2.sql` | 219 | audit_events_table | `CREATE INDEX IF NOT EXISTS ix_audit_events_learner ON audit_events(learner_id);` |
| `scripts/archive/db_migration_phase2.sql` | 220 | audit_events_table | `CREATE INDEX IF NOT EXISTS ix_audit_events_occurred ON audit_events(occurred_at);` |
| `scripts/archive/db_migration_phase2.sql` | 221 | audit_events_table | `CREATE INDEX IF NOT EXISTS ix_audit_events_type ON audit_events(event_type);` |
| `scripts/audit_baseline_refresh.py` | 170 | audit_append_call | `values.append(str(value))` |
| `scripts/audit_baseline_refresh.py` | 252 | audit_append_call | `blockers.append(item_id)` |
| `scripts/audit_baseline_refresh.py` | 299 | audit_append_call | `lines.append("- None")` |
| `scripts/audit_baseline_refresh.py` | 359 | audit_append_call | `commands.append(` |
| `scripts/audit_baseline_refresh.py` | 367 | audit_append_call | `commands.append(_refresh_docs_inventory())` |
| `scripts/audit_baseline_refresh.py` | 389 | audit_append_call | `blockers.append(f"command failed: {command.command}")` |
| `scripts/audit_baseline_refresh.py` | 394 | audit_append_call | `blockers.append(f"required status surface missing: {surface.name}")` |
| `scripts/audit_baseline_refresh.py` | 396 | audit_append_call | `blockers.append(` |
| `scripts/audit_baseline_refresh.py` | 401 | audit_append_call | `blockers.append("final gate reports GO while registry still contains beta blockers")` |
| `scripts/audit_baseline_refresh.py` | 444 | audit_append_call | `lines.append(f"\| `{command.command}` \| {command.return_code} \|")` |
| `scripts/audit_baseline_refresh.py` | 457 | audit_append_call | `lines.append(` |
| `scripts/audit_baseline_refresh.py` | 473 | audit_append_call | `lines.append(` |
| `scripts/audit_baseline_refresh.py` | 482 | audit_append_call | `lines.append("- None")` |
| `scripts/audit_baseline_refresh.py` | 488 | audit_append_call | `lines.append("- None")` |
| `scripts/audit_router_thinness.py` | 187 | audit_append_call | `report.violations.append(` |
| `scripts/audit_router_thinness.py` | 198 | audit_append_call | `report.violations.append(` |
| `scripts/audit_router_thinness.py` | 212 | audit_append_call | `report.violations.append(` |
| `scripts/audit_router_thinness.py` | 234 | audit_append_call | `report.violations.append(` |
| `scripts/audit_write_flow.py` | 8 | audit_events_table | `in the payload, and satisfies all audit_events CHECK constraints.` |
| `scripts/audit_write_flow.py` | 93 | audit_events_table | `INSERT INTO public.audit_events` |
| `scripts/audit_write_flow_command.py` | 4 | audit_repository | `Writes one real audit_events row via the app's AuditRepository using psycopg2 (sync)` |
| `scripts/audit_write_flow_command.py` | 4 | audit_events_table | `Writes one real audit_events row via the app's AuditRepository using psycopg2 (sync)` |
| `scripts/audit_write_flow_command.py` | 40 | audit_events_table | `INSERT INTO audit_events (` |
| `scripts/audit_write_runtime_evidence.py` | 27 | audit_events_table | `AUDIT_TABLE = "audit_events"` |
| `scripts/audit_write_runtime_evidence.py` | 129 | audit_append_call | `blockers.append("AUDIT_WRITE_RUN_ID is required for accepted evidence")` |
| `scripts/audit_write_runtime_evidence.py` | 132 | audit_append_call | `blockers.append("AUDIT_WRITE_RUN_ID is not numeric")` |
| `scripts/audit_write_runtime_evidence.py` | 135 | audit_append_call | `blockers.append("GitHub CLI is unavailable or not authenticated")` |
| `scripts/audit_write_runtime_evidence.py` | 140 | audit_append_call | `blockers.append(f"unable to read GitHub Actions run {run_id}")` |
| `scripts/audit_write_runtime_evidence.py` | 150 | audit_append_call | `blockers.append("run URL does not contain numeric run ID")` |
| `scripts/audit_write_runtime_evidence.py` | 152 | audit_append_call | `blockers.append(f"GitHub Actions run status is {run_status or 'missing'}, expected completed")` |
| `scripts/audit_write_runtime_evidence.py` | 154 | audit_append_call | `blockers.append(f"GitHub Actions run conclusion is {conclusion or 'missing'}, expected success")` |
| `scripts/audit_write_runtime_evidence.py` | 156 | audit_append_call | `blockers.append(f"GitHub Actions run SHA {head_sha or 'missing'} does not match current commit {expected_sha}")` |
| `scripts/audit_write_runtime_evidence.py` | 158 | audit_append_call | `blockers.append("workflow name is missing")` |
| `scripts/audit_write_runtime_evidence.py` | 252 | audit_append_call | `blockers.append("AUDIT_WRITE_DATABASE_URL/DATABASE_URL is missing, placeholder, local, or invalid")` |
| `scripts/audit_write_runtime_evidence.py` | 259 | audit_append_call | `blockers.append("audit_events table is missing")` |
| `scripts/audit_write_runtime_evidence.py` | 259 | audit_events_table | `blockers.append("audit_events table is missing")` |
| `scripts/audit_write_runtime_evidence.py` | 265 | audit_append_call | `blockers.append(f"flow command failed with exit code {flow_result.return_code}")` |
| `scripts/audit_write_runtime_evidence.py` | 271 | audit_append_call | `blockers.append("audit_events did not increase and trace ID was not found")` |
| `scripts/audit_write_runtime_evidence.py` | 271 | audit_events_table | `blockers.append("audit_events did not increase and trace ID was not found")` |
| `scripts/audit_write_runtime_evidence.py` | 273 | audit_append_call | `blockers.append("audit_events has no rows after audited flow")` |
| `scripts/audit_write_runtime_evidence.py` | 273 | audit_events_table | `blockers.append("audit_events has no rows after audited flow")` |
| `scripts/audit_write_runtime_evidence.py` | 275 | audit_append_call | `blockers.append(f"database audit-write check failed: {type(exc).__name__}: {exc}")` |
| `scripts/audit_write_runtime_evidence.py` | 279 | audit_append_call | `blockers.append("accepted evidence requires run_flow unless AUDIT_WRITE_ATTACH_ONLY=1")` |
| `scripts/audit_write_runtime_evidence.py` | 281 | audit_append_call | `blockers.append("AUDIT_WRITE_FLOW_COMMAND is missing or placeholder")` |
| `scripts/audit_write_runtime_evidence.py` | 283 | audit_append_call | `blockers.append("AUDIT_WRITE_FLOW_RESULT must be passed when provided")` |
| `scripts/audit_write_runtime_evidence.py` | 323 | audit_events_table | `f"**audit_events exists:** `{status.audit_table_exists}`",` |
| `scripts/audit_write_runtime_evidence.py` | 324 | audit_events_table | `f"**audit_events before:** `{status.audit_events_count_before}`",` |
| `scripts/audit_write_runtime_evidence.py` | 325 | audit_events_table | `f"**audit_events after:** `{status.audit_events_count_after}`",` |
| `scripts/audit_write_runtime_evidence.py` | 326 | audit_events_table | `f"**audit_events delta:** `{status.audit_events_delta}`",` |
| `scripts/audit_write_runtime_evidence.py` | 347 | audit_append_call | `lines.append("- None")` |
| `scripts/audit_write_runtime_evidence.py` | 354 | audit_events_table | `"- The audit_events table must contain rows after the flow.",` |
| `scripts/audit_write_runtime_evidence.py` | 355 | audit_events_table | `"- Either audit_events count must increase or the trace ID must be found in recent audit rows.",` |
| `scripts/auth_lifecycle_http_proof.py` | 88 | audit_append_call | `parts.append(value.attr)` |
| `scripts/auth_lifecycle_http_proof.py` | 91 | audit_append_call | `parts.append(value.id)` |
| `scripts/auth_lifecycle_http_proof.py` | 131 | audit_append_call | `routes[endpoint_name]["paths"].append(route.path)` |
| `scripts/auth_lifecycle_http_proof.py` | 147 | audit_append_call | `blockers.append("auth router import failed")` |
| `scripts/auth_lifecycle_http_proof.py` | 149 | audit_append_call | `blockers.append("auth router synthetic FastAPI registration failed")` |
| `scripts/auth_lifecycle_http_proof.py` | 173 | audit_append_call | `blockers.append(f"{function} HTTP route/service proof incomplete")` |
| `scripts/auth_lifecycle_http_proof.py` | 174 | audit_append_call | `proofs.append(proof)` |
| `scripts/auth_lifecycle_http_proof.py` | 205 | audit_append_call | `lines.append(` |
| `scripts/auth_lifecycle_http_proof.py` | 216 | audit_append_call | `lines.append("- None")` |
| `scripts/auth_lifecycle_semantic_proof.py` | 66 | audit_append_call | `self.deleted_cookies.append(key)` |
| `scripts/auth_lifecycle_semantic_proof.py` | 106 | audit_append_call | `parts.append(value.attr)` |
| `scripts/auth_lifecycle_semantic_proof.py` | 109 | audit_append_call | `parts.append(value.id)` |
| `scripts/auth_lifecycle_semantic_proof.py` | 194 | audit_append_call | `proofs.append(RouteSemanticProof(method, delegated, has_param, keywords, prohibited, delegated and has_param and not prohibited))` |
| `scripts/auth_lifecycle_semantic_proof.py` | 214 | audit_append_call | `blockers.append(f"AuthApplicationService missing {method}")` |
| `scripts/auth_lifecycle_semantic_proof.py` | 217 | audit_append_call | `blockers.append(f"{proof.function} route semantic delegation incomplete")` |
| `scripts/auth_lifecycle_semantic_proof.py` | 220 | audit_append_call | `blockers.append(f"{proof.method} controlled cookie clearing proof failed: {proof.detail}")` |
| `scripts/auth_lifecycle_semantic_proof.py` | 249 | audit_append_call | `lines.append(` |
| `scripts/auth_lifecycle_semantic_proof.py` | 255 | audit_append_call | `lines.append(` |
| `scripts/auth_lifecycle_semantic_proof.py` | 262 | audit_append_call | `lines.append("- None")` |
| `scripts/auth_refresh_db_evidence_gate.py` | 287 | audit_append_call | `lines.append(f"\| `{field.name}` \| `{field.value}` \| {field.valid} \| {field.reason} \|")` |
| `scripts/auth_refresh_db_evidence_gate.py` | 292 | audit_append_call | `lines.append("- None")` |
| `scripts/auth_refresh_db_proof.py` | 136 | audit_append_call | `fields.append(EvidenceField(name, value, False, "pending"))` |
| `scripts/auth_refresh_db_proof.py` | 138 | audit_append_call | `fields.append(EvidenceField(name, value, False, "placeholder value"))` |
| `scripts/auth_refresh_db_proof.py` | 140 | audit_append_call | `fields.append(EvidenceField(name, value, False, "must be passed"))` |
| `scripts/auth_refresh_db_proof.py` | 142 | audit_append_call | `fields.append(EvidenceField(name, value, False, "must be non-placeholder URL"))` |
| `scripts/auth_refresh_db_proof.py` | 144 | audit_append_call | `fields.append(EvidenceField(name, value, False, "must look like git SHA"))` |
| `scripts/auth_refresh_db_proof.py` | 146 | audit_append_call | `fields.append(EvidenceField(name, value, True, "ok"))` |
| `scripts/auth_refresh_db_proof.py` | 197 | audit_append_call | `blockers.append("AUTH_REFRESH_DB_PROOF_DSN is not set")` |
| `scripts/auth_refresh_db_proof.py` | 199 | audit_append_call | `blockers.append("DB pytest did not pass")` |
| `scripts/auth_refresh_db_proof.py` | 201 | audit_append_call | `blockers.append("DB pytest output contains skipped tests; skipped DB proof is not accepted")` |
| `scripts/auth_refresh_db_proof.py` | 204 | audit_append_call | `blockers.append(f"evidence field {field.name}: {field.reason}")` |
| `scripts/auth_refresh_db_proof.py` | 247 | audit_append_call | `lines.append(f"\| `{field.name}` \| `{field.value}` \| {field.valid} \| {field.reason} \|")` |
| `scripts/auth_refresh_db_proof.py` | 253 | audit_append_call | `lines.append("- None")` |
| `scripts/auth_refresh_db_proof.py` | 257 | audit_append_call | `lines.append("")` |
| `scripts/auth_route_logout_delegate.py` | 87 | audit_append_call | `parts.append(value.attr)` |
| `scripts/auth_route_logout_delegate.py` | 90 | audit_append_call | `parts.append(value.id)` |
| `scripts/auth_route_logout_delegate.py` | 265 | audit_append_call | `blockers.append(f"{route} route is not fully delegated to auth service")` |
| `scripts/auth_route_logout_delegate.py` | 266 | audit_append_call | `targets.append(TargetStatus(route, exists, has_param, delegates, direct, passed))` |
| `scripts/auth_route_logout_delegate.py` | 292 | audit_append_call | `lines.append(` |
| `scripts/auth_route_logout_delegate.py` | 299 | audit_append_call | `lines.append("- None")` |
| `scripts/auth_route_service_dependency_repair.py` | 154 | audit_append_call | `missing.append(node.name)` |
| `scripts/auth_route_service_dependency_repair.py` | 182 | audit_append_call | `blockers.append(f"{node.name} references auth_service without dependency parameter")` |
| `scripts/auth_route_service_dependency_repair.py` | 183 | audit_append_call | `functions.append(FunctionStatus(node.name, node.lineno, refs, has, passed))` |
| `scripts/auth_route_service_dependency_repair.py` | 208 | audit_append_call | `lines.append(f"\| `{item.function}` \| {item.line} \| {item.references_auth_service} \| {item.has_auth_service_param} \| {item.passed} \|")` |
| `scripts/auth_route_service_dependency_repair.py` | 212 | audit_append_call | `lines.append("- None")` |
| `scripts/auth_service_cleanup.py` | 77 | audit_append_call | `parts.append(value.attr)` |
| `scripts/auth_service_cleanup.py` | 80 | audit_append_call | `parts.append(value.id)` |
| `scripts/auth_service_cleanup.py` | 179 | audit_append_call | `additions.append(_wrapper(method, impl))` |
| `scripts/auth_service_cleanup.py` | 183 | audit_append_call | `additions.append(_fallback(method))` |
| `scripts/auth_service_cleanup.py` | 207 | audit_append_call | `blockers.append("AuthApplicationService module-level monkey-patches remain")` |
| `scripts/auth_service_cleanup.py` | 210 | audit_append_call | `blockers.append("AuthApplicationService missing methods: " + ", ".join(missing_methods))` |
| `scripts/auth_service_cleanup.py` | 257 | audit_append_call | `lines.append("- None")` |
| `scripts/auth_service_cleanup.py` | 261 | audit_append_call | `lines.append("- None")` |
| `scripts/beta_blocker_burndown.py` | 86 | audit_append_call | `items.append(current)` |
| `scripts/beta_blocker_burndown.py` | 97 | audit_append_call | `items.append(current)` |
| `scripts/beta_blocker_burndown.py` | 174 | audit_append_call | `actions.append(make_action(item_id, reason.strip(), findings.get(item_id, {}), registry.get(item_id, {})))` |
| `scripts/beta_blocker_burndown.py` | 179 | audit_append_call | `actions.append(make_action(item_id, str(registry_item.get("closure_blocker") or "release-critical blocker"), findings.get(item_id, {}), registry_item))` |
| `scripts/beta_blocker_burndown.py` | 220 | audit_append_call | `lines.append(` |
| `scripts/beta_no_go_handoff_packet.py` | 249 | audit_append_call | `lines.append(f"\| `{source.name}` \| {source.exists} \| `{source.status}` \| `{source.path}` \|")` |
| `scripts/beta_no_go_handoff_packet.py` | 261 | audit_append_call | `lines.append(` |
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
| `scripts/check_answer_key_independence.py` | 106 | audit_append_call | `errors.append(f"{json_file.name}: {msg}")` |
| `scripts/check_answer_key_independence.py` | 110 | audit_append_call | `errors.append(f"{json_file.name}: Invalid JSON - {e}")` |
| `scripts/check_answer_key_independence.py` | 113 | audit_append_call | `errors.append(f"{json_file.name}: {e}")` |
| `scripts/check_api_envelope_error_contract.py` | 91 | audit_append_call | `results.append(EvidenceResult(rel_path, path.exists(), "present" if path.exists() else "missing"))` |
| `scripts/check_api_envelope_error_contract.py` | 97 | audit_append_call | `results.append(` |
| `scripts/check_api_envelope_error_contract.py` | 107 | audit_append_call | `results.append(` |
| `scripts/check_approval_evidence.py` | 39 | audit_append_call | `failures.append("not all approval records evaluated")` |
| `scripts/check_approval_evidence.py` | 46 | audit_append_call | `failures.append(f"unexpected approval evidence status: {status.status}")` |
| `scripts/check_approval_evidence.py` | 49 | audit_append_call | `failures.append("release mode requires all legal/security/content approvals complete")` |
| `scripts/check_approval_evidence.py` | 80 | audit_append_call | `failures.append("approval evidence tests failed")` |
| `scripts/check_approval_evidence.py` | 101 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_architecture_boundary_contracts.py` | 31 | audit_append_call | `modules.append(node.module or "")` |
| `scripts/check_architecture_boundary_contracts.py` | 49 | audit_append_call | `failures.append(f"{' '.join(command)} failed: {result.stdout}")` |
| `scripts/check_architecture_boundary_contracts.py` | 54 | audit_append_call | `failures.append(f"{router} missing")` |
| `scripts/check_architecture_boundary_contracts.py` | 63 | audit_append_call | `failures.append(f"{router}: missing required import {required}")` |
| `scripts/check_architecture_boundary_contracts.py` | 68 | audit_append_call | `failures.append(f"{router}: forbidden import {forbidden}")` |
| `scripts/check_architecture_boundary_contracts.py` | 76 | audit_append_call | `failures.append(f"{router}: forbidden {prefix} imports {offenders}")` |
| `scripts/check_architecture_boundary_contracts.py` | 85 | audit_append_call | `failures.append(".importlinter missing")` |
| `scripts/check_architecture_boundary_contracts.py` | 92 | audit_append_call | `failures.append("service boundary classification policy missing")` |
| `scripts/check_archival_lock_assertion.py` | 51 | audit_append_call | `results.append(` |
| `scripts/check_arq_worker_import.py` | 41 | audit_append_call | `found.append(item)` |
| `scripts/check_arq_worker_import.py` | 61 | audit_append_call | `failures.append("arq not pinned in dependency files")` |
| `scripts/check_arq_worker_import.py` | 67 | audit_append_call | `failures.append(f"app.modules.jobs import failed: {exc!r}")` |
| `scripts/check_arq_worker_import.py` | 75 | audit_append_call | `failures.append(f"arq compat import failed: {exc!r}")` |
| `scripts/check_arq_worker_import.py` | 89 | audit_append_call | `failures.append(f"WorkerSettings/functions missing {expected}")` |
| `scripts/check_arq_worker_import.py` | 95 | audit_append_call | `failures.append("jobs.py missing run_consent_reminder_cycle")` |
| `scripts/check_arq_worker_import.py` | 123 | audit_append_call | `failures.append("ARQ worker import contract tests failed")` |
| `scripts/check_arq_worker_import.py` | 144 | audit_append_call | `failures.append("focused ruff failed")` |
| `scripts/check_audit_baseline_refresh.py` | 42 | audit_append_call | `failures.append(f"unexpected branch {status.current_branch}")` |
| `scripts/check_audit_baseline_refresh.py` | 45 | audit_append_call | `failures.append("beta decision is GO while beta blockers remain")` |
| `scripts/check_audit_baseline_refresh.py` | 49 | audit_append_call | `failures.append("audit status JSON commit does not match current commit")` |
| `scripts/check_audit_baseline_refresh.py` | 59 | audit_append_call | `failures.append(f"missing required surface {name}")` |
| `scripts/check_audit_baseline_refresh.py` | 61 | audit_append_call | `failures.append(f"surface {name} is stale")` |
| `scripts/check_audit_baseline_refresh.py` | 86 | audit_append_call | `failures.append("audit baseline refresh unit tests failed")` |
| `scripts/check_audit_baseline_refresh.py` | 108 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_audit_canonicalization_registry.py` | 25 | audit_append_call | `failures.append("no ready candidates")` |
| `scripts/check_audit_canonicalization_registry.py` | 38 | audit_append_call | `failures.append("registry doc missing")` |
| `scripts/check_audit_canonicalization_slice.py` | 18 | audit_append_call | `failures.append("action mismatch")` |
| `scripts/check_audit_canonicalization_slice.py` | 20 | audit_append_call | `failures.append("resource_type mismatch")` |
| `scripts/check_audit_canonicalization_slice.py` | 22 | audit_append_call | `failures.append("resource_id mismatch")` |
| `scripts/check_audit_canonicalization_slice.py` | 24 | audit_append_call | `failures.append("learner_id missing from payload")` |
| `scripts/check_audit_event_contracts.py` | 33 | audit_log_identifier | `"AuditLog emission is handled inside ConsentService",` |
| `scripts/check_audit_event_contracts.py` | 51 | audit_append_call | `results.append(CheckResult(rel_path, marker, marker in text))` |
| `scripts/check_audit_review_closeout_certificate.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_audit_write_runtime_evidence.py` | 41 | audit_events_table | `print(f"- INFO audit_events before: {status.audit_events_count_before}")` |
| `scripts/check_audit_write_runtime_evidence.py` | 42 | audit_events_table | `print(f"- INFO audit_events after: {status.audit_events_count_after}")` |
| `scripts/check_audit_write_runtime_evidence.py` | 43 | audit_events_table | `print(f"- INFO audit_events delta: {status.audit_events_delta}")` |
| `scripts/check_audit_write_runtime_evidence.py` | 60 | audit_append_call | `failures.append(f"{item_id} missing {required}")` |
| `scripts/check_audit_write_runtime_evidence.py` | 72 | audit_append_call | `failures.append("audit write runtime evidence unit tests failed")` |
| `scripts/check_audit_write_runtime_evidence.py` | 81 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_auth_boundary_evidence.py` | 58 | audit_append_call | `results.append(EvidenceResult(rel_path, path.exists(), "present" if path.exists() else "missing"))` |
| `scripts/check_auth_boundary_evidence.py` | 62 | audit_append_call | `results.append(EvidenceResult(rel_path, snippet in text, f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}"))` |
| `scripts/check_auth_db_lifecycle_proof.py` | 37 | audit_append_call | `failures.append(f"proof source missing {token}")` |
| `scripts/check_auth_db_lifecycle_proof.py` | 63 | audit_append_call | `failures.append("transactional auth DB lifecycle tests failed")` |
| `scripts/check_auth_db_lifecycle_proof.py` | 84 | audit_append_call | `failures.append("focused ruff failed")` |
| `scripts/check_auth_forward_refs.py` | 27 | audit_append_call | `failures.append("repair_auth_forward_refs.py failed")` |
| `scripts/check_auth_forward_refs.py` | 35 | audit_append_call | `failures.append("auth.RegisterRequest missing")` |
| `scripts/check_auth_forward_refs.py` | 38 | audit_append_call | `failures.append(f"auth router import failed: {exc!r}")` |
| `scripts/check_auth_forward_refs.py` | 48 | audit_append_call | `failures.append("register route missing after app import")` |
| `scripts/check_auth_forward_refs.py` | 51 | audit_append_call | `failures.append(f"app.api_v2 import failed: {exc!r}")` |
| `scripts/check_auth_forward_refs.py` | 58 | audit_append_call | `failures.append("repair report missing")` |
| `scripts/check_auth_http_success_scope.py` | 32 | audit_append_call | `failures.append("auth.py has future annotations")` |
| `scripts/check_auth_http_success_scope.py` | 37 | audit_append_call | `failures.append("auth.py imports app.repositories")` |
| `scripts/check_auth_http_success_scope.py` | 45 | audit_append_call | `failures.append(f"missing {token}")` |
| `scripts/check_auth_http_success_scope.py` | 59 | audit_append_call | `failures.append(f"test missing {token}")` |
| `scripts/check_auth_http_success_scope.py` | 66 | audit_append_call | `failures.append(f"missing {path}")` |
| `scripts/check_auth_http_success_scope.py` | 87 | audit_append_call | `failures.append("focused ruff failed")` |
| `scripts/check_auth_http_success_scope.py` | 112 | audit_append_call | `failures.append("auth HTTP success/scope integration tests failed")` |
| `scripts/check_auth_lifecycle_http_proof.py` | 40 | audit_append_call | `failures.append("release mode requires auth lifecycle HTTP route proof passing")` |
| `scripts/check_auth_lifecycle_http_proof.py` | 59 | audit_append_call | `failures.append("auth lifecycle HTTP proof tests failed")` |
| `scripts/check_auth_lifecycle_http_proof.py` | 72 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_auth_lifecycle_method_extraction.py` | 25 | audit_append_call | `failures.append("auth.py still has future annotations")` |
| `scripts/check_auth_lifecycle_method_extraction.py` | 30 | audit_append_call | `failures.append("auth.py imports app.repositories")` |
| `scripts/check_auth_lifecycle_method_extraction.py` | 36 | audit_append_call | `failures.append(f"direct constructor remains: {constructor}")` |
| `scripts/check_auth_lifecycle_method_extraction.py` | 44 | audit_append_call | `failures.append(f"auth_service.{method} missing")` |
| `scripts/check_auth_lifecycle_method_extraction.py` | 52 | audit_append_call | `failures.append(f"missing helper {helper} in service impl")` |
| `scripts/check_auth_lifecycle_method_extraction.py` | 58 | audit_append_call | `failures.append(f"missing service marker {marker}")` |
| `scripts/check_auth_lifecycle_method_extraction.py` | 66 | audit_append_call | `failures.append("RegisterRequest missing in auth globals")` |
| `scripts/check_auth_lifecycle_method_extraction.py` | 68 | audit_append_call | `failures.append(f"auth import failed: {exc!r}")` |
| `scripts/check_auth_lifecycle_method_extraction.py` | 75 | audit_append_call | `failures.append(f"app.api_v2 import failed: {exc!r}")` |
| `scripts/check_auth_lifecycle_method_extraction.py` | 101 | audit_append_call | `failures.append("focused ruff failed")` |
| `scripts/check_auth_lifecycle_semantic_proof.py` | 40 | audit_append_call | `failures.append("release mode requires controlled auth lifecycle semantic proof passing")` |
| `scripts/check_auth_lifecycle_semantic_proof.py` | 59 | audit_append_call | `failures.append("auth lifecycle semantic proof tests failed")` |
| `scripts/check_auth_lifecycle_semantic_proof.py` | 72 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_auth_refresh_db_evidence_gate.py` | 36 | audit_append_call | `failures.append("release mode requires accepted auth refresh DB evidence")` |
| `scripts/check_auth_refresh_db_evidence_gate.py` | 67 | audit_append_call | `failures.append("auth refresh DB evidence gate unit tests failed")` |
| `scripts/check_auth_refresh_db_evidence_gate.py` | 80 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_auth_refresh_db_proof.py` | 36 | audit_append_call | `failures.append("release mode requires accepted auth refresh DB proof")` |
| `scripts/check_auth_refresh_db_proof.py` | 58 | audit_append_call | `failures.append("auth refresh DB proof unit tests failed")` |
| `scripts/check_auth_refresh_db_proof.py` | 72 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_auth_repository_fixture_proof.py` | 43 | audit_append_call | `failures.append(f"{source_name} does not prefer {canonical}")` |
| `scripts/check_auth_repository_fixture_proof.py` | 72 | audit_append_call | `failures.append("auth repository fixture proof tests failed")` |
| `scripts/check_auth_repository_fixture_proof.py` | 93 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_auth_route_logout_delegate.py` | 56 | audit_append_call | `failures.append("auth route logout delegation tests failed")` |
| `scripts/check_auth_route_logout_delegate.py` | 69 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_auth_route_service_dependencies.py` | 54 | audit_append_call | `failures.append("auth route service dependency tests failed")` |
| `scripts/check_auth_route_service_dependencies.py` | 67 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_auth_router_boundary.py` | 25 | audit_append_call | `failures.append("missing auth runtime dependency import")` |
| `scripts/check_auth_router_boundary.py` | 31 | audit_append_call | `failures.append("LearnerRepository remains in auth router")` |
| `scripts/check_auth_router_boundary.py` | 37 | audit_append_call | `failures.append("direct get_by_guardian remains")` |
| `scripts/check_auth_router_boundary.py` | 44 | audit_append_call | `failures.append("guardian learner ids not referenced in service impl")` |
| `scripts/check_auth_router_boundary.py` | 51 | audit_append_call | `failures.append("missing repair report")` |
| `scripts/check_auth_service_cleanup.py` | 41 | audit_append_call | `failures.append("release mode requires logout/revoke route delegation")` |
| `scripts/check_auth_service_cleanup.py` | 60 | audit_append_call | `failures.append("auth service cleanup tests failed")` |
| `scripts/check_auth_service_cleanup.py` | 73 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_auth_service_extraction.py` | 19 | audit_repository | `"AuditRepository",` |
| `scripts/check_auth_service_extraction.py` | 39 | audit_append_call | `failures.append("repair_auth_service_extraction.py failed")` |
| `scripts/check_auth_service_extraction.py` | 46 | audit_append_call | `failures.append(f"auth.py syntax error: {exc}")` |
| `scripts/check_auth_service_extraction.py` | 51 | audit_append_call | `failures.append("auth router missing AuthApplicationService dependency import")` |
| `scripts/check_auth_service_extraction.py` | 54 | audit_append_call | `failures.append("auth router still imports app.repositories")` |
| `scripts/check_auth_service_extraction.py` | 61 | audit_append_call | `failures.append(f"auth router still directly constructs {token}")` |
| `scripts/check_auth_service_extraction.py` | 65 | audit_append_call | `failures.append("auth.py future annotations can reintroduce FastAPI forward-ref failures")` |
| `scripts/check_auth_service_extraction.py` | 74 | audit_append_call | `failures.append(f"auth router import failed: {exc!r}")` |
| `scripts/check_auth_service_extraction.py` | 82 | audit_append_call | `failures.append("app.api_v2 has no routes")` |
| `scripts/check_auth_service_extraction.py` | 84 | audit_append_call | `failures.append(f"app.api_v2 import failed: {exc!r}")` |
| `scripts/check_auth_service_extraction.py` | 107 | audit_append_call | `failures.append("focused ruff auth service extraction check failed")` |
| `scripts/check_auth_service_ownership.py` | 23 | audit_append_call | `failures.append(f"missing {path.relative_to(ROOT)}")` |
| `scripts/check_auth_service_ownership.py` | 33 | audit_append_call | `failures.append("auth.py still contains legacy lifecycle helpers")` |
| `scripts/check_auth_service_ownership.py` | 41 | audit_append_call | `failures.append(f"auth.py does not delegate {method}")` |
| `scripts/check_auth_service_ownership.py` | 45 | audit_append_call | `failures.append(f"AuthApplicationService.{method} assignment missing")` |
| `scripts/check_auth_service_ownership.py` | 49 | audit_append_call | `failures.append(f"implementation module missing {method}_impl")` |
| `scripts/check_auth_service_ownership.py` | 52 | audit_append_call | `failures.append("auth.py has future annotations")` |
| `scripts/check_auth_service_ownership.py` | 57 | audit_append_call | `failures.append("auth.py imports app.repositories")` |
| `scripts/check_auth_service_ownership.py` | 67 | audit_append_call | `failures.append("RegisterRequest missing from auth module")` |
| `scripts/check_auth_service_ownership.py` | 69 | audit_append_call | `failures.append(f"auth import failed: {exc!r}")` |
| `scripts/check_auth_service_ownership.py` | 76 | audit_append_call | `failures.append(f"app.api_v2 import failed: {exc!r}")` |
| `scripts/check_auth_service_ownership.py` | 100 | audit_append_call | `failures.append("focused ruff failed")` |
| `scripts/check_auth_token_claims_repair.py` | 38 | audit_append_call | `failures.append("helper missing")` |
| `scripts/check_auth_token_claims_repair.py` | 43 | audit_append_call | `failures.append("router missing")` |
| `scripts/check_auth_token_claims_repair.py` | 51 | audit_append_call | `failures.append("helper import missing")` |
| `scripts/check_auth_token_claims_repair.py` | 56 | audit_append_call | `failures.append("helper marker missing")` |
| `scripts/check_auth_token_claims_repair.py` | 59 | audit_append_call | `failures.append("raw email_encrypted")` |
| `scripts/check_auth_token_claims_repair.py` | 67 | audit_append_call | `failures.append("report missing")` |
| `scripts/check_auth_transaction_rollback_proof.py` | 39 | audit_append_call | `failures.append(f"service missing {token}")` |
| `scripts/check_auth_transaction_rollback_proof.py` | 51 | audit_append_call | `failures.append(f"test missing {token}")` |
| `scripts/check_auth_transaction_rollback_proof.py` | 83 | audit_append_call | `failures.append("auth transaction rollback proof tests failed")` |
| `scripts/check_auth_transaction_rollback_proof.py` | 104 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_backend_consolidation_dragons.py` | 28 | audit_append_call | `paths.append(path)` |
| `scripts/check_backend_consolidation_dragons.py` | 44 | audit_append_call | `matched_paths.append(str(path.relative_to(REPO_ROOT)))` |
| `scripts/check_backend_consolidation_dragons.py` | 51 | audit_events_table | `"audit_events": _scan(r"\baudit_events\b"),` |
| `scripts/check_backend_consolidation_dragons.py` | 52 | audit_logs_table | `"audit_logs": _scan(r"\baudit_logs\b"),` |
| `scripts/check_backend_consolidation_execution_packet.py` | 54 | audit_append_call | `failures.append(f"missing {path}")` |
| `scripts/check_backend_consolidation_execution_packet.py` | 64 | audit_append_call | `failures.append(f"{path} missing {needle!r}")` |
| `scripts/check_backend_consolidation_execution_packet.py` | 68 | audit_append_call | `failures.append(f"{path} has premature phrase {phrase!r}")` |
| `scripts/check_backend_consolidation_implementation_foundation.py` | 49 | audit_append_call | `failures.append(f"missing {relative}")` |
| `scripts/check_backend_consolidation_implementation_foundation.py` | 59 | audit_append_call | `failures.append(f"{relative} missing {needle!r}")` |
| `scripts/check_backend_consolidation_implementation_foundation.py` | 63 | audit_append_call | `failures.append(f"forbidden phrase {phrase!r}")` |
| `scripts/check_backend_consolidation_implementation_foundation.py` | 77 | audit_append_call | `failures.append("backend_consolidation_runtime.py compile failed")` |
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
| `scripts/check_backend_destructive_action_blocklist.py` | 15 | audit_logs_table | `"audit_logs deletion: approved",` |
| `scripts/check_backend_destructive_action_blocklist.py` | 31 | audit_append_call | `failures.append(f"missing {relative}")` |
| `scripts/check_backend_destructive_action_blocklist.py` | 37 | audit_append_call | `failures.append(f"{relative}: {phrase}")` |
| `scripts/check_backend_first_wiring_candidates.py` | 46 | audit_append_call | `failures.append("no safe candidates")` |
| `scripts/check_backend_first_wiring_candidates.py` | 52 | audit_append_call | `failures.append("unsafe candidates detected")` |
| `scripts/check_backend_first_wiring_candidates.py` | 58 | audit_append_call | `failures.append("payload count mismatch")` |
| `scripts/check_backend_first_wiring_candidates.py` | 65 | audit_append_call | `failures.append(message)` |
| `scripts/check_backend_first_wiring_candidates.py` | 73 | audit_append_call | `failures.append(f"missing {doc}")` |
| `scripts/check_backend_implementation_371_375.py` | 31 | audit_append_call | `failures.append("no audit candidates")` |
| `scripts/check_backend_implementation_371_375.py` | 44 | audit_append_call | `failures.append("audit event mapping")` |
| `scripts/check_backend_implementation_371_375.py` | 55 | audit_append_call | `failures.append("consent payload classification")` |
| `scripts/check_backend_implementation_371_375.py` | 62 | audit_append_call | `failures.append("unsafe public readiness")` |
| `scripts/check_backend_implementation_371_375.py` | 70 | audit_append_call | `failures.append("deep readiness catalogue")` |
| `scripts/check_backend_implementation_371_375.py` | 78 | audit_append_call | `failures.append(f"missing {doc}")` |
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
| `scripts/check_backend_runtime_enablement_guard.py` | 26 | audit_append_call | `failures.append(result.name)` |
| `scripts/check_backend_runtime_enablement_guard.py` | 41 | audit_append_call | `failures.append(f"missing {relative}")` |
| `scripts/check_backend_runtime_integration_blocklists.py` | 33 | audit_append_call | `failures.append(f"missing {relative}")` |
| `scripts/check_backend_runtime_integration_blocklists.py` | 40 | audit_append_call | `failures.append(f"{relative}: {pattern}")` |
| `scripts/check_backend_runtime_integration_readiness.py` | 38 | audit_append_call | `failures.append("insufficient targets")` |
| `scripts/check_backend_runtime_integration_readiness.py` | 44 | audit_append_call | `failures.append(result.target_id)` |
| `scripts/check_backend_runtime_integration_readiness.py` | 52 | audit_append_call | `failures.append(f"missing blocked change {expected}")` |
| `scripts/check_backend_runtime_integration_readiness.py` | 60 | audit_append_call | `failures.append(f"missing {doc}")` |
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
| `scripts/check_backend_runtime_wiring_cases.py` | 30 | audit_append_call | `failures.append(f"missing {path}")` |
| `scripts/check_backend_runtime_wiring_cases.py` | 36 | audit_append_call | `failures.append(result.case_name)` |
| `scripts/check_backend_runtime_wiring_preflight.py` | 27 | audit_append_call | `failures.append(result.area.value)` |
| `scripts/check_backend_runtime_wiring_preflight.py` | 35 | audit_append_call | `failures.append(f"missing {doc}")` |
| `scripts/check_backend_runtime_wiring_preflight.py` | 45 | audit_append_call | `failures.append(f"ledger missing {needle}")` |
| `scripts/check_backup_restore_disaster_recovery_production_readiness.py` | 145 | audit_append_call | `results.append(` |
| `scripts/check_backup_restore_disaster_recovery_production_readiness.py` | 156 | audit_append_call | `results.append(` |
| `scripts/check_backup_restore_disaster_recovery_production_readiness.py` | 180 | audit_append_call | `results.append(DisasterRecoveryReadinessResult("disaster_recovery_contracts", False, f"contract check failed: {exc}"))` |
| `scripts/check_beta_acceptance_exit_criteria.py` | 53 | audit_append_call | `results.append(` |
| `scripts/check_beta_blocker_burndown.py` | 35 | audit_append_call | `failures.append("NO-GO source decision must have blocker actions")` |
| `scripts/check_beta_blocker_burndown.py` | 39 | audit_append_call | `failures.append("release mode cannot be allowed while blocker actions exist")` |
| `scripts/check_beta_blocker_burndown.py` | 43 | audit_append_call | `failures.append("release mode requires blocker burn-down status clear")` |
| `scripts/check_beta_blocker_burndown.py` | 62 | audit_append_call | `failures.append("beta blocker burn-down tests failed")` |
| `scripts/check_beta_blocker_burndown.py` | 74 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_beta_evidence_consistency.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_beta_evidence_consistency.py` | 71 | audit_append_call | `results.append(` |
| `scripts/check_beta_evidence_consistency.py` | 83 | audit_append_call | `results.append(` |
| `scripts/check_beta_evidence_consistency.py` | 98 | audit_append_call | `results.append(` |
| `scripts/check_beta_evidence_consistency.py` | 113 | audit_append_call | `results.append(` |
| `scripts/check_beta_evidence_consistency.py` | 128 | audit_append_call | `results.append(` |
| `scripts/check_beta_evidence_integrity.py` | 41 | audit_append_call | `failures.append(f"{gate}: missing evidence_source_type")` |
| `scripts/check_beta_evidence_integrity.py` | 46 | audit_append_call | `failures.append(f"{gate}: pass-like status without valid integrity")` |
| `scripts/check_beta_evidence_integrity.py` | 55 | audit_append_call | `failures.append(f"readiness marked beta_ready with invalid gate {gate}")` |
| `scripts/check_beta_feedback_intake_contract.py` | 53 | audit_append_call | `results.append(` |
| `scripts/check_beta_governance_seal.py` | 53 | audit_append_call | `results.append(BetaGovernanceSealResult(snippet in text, f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}"))` |
| `scripts/check_beta_known_issues_register.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_beta_launch_staging_acceptance_production_readiness.py` | 151 | audit_append_call | `results.append(` |
| `scripts/check_beta_launch_staging_acceptance_production_readiness.py` | 158 | audit_append_call | `results.append(` |
| `scripts/check_beta_launch_staging_acceptance_production_readiness.py` | 185 | audit_append_call | `results.append(BetaLaunchReadinessResult("beta_launch_contracts", False, f"contract check failed: {exc}"))` |
| `scripts/check_beta_monitoring_incident_trigger.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_beta_no_go_handoff_packet.py` | 45 | audit_append_call | `failures.append("required evidence items missing")` |
| `scripts/check_beta_no_go_handoff_packet.py` | 50 | audit_append_call | `failures.append("some required evidence item is locally closeable")` |
| `scripts/check_beta_no_go_handoff_packet.py` | 81 | audit_append_call | `failures.append("beta NO-GO handoff packet tests failed")` |
| `scripts/check_beta_no_go_handoff_packet.py` | 102 | audit_append_call | `failures.append("focused Ruff failed")` |
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
| `scripts/check_ci_auth_refresh_db_proof_workflow.py` | 55 | audit_append_call | `failures.append("CI auth refresh DB proof workflow unit tests failed")` |
| `scripts/check_ci_auth_refresh_db_proof_workflow.py` | 68 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_ci_authority.py` | 39 | audit_append_call | `failures.append("No GitHub workflow file found")` |
| `scripts/check_ci_authority.py` | 44 | audit_append_call | `failures.append("No required local CI-equivalent targets found")` |
| `scripts/check_ci_authority.py` | 49 | audit_append_call | `failures.append("ci_evidence.md missing")` |
| `scripts/check_ci_authority.py` | 57 | audit_append_call | `failures.append(f"Unexpected CI-001 registry proof_status: {registry_status}")` |
| `scripts/check_ci_authority.py` | 65 | audit_append_call | `failures.append("release mode requires real GitHub Actions run URL")` |
| `scripts/check_ci_authority.py` | 96 | audit_append_call | `failures.append("CI authority unit tests failed")` |
| `scripts/check_ci_authority.py` | 117 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_ci_cd_deployment_production_readiness.py` | 147 | audit_append_call | `results.append(` |
| `scripts/check_ci_cd_deployment_production_readiness.py` | 158 | audit_append_call | `results.append(` |
| `scripts/check_ci_cd_deployment_production_readiness.py` | 183 | audit_append_call | `results.append(DeploymentReadinessResult("deployment_contracts", False, f"contract check failed: {exc}"))` |
| `scripts/check_ci_evidence_acceptance.py` | 82 | audit_append_call | `failures.append("CI evidence acceptance unit tests failed")` |
| `scripts/check_ci_evidence_acceptance.py` | 106 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_ci_evidence_acceptance.py` | 121 | audit_append_call | `failures.append(f"{item_id} missing {required}")` |
| `scripts/check_ci_evidence_acceptance.py` | 123 | audit_append_call | `failures.append(f"{item_id} missing run ID {status.run_id}")` |
| `scripts/check_ci_evidence_acceptance.py` | 125 | audit_append_call | `failures.append(f"{item_id} missing commit SHA {status.current_commit}")` |
| `scripts/check_ci_run_evidence.py` | 39 | audit_append_call | `failures.append("GitHub Actions run URL validator rejected canonical URL")` |
| `scripts/check_ci_run_evidence.py` | 46 | audit_append_call | `failures.append(f"unexpected CI run evidence status: {status.status}")` |
| `scripts/check_ci_run_evidence.py` | 49 | audit_append_call | `failures.append("release mode requires accepted CI run evidence")` |
| `scripts/check_ci_run_evidence.py` | 70 | audit_append_call | `failures.append("CI run evidence tests failed")` |
| `scripts/check_ci_run_evidence.py` | 83 | audit_append_call | `failures.append("focused Ruff failed")` |
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
| `scripts/check_consent_runtime_compatibility_slice.py` | 30 | audit_append_call | `failures.append("normalization failed")` |
| `scripts/check_consent_runtime_compatibility_slice.py` | 37 | audit_append_call | `failures.append("no probes")` |
| `scripts/check_consent_runtime_compatibility_slice.py` | 48 | audit_append_call | `failures.append("doc missing")` |
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
| `scripts/check_db_backup_restore_rollback_evidence.py` | 66 | audit_append_call | `failures.append(f"{item_id} missing {required}")` |
| `scripts/check_db_backup_restore_rollback_evidence.py` | 83 | audit_append_call | `failures.append("DB backup/restore/rollback unit tests failed")` |
| `scripts/check_db_backup_restore_rollback_evidence.py` | 96 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_db_live_only_table_ownership.py` | 48 | audit_append_call | `failures.append(f"missing ownership record for {table}")` |
| `scripts/check_db_live_only_table_ownership.py` | 58 | audit_append_call | `failures.append("DB-OWNERSHIP-001R should not block beta unless ownership is migration-required")` |
| `scripts/check_db_live_only_table_ownership.py` | 83 | audit_append_call | `failures.append("DB live-only table ownership unit tests failed")` |
| `scripts/check_db_live_only_table_ownership.py` | 105 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_db_migration_seed_repeatability.py` | 56 | audit_append_call | `failures.append(f"Supabase SQL still contains forbidden token: {token}")` |
| `scripts/check_db_migration_seed_repeatability.py` | 59 | audit_append_call | `failures.append("IRT seed SQL insert count does not match expected row count")` |
| `scripts/check_db_migration_seed_repeatability.py` | 84 | audit_append_call | `failures.append("DB repeatability unit tests failed")` |
| `scripts/check_db_migration_seed_repeatability.py` | 106 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_deep_readiness_readonly_guard.py` | 21 | audit_append_call | `failures.append("invalid readiness spec summary")` |
| `scripts/check_deep_readiness_readonly_guard.py` | 23 | audit_events_table | `for bad in ["session.commit()", "INSERT INTO audit_events", "alembic stamp head"]:` |
| `scripts/check_deep_readiness_readonly_guard.py` | 30 | audit_append_call | `failures.append(f"accepted {bad!r}")` |
| `scripts/check_deep_readiness_readonly_guard.py` | 39 | audit_append_call | `failures.append("deep readiness checklist lacks guardrails")` |
| `scripts/check_dev_only_endpoint_exposure.py` | 42 | audit_append_call | `results.append(` |
| `scripts/check_diag_deep_health_runtime.py` | 48 | audit_append_call | `failures.append("diagnostic deep-health runtime unit tests failed")` |
| `scripts/check_diag_deep_health_runtime.py` | 53 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_diag_deep_health_runtime.py` | 66 | audit_append_call | `failures.append(f"{item_id} missing {required}")` |
| `scripts/check_diagnostic_generation_safety_contract.py` | 40 | audit_append_call | `results.append(` |
| `scripts/check_diagnostic_item_bank_canonicality.py` | 68 | audit_append_call | `failures.append(f"DIAG-ITEMS-001R missing {required}")` |
| `scripts/check_diagnostic_item_bank_canonicality.py` | 76 | audit_append_call | `failures.append(f"DIAG-SCORE-001 missing {required}")` |
| `scripts/check_diagnostic_item_bank_canonicality.py` | 101 | audit_append_call | `failures.append("diagnostic item-bank policy unit tests failed")` |
| `scripts/check_diagnostic_item_bank_canonicality.py` | 123 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_diagnostic_score_live_audit.py` | 68 | audit_append_call | `failures.append(f"{item_id} missing {required}")` |
| `scripts/check_diagnostic_score_live_audit.py` | 95 | audit_append_call | `failures.append("diagnostic score live audit unit tests failed")` |
| `scripts/check_diagnostic_score_live_audit.py` | 117 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_diagnostics_assessment_production_readiness.py` | 113 | audit_append_call | `results.append(CheckResult(rel_path, path.exists(), "present" if path.exists() else "missing"))` |
| `scripts/check_diagnostics_assessment_production_readiness.py` | 117 | audit_append_call | `results.append(` |
| `scripts/check_diagnostics_dynamic_repository_boundary.py` | 51 | audit_append_call | `failures.append(f"diagnostics.py still contains disallowed token: {token}")` |
| `scripts/check_diagnostics_dynamic_repository_boundary.py` | 57 | audit_append_call | `failures.append(f"diagnostics.py still directly constructs/resolves repository: {call}")` |
| `scripts/check_diagnostics_dynamic_repository_boundary.py` | 70 | audit_append_call | `failures.append(f"diagnostics.py missing required boundary token: {token}")` |
| `scripts/check_diagnostics_dynamic_repository_boundary.py` | 83 | audit_append_call | `failures.append(f"diagnostic_repositories.py missing {token}")` |
| `scripts/check_diagnostics_dynamic_repository_boundary.py` | 111 | audit_append_call | `failures.append("diagnostics dynamic boundary unit tests failed")` |
| `scripts/check_diagnostics_dynamic_repository_boundary.py` | 132 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_diagnostics_jobs_integrity.py` | 23 | audit_append_call | `failures.append("missing diagnostic helper")` |
| `scripts/check_diagnostics_jobs_integrity.py` | 29 | audit_append_call | `failures.append("missing job runtime helper")` |
| `scripts/check_diagnostics_jobs_integrity.py` | 36 | audit_append_call | `failures.append("diagnostics helper import")` |
| `scripts/check_diagnostics_jobs_integrity.py` | 42 | audit_append_call | `failures.append("diagnostics markers")` |
| `scripts/check_diagnostics_jobs_integrity.py` | 47 | audit_append_call | `failures.append("ConsentService empty constructor")` |
| `scripts/check_diagnostics_jobs_integrity.py` | 56 | audit_append_call | `failures.append(f"jobs missing {token}")` |
| `scripts/check_diagnostics_jobs_integrity.py` | 63 | audit_append_call | `failures.append("background task policy")` |
| `scripts/check_diagnostics_scoring_snapshot.py` | 28 | audit_append_call | `failures.append("diagnostic session service still scores all history with current item")` |
| `scripts/check_diagnostics_scoring_snapshot.py` | 32 | audit_append_call | `failures.append("diagnostic item reconstruction missing")` |
| `scripts/check_diagnostics_scoring_snapshot.py` | 36 | audit_append_call | `failures.append("diagnostic response scoring snapshot missing")` |
| `scripts/check_diagnostics_scoring_snapshot.py` | 63 | audit_append_call | `failures.append("diagnostics scoring snapshot tests failed")` |
| `scripts/check_diagnostics_scoring_snapshot.py` | 76 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_diagnostics_session_binding.py` | 39 | audit_append_call | `failures.append(f"diagnostics.py missing {token}")` |
| `scripts/check_diagnostics_session_binding.py` | 63 | audit_append_call | `failures.append(str(exc))` |
| `scripts/check_diagnostics_session_binding.py` | 76 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_diagnostics_transaction_rollback_proof.py` | 40 | audit_append_call | `failures.append(f"service missing {token}")` |
| `scripts/check_diagnostics_transaction_rollback_proof.py` | 53 | audit_append_call | `failures.append(f"test missing {token}")` |
| `scripts/check_diagnostics_transaction_rollback_proof.py` | 85 | audit_append_call | `failures.append("diagnostic transaction rollback proof tests failed")` |
| `scripts/check_diagnostics_transaction_rollback_proof.py` | 106 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_docker_production_hardening.py` | 27 | audit_append_call | `failures.append(msg)` |
| `scripts/check_docs_intelligence.py` | 39 | audit_append_call | `failures.append("docs inventory generation failed")` |
| `scripts/check_docs_intelligence.py` | 53 | audit_append_call | `failures.append("docs inventory check failed")` |
| `scripts/check_docs_intelligence.py` | 84 | audit_append_call | `failures.append("docs intelligence unit tests failed")` |
| `scripts/check_docs_intelligence.py` | 105 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_documentation_adrs_claim_discipline_production_readiness.py` | 109 | audit_append_call | `results.append(DocumentationGovernanceReadinessResult(rel_path, path.exists(), "file present" if path.exists() else "file missing"))` |
| `scripts/check_documentation_adrs_claim_discipline_production_readiness.py` | 113 | audit_append_call | `results.append(DocumentationGovernanceReadinessResult(rel_path, snippet in text, f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}"))` |
| `scripts/check_documentation_adrs_claim_discipline_production_readiness.py` | 131 | audit_append_call | `results.append(DocumentationGovernanceReadinessResult("documentation_governance_contracts", False, f"contract check failed: {exc}"))` |
| `scripts/check_environment_security_contract.py` | 41 | audit_append_call | `results.append(` |
| `scripts/check_evidence_archive_completeness_guard.py` | 58 | audit_append_call | `results.append(EvidenceArchiveCompletenessGuardResult(snippet in text, f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}"))` |
| `scripts/check_evidence_attachment_runbook.py` | 35 | audit_append_call | `failures.append("too few evidence attachment commands")` |
| `scripts/check_evidence_attachment_runbook.py` | 42 | audit_append_call | `failures.append(f"runbook missing {item}")` |
| `scripts/check_evidence_attachment_runbook.py` | 48 | audit_append_call | `failures.append(f"release sequence missing {command}")` |
| `scripts/check_evidence_attachment_runbook.py` | 64 | audit_append_call | `failures.append("evidence attachment runbook tests failed")` |
| `scripts/check_evidence_attachment_runbook.py` | 70 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_evidence_freeze_confirmation_record.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_evidence_registry_commit_provenance.py` | 39 | audit_append_call | `failures.append(f"{finding.id} missing last_verified_commit")` |
| `scripts/check_evidence_registry_commit_provenance.py` | 66 | audit_append_call | `failures.append("evidence registry commit provenance tests failed")` |
| `scripts/check_evidence_status_registry.py` | 51 | audit_append_call | `failures.append("POPIA-001 must remain not-proven while focused tests skip cases")` |
| `scripts/check_evidence_status_registry.py` | 79 | audit_append_call | `failures.append("evidence registry unit tests failed")` |
| `scripts/check_evidence_status_registry.py` | 100 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_external_approval_gate.py` | 39 | audit_append_call | `failures.append("not all approval records evaluated")` |
| `scripts/check_external_approval_gate.py` | 45 | audit_append_call | `failures.append(f"{approval.id} evidence file missing")` |
| `scripts/check_external_approval_gate.py` | 59 | audit_append_call | `failures.append(f"{approval_id} registry status is unexpected: {registry_status}")` |
| `scripts/check_external_approval_gate.py` | 62 | audit_append_call | `failures.append("release mode requires all external approvals to be complete")` |
| `scripts/check_external_approval_gate.py` | 93 | audit_append_call | `failures.append("external approval gate tests failed")` |
| `scripts/check_external_approval_gate.py` | 114 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_final_acceptance_memo.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_final_acceptance_packet_index.py` | 57 | audit_append_call | `results.append(` |
| `scripts/check_final_archive_accession_record.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_final_audit_handoff_register.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_final_beta_operator_packet.py` | 51 | audit_append_call | `results.append(` |
| `scripts/check_final_closure_manifest.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_final_evidence_noop_execution_assertion.py` | 51 | audit_append_call | `results.append(` |
| `scripts/check_final_gate_refresh.py` | 40 | audit_append_call | `failures.append("no status surfaces refreshed")` |
| `scripts/check_final_gate_refresh.py` | 47 | audit_append_call | `failures.append(f"unexpected beta decision: {refresh.beta_decision}")` |
| `scripts/check_final_gate_refresh.py` | 50 | audit_append_call | `failures.append("release mode requires final beta gate decision GO")` |
| `scripts/check_final_gate_refresh.py` | 82 | audit_append_call | `failures.append("final gate refresh tests failed")` |
| `scripts/check_final_gate_refresh.py` | 104 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_final_gate_refresh_classifier.py` | 38 | audit_append_call | `failures.append(f"{item_id} is not classified as resolved non-blocking accepted finding")` |
| `scripts/check_final_gate_refresh_classifier.py` | 43 | audit_append_call | `failures.append(f"{item_id} must remain beta-blocking")` |
| `scripts/check_final_gate_refresh_classifier.py` | 62 | audit_append_call | `failures.append("final gate refresh classifier unit tests failed")` |
| `scripts/check_final_gate_refresh_classifier.py` | 75 | audit_append_call | `failures.append("focused Ruff failed")` |
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
| `scripts/check_first_audit_runtime_wiring.py` | 49 | audit_append_call | `failures.append("unsafe candidate")` |
| `scripts/check_first_audit_runtime_wiring.py` | 55 | audit_append_call | `failures.append("candidate boundary")` |
| `scripts/check_first_audit_runtime_wiring.py` | 62 | audit_append_call | `failures.append("payload mapping")` |
| `scripts/check_first_audit_runtime_wiring.py` | 69 | audit_append_call | `failures.append(message)` |
| `scripts/check_first_audit_runtime_wiring.py` | 77 | audit_append_call | `failures.append(f"missing {doc}")` |
| `scripts/check_first_audit_runtime_wiring_no_destructive_actions.py` | 18 | audit_logs_table | `"delete audit_logs",` |
| `scripts/check_first_audit_runtime_wiring_no_destructive_actions.py` | 33 | audit_append_call | `failures.append(f"missing {relative}")` |
| `scripts/check_first_audit_runtime_wiring_no_destructive_actions.py` | 39 | audit_append_call | `failures.append(f"{relative}: {pattern}")` |
| `scripts/check_first_consent_and_deep_readiness_runtime_wiring.py` | 38 | audit_append_call | `failures.append("consent candidate unsafe")` |
| `scripts/check_first_consent_and_deep_readiness_runtime_wiring.py` | 45 | audit_append_call | `failures.append("consent payload invalid")` |
| `scripts/check_first_consent_and_deep_readiness_runtime_wiring.py` | 52 | audit_append_call | `failures.append("deep-readiness candidate unsafe")` |
| `scripts/check_first_consent_and_deep_readiness_runtime_wiring.py` | 59 | audit_append_call | `failures.append("deep-readiness plan invalid")` |
| `scripts/check_first_consent_and_deep_readiness_runtime_wiring.py` | 67 | audit_append_call | `failures.append(f"missing {doc}")` |
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
| `scripts/check_jwt_production_guard.py` | 46 | audit_append_call | `failures.append(f"jwt_keyring.py missing {token}")` |
| `scripts/check_jwt_production_guard.py` | 62 | audit_append_call | `failures.append(label)` |
| `scripts/check_jwt_production_guard.py` | 77 | audit_append_call | `failures.append("JWT production guard tests failed")` |
| `scripts/check_jwt_production_guard.py` | 91 | audit_append_call | `failures.append("app.api_v2 import failed with safe JWT secret")` |
| `scripts/check_jwt_production_guard.py` | 105 | audit_append_call | `failures.append("focused ruff failed")` |
| `scripts/check_jwt_rotation.py` | 21 | audit_append_call | `failures.append("missing keyring helper")` |
| `scripts/check_jwt_rotation.py` | 27 | audit_append_call | `failures.append("security.py missing keyring import")` |
| `scripts/check_jwt_rotation.py` | 33 | audit_append_call | `failures.append("no kid header path or blocker")` |
| `scripts/check_jwt_secret_rotation_evidence.py` | 34 | audit_append_call | `if req not in e: failures.append(f"{item} missing {req}")` |
| `scripts/check_jwt_secret_rotation_evidence.py` | 41 | audit_append_call | `if r.returncode != 0: failures.append("JWT secret rotation unit tests failed")` |
| `scripts/check_jwt_secret_rotation_evidence.py` | 44 | audit_append_call | `else: failures.append("focused Ruff failed"); print(ruff.stdout)` |
| `scripts/check_learner_vertical_journey_contract.py` | 49 | audit_append_call | `results.append(` |
| `scripts/check_learner_vertical_journey_contract.py` | 54 | audit_append_call | `results.append(` |
| `scripts/check_learner_vertical_journey_contract.py` | 62 | audit_append_call | `results.append(` |
| `scripts/check_learner_vertical_journey_contract.py` | 71 | audit_append_call | `results.append(` |
| `scripts/check_learning_evidence.py` | 74 | audit_append_call | `results.append(EvidenceResult(rel_path, path.exists(), "present" if path.exists() else "missing"))` |
| `scripts/check_learning_evidence.py` | 80 | audit_append_call | `results.append(` |
| `scripts/check_lesson_authorization_hardening.py` | 43 | audit_append_call | `failures.append("lesson_owner_learner_id still swallows broad Exception")` |
| `scripts/check_lesson_authorization_hardening.py` | 51 | audit_append_call | `failures.append("expected narrowed compatibility exceptions missing")` |
| `scripts/check_lesson_authorization_hardening.py` | 67 | audit_append_call | `failures.append(f"missing router token {token}")` |
| `scripts/check_lesson_authorization_hardening.py` | 96 | audit_append_call | `failures.append("lesson authorization hardening tests failed")` |
| `scripts/check_lesson_authorization_hardening.py` | 110 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_lesson_gamification_transaction_rollback_proof.py` | 39 | audit_append_call | `failures.append(f"service missing {token}")` |
| `scripts/check_lesson_gamification_transaction_rollback_proof.py` | 52 | audit_append_call | `failures.append(f"test missing {token}")` |
| `scripts/check_lesson_gamification_transaction_rollback_proof.py` | 84 | audit_append_call | `failures.append("lesson gamification transaction rollback proof tests failed")` |
| `scripts/check_lesson_gamification_transaction_rollback_proof.py` | 105 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_lesson_generation_safety_contract.py` | 41 | audit_append_call | `results.append(` |
| `scripts/check_lesson_object_authorization_repair.py` | 34 | audit_append_call | `failures.append("helper import")` |
| `scripts/check_lesson_object_authorization_repair.py` | 45 | audit_append_call | `failures.append(f"{node.name} read")` |
| `scripts/check_lesson_object_authorization_repair.py` | 51 | audit_append_call | `failures.append(f"{node.name} write")` |
| `scripts/check_lesson_object_authorization_repair.py` | 57 | audit_append_call | `failures.append(f"{node.name} sync")` |
| `scripts/check_lesson_object_authorization_repair.py` | 65 | audit_append_call | `failures.append("report")` |
| `scripts/check_live_db_tx_evidence.py` | 39 | audit_append_call | `failures.append("not all route transaction slices evaluated")` |
| `scripts/check_live_db_tx_evidence.py` | 46 | audit_append_call | `failures.append(f"unexpected live DB evidence status: {status.status}")` |
| `scripts/check_live_db_tx_evidence.py` | 49 | audit_append_call | `failures.append("release mode requires complete live DB transaction evidence")` |
| `scripts/check_live_db_tx_evidence.py` | 80 | audit_append_call | `failures.append("live DB transaction evidence tests failed")` |
| `scripts/check_live_db_tx_evidence.py` | 101 | audit_append_call | `failures.append("focused Ruff failed")` |
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
| `scripts/check_popia_consent_lifecycle_repair.py` | 28 | audit_append_call | `failures.append("deprecated consent service import")` |
| `scripts/check_popia_consent_lifecycle_repair.py` | 36 | audit_append_call | `failures.append("canonical consent service import")` |
| `scripts/check_popia_consent_lifecycle_repair.py` | 40 | audit_append_call | `failures.append("generated actor dependency")` |
| `scripts/check_popia_consent_lifecycle_repair.py` | 48 | audit_append_call | `failures.append("canonical consent dependency helper")` |
| `scripts/check_popia_consent_lifecycle_repair.py` | 60 | audit_append_call | `failures.append("no lifecycle functions")` |
| `scripts/check_popia_consent_lifecycle_repair.py` | 67 | audit_append_call | `failures.append(f"{node.name} current_user")` |
| `scripts/check_popia_consent_lifecycle_repair.py` | 72 | audit_append_call | `failures.append(f"{node.name} learner-write")` |
| `scripts/check_popia_consent_lifecycle_repair.py` | 77 | audit_append_call | `failures.append(f"{node.name} actor")` |
| `scripts/check_popia_consent_lifecycle_repair.py` | 85 | audit_append_call | `failures.append("repair report")` |
| `scripts/check_popia_legal_evidence.py` | 34 | audit_append_call | `results.append(Result("docs/legal/legal_documents_index.md", snippet.lower() in text.lower(), f"contains {snippet!r}"))` |
| `scripts/check_popia_response_contract_no_skips.py` | 69 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_popia_route_tx_no_false_closure.py` | 64 | audit_append_call | `failures.append(` |
| `scripts/check_popia_route_tx_no_false_closure.py` | 73 | audit_append_call | `failures.append("gap plan with actions must remain blocked")` |
| `scripts/check_popia_route_tx_no_false_closure.py` | 106 | audit_append_call | `failures.append("POPIA route transaction gap-plan tests failed")` |
| `scripts/check_popia_route_tx_no_false_closure.py` | 127 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_popia_transaction_rollback_proof.py` | 41 | audit_append_call | `failures.append(f"service missing {token}")` |
| `scripts/check_popia_transaction_rollback_proof.py` | 73 | audit_append_call | `failures.append("POPIA transaction rollback proof tests failed")` |
| `scripts/check_popia_transaction_rollback_proof.py` | 88 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_post_beta_evidence_archive_manifest.py` | 59 | audit_append_call | `results.append(` |
| `scripts/check_post_closeout_custody_register.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_post_closeout_evidence_access_policy.py` | 50 | audit_append_call | `results.append(` |
| `scripts/check_post_closeout_maintenance_boundary.py` | 49 | audit_append_call | `results.append(` |
| `scripts/check_post_deploy_staging_smoke_checklist.py` | 51 | audit_append_call | `results.append(` |
| `scripts/check_post_merge_evidence_continuity_note.py` | 51 | audit_append_call | `results.append(` |
| `scripts/check_post_merge_release_handoff.py` | 52 | audit_append_call | `results.append(` |
| `scripts/check_post_terminal_audit_readiness.py` | 50 | audit_append_call | `results.append(PostTerminalAuditReadinessResult(snippet in text, f"contains {snippet!r}" if snippet in text else f"missing {snippet!r}"))` |
| `scripts/check_pr002r_evidence.py` | 103 | audit_append_call | `results.append(` |
| `scripts/check_pr002r_evidence.py` | 121 | audit_append_call | `results.append(` |
| `scripts/check_pr002r_evidence.py` | 133 | audit_append_call | `results.append(` |
| `scripts/check_pr002r_evidence.py` | 154 | audit_append_call | `lines.append(f"- {status} [{result.kind}] {result.path}: {result.message}")` |
| `scripts/check_pr_closeout_evidence_checklist.py` | 47 | audit_append_call | `results.append(` |
| `scripts/check_pr_merge_evidence_summary.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_pr_ready_final_closure_certificate.py` | 53 | audit_append_call | `results.append(` |
| `scripts/check_privacy_boundary_evidence.py` | 66 | audit_append_call | `results.append(` |
| `scripts/check_privacy_boundary_evidence.py` | 74 | audit_append_call | `results.append(` |
| `scripts/check_prod_frontend_deployment.py` | 42 | audit_append_call | `failures.append("release mode requires production frontend deployment configuration")` |
| `scripts/check_prod_frontend_deployment.py` | 74 | audit_append_call | `failures.append("production frontend deployment tests failed")` |
| `scripts/check_prod_frontend_deployment.py` | 96 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_prod_frontend_runtime.py` | 49 | audit_append_call | `failures.append("release mode requires accepted production frontend runtime evidence")` |
| `scripts/check_prod_frontend_runtime.py` | 81 | audit_append_call | `failures.append("production frontend runtime tests failed")` |
| `scripts/check_prod_frontend_runtime.py` | 103 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_production_restore_approval.py` | 43 | audit_append_call | `results.append(` |
| `scripts/check_production_restore_approval.py` | 52 | audit_append_call | `results.append(` |
| `scripts/check_production_restore_approval.py` | 61 | audit_append_call | `results.append(` |
| `scripts/check_production_secret_placeholders.py` | 41 | audit_append_call | `results.append(` |
| `scripts/check_production_secret_placeholders.py` | 50 | audit_append_call | `results.append(` |
| `scripts/check_project_release_closure_index.py` | 46 | audit_append_call | `results.append(` |
| `scripts/check_recommended_operating_model.py` | 59 | audit_append_call | `results.append(` |
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
| `scripts/check_release_go_no_go.py` | 42 | audit_append_call | `failures.append(f"unexpected decision: {status.decision}")` |
| `scripts/check_release_go_no_go.py` | 45 | audit_append_call | `failures.append("release mode requires generated decision GO")` |
| `scripts/check_release_go_no_go.py` | 76 | audit_append_call | `failures.append("release go/no-go unit tests failed")` |
| `scripts/check_release_go_no_go.py` | 97 | audit_append_call | `failures.append("focused Ruff failed")` |
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
| `scripts/check_route_tx_auth_slice.py` | 40 | audit_append_call | `failures.append("auth route delegation slice is not locally proven")` |
| `scripts/check_route_tx_auth_slice.py` | 47 | audit_append_call | `failures.append(f"unexpected live DB status: {report.live_db_status}")` |
| `scripts/check_route_tx_auth_slice.py` | 50 | audit_append_call | `failures.append("release mode requires live DB auth route transaction evidence")` |
| `scripts/check_route_tx_auth_slice.py` | 81 | audit_append_call | `failures.append("auth route transaction slice tests failed")` |
| `scripts/check_route_tx_auth_slice.py` | 102 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_route_tx_diagnostics_slice.py` | 43 | audit_append_call | `failures.append("gap plan with actions must remain blocked")` |
| `scripts/check_route_tx_diagnostics_slice.py` | 51 | audit_append_call | `failures.append(f"unexpected live DB status: {report.live_db_status}")` |
| `scripts/check_route_tx_diagnostics_slice.py` | 53 | audit_append_call | `failures.append("release mode requires local diagnostics route source passing and live DB evidence")` |
| `scripts/check_route_tx_diagnostics_slice.py` | 64 | audit_append_call | `failures.append("diagnostics route transaction slice tests failed")` |
| `scripts/check_route_tx_diagnostics_slice.py` | 69 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_route_tx_impl_plan.py` | 38 | audit_append_call | `failures.append("TX route inventory is missing")` |
| `scripts/check_route_tx_impl_plan.py` | 50 | audit_append_call | `failures.append("route transaction actions must not be closable by static marker")` |
| `scripts/check_route_tx_impl_plan.py` | 55 | audit_append_call | `failures.append("release mode requires route transaction implementation actions to be zero")` |
| `scripts/check_route_tx_impl_plan.py` | 86 | audit_append_call | `failures.append("route transaction implementation plan tests failed")` |
| `scripts/check_route_tx_impl_plan.py` | 107 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_route_tx_popia_slice.py` | 41 | audit_append_call | `failures.append("no POPIA routes selected for slice")` |
| `scripts/check_route_tx_popia_slice.py` | 46 | audit_append_call | `failures.append("POPIA route delegation slice is not locally proven")` |
| `scripts/check_route_tx_popia_slice.py` | 53 | audit_append_call | `failures.append(f"unexpected live DB status: {report.live_db_status}")` |
| `scripts/check_route_tx_popia_slice.py` | 56 | audit_append_call | `failures.append("release mode requires live DB POPIA route transaction evidence")` |
| `scripts/check_route_tx_popia_slice.py` | 87 | audit_append_call | `failures.append("POPIA route transaction slice tests failed")` |
| `scripts/check_route_tx_popia_slice.py` | 108 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_route_tx_slice_rollup.py` | 40 | audit_append_call | `failures.append("expected three route transaction slices in rollup")` |
| `scripts/check_route_tx_slice_rollup.py` | 47 | audit_append_call | `failures.append(f"unexpected rollup status: {rollup.status}")` |
| `scripts/check_route_tx_slice_rollup.py` | 50 | audit_append_call | `failures.append("release mode requires route transaction slice rollup release-ready")` |
| `scripts/check_route_tx_slice_rollup.py` | 81 | audit_append_call | `failures.append("route transaction slice rollup tests failed")` |
| `scripts/check_route_tx_slice_rollup.py` | 102 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_router_boundary_enforcement.py` | 24 | audit_append_call | `failures.append(f"{router}: {violations}")` |
| `scripts/check_runtime_blockers_after_followup_audit.py` | 23 | audit_append_call | `failures.append(f"POPIA adapter missing {method}")` |
| `scripts/check_runtime_blockers_after_followup_audit.py` | 26 | audit_append_call | `failures.append("consent dependency missing POPIA adapter")` |
| `scripts/check_runtime_blockers_after_followup_audit.py` | 29 | audit_append_call | `failures.append("auth.py still contains `learners` token")` |
| `scripts/check_runtime_blockers_after_followup_audit.py` | 32 | audit_append_call | `failures.append(f"auth.py direct constructor remains: {token}")` |
| `scripts/check_runtime_blockers_after_followup_audit.py` | 35 | audit_append_call | `failures.append("diagnostics still uses require_items=False")` |
| `scripts/check_runtime_blockers_after_followup_audit.py` | 39 | audit_append_call | `failures.append(f"jobs missing {name}")` |
| `scripts/check_runtime_blockers_after_followup_audit.py` | 42 | audit_append_call | `failures.append(f"jobs.py still directly references {token}")` |
| `scripts/check_runtime_entrypoints.py` | 123 | audit_append_call | `results.append(check_entrypoint(spec, canonical=index == 0))` |
| `scripts/check_runtime_entrypoints.py` | 153 | audit_append_call | `lines.append(f"- {status} {result.spec}")` |
| `scripts/check_runtime_entrypoints.py` | 156 | audit_append_call | `lines.append(f"  title: {result.title}")` |
| `scripts/check_runtime_entrypoints.py` | 158 | audit_append_call | `lines.append(f"  version: {result.version}")` |
| `scripts/check_runtime_entrypoints.py` | 160 | audit_append_call | `lines.append(f"  route_count: {result.route_count}")` |
| `scripts/check_runtime_entrypoints.py` | 162 | audit_append_call | `lines.append(f"  missing_routes: {', '.join(result.missing_routes)}")` |
| `scripts/check_runtime_entrypoints.py` | 164 | audit_append_call | `lines.append(f"  missing_prefixes: {', '.join(result.missing_prefixes)}")` |
| `scripts/check_runtime_entrypoints.py` | 166 | audit_append_call | `lines.append(f"  error: {result.error}")` |
| `scripts/check_runtime_integration_proof.py` | 35 | audit_append_call | `failures.append("POPIA dependency missing lifecycle adapter")` |
| `scripts/check_runtime_integration_proof.py` | 40 | audit_append_call | `failures.append(f"POPIA adapter missing {method}")` |
| `scripts/check_runtime_integration_proof.py` | 44 | audit_append_call | `failures.append("diagnostics contains require_items=False")` |
| `scripts/check_runtime_integration_proof.py` | 52 | audit_append_call | `failures.append("missing validate_session_served_item_binding helper")` |
| `scripts/check_runtime_integration_proof.py` | 78 | audit_append_call | `failures.append("focused ruff critical runtime check failed")` |
| `scripts/check_runtime_release_evidence.py` | 67 | audit_append_call | `failures.append(f"missing file {path}")` |
| `scripts/check_runtime_release_evidence.py` | 77 | audit_append_call | `failures.append(f"{path} missing {needle!r}")` |
| `scripts/check_runtime_release_evidence.py` | 88 | audit_append_call | `failures.append(f"{path} pending status removed")` |
| `scripts/check_runtime_wiring_no_destructive_actions.py` | 35 | audit_append_call | `failures.append(f"missing {relative}")` |
| `scripts/check_runtime_wiring_no_destructive_actions.py` | 41 | audit_append_call | `failures.append(f"{relative}: {pattern}")` |
| `scripts/check_schema_drift_contract.py` | 27 | audit_append_call | `failures.append(f"missing {path}")` |
| `scripts/check_schema_drift_contract.py` | 41 | audit_append_call | `failures.append("compare_orm_tables_to_database.py failed without DB")` |
| `scripts/check_sealed_evidence_access_handoff.py` | 54 | audit_append_call | `results.append(` |
| `scripts/check_sealed_reviewer_closeout_packet.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_security_posture_threat_modeling_production_readiness.py` | 172 | audit_append_call | `results.append(` |
| `scripts/check_security_posture_threat_modeling_production_readiness.py` | 183 | audit_append_call | `results.append(` |
| `scripts/check_security_posture_threat_modeling_production_readiness.py` | 211 | audit_append_call | `results.append(SecurityPostureReadinessResult("security_posture_contracts", False, f"contract check failed: {exc}"))` |
| `scripts/check_staging_acceptance.py` | 41 | audit_append_call | `failures.append(f"unexpected staging status: {status.status}")` |
| `scripts/check_staging_acceptance.py` | 49 | audit_append_call | `failures.append(f"unexpected STAGING-001 registry status: {registry_status}")` |
| `scripts/check_staging_acceptance.py` | 52 | audit_append_call | `failures.append("release mode requires accepted staging evidence")` |
| `scripts/check_staging_acceptance.py` | 83 | audit_append_call | `failures.append("staging acceptance evidence tests failed")` |
| `scripts/check_staging_acceptance.py` | 104 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_staging_release_gate.py` | 45 | audit_append_call | `results.append(StagingGateResult("file", str(DOC.relative_to(REPO_ROOT)), DOC.exists(), "present" if DOC.exists() else "missing"))` |
| `scripts/check_staging_release_gate.py` | 48 | audit_append_call | `results.append(` |
| `scripts/check_staging_release_gate.py` | 59 | audit_append_call | `results.append(` |
| `scripts/check_staging_smoke_evidence_acceptance.py` | 81 | audit_append_call | `failures.append("staging smoke evidence unit tests failed")` |
| `scripts/check_staging_smoke_evidence_acceptance.py` | 103 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_staging_smoke_evidence_acceptance.py` | 118 | audit_append_call | `failures.append(f"{item_id} missing {required}")` |
| `scripts/check_staging_smoke_evidence_acceptance.py` | 120 | audit_append_call | `failures.append(f"{item_id} missing run ID {status.run_id}")` |
| `scripts/check_staging_smoke_evidence_acceptance.py` | 122 | audit_append_call | `failures.append(f"{item_id} missing commit SHA {status.current_commit}")` |
| `scripts/check_staging_smoke_evidence_acceptance.py` | 124 | audit_append_call | `failures.append(f"{item_id} missing staging URL {status.staging_base_url}")` |
| `scripts/check_staging_smoke_evidence_manifest.py` | 49 | audit_append_call | `results.append(` |
| `scripts/check_staging_smoke_evidence_manifest.py` | 58 | audit_append_call | `results.append(` |
| `scripts/check_staging_smoke_workflow_config.py` | 67 | audit_append_call | `blockers.append(blocker)` |
| `scripts/check_staging_smoke_workflow_config.py` | 113 | audit_append_call | `lines.append("- None")` |
| `scripts/check_terminal_evidence_retrieval_guide.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_terminal_evidence_seal.py` | 61 | audit_append_call | `results.append(` |
| `scripts/check_terminal_handoff_closure_note.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_terminal_pr_evidence_index.py` | 55 | audit_append_call | `results.append(` |
| `scripts/check_terminal_review_index.py` | 54 | audit_append_call | `results.append(` |
| `scripts/check_test_environment.py` | 105 | audit_append_call | `failures.append(result.name)` |
| `scripts/check_testing_release_quality_gates_production_readiness.py` | 141 | audit_append_call | `results.append(` |
| `scripts/check_testing_release_quality_gates_production_readiness.py` | 152 | audit_append_call | `results.append(` |
| `scripts/check_testing_release_quality_gates_production_readiness.py` | 177 | audit_append_call | `results.append(QualityGateReadinessResult("quality_gate_contracts", False, f"contract check failed: {exc}"))` |
| `scripts/check_todo_implementation_plan.py` | 38 | audit_append_call | `ids.append(match.group(0))` |
| `scripts/check_todo_implementation_plan.py` | 67 | audit_append_call | `results.append(` |
| `scripts/check_todo_implementation_plan.py` | 75 | audit_append_call | `results.append(` |
| `scripts/check_todo_implementation_plan.py` | 83 | audit_append_call | `results.append(` |
| `scripts/check_transaction_boundary_guardrails.py` | 43 | audit_append_call | `failures.append("transaction boundary inventory generation failed")` |
| `scripts/check_transaction_boundary_guardrails.py` | 56 | audit_append_call | `failures.append("inventory contains no findings")` |
| `scripts/check_transaction_boundary_guardrails.py` | 63 | audit_append_call | `failures.append(f"inventory missing expected term: {term}")` |
| `scripts/check_transaction_boundary_guardrails.py` | 68 | audit_append_call | `failures.append("evidence registry missing TX-001")` |
| `scripts/check_transaction_boundary_guardrails.py` | 97 | audit_append_call | `failures.append("transaction boundary guardrail unit tests failed")` |
| `scripts/check_transaction_boundary_guardrails.py` | 120 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_transaction_rollback_rollup.py` | 37 | audit_append_call | `failures.append("isolated rollback coverage incomplete")` |
| `scripts/check_transaction_rollback_rollup.py` | 43 | audit_append_call | `failures.append(f"{proof.id} missing from registry")` |
| `scripts/check_transaction_rollback_rollup.py` | 47 | audit_append_call | `failures.append(f"{proof.id} is not integration-passing")` |
| `scripts/check_transaction_rollback_rollup.py` | 51 | audit_append_call | `failures.append(f"{proof.id} evidence file missing: {proof.evidence_file}")` |
| `scripts/check_transaction_rollback_rollup.py` | 56 | audit_append_call | `failures.append(f"registry missing {proof_id}")` |
| `scripts/check_transaction_rollback_rollup.py` | 61 | audit_append_call | `failures.append("TX-001 must not be marked production-ready by this rollup")` |
| `scripts/check_transaction_rollback_rollup.py` | 92 | audit_append_call | `failures.append("transaction rollback rollup tests failed")` |
| `scripts/check_transaction_rollback_rollup.py` | 113 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_tx_route_wiring.py` | 37 | audit_append_call | `failures.append("no route functions scanned")` |
| `scripts/check_tx_route_wiring.py` | 81 | audit_append_call | `failures.append("TX route wiring inventory tests failed")` |
| `scripts/check_tx_route_wiring.py` | 102 | audit_append_call | `failures.append("focused Ruff failed")` |
| `scripts/check_warning_cleanup.py` | 36 | audit_append_call | `failures.append("pytest.ini norecursedirs missing: " + ", ".join(sorted(missing)))` |
| `scripts/check_warning_cleanup.py` | 45 | audit_append_call | `failures.append(f"{repo_test} _mock_session block {idx} lacks synchronous add MagicMock")` |
| `scripts/check_warning_cleanup.py` | 49 | audit_append_call | `failures.append(f"missing {repo_test}")` |
| `scripts/check_warning_cleanup.py` | 55 | audit_append_call | `failures.append(f"{register} missing or incomplete")` |
| `scripts/ci/ci_lesson_bank_check.py` | 169 | audit_append_call | `results.append(result)` |
| `scripts/ci/ci_lesson_bank_check.py` | 218 | audit_append_call | `violations.append(violation)` |
| `scripts/ci_auth_refresh_db_proof_workflow.py` | 88 | audit_append_call | `lines.append(f"\| `{check.name}` \| {check.passed} \| {check.detail} \|")` |
| `scripts/ci_auth_refresh_db_proof_workflow.py` | 90 | audit_append_call | `lines.extend(f"- {blocker}" for blocker in status.blockers) if status.blockers else lines.append("- None")` |
| `scripts/ci_authority.py` | 106 | audit_append_call | `blockers.append("No GitHub Actions workflow file found under .github/workflows")` |
| `scripts/ci_authority.py` | 108 | audit_append_call | `blockers.append("Workflow file does not mention every required local CI-equivalent command family")` |
| `scripts/ci_authority.py` | 110 | audit_append_call | `blockers.append("Missing local CI-equivalent Makefile targets: " + ", ".join(missing_targets))` |
| `scripts/ci_authority.py` | 112 | audit_append_call | `blockers.append("No GitHub Actions run URL recorded in docs/release/ci_evidence.md")` |
| `scripts/ci_authority.py` | 214 | audit_append_call | `lines.append(f"\| `{target}` \| {target in present} \|")` |
| `scripts/ci_authority.py` | 220 | audit_append_call | `lines.append("- None")` |
| `scripts/ci_evidence_acceptance.py` | 168 | audit_append_call | `blockers.append("GitHub CLI is unavailable or not authenticated")` |
| `scripts/ci_evidence_acceptance.py` | 177 | audit_append_call | `blockers.append("CI_EVIDENCE_RUN_ID is not numeric")` |
| `scripts/ci_evidence_acceptance.py` | 181 | audit_append_call | `blockers.append(f"unable to read GitHub Actions run {requested_run_id}")` |
| `scripts/ci_evidence_acceptance.py` | 185 | audit_append_call | `blockers.append("no successful non-auth-refresh GitHub Actions run found for current commit")` |
| `scripts/ci_evidence_acceptance.py` | 198 | audit_append_call | `blockers.append("run ID is missing or non-numeric")` |
| `scripts/ci_evidence_acceptance.py` | 201 | audit_append_call | `blockers.append("run URL does not contain the numeric run ID")` |
| `scripts/ci_evidence_acceptance.py` | 204 | audit_append_call | `blockers.append("run URL contains placeholder evidence")` |
| `scripts/ci_evidence_acceptance.py` | 207 | audit_append_call | `blockers.append(f"GitHub Actions run status is {run_status or 'missing'}, expected completed")` |
| `scripts/ci_evidence_acceptance.py` | 210 | audit_append_call | `blockers.append(f"GitHub Actions run conclusion is {conclusion or 'missing'}, expected success")` |
| `scripts/ci_evidence_acceptance.py` | 213 | audit_append_call | `blockers.append(f"GitHub Actions run SHA {head_sha or 'missing'} does not match current commit {sha}")` |
| `scripts/ci_evidence_acceptance.py` | 216 | audit_append_call | `blockers.append("workflow name is missing")` |
| `scripts/ci_evidence_acceptance.py` | 219 | audit_append_call | `blockers.append(f"workflow {workflow_name!r} is not valid general CI evidence")` |
| `scripts/ci_evidence_acceptance.py` | 222 | audit_append_call | `blockers.append(` |
| `scripts/ci_evidence_acceptance.py` | 273 | audit_append_call | `lines.append("- None")` |
| `scripts/ci_run_evidence.py` | 164 | audit_append_call | `blockers.append("repository is pending")` |
| `scripts/ci_run_evidence.py` | 166 | audit_append_call | `blockers.append("branch is pending")` |
| `scripts/ci_run_evidence.py` | 168 | audit_append_call | `blockers.append("commit SHA is pending or invalid")` |
| `scripts/ci_run_evidence.py` | 170 | audit_append_call | `blockers.append("GitHub Actions run URL is pending or invalid")` |
| `scripts/ci_run_evidence.py` | 172 | audit_append_call | `blockers.append("result must be pass/passed/success/successful/green/ok")` |
| `scripts/ci_run_evidence.py` | 174 | audit_append_call | `blockers.append("workflow is pending")` |
| `scripts/ci_run_evidence.py` | 176 | audit_append_call | `blockers.append("verified by is pending")` |
| `scripts/ci_run_evidence.py` | 178 | audit_append_call | `blockers.append("date verified is pending")` |
| `scripts/ci_run_evidence.py` | 257 | audit_append_call | `lines.extend(f"- {b}" for b in status.blockers) if status.blockers else lines.append("- None")` |
| `scripts/curriculum/build_launch_content_artifacts.py` | 40 | audit_append_call | `targets.append(` |
| `scripts/curriculum/build_scope_content_artifacts.py` | 231 | audit_append_call | `item_errors.append(f"{ref}/{item['item_id']}: {[error.rule for error in validation_errors]}")` |
| `scripts/curriculum/build_scope_content_artifacts.py` | 234 | audit_append_call | `item_errors.append(` |
| `scripts/curriculum/build_scope_content_artifacts.py` | 237 | audit_append_call | `generated_items.append(item)` |
| `scripts/curriculum/build_scope_content_artifacts.py` | 252 | audit_append_call | `lesson_errors.append(f"{ref}/{lesson['lesson_id']}: {validation.failures}")` |
| `scripts/curriculum/build_scope_content_artifacts.py` | 261 | audit_append_call | `lesson_errors.append(` |
| `scripts/curriculum/build_scope_content_artifacts.py` | 264 | audit_append_call | `generated_lessons.append(lesson)` |
| `scripts/curriculum/build_scope_content_artifacts.py` | 270 | audit_append_call | `item_errors.append(` |
| `scripts/curriculum/build_scope_content_artifacts.py` | 292 | audit_append_call | `blueprint_errors.append(f"blueprint refs outside scope: {sorted(blueprint_refs - set(scope.caps_refs))}")` |
| `scripts/curriculum/build_scope_content_artifacts.py` | 309 | audit_append_call | `study_plan_errors.append(` |
| `scripts/curriculum/build_topic_map_worklist.py` | 76 | audit_append_call | `tasks.append("resolve_source_document")` |
| `scripts/curriculum/build_topic_map_worklist.py` | 79 | audit_append_call | `tasks.append("load_source_pdf_and_sha256")` |
| `scripts/curriculum/build_topic_map_worklist.py` | 81 | audit_append_call | `tasks.append("upload_source_pdf_to_object_store")` |
| `scripts/curriculum/build_topic_map_worklist.py` | 84 | audit_append_call | `tasks.append("extract_topic_map")` |
| `scripts/curriculum/build_topic_map_worklist.py` | 86 | audit_append_call | `tasks.append("approve_scope_caps_refs")` |
| `scripts/curriculum/build_topic_map_worklist.py` | 88 | audit_append_call | `tasks.append("approve_topic_map")` |
| `scripts/curriculum/build_topic_map_worklist.py` | 90 | audit_append_call | `tasks.append("activate_scope")` |
| `scripts/curriculum/build_topic_map_worklist.py` | 120 | audit_append_call | `items.append(` |
| `scripts/curriculum/download_caps_sources.py` | 116 | audit_append_call | `errors.append(f"{document.get('document_id')}: {exc}")` |
| `scripts/curriculum/download_caps_sources.py` | 119 | audit_append_call | `results.append(result)` |
| `scripts/curriculum/extract_caps_source_text.py` | 45 | audit_append_call | `page_text.append(f"\n\n--- page {page_number} ---\n{text.strip()}")` |
| `scripts/curriculum/extract_caps_source_text.py` | 85 | audit_append_call | `errors.append(f"{document.document_id}: {exc}")` |
| `scripts/curriculum/extract_caps_source_text.py` | 88 | audit_append_call | `records.append(record)` |
| `scripts/curriculum/report_content_coverage.py` | 62 | audit_append_call | `rows.append(row)` |
| `scripts/curriculum/resolve_dbe_caps_urls.py` | 89 | audit_append_call | `self.links.append(Link(self.phase, self.current_section, label, self._current_href))` |
| `scripts/curriculum/resolve_dbe_caps_urls.py` | 97 | audit_append_call | `self._current_text.append(value)` |
| `scripts/curriculum/resolve_dbe_caps_urls.py` | 116 | audit_append_call | `links.append(Link(phase, section, label, link.href))` |
| `scripts/curriculum/resolve_dbe_caps_urls.py` | 170 | audit_append_call | `manifest["documents"].append(grade_r_doc)` |
| `scripts/curriculum/resolve_dbe_caps_urls.py` | 172 | audit_append_call | `changed.append(grade_r_doc["document_id"])` |
| `scripts/curriculum/resolve_dbe_caps_urls.py` | 180 | audit_append_call | `changed.append(document_id)` |
| `scripts/curriculum/resolve_dbe_caps_urls.py` | 190 | audit_append_call | `changed.append(scope["scope_id"])` |
| `scripts/curriculum/rollback_staging_seed.py` | 44 | audit_append_call | `run_ids_to_rollback.append((scope_id, UUID(run_id_str)))` |
| `scripts/curriculum/rollback_staging_seed.py` | 58 | audit_append_call | `run_ids_to_rollback.append((args.scope_id, run.seed_run_id))` |
| `scripts/curriculum/rollback_staging_seed.py` | 87 | audit_append_call | `failed_rollbacks.append(run_id)` |
| `scripts/curriculum/scaffold_topic_map_drafts.py` | 62 | audit_append_call | `skipped.append(item["scope_id"])` |
| `scripts/curriculum/scaffold_topic_map_drafts.py` | 66 | audit_append_call | `created.append(str(target.relative_to(ROOT)))` |
| `scripts/curriculum/seed_staging_review_scopes.py` | 61 | audit_append_call | `scopes_summary.append({` |
| `scripts/curriculum/seed_staging_review_scopes.py` | 108 | audit_append_call | `failed_scopes.append(scope_id)` |
| `scripts/curriculum/seed_staging_review_scopes.py` | 113 | audit_append_call | `succeeded_scopes.append(scope_id)` |
| `scripts/curriculum/seed_staging_review_scopes.py` | 119 | audit_append_call | `failed_scopes.append(scope_id)` |
| `scripts/curriculum/seed_staging_review_scopes.py` | 123 | audit_append_call | `failed_scopes.append(scope_id)` |
| `scripts/curriculum/source_inventory.py` | 74 | audit_append_call | `rows.append(` |
| `scripts/curriculum/stamp_dev_approved_review_scopes.py` | 47 | audit_append_call | `rows.append({` |
| `scripts/curriculum/upload_caps_sources_to_azure.py` | 143 | audit_append_call | `errors.append(f"container create failed: {exc}")` |
| `scripts/curriculum/upload_caps_sources_to_azure.py` | 157 | audit_append_call | `errors.append(f"{document.get('document_id')}: {exc}")` |
| `scripts/curriculum/upload_caps_sources_to_azure.py` | 159 | audit_append_call | `uploads.append(upload)` |
| `scripts/curriculum/validate_scope_content.py` | 68 | audit_append_call | `result.errors.append(f"generation scope {scope.scope_id} must declare topic_map_path")` |
| `scripts/curriculum/validate_scope_content.py` | 70 | audit_append_call | `result.errors.append(f"generation scope {scope.scope_id} must declare caps_refs")` |
| `scripts/curriculum/validate_scope_content.py` | 72 | audit_append_call | `result.errors.append(f"generation scope {scope.scope_id} is not generation-ready")` |
| `scripts/curriculum/validate_scope_content.py` | 75 | audit_append_call | `result.errors.append(f"non-generation scope {scope.scope_id} must not declare caps_refs")` |
| `scripts/curriculum/validate_scope_content.py` | 77 | audit_append_call | `result.errors.append(f"non-generation scope {scope.scope_id} must not declare coverage targets")` |
| `scripts/curriculum/validate_scope_content.py` | 79 | audit_append_call | `result.errors.append(f"non-generation scope {scope.scope_id} must not be generation-ready")` |
| `scripts/curriculum/validate_scope_content.py` | 84 | audit_append_call | `result.errors.append(f"active scope {scope.scope_id} is not generation-ready from approved source manifest")` |
| `scripts/curriculum/validate_scope_content.py` | 87 | audit_append_call | `result.errors.append(f"active scope {scope.scope_id} has no caps_refs")` |
| `scripts/curriculum/validate_scope_content.py` | 94 | audit_append_call | `result.errors.append(str(exc))` |
| `scripts/curriculum/validate_scope_content.py` | 103 | audit_append_call | `result.errors.append(str(exc))` |
| `scripts/curriculum/validate_scope_content.py` | 115 | audit_append_call | `result.errors.append(f"item {item.get('item_id')} failed: {[error.rule for error in item_errors]}")` |
| `scripts/curriculum/validate_scope_content.py` | 125 | audit_append_call | `result.errors.append(f"lesson {lesson.get('lesson_id')} has out-of-scope ref {caps_ref}")` |
| `scripts/curriculum/validate_scope_content.py` | 129 | audit_append_call | `result.errors.append(f"lesson {lesson.get('lesson_id')} failed: {validation.failures}")` |
| `scripts/curriculum/validate_scope_content.py` | 137 | audit_append_call | `result.errors.append(f"blueprint {blueprint.get('blueprint_id')} refs invalid: {sorted(refs)}")` |
| `scripts/curriculum/validate_scope_content.py` | 153 | audit_append_call | `result.errors.append(f"study template missing refs: {missing_template_refs}")` |
| `scripts/curriculum/validate_scope_content.py` | 201 | audit_append_call | `result.errors.append(f"{caps_ref} {layer.value} approved target unmet: {approved}/{expected}")` |
| `scripts/curriculum/validate_source_manifest.py` | 50 | audit_append_call | `result.errors.append("duplicate source document_id values")` |
| `scripts/curriculum/validate_source_manifest.py` | 55 | audit_append_call | `result.errors.append(f"source document {document.document_id} is {document.status.value} without source_path")` |
| `scripts/curriculum/validate_source_manifest.py` | 58 | audit_append_call | `result.errors.append(f"source document {document.document_id} is {document.status.value} without source_hash")` |
| `scripts/curriculum/validate_source_manifest.py` | 60 | audit_append_call | `result.errors.append(f"source document {document.document_id} source_sha256/source_hash mismatch")` |
| `scripts/curriculum/validate_source_manifest.py` | 64 | audit_append_call | `result.errors.append(f"source document {document.document_id} path does not exist: {document.source_path}")` |
| `scripts/curriculum/validate_source_manifest.py` | 68 | audit_append_call | `result.errors.append(f"source document {document.document_id} source_hash mismatch")` |
| `scripts/curriculum/validate_source_manifest.py` | 71 | audit_append_call | `result.errors.append(f"source document {document.document_id} is topic_map_approved without reviewer metadata")` |
| `scripts/curriculum/validate_source_manifest.py` | 75 | audit_append_call | `result.errors.append(f"scope {scope.scope_id} does not reference a source document")` |
| `scripts/curriculum/validate_source_manifest.py` | 79 | audit_append_call | `result.errors.append(f"scope {scope.scope_id} references unknown source documents: {missing}")` |
| `scripts/curriculum/validate_source_manifest.py` | 85 | audit_append_call | `result.generation_ready_scope_ids.append(scope.scope_id)` |
| `scripts/curriculum/validate_source_manifest.py` | 87 | audit_append_call | `result.errors.append(f"active scope {scope.scope_id} has no topic_map_approved source document")` |
| `scripts/curriculum/validate_source_manifest.py` | 92 | audit_append_call | `result.warnings.append(f"scope {scope.scope_id} has approved source material but is not in a generation-ready status")` |
| `scripts/curriculum/validate_topic_maps.py` | 68 | audit_append_call | `refs.append(topic["caps_ref"])` |
| `scripts/curriculum/validate_topic_maps.py` | 71 | audit_append_call | `refs.append(subtopic["caps_ref"])` |
| `scripts/curriculum/validate_topic_maps.py` | 87 | audit_append_call | `result.errors.append(f"draft {path.relative_to(ROOT)} filename/scope_id mismatch")` |
| `scripts/curriculum/validate_topic_maps.py` | 92 | audit_append_call | `result.errors.append(f"draft {path.relative_to(ROOT)} references unknown scope {scope_id}")` |
| `scripts/curriculum/validate_topic_maps.py` | 98 | audit_append_call | `result.errors.append(f"draft {scope_id} has unsupported status {status}")` |
| `scripts/curriculum/validate_topic_maps.py` | 100 | audit_append_call | `result.errors.append(f"draft {scope_id} must keep review_required=true until reviewed")` |
| `scripts/curriculum/validate_topic_maps.py` | 104 | audit_append_call | `result.errors.append(f"draft {scope_id} source_document_ids do not match scope source_documents")` |
| `scripts/curriculum/validate_topic_maps.py` | 114 | audit_append_call | `result.errors.append(f"draft {scope_id} references unknown source document {document_id}")` |
| `scripts/curriculum/validate_topic_maps.py` | 117 | audit_append_call | `expected_source_paths.append(document.source_path)` |
| `scripts/curriculum/validate_topic_maps.py` | 120 | audit_append_call | `expected_source_hashes.append(checksum)` |
| `scripts/curriculum/validate_topic_maps.py` | 122 | audit_append_call | `expected_urls.append(document.canonical_source_url)` |
| `scripts/curriculum/validate_topic_maps.py` | 124 | audit_append_call | `expected_object_uris.append(document.object_store_uri)` |
| `scripts/curriculum/validate_topic_maps.py` | 127 | audit_append_call | `expected_text_paths.append(text_record["text_extract_path"])` |
| `scripts/curriculum/validate_topic_maps.py` | 128 | audit_append_call | `expected_text_hashes.append(text_record["text_sha256"])` |
| `scripts/curriculum/validate_topic_maps.py` | 140 | audit_append_call | `result.errors.append(f"draft {scope_id} {key} does not match current source inventory")` |
| `scripts/curriculum/validate_topic_maps.py` | 143 | audit_append_call | `result.errors.append(f"draft {scope_id} grade does not match scope")` |
| `scripts/curriculum/validate_topic_maps.py` | 145 | audit_append_call | `result.errors.append(f"draft {scope_id} subject_code does not match scope")` |
| `scripts/curriculum/validate_topic_maps.py` | 153 | audit_append_call | `result.errors.append(f"runtime map {path.relative_to(ROOT)} missing _meta.{key}")` |
| `scripts/curriculum/validate_topic_maps.py` | 155 | audit_append_call | `result.errors.append(f"runtime map {path.relative_to(ROOT)} missing integer grade")` |
| `scripts/curriculum/validate_topic_maps.py` | 157 | audit_append_call | `result.errors.append(f"runtime map {path.relative_to(ROOT)} missing subject metadata")` |
| `scripts/curriculum/validate_topic_maps.py` | 159 | audit_append_call | `result.errors.append(f"runtime map {path.relative_to(ROOT)} has no terms")` |
| `scripts/curriculum/validate_topic_maps.py` | 163 | audit_append_call | `result.errors.append(f"runtime map {path.relative_to(ROOT)} has duplicate caps_refs: {duplicate_refs}")` |
| `scripts/curriculum/validate_topic_maps.py` | 188 | audit_append_call | `result.errors.append(f"active scope {scope_id} has no runtime topic map")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 29 | audit_events_table | `"audit_events",` |
| `scripts/db_backup_restore_rollback_evidence.py` | 175 | audit_append_call | `out["blockers"].append(f"database smoke failed: {type(exc).__name__}: {exc}")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 178 | audit_append_call | `out["blockers"].append("alembic_version not detected")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 180 | audit_append_call | `out["blockers"].append("no public tables detected")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 219 | audit_append_call | `blockers.append("DB_ROLLBACK_RUN_ID is required")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 222 | audit_append_call | `blockers.append("DB_ROLLBACK_RUN_ID is not numeric")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 225 | audit_append_call | `blockers.append("GitHub CLI is unavailable")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 233 | audit_append_call | `blockers.append(f"unable to read GitHub Actions run {run_id}")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 247 | audit_append_call | `blockers.append(f"run status is {evidence['run_status']}, expected completed")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 249 | audit_append_call | `blockers.append(f"run conclusion is {evidence['conclusion']}, expected success")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 251 | audit_append_call | `blockers.append(f"run SHA {evidence['head_sha']} does not match current commit {expected_sha}")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 253 | audit_append_call | `blockers.append("run URL does not contain run ID")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 286 | audit_append_call | `blockers.append("DB_ROLLBACK_SOURCE_DATABASE_URL is missing, placeholder, local, or invalid")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 288 | audit_append_call | `blockers.append("DB_ROLLBACK_RESTORE_DATABASE_URL is missing, placeholder, local, or invalid")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 290 | audit_append_call | `blockers.append("source and restore database URLs must differ")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 307 | audit_append_call | `blockers.append("pg_dump is not installed")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 309 | audit_append_call | `blockers.append("pg_restore is not installed")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 319 | audit_append_call | `blockers.append(f"backup command failed with exit code {backup.returncode}")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 325 | audit_append_call | `blockers.append("backup dump was not created or was empty")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 331 | audit_append_call | `blockers.append(f"restore command failed with exit code {restore.returncode}")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 337 | audit_append_call | `blockers.append(f"table count mismatch: source={src_smoke['table_count']}, restore={dst_smoke['table_count']}")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 339 | audit_append_call | `blockers.append(f"alembic mismatch: source={src_smoke['alembic_version']}, restore={dst_smoke['alembic_version']}")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 342 | audit_append_call | `blockers.append("key table count mismatches detected")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 349 | audit_append_call | `blockers.append("accepted evidence requires run_drill unless DB_ROLLBACK_ATTACH_ONLY=1")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 351 | audit_append_call | `blockers.append("valid dump SHA256 checksum is required")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 353 | audit_append_call | `blockers.append("non-empty dump size is required")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 355 | audit_append_call | `blockers.append("restore command did not run")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 415 | audit_append_call | `lines.append(f"\| `{table}` \| {status['source_smoke']['key_table_counts'].get(table)} \| {status['restore_smoke']['key_table_counts'].get(table)} \|")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 420 | audit_append_call | `lines.append(f"- `{table}` source={values.get('source')} restore={values.get('restore')}")` |
| `scripts/db_backup_restore_rollback_evidence.py` | 422 | audit_append_call | `lines.append("- None")` |
| `scripts/db_live_only_table_ownership.py` | 129 | audit_append_call | `blockers.append("table missing from ownership policy")` |
| `scripts/db_live_only_table_ownership.py` | 140 | audit_append_call | `blockers.append("domain is missing")` |
| `scripts/db_live_only_table_ownership.py` | 143 | audit_append_call | `blockers.append(f"ownership must be one of {sorted(ALLOWED_OWNERSHIP)}")` |
| `scripts/db_live_only_table_ownership.py` | 146 | audit_append_call | `blockers.append("reason is missing")` |
| `scripts/db_live_only_table_ownership.py` | 149 | audit_append_call | `blockers.append("migration_action is missing")` |
| `scripts/db_live_only_table_ownership.py` | 152 | audit_append_call | `blockers.append("orm_model_required must be boolean")` |
| `scripts/db_live_only_table_ownership.py` | 155 | audit_append_call | `blockers.append("beta_blocking must be boolean")` |
| `scripts/db_live_only_table_ownership.py` | 158 | audit_append_call | `blockers.append("ownership is orm-managed but no ORM table declaration was detected")` |
| `scripts/db_live_only_table_ownership.py` | 161 | audit_append_call | `blockers.append("sql-owned table cannot require ORM model in this policy")` |
| `scripts/db_live_only_table_ownership.py` | 164 | audit_append_call | `blockers.append("migration-required table must remain beta_blocking")` |
| `scripts/db_live_only_table_ownership.py` | 168 | audit_append_call | `records.append(` |
| `scripts/db_live_only_table_ownership.py` | 237 | audit_append_call | `lines.append(` |
| `scripts/db_live_only_table_ownership.py` | 247 | audit_append_call | `lines.append("- None")` |
| `scripts/db_migration_seed_repeatability.py` | 26 | audit_events_table | `"audit_events",` |
| `scripts/db_migration_seed_repeatability.py` | 27 | audit_logs_table | `"audit_logs",` |
| `scripts/db_migration_seed_repeatability.py` | 156 | audit_append_call | `unique.append(row)` |
| `scripts/db_migration_seed_repeatability.py` | 172 | audit_append_call | `lines.append(` |
| `scripts/db_migration_seed_repeatability.py` | 177 | audit_append_call | `lines.append("COMMIT;")` |
| `scripts/db_migration_seed_repeatability.py` | 191 | audit_append_call | `blockers.append("alembic upgrade head --sql failed")` |
| `scripts/db_migration_seed_repeatability.py` | 202 | audit_append_call | `blockers.append(f"expected Alembic head {EXPECTED_HEAD} missing from generated SQL")` |
| `scripts/db_migration_seed_repeatability.py` | 206 | audit_append_call | `blockers.append("required runtime table DDL missing: " + ", ".join(missing_tables))` |
| `scripts/db_migration_seed_repeatability.py` | 209 | audit_append_call | `blockers.append("generated Supabase SQL still contains non-SQL chatter")` |
| `scripts/db_migration_seed_repeatability.py` | 212 | audit_append_call | `blockers.append("generated Supabase SQL still contains broken null IRT seed rows")` |
| `scripts/db_migration_seed_repeatability.py` | 215 | audit_append_call | `blockers.append("generated Supabase SQL still references missing Supabase role eduboost_app")` |
| `scripts/db_migration_seed_repeatability.py` | 218 | audit_append_call | `blockers.append(f"expected {EXPECTED_IRT_ROWS} unique IRT seed rows, generated {unique_rows}")` |
| `scripts/db_migration_seed_repeatability.py` | 221 | audit_append_call | `blockers.append("IRT seed SQL is not idempotent")` |
| `scripts/db_migration_seed_repeatability.py` | 279 | audit_append_call | `lines.append(f"\| `{table}` \| {present} \|")` |
| `scripts/db_migration_seed_repeatability.py` | 301 | audit_append_call | `lines.append("- None")` |
| `scripts/db_migration_seed_repeatability.py` | 336 | audit_append_call | `lines.append(line)` |
| `scripts/deduplicate_makefile_targets.py` | 64 | audit_append_call | `occurrences[m.group(1)].append(i)` |
| `scripts/deduplicate_makefile_targets.py` | 89 | audit_append_call | `block.append(i)` |
| `scripts/deduplicate_makefile_targets.py` | 149 | audit_append_call | `new_lines.append(phony_line)` |
| `scripts/deduplicate_makefile_targets.py` | 152 | audit_append_call | `new_lines.append(line)` |
| `scripts/diag_deep_health_runtime_evidence.py` | 121 | audit_append_call | `items.append((prefix, obj))` |
| `scripts/diag_deep_health_runtime_evidence.py` | 132 | audit_log_identifier | `"audit": ("audit", "audit_log", "auditlog"),` |
| `scripts/diag_deep_health_runtime_evidence.py` | 163 | audit_append_call | `blockers.append("DIAG_DEEP_HEALTH_RUN_ID is required for accepted evidence")` |
| `scripts/diag_deep_health_runtime_evidence.py` | 166 | audit_append_call | `blockers.append("DIAG_DEEP_HEALTH_RUN_ID is not numeric")` |
| `scripts/diag_deep_health_runtime_evidence.py` | 169 | audit_append_call | `blockers.append("GitHub CLI is unavailable or not authenticated")` |
| `scripts/diag_deep_health_runtime_evidence.py` | 173 | audit_append_call | `blockers.append(f"unable to read GitHub Actions run {run_id}")` |
| `scripts/diag_deep_health_runtime_evidence.py` | 181 | audit_append_call | `blockers.append("run URL does not contain numeric run ID")` |
| `scripts/diag_deep_health_runtime_evidence.py` | 183 | audit_append_call | `blockers.append(f"GitHub Actions run status is {run_status or 'missing'}, expected completed")` |
| `scripts/diag_deep_health_runtime_evidence.py` | 185 | audit_append_call | `blockers.append(f"GitHub Actions run conclusion is {conclusion or 'missing'}, expected success")` |
| `scripts/diag_deep_health_runtime_evidence.py` | 187 | audit_append_call | `blockers.append(f"GitHub Actions run SHA {head_sha or 'missing'} does not match current commit {expected_sha}")` |
| `scripts/diag_deep_health_runtime_evidence.py` | 189 | audit_append_call | `blockers.append("workflow name is missing")` |
| `scripts/diag_deep_health_runtime_evidence.py` | 191 | audit_append_call | `blockers.append("auth refresh DB proof workflow is not valid deep-health runtime evidence")` |
| `scripts/diag_deep_health_runtime_evidence.py` | 204 | audit_append_call | `blockers.append("deep health URL is missing, non-HTTPS, localhost/example, or placeholder")` |
| `scripts/diag_deep_health_runtime_evidence.py` | 206 | audit_append_call | `blockers.append("deep health URL must target /api/v2/health/deep or an equivalent /deep endpoint")` |
| `scripts/diag_deep_health_runtime_evidence.py` | 208 | audit_append_call | `blockers.append("DIAG_DEEP_HEALTH_TEST_COMMAND is missing or placeholder")` |
| `scripts/diag_deep_health_runtime_evidence.py` | 211 | audit_append_call | `blockers.append(f"deep health HTTP probe error: {probe.error}")` |
| `scripts/diag_deep_health_runtime_evidence.py` | 213 | audit_append_call | `blockers.append(f"deep health HTTP status is {probe.status_code}, expected 200")` |
| `scripts/diag_deep_health_runtime_evidence.py` | 215 | audit_append_call | `blockers.append("deep health HTTP probe was not attempted")` |
| `scripts/diag_deep_health_runtime_evidence.py` | 219 | audit_append_call | `blockers.append(f"DIAG_DEEP_HEALTH_{component.upper()}_RESULT must be passed")` |
| `scripts/diag_deep_health_runtime_evidence.py` | 242 | audit_append_call | `lines.append(f"\| `{component}` \| `{result}` \|")` |
| `scripts/diag_deep_health_runtime_evidence.py` | 246 | audit_append_call | `lines.append(f"\| `{component}` \| `{signal}` \|")` |
| `scripts/diag_deep_health_runtime_evidence.py` | 248 | audit_append_call | `lines.append("\| `-` \| `none inferred` \|")` |
| `scripts/diag_deep_health_runtime_evidence.py` | 250 | audit_append_call | `lines.extend(f"- {blocker}" for blocker in status.blockers) if status.blockers else lines.append("- None")` |
| `scripts/diagnostic_item_bank_canonicality.py` | 110 | audit_append_call | `records.append(` |
| `scripts/diagnostic_item_bank_canonicality.py` | 131 | audit_append_call | `blockers.append("diagnostic item-bank canonicality policy file is missing")` |
| `scripts/diagnostic_item_bank_canonicality.py` | 136 | audit_append_call | `blockers.append(f"policy missing marker: {marker}")` |
| `scripts/diagnostic_item_bank_canonicality.py` | 142 | audit_append_call | `blockers.append("no diagnostic_items references found; runtime-required policy is unsupported")` |
| `scripts/diagnostic_item_bank_canonicality.py` | 145 | audit_append_call | `blockers.append(` |
| `scripts/diagnostic_item_bank_canonicality.py` | 196 | audit_append_call | `lines.append(f"\| `{marker}` \| {present} \|")` |
| `scripts/diagnostic_item_bank_canonicality.py` | 210 | audit_append_call | `lines.append(` |
| `scripts/diagnostic_item_bank_canonicality.py` | 214 | audit_append_call | `lines.append("\| `-` \| 0 \| `none` \|")` |
| `scripts/diagnostic_item_bank_canonicality.py` | 220 | audit_append_call | `lines.append("- None")` |
| `scripts/diagnostic_score_live_audit.py` | 358 | audit_append_call | `unsupported.append(column.name)` |
| `scripts/diagnostic_score_live_audit.py` | 360 | audit_append_call | `insert_columns.append(column.name)` |
| `scripts/diagnostic_score_live_audit.py` | 361 | audit_append_call | `select_exprs.append(expr)` |
| `scripts/diagnostic_score_live_audit.py` | 412 | audit_append_call | `blockers.append("DIAG_SCORE_RUN_ID is required for accepted evidence")` |
| `scripts/diagnostic_score_live_audit.py` | 416 | audit_append_call | `blockers.append("DIAG_SCORE_RUN_ID is not numeric")` |
| `scripts/diagnostic_score_live_audit.py` | 420 | audit_append_call | `blockers.append("GitHub CLI is unavailable or not authenticated")` |
| `scripts/diagnostic_score_live_audit.py` | 425 | audit_append_call | `blockers.append(f"unable to read GitHub Actions run {run_id}")` |
| `scripts/diagnostic_score_live_audit.py` | 435 | audit_append_call | `blockers.append("run URL does not contain numeric run ID")` |
| `scripts/diagnostic_score_live_audit.py` | 437 | audit_append_call | `blockers.append(f"GitHub Actions run status is {run_status or 'missing'}, expected completed")` |
| `scripts/diagnostic_score_live_audit.py` | 439 | audit_append_call | `blockers.append(f"GitHub Actions run conclusion is {conclusion or 'missing'}, expected success")` |
| `scripts/diagnostic_score_live_audit.py` | 441 | audit_append_call | `blockers.append(f"GitHub Actions run SHA {head_sha or 'missing'} does not match current commit {expected_sha}")` |
| `scripts/diagnostic_score_live_audit.py` | 443 | audit_append_call | `blockers.append("workflow name is missing")` |
| `scripts/diagnostic_score_live_audit.py` | 475 | audit_append_call | `blockers.append("DIAG_SCORE_DATABASE_URL/DATABASE_URL is missing, non-Postgres async, local, example, or placeholder")` |
| `scripts/diagnostic_score_live_audit.py` | 493 | audit_append_call | `blockers.append("diagnostic_items table is missing")` |
| `scripts/diagnostic_score_live_audit.py` | 495 | audit_append_call | `blockers.append("irt_items table is missing")` |
| `scripts/diagnostic_score_live_audit.py` | 508 | audit_append_call | `blockers.append(f"irt_items has {irt_count} rows, expected at least {EXPECTED_IRT_MIN_ROWS}")` |
| `scripts/diagnostic_score_live_audit.py` | 513 | audit_append_call | `blockers.append("DIAG_SCORE_ALLOW_BRIDGE_SEED must be 1 before mutating diagnostic_items")` |
| `scripts/diagnostic_score_live_audit.py` | 515 | audit_append_call | `blockers.append("cannot bridge-seed without both diagnostic_items and irt_items")` |
| `scripts/diagnostic_score_live_audit.py` | 523 | audit_append_call | `blockers.append(` |
| `scripts/diagnostic_score_live_audit.py` | 531 | audit_append_call | `blockers.append("diagnostic_items has 0 rows; runtime-required item bank is not seeded")` |
| `scripts/diagnostic_score_live_audit.py` | 537 | audit_append_call | `blockers.append(f"DB connection/query error: {exc}")` |
| `scripts/diagnostic_score_live_audit.py` | 546 | audit_append_call | `blockers.append("DIAG_SCORE_TEST_COMMAND is missing or placeholder")` |
| `scripts/diagnostic_score_live_audit.py` | 548 | audit_append_call | `blockers.append("DIAG_SCORE_SEED_RESULT must be passed")` |
| `scripts/diagnostic_score_live_audit.py` | 550 | audit_append_call | `blockers.append("DIAG_SCORE_SCORING_RESULT must be passed")` |
| `scripts/diagnostic_score_live_audit.py` | 552 | audit_append_call | `blockers.append("DIAG_SCORE_AUDIT_RESULT must be passed")` |
| `scripts/diagnostic_score_live_audit.py` | 620 | audit_append_call | `lines.append("- None")` |
| `scripts/diagnostic_score_live_audit.py` | 626 | audit_append_call | `lines.append("- None")` |
| `scripts/diagnostic_score_live_audit.py` | 630 | audit_append_call | `lines.append(` |
| `scripts/diagnostic_score_live_audit.py` | 638 | audit_append_call | `lines.append("- None")` |
| `scripts/docs_inventory.py` | 84 | audit_append_call | `headings.append(` |
| `scripts/docs_inventory.py` | 124 | audit_append_call | `statuses.append(status)` |
| `scripts/docs_inventory.py` | 133 | audit_append_call | `dates.append(value)` |
| `scripts/docs_inventory.py` | 142 | audit_append_call | `markdown_spans.append(match.span(2))` |
| `scripts/docs_inventory.py` | 143 | audit_append_call | `links.append(` |
| `scripts/docs_inventory.py` | 154 | audit_append_call | `links.append({"text": match.group(0), "target": match.group(0), "kind": "external"})` |
| `scripts/docs_inventory.py` | 163 | audit_append_call | `references.append(value)` |
| `scripts/docs_inventory.py` | 174 | audit_append_call | `refs.append(candidate)` |
| `scripts/docs_inventory.py` | 217 | audit_append_call | `paths.append(resolved)` |
| `scripts/docs_inventory.py` | 251 | audit_append_call | `items.append(` |
| `scripts/docs_inventory.py` | 308 | audit_append_call | `lines.append(f"\| `{category}` \| {count} \|")` |
| `scripts/docs_inventory.py` | 312 | audit_append_call | `lines.append(f"\| `{item.path}` \| `{item.category}` \| {item.title} \| {item.size_bytes} \| {item.generated} \|")` |
| `scripts/docs_inventory.py` | 331 | audit_append_call | `lines.append(f"\| `{path}` \| {path not in missing} \|")` |
| `scripts/docs_inventory.py` | 337 | audit_append_call | `lines.append("- No required documentation intelligence gaps detected.")` |
| `scripts/docs_inventory.py` | 405 | audit_append_call | `errors.append("docs/docs_inventory.json is stale")` |
| `scripts/docs_inventory.py` | 407 | audit_append_call | `errors.append("docs/docs_inventory.json is missing")` |
| `scripts/docs_inventory.py` | 410 | audit_append_call | `errors.append("docs/docs_inventory.md is missing")` |
| `scripts/docs_inventory.py` | 412 | audit_append_call | `errors.append("docs/docs_gap_report.md is missing")` |
| `scripts/docs_inventory.py` | 414 | audit_append_call | `errors.append("docs/docs_generation_plan.md is missing")` |
| `scripts/docs_inventory.py` | 417 | audit_append_call | `errors.append("Missing important docs: " + ", ".join(expected.missing_important_docs))` |
| `scripts/ensure_irt_seed.py` | 88 | audit_append_call | `rows.append(` |
| `scripts/evaluate_pedagogy.py` | 88 | audit_append_call | `cases.append(BenchmarkCase(**record))` |
| `scripts/evaluate_pedagogy.py` | 171 | audit_append_call | `case_results.append(result)` |
| `scripts/evidence_attachment_runbook.py` | 84 | audit_append_call | `lines.append(f"\| `{command.id}` \| `{command.category}` \| {command.purpose} \| `{command.command}` \| {command.expected_until_evidence} \|")` |
| `scripts/evidence_registry.py` | 66 | audit_append_call | `findings.append(current)` |
| `scripts/evidence_registry.py` | 78 | audit_append_call | `findings.append(current)` |
| `scripts/evidence_registry.py` | 89 | audit_append_call | `errors.append(f"duplicate finding id: {finding.id}")` |
| `scripts/evidence_registry.py` | 93 | audit_append_call | `errors.append(f"{finding.id}: invalid proof_status {finding.proof_status!r}")` |
| `scripts/evidence_registry.py` | 96 | audit_append_call | `errors.append(f"{finding.id}: P0/P1 item cannot close on static-passing proof")` |
| `scripts/evidence_registry.py` | 99 | audit_append_call | `errors.append(f"{finding.id}: {finding.proof_status} requires last_verified_commit")` |
| `scripts/evidence_registry.py` | 103 | audit_append_call | `errors.append(f"{finding.id}: production-ready requires evidence_file")` |
| `scripts/evidence_registry.py` | 105 | audit_append_call | `errors.append(f"{finding.id}: production-ready cannot have closure_blocker")` |
| `scripts/evidence_registry.py` | 109 | audit_append_call | `errors.append(f"{finding.id}: beta-blocking incomplete item must name closure_blocker")` |
| `scripts/evidence_registry.py` | 118 | audit_append_call | `errors.append(f"{finding.id}: evidence_file missing: {finding.evidence_file}")` |
| `scripts/execute_disposable_db_schema_proof.py` | 27 | audit_append_call | `code,out=run(cmd); overall=max(overall,code); lines.append(f"\| `{' '.join(cmd).replace(url,'<DATABASE_URL>')}` \| {code} \|"); lines+=["","```text",out.rstrip(),"```"]` |
| `scripts/external_approval_gate.py` | 167 | audit_append_call | `blockers.append(f"decision must be {meta['required_decision']}")` |
| `scripts/external_approval_gate.py` | 169 | audit_append_call | `blockers.append("approver is pending")` |
| `scripts/external_approval_gate.py` | 171 | audit_append_call | `blockers.append("evidence URL is pending or invalid")` |
| `scripts/external_approval_gate.py` | 173 | audit_append_call | `blockers.append("date verified is pending")` |
| `scripts/external_approval_gate.py` | 222 | audit_append_call | `lines.append(` |
| `scripts/external_approval_gate.py` | 231 | audit_append_call | `lines.append("- None")` |
| `scripts/final_gate_classifier.py` | 165 | audit_append_call | `findings.append(item)` |
| `scripts/final_gate_classifier.py` | 197 | audit_append_call | `findings.append(` |
| `scripts/final_gate_classifier.py` | 276 | audit_append_call | `required_actions.append(action)` |
| `scripts/final_gate_classifier.py` | 320 | audit_append_call | `lines.append(f"\| `{surface.name}` \| `{surface.status}` \| `{surface.detail}` \|")` |
| `scripts/final_gate_classifier.py` | 332 | audit_append_call | `lines.append(` |
| `scripts/final_gate_classifier.py` | 348 | audit_append_call | `lines.append(` |
| `scripts/final_gate_classifier.py` | 354 | audit_append_call | `lines.append("\| `-` \| `-` \| False \| False \| False \| False \| none \|")` |
| `scripts/final_gate_classifier.py` | 360 | audit_append_call | `lines.append("- None")` |
| `scripts/generate_ai_prompt_surface_inventory.py` | 49 | audit_append_call | `surfaces.append(PromptSurface(str(path.relative_to(REPO_ROOT)), markers))` |
| `scripts/generate_ai_prompt_surface_inventory.py` | 76 | audit_append_call | `lines.append("\| _none found_ \| _none_ \|")` |
| `scripts/generate_ai_prompt_surface_inventory.py` | 79 | audit_append_call | `lines.append(f"\| `{surface.path}` \| `{', '.join(surface.markers)}` \|")` |
| `scripts/generate_audit_callsite_inventory.py` | 42 | audit_append_call | `files.append(path)` |
| `scripts/generate_audit_callsite_inventory.py` | 57 | audit_append_call | `rows.append(` |
| `scripts/generate_audit_callsite_inventory.py` | 79 | audit_append_call | `output.append(f"\| `{row.path}` \| {row.line} \| {row.category} \| `{text}` \|")` |
| `scripts/generate_audit_callsite_inventory.py` | 89 | audit_logs_table | `"- [ ] Identify any `audit_logs` data-retention requirement.",` |
| `scripts/generate_auth_boundary_debt_report.py` | 25 | audit_append_call | `modules.append(node.module or "")` |
| `scripts/generate_auth_extraction_followup.py` | 22 | audit_append_call | `modules.append(node.module or "")` |
| `scripts/generate_auth_http_success_scope_report.py` | 25 | audit_append_call | `rows.append(` |
| `scripts/generate_auth_lifecycle_extraction_report.py` | 46 | audit_append_call | `lines.append(f"\| `{method}` \| {delegated} \|")` |
| `scripts/generate_auth_service_extraction_report.py` | 25 | audit_append_call | `modules.append(node.module or "")` |
| `scripts/generate_auth_service_ownership_report.py` | 59 | audit_append_call | `lines.append("")` |
| `scripts/generate_backend_consolidation_evidence_manifest.py` | 62 | audit_append_call | `rows.append(ManifestRow(relative, True, path.stat().st_size, _sha256(path)))` |
| `scripts/generate_backend_consolidation_evidence_manifest.py` | 64 | audit_append_call | `rows.append(ManifestRow(relative, False, 0, ""))` |
| `scripts/generate_backend_consolidation_evidence_manifest.py` | 80 | audit_append_call | `lines.append(` |
| `scripts/generate_backend_consolidation_execution_report.py` | 48 | audit_append_call | `rows.append((name, code, " ".join(command), output))` |
| `scripts/generate_backend_consolidation_execution_report.py` | 60 | audit_append_call | `lines.append(f"\| {name} \| {code} \| `{command}` \|")` |
| `scripts/generate_backend_consolidation_implementation_report.py` | 48 | audit_append_call | `rows.append((name, code, " ".join(command), output))` |
| `scripts/generate_backend_consolidation_implementation_report.py` | 59 | audit_append_call | `lines.append(f"\| {name} \| {code} \| `{command}` \|")` |
| `scripts/generate_backend_consolidation_progress_report.py` | 43 | audit_append_call | `rows.append((name, code, " ".join(command), output))` |
| `scripts/generate_backend_consolidation_progress_report.py` | 55 | audit_append_call | `lines.append(f"\| {name} \| {code} \| `{command}` \|")` |
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
| `scripts/generate_backend_first_wiring_candidates_report.py` | 41 | audit_append_call | `rows.append((name, code, " ".join(command), output))` |
| `scripts/generate_backend_first_wiring_candidates_report.py` | 53 | audit_append_call | `lines.append(f"\| {name} \| {code} \| `{command}` \|")` |
| `scripts/generate_backend_implementation_371_375_report.py` | 42 | audit_append_call | `rows.append((name, code, " ".join(command), output))` |
| `scripts/generate_backend_implementation_371_375_report.py` | 54 | audit_append_call | `lines.append(f"\| {name} \| {code} \| `{command}` \|")` |
| `scripts/generate_backend_runtime_compatibility_report.py` | 48 | audit_append_call | `rows.append((name, code, " ".join(command), output))` |
| `scripts/generate_backend_runtime_compatibility_report.py` | 60 | audit_append_call | `lines.append(f"\| {name} \| {code} \| `{command}` \|")` |
| `scripts/generate_backend_runtime_enablement_report.py` | 62 | audit_append_call | `lines.append(f"\| `{relative}` \| `{_sha256(path)}` \|")` |
| `scripts/generate_backend_runtime_enablement_report.py` | 64 | audit_append_call | `lines.append(f"\| `{relative}` \| `MISSING` \|")` |
| `scripts/generate_backend_runtime_enablement_report.py` | 75 | audit_append_call | `rows.append((name, code, " ".join(command), output))` |
| `scripts/generate_backend_runtime_enablement_report.py` | 89 | audit_append_call | `lines.append(f"\| {name} \| {code} \| `{command}` \|")` |
| `scripts/generate_backend_runtime_integration_readiness_report.py` | 56 | audit_append_call | `lines.append(f"\| `{relative}` \| `{_sha(path) if path.exists() else 'MISSING'}` \|")` |
| `scripts/generate_backend_runtime_integration_readiness_report.py` | 67 | audit_append_call | `rows.append((name, code, " ".join(command), output))` |
| `scripts/generate_backend_runtime_integration_readiness_report.py` | 81 | audit_append_call | `lines.append(f"\| {name} \| {code} \| `{command}` \|")` |
| `scripts/generate_backend_runtime_probe_report.py` | 48 | audit_append_call | `rows.append((name, code, " ".join(command), output))` |
| `scripts/generate_backend_runtime_probe_report.py` | 59 | audit_append_call | `lines.append(f"\| {name} \| {code} \| `{command}` \|")` |
| `scripts/generate_backend_runtime_wiring_cases_report.py` | 41 | audit_append_call | `rows.append((name, code, " ".join(command), output))` |
| `scripts/generate_backend_runtime_wiring_cases_report.py` | 53 | audit_append_call | `lines.append(f"\| {name} \| {code} \| `{command}` \|")` |
| `scripts/generate_backend_runtime_wiring_preflight_report.py` | 42 | audit_append_call | `rows.append((name, code, " ".join(command), output))` |
| `scripts/generate_backend_runtime_wiring_preflight_report.py` | 54 | audit_append_call | `lines.append(f"\| {name} \| {code} \| `{command}` \|")` |
| `scripts/generate_beta_readiness_status.py` | 40 | audit_append_call | `lines.append(f"\| {name} \| {item.get('status')} \|")` |
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
| `scripts/generate_dependency_pin_report.py` | 46 | audit_append_call | `blockers.append(f"{path.relative_to(ROOT)}:{lineno}: {line.strip()}")` |
| `scripts/generate_dependency_pin_report.py` | 47 | audit_append_call | `rows.append({"file": str(path.relative_to(ROOT)), "line": lineno, "classification": classification, "text": line.strip()})` |
| `scripts/generate_dependency_pin_report.py` | 59 | audit_append_call | `lines.append("- None")` |
| `scripts/generate_first_audit_runtime_wiring_report.py` | 42 | audit_append_call | `rows.append((name, code, " ".join(command), output))` |
| `scripts/generate_first_audit_runtime_wiring_report.py` | 54 | audit_append_call | `lines.append(f"\| {name} \| {code} \| `{command}` \|")` |
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
| `scripts/generate_items.py` | 269 | audit_append_call | `seed["items"].append(item)` |
| `scripts/generate_learner_authz_matrix.py` | 127 | audit_append_call | `rows.append(` |
| `scripts/generate_learner_authz_matrix.py` | 161 | audit_append_call | `lines.append(` |
| `scripts/generate_learner_authz_matrix.py` | 169 | audit_append_call | `lines.append(f"- `{row.router}` `{row.method} {row.path}` via `{row.function}`")` |
| `scripts/generate_legacy_learner_access_guard_report.py` | 18 | audit_append_call | `rows.append({"path": str(path.relative_to(ROOT)), "count": text.count("assert_can_access_learner")})` |
| `scripts/generate_legacy_learner_access_guard_report.py` | 29 | audit_append_call | `lines.append(f"\| `{row['path']}` \| {row['count']} \|")` |
| `scripts/generate_legacy_learner_access_guard_report.py` | 31 | audit_append_call | `lines.append("\| - \| 0 \|")` |
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
| `scripts/generate_release_owner_beta_go_no_go.py` | 27 | audit_logs_table | `"This memo does not approve production launch, destructive database changes, consent-table merge, audit_logs drop, or public mutating health probes.", "",` |
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
| `scripts/generate_router_boundary_matrix.py` | 26 | audit_append_call | `modules.append(node.module or "")` |
| `scripts/generate_router_boundary_matrix.py` | 42 | audit_append_call | `allowed.append(module)` |
| `scripts/generate_router_boundary_matrix.py` | 44 | audit_append_call | `violations.append(module)` |
| `scripts/generate_router_boundary_matrix.py` | 45 | audit_append_call | `rows.append({` |
| `scripts/generate_router_boundary_matrix.py` | 71 | audit_append_call | `lines.append(f"\| `{row['router']}` \| {row['p0_router']} \| {repo} \| {allowed} \| {violations} \|")` |
| `scripts/generate_router_service_dependency_map.py` | 21 | audit_append_call | `modules.append(node.module or "")` |
| `scripts/generate_router_service_dependency_map.py` | 32 | audit_append_call | `rows.append({` |
| `scripts/generate_router_service_dependency_map.py` | 55 | audit_append_call | `lines.append(` |
| `scripts/generate_runtime_wiring_431_450_report.py` | 42 | audit_append_call | `rows.append((name, code, " ".join(command), output))` |
| `scripts/generate_runtime_wiring_431_450_report.py` | 54 | audit_append_call | `lines.append(f"\| {name} \| {code} \| `{command}` \|")` |
| `scripts/generate_service_boundary_inventory.py` | 35 | audit_append_call | `rows.append({"path": str(path.relative_to(ROOT)), "classification": classify(path)})` |
| `scripts/generate_service_boundary_inventory.py` | 45 | audit_append_call | `lines.append(f"\| `{row['path']}` \| {row['classification']} \|")` |
| `scripts/generate_service_family_map.py` | 74 | audit_append_call | `rows.append({` |
| `scripts/generate_service_family_map.py` | 83 | audit_append_call | `grouped[row["domain"]].append(row)` |
| `scripts/generate_service_family_map.py` | 101 | audit_append_call | `lines.append(` |
| `scripts/generate_staging_smoke_evidence_manifest.py` | 63 | audit_append_call | `lines.append(f"\| {entry.name} \| `{entry.command}` \|")` |
| `scripts/generate_truthful_beta_readiness_status.py` | 71 | audit_append_call | `lines.append(f"\| {gate} \| {data.get('status')} \| {data.get('integrity_status')} \| {data.get('evidence_source_type', 'unknown')} \|")` |
| `scripts/generate_truthful_beta_readiness_status.py` | 76 | audit_append_call | `lines.append("- None")` |
| `scripts/generate_truthful_release_owner_beta_go_no_go.py` | 38 | audit_append_call | `lines.append("- None")` |
| `scripts/generate_truthful_release_owner_beta_go_no_go.py` | 43 | audit_logs_table | `"This memo does not approve production launch, destructive database changes, consent-table merge, audit_logs drop, public mutating health probes, or synthetic evidence substitution.",` |
| `scripts/ingestion/api.py` | 133 | audit_append_call | `result.append(SourceInfo(` |
| `scripts/ingestion/main.py` | 356 | audit_append_call | `resolved.append(sid)` |
| `scripts/ingestion/pipeline/__init__.py` | 181 | audit_append_call | `self._raw_buf.append(raw)` |
| `scripts/ingestion/pipeline/__init__.py` | 182 | audit_append_call | `self._norm_buf.append(aligned)` |
| `scripts/ingestion/pipeline/__init__.py` | 183 | audit_append_call | `self._train_buf.append(record)` |
| `scripts/ingestion/pipeline/__init__.py` | 234 | audit_append_call | `by_source.setdefault(rec.source_id, []).append(rec)` |
| `scripts/ingestion/pipeline/caps_aligner.py` | 148 | audit_append_call | `results.append(align(item))` |
| `scripts/ingestion/pipeline/caps_aligner.py` | 151 | audit_append_call | `results.append(item)` |
| `scripts/ingestion/pipeline/normaliser.py` | 144 | audit_append_call | `results.append(norm)` |
| `scripts/ingestion/pipeline/storage.py` | 290 | audit_append_call | `where_parts.append("subject = :subject")` |
| `scripts/ingestion/pipeline/storage.py` | 293 | audit_append_call | `where_parts.append("grade = :grade")` |
| `scripts/ingestion/pipeline/storage.py` | 296 | audit_append_call | `where_parts.append("caps_phase = :caps_phase")` |
| `scripts/ingestion/pipeline/training_formatter.py` | 108 | audit_append_call | `records.append(rec)` |
| `scripts/ingestion/pipeline/training_formatter.py` | 325 | audit_append_call | `tags.append(f"grade-{c.grade}")` |
| `scripts/ingestion/pipeline/training_formatter.py` | 327 | audit_append_call | `tags.append(f"phase-{c.caps_phase}")` |
| `scripts/ingestion/pipeline/training_formatter.py` | 329 | audit_append_call | `tags.append(f"subject-{c.subject}")` |
| `scripts/ingestion/pipeline/training_formatter.py` | 331 | audit_append_call | `tags.append(f"topic-{c.caps_topic_code}")` |
| `scripts/ingestion/pipeline/training_formatter.py` | 333 | audit_append_call | `tags.append(f"jurisdiction-{c.jurisdiction}")` |
| `scripts/ingestion/pipeline/training_formatter.py` | 335 | audit_append_call | `tags.append(f"difficulty-{c.difficulty.value}")` |
| `scripts/ingestion/pipeline/training_formatter.py` | 337 | audit_append_call | `tags.append(f"lang-{c.language}")` |
| `scripts/ingestion/pipeline/training_formatter.py` | 338 | audit_append_call | `tags.append(f"source-{c.source_id}")` |
| `scripts/ingestion/pipeline/training_formatter.py` | 339 | audit_append_call | `tags.append(f"type-{c.content_type.value}")` |
| `scripts/ingestion/queue_manager.py` | 285 | audit_append_call | `jobs.append(json.loads(payload))` |
| `scripts/ingestion/run_pipeline.py` | 57 | audit_append_call | `errors.append(f"{doc_id}: page_count={pages}")` |
| `scripts/ingestion/run_pipeline.py` | 59 | audit_append_call | `errors.append(f"{doc_id}: char_count={chars}")` |
| `scripts/ingestion/run_pipeline.py` | 62 | audit_append_call | `errors.append(f"{doc_id}: missing text file {text_path}")` |
| `scripts/ingestion/run_pipeline.py` | 71 | audit_append_call | `args.append("--strict")` |
| `scripts/ingestion/run_pipeline.py` | 91 | audit_append_call | `args.append("--commit")` |
| `scripts/ingestion/run_pipeline.py` | 93 | audit_append_call | `args.append("--refresh")` |
| `scripts/ingestion/run_pipeline.py` | 110 | audit_append_call | `args.append("--commit")` |
| `scripts/ingestion/run_pipeline.py` | 150 | audit_append_call | `report["results"].append(stage_1_inventory(strict=args.strict))` |
| `scripts/ingestion/run_pipeline.py` | 152 | audit_append_call | `report["results"].append(stage_2_download(commit=args.commit, refresh=args.refresh))` |
| `scripts/ingestion/run_pipeline.py` | 154 | audit_append_call | `report["results"].append(` |
| `scripts/ingestion/run_pipeline.py` | 163 | audit_append_call | `report["results"].append(stage_4_extract(commit=args.commit))` |
| `scripts/ingestion/sources/base.py` | 242 | audit_append_call | `responses.append({` |
| `scripts/ingestion/sources/base.py` | 255 | audit_append_call | `pending_reads.append(asyncio.create_task(_read()))` |
| `scripts/ingestion/sources/bbc_bitesize.py` | 130 | audit_append_call | `links.append(full)` |
| `scripts/ingestion/sources/bbc_bitesize.py` | 156 | audit_append_call | `key_points.append(text)` |
| `scripts/ingestion/sources/bbc_bitesize.py` | 214 | audit_append_call | `items.append({"question": q, "options": opts, "answer": correct})` |
| `scripts/ingestion/sources/ck12.py` | 241 | audit_append_call | `questions.append({` |
| `scripts/ingestion/sources/commonlit.py` | 125 | audit_append_call | `links.append(full)` |
| `scripts/ingestion/sources/commonlit.py` | 229 | audit_append_call | `questions.append({` |
| `scripts/ingestion/sources/dbe_south_africa.py` | 113 | audit_append_call | `pages.append({"page": page_num, "text": text.strip()})` |
| `scripts/ingestion/sources/dbe_south_africa.py` | 211 | audit_append_call | `docs.append({` |
| `scripts/ingestion/sources/khan_academy.py` | 105 | audit_append_call | `links.append((match, kind))` |
| `scripts/ingestion/sources/khan_academy.py` | 224 | audit_append_call | `questions.append(parsed)` |
| `scripts/ingestion/sources/libretexts.py` | 152 | audit_append_call | `links.append(full)` |
| `scripts/ingestion/sources/libretexts.py` | 198 | audit_append_call | `examples.append(text)` |
| `scripts/ingestion/sources/siyavula.py` | 136 | audit_append_call | `links.append((full_url, text))` |
| `scripts/ingestion/sources/siyavula.py` | 143 | audit_append_call | `unique.append((u, t))` |
| `scripts/ingestion/sources/siyavula.py` | 175 | audit_append_call | `worked_examples.append({` |
| `scripts/ingestion/sources/siyavula.py` | 185 | audit_append_call | `exercises.append(text)` |
| `scripts/ingestion/sources/wced.py` | 138 | audit_append_call | `links.append((full, title))` |
| `scripts/ingestion/sources/wced.py` | 210 | audit_append_call | `pages.append({"page": page_num, "text": text.strip()})` |
| `scripts/inspect_auth_router_boundary.py` | 23 | audit_append_call | `modules.append(node.module or "")` |
| `scripts/inspect_auth_router_boundary.py` | 36 | audit_append_call | `rows.append({` |
| `scripts/inspect_auth_token_claims.py` | 35 | audit_append_call | `rows.append(node.module or "")` |
| `scripts/inspect_diagnostics_and_jobs_integrity.py` | 32 | audit_append_call | `modules.append(node.module or "")` |
| `scripts/inspect_learner_routes.py` | 106 | audit_append_call | `candidates.append(` |
| `scripts/inspect_learner_routes.py` | 128 | audit_append_call | `references.append(` |
| `scripts/inspect_learner_routes.py` | 156 | audit_append_call | `lines.append(` |
| `scripts/inspect_learner_routes.py` | 161 | audit_append_call | `lines.append("\| — \| — \| — \| — \| — \| no route candidates found \|")` |
| `scripts/inspect_learner_routes.py` | 175 | audit_append_call | `lines.append(f"\| `{reference.file}` \| {reference.line} \| `{safe_text}` \|")` |
| `scripts/inspect_learner_routes.py` | 178 | audit_append_call | `lines.append(f"\| — \| — \| `{len(references) - 200} additional references omitted` \|")` |
| `scripts/inspect_lesson_object_authorization.py` | 23 | audit_append_call | `rows.append({"name": node.name, "args": args, "lineno": node.lineno})` |
| `scripts/inspect_popia_consent_lifecycle.py` | 34 | audit_append_call | `imports.append(node.module or "")` |
| `scripts/integrate_patch.py` | 59 | audit_append_call | `staged_conflicts.append(target)` |
| `scripts/integrate_patch.py` | 64 | audit_append_call | `moved.append(dest_file)` |
| `scripts/inventory_services.py` | 92 | audit_append_call | `found_duplicates.append((dup_path, canonical_rel))` |
| `scripts/jwt_secret_rotation_evidence.py` | 159 | audit_append_call | `blockers.append(f"JWT self-test raised {type(exc).__name__}: {exc}")` |
| `scripts/jwt_secret_rotation_evidence.py` | 160 | audit_append_call | `if not access_ok: blockers.append("access token issue/verify self-test failed")` |
| `scripts/jwt_secret_rotation_evidence.py` | 161 | audit_append_call | `if not refresh_ok: blockers.append("refresh token issue/verify self-test failed")` |
| `scripts/jwt_secret_rotation_evidence.py` | 162 | audit_append_call | `if not access_tamper: blockers.append("access token tamper rejection failed")` |
| `scripts/jwt_secret_rotation_evidence.py` | 163 | audit_append_call | `if not refresh_tamper: blockers.append("refresh token tamper rejection failed")` |
| `scripts/jwt_secret_rotation_evidence.py` | 164 | audit_append_call | `if not separated: blockers.append("access and refresh secrets must be different")` |
| `scripts/jwt_secret_rotation_evidence.py` | 180 | audit_append_call | `if not re.fullmatch(r"[0-9]+", run_id): blockers.append("JWT_EVIDENCE_RUN_ID is not numeric")` |
| `scripts/jwt_secret_rotation_evidence.py` | 181 | audit_append_call | `if not _gh_available(): blockers.append("GitHub CLI is unavailable or not authenticated")` |
| `scripts/jwt_secret_rotation_evidence.py` | 184 | audit_append_call | `blockers.append(f"unable to read GitHub Actions run {run_id}")` |
| `scripts/jwt_secret_rotation_evidence.py` | 191 | audit_append_call | `if f"/actions/runs/{run_id}" not in url: blockers.append("run URL does not contain numeric run ID")` |
| `scripts/jwt_secret_rotation_evidence.py` | 192 | audit_append_call | `if status != "completed": blockers.append(f"GitHub Actions run status is {status or 'missing'}, expected completed")` |
| `scripts/jwt_secret_rotation_evidence.py` | 193 | audit_append_call | `if conclusion != "success": blockers.append(f"GitHub Actions run conclusion is {conclusion or 'missing'}, expected success")` |
| `scripts/jwt_secret_rotation_evidence.py` | 194 | audit_append_call | `if head_sha != expected_sha: blockers.append(f"GitHub Actions run SHA {head_sha or 'missing'} does not match current commit {expected_sha}")` |
| `scripts/jwt_secret_rotation_evidence.py` | 195 | audit_append_call | `if not workflow: blockers.append("workflow name is missing")` |
| `scripts/jwt_secret_rotation_evidence.py` | 208 | audit_append_call | `if not ev.present: blockers.append(f"current {label} JWT secret is missing")` |
| `scripts/jwt_secret_rotation_evidence.py` | 209 | audit_append_call | `if ev.present and ev.length < MIN_SECRET_LENGTH: blockers.append(f"current {label} JWT secret length is {ev.length}, expected at least {MIN_SECRET_LENGTH}")` |
| `scripts/jwt_secret_rotation_evidence.py` | 210 | audit_append_call | `if ev.placeholder_like: blockers.append(f"current {label} JWT secret looks placeholder-like")` |
| `scripts/jwt_secret_rotation_evidence.py` | 214 | audit_append_call | `if evidence_env not in {"staging", "production"}: blockers.append("JWT_EVIDENCE_ENV must be staging or production")` |
| `scripts/jwt_secret_rotation_evidence.py` | 215 | audit_append_call | `if not store or has_placeholder(store): blockers.append("JWT_SECRET_STORE is missing or placeholder-like")` |
| `scripts/jwt_secret_rotation_evidence.py` | 216 | audit_append_call | `if not ref or has_placeholder(ref): blockers.append("JWT_ROTATION_REFERENCE is missing or placeholder-like")` |
| `scripts/jwt_secret_rotation_evidence.py` | 217 | audit_append_call | `if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", date): blockers.append("JWT_ROTATION_DATE must be YYYY-MM-DD")` |
| `scripts/jwt_secret_rotation_evidence.py` | 218 | audit_append_call | `if rotation_result != "passed": blockers.append("JWT_ROTATION_RESULT must be passed")` |
| `scripts/jwt_secret_rotation_evidence.py` | 219 | audit_append_call | `if not prev_access: blockers.append("previous access JWT fingerprint/secret is required for rotation evidence")` |
| `scripts/jwt_secret_rotation_evidence.py` | 220 | audit_append_call | `if not prev_refresh: blockers.append("previous refresh JWT fingerprint/secret is required for rotation evidence")` |
| `scripts/jwt_secret_rotation_evidence.py` | 221 | audit_append_call | `if prev_access and not access_rotated: blockers.append("current access JWT fingerprint matches previous fingerprint; rotation not proven")` |
| `scripts/jwt_secret_rotation_evidence.py` | 222 | audit_append_call | `if prev_refresh and not refresh_rotated: blockers.append("current refresh JWT fingerprint matches previous fingerprint; rotation not proven")` |
| `scripts/lessons/generate_lessons.py` | 150 | audit_append_call | `result.errors.append(msg)` |
| `scripts/lessons/generate_lessons.py` | 157 | audit_append_call | `result.errors.append(msg)` |
| `scripts/lessons/generate_lessons.py` | 164 | audit_append_call | `result.errors.append(msg)` |
| `scripts/lessons/generate_lessons.py` | 227 | audit_append_call | `results.append(result)` |
| `scripts/lessons/validate_lessons.py` | 185 | audit_append_call | `failed_lessons.append((lesson_id, caps_ref, result))` |
| `scripts/live_db_tx_evidence.py` | 181 | audit_append_call | `blockers.append("route slice is pending")` |
| `scripts/live_db_tx_evidence.py` | 183 | audit_append_call | `blockers.append("live DB evidence URL is pending or invalid")` |
| `scripts/live_db_tx_evidence.py` | 185 | audit_append_call | `blockers.append("test result must be pass/passed/success/successful/green/ok")` |
| `scripts/live_db_tx_evidence.py` | 187 | audit_append_call | `blockers.append("database is pending")` |
| `scripts/live_db_tx_evidence.py` | 189 | audit_append_call | `blockers.append("commit SHA is pending or invalid")` |
| `scripts/live_db_tx_evidence.py` | 191 | audit_append_call | `blockers.append("verified by is pending")` |
| `scripts/live_db_tx_evidence.py` | 193 | audit_append_call | `blockers.append("date verified is pending")` |
| `scripts/live_db_tx_evidence.py` | 328 | audit_append_call | `lines.append(` |
| `scripts/live_db_tx_evidence.py` | 337 | audit_append_call | `lines.append("- None")` |
| `scripts/maintenance/audit_todo_backlog.py` | 19 | audit_append_call | `paths.append(str(rel))` |
| `scripts/maintenance/audit_todo_backlog.py` | 35 | audit_append_call | `hits.append(rel)` |
| `scripts/maintenance/audit_todo_backlog.py` | 53 | audit_append_call | `tasks.append({'id':f'TODO-{idx:03d}','line':lineno,'section':section,'subsection':subsection,'todo_checked':'x' if m.group(1)=='x' else '', 'priority':m.group(2),'task':m.group(3).strip()})` |
| `scripts/maintenance/audit_todo_backlog.py` | 71 | audit_append_call | `RULES.append((marker.lower(),paths,status,note))` |
| `scripts/maintenance/audit_todo_backlog.py` | 334 | audit_append_call | `rows.append({**t,'repo_status':st,'owner':owner,'evidence_paths':'; '.join(ev),'audit_note':note,'pr_bucket':pr_bucket(t,st),'rank_score':rank(t,st)})` |
| `scripts/maintenance/audit_todo_backlog.py` | 341 | audit_append_call | `for st in ['Done','Partial','Missing','Blocked','Human-decision']: md.append(f'\| {st} \| {counts[st]} \|')` |
| `scripts/maintenance/audit_todo_backlog.py` | 345 | audit_append_call | `md.append(f"\| {p} \| {sum(r['repo_status']=='Done' for r in sub)} \| {sum(r['repo_status']=='Partial' for r in sub)} \| {sum(r['repo_status']=='Missing' for r in sub)} \| {sum(r['repo_status']=='Blocked' for r in sub)} \| {su` |
| `scripts/maintenance/audit_todo_backlog.py` | 350 | audit_append_call | `md.append(f"\| {i} \| {r['id']} \| {r['priority']} \| {r['repo_status']} \| {r['owner']} \| {task} \| {evidence} \|")` |
| `scripts/maintenance/audit_todo_backlog.py` | 351 | audit_append_call | `md.append('\n## PR-sized backlog buckets\n')` |
| `scripts/maintenance/audit_todo_backlog.py` | 353 | audit_append_call | `for r in sorted(rows,key=lambda r:(-r['rank_score'],r['id'])): by_pr[r['pr_bucket']].append(r)` |
| `scripts/maintenance/audit_todo_backlog.py` | 358 | audit_append_call | `md.append(f'\n### {bucket}\n')` |
| `scripts/maintenance/audit_todo_backlog.py` | 359 | audit_append_call | `md.append(f"Open items: {len(open_items)} — Partial {c['Partial']}, Missing {c['Missing']}, Blocked {c['Blocked']}, Human-decision {c['Human-decision']}.\n")` |
| `scripts/maintenance/audit_todo_backlog.py` | 360 | audit_append_call | `md.append('\| ID \| Priority \| Status \| Task \| Evidence \|\n\|---\|---\|---\|---\|---\|')` |
| `scripts/maintenance/audit_todo_backlog.py` | 364 | audit_append_call | `md.append(f"\| {r['id']} \| {r['priority']} \| {r['repo_status']} \| {task} \| {evidence} \|")` |
| `scripts/maintenance/audit_todo_backlog.py` | 365 | audit_append_call | `if len(open_items)>18: md.append(f'\n_Additional items in CSV: {len(open_items)-18}._\n')` |
| `scripts/maintenance/audit_todo_backlog.py` | 371 | audit_append_call | `cp.append(f'{i}. **{b}** — {len(oi)} open, {crit} critical.')` |
| `scripts/maintenance/audit_todo_backlog.py` | 375 | audit_append_call | `cp.append(f"\| {r['id']} \| {r['priority']} \| {r['repo_status']} \| {task} \|")` |
| `scripts/maintenance/audit_todo_backlog.py` | 383 | audit_append_call | `fb.append(f"\| {r['id']} \| {r['priority']} \| {r['repo_status']} \| {task} \| {evidence} \|")` |
| `scripts/maintenance/check_repo_hygiene.py` | 107 | audit_append_call | `failures.append(` |
| `scripts/maintenance/check_repo_hygiene.py` | 115 | audit_append_call | `failures.append(` |
| `scripts/maintenance/check_repo_hygiene.py` | 124 | audit_append_call | `failures.append(` |
| `scripts/migrate_auth_lifecycle_helpers_to_service.py` | 60 | audit_append_call | `imports.append(text)` |
| `scripts/migrate_auth_lifecycle_helpers_to_service.py` | 66 | audit_append_call | `unique.append(item)` |
| `scripts/migrate_auth_lifecycle_helpers_to_service.py` | 87 | audit_append_call | `helpers.append((node.name, method, start, end))` |
| `scripts/migrate_auth_lifecycle_helpers_to_service.py` | 99 | audit_append_call | `extracted.append((method, block))` |
| `scripts/migrate_auth_lifecycle_helpers_to_service.py` | 132 | audit_append_call | `exported.append(f"{method}_impl")` |
| `scripts/patch_audit_write_runtime_registry.py` | 34 | audit_events_table | `closure_blocker = "none" if accepted else "real audit_events write proof required"` |
| `scripts/patch_audit_write_runtime_registry.py` | 39 | audit_events_table | `title: Runtime audit_events write proof` |
| `scripts/patch_audit_write_runtime_registry.py` | 63 | audit_events_table | `title: Runtime audit_events write evidence repair` |
| `scripts/patch_diagnostics_scoring_snapshot.py` | 26 | audit_append_call | `old_append = 'snap.responses.append({"item_id": item_id, "correct": correct, "response": response})'` |
| `scripts/patch_diagnostics_scoring_snapshot.py` | 28 | audit_append_call | `'snap.responses.append({**diagnostic_response_snapshot(item, item_id=item_id), '` |
| `scripts/patch_final_gate_refresh_classifier_registry.py` | 49 | audit_append_call | `patched_ids.append(item_id)` |
| `scripts/patch_popia_router_boundary.py` | 50 | audit_append_call | `lines.append(line)` |
| `scripts/popia_response_contract_no_skips.py` | 115 | audit_append_call | `contracts.append(` |
| `scripts/popia_response_contract_no_skips.py` | 190 | audit_append_call | `blockers.append(f"{route.name} route missing response_model=ConsentRecord for {route.path}")` |
| `scripts/popia_response_contract_no_skips.py` | 194 | audit_append_call | `blockers.append(f"adapter contract missing: {name}")` |
| `scripts/popia_response_contract_no_skips.py` | 197 | audit_append_call | `blockers.append("POPIA no-skip response-contract pytest failed")` |
| `scripts/popia_response_contract_no_skips.py` | 200 | audit_append_call | `blockers.append("pytest output contains skipped tests; skipped tests are not proof")` |
| `scripts/popia_response_contract_no_skips.py` | 235 | audit_append_call | `lines.append(` |
| `scripts/popia_response_contract_no_skips.py` | 242 | audit_append_call | `lines.append(f"\| `{name}` \| {passed} \|")` |
| `scripts/popia_response_contract_no_skips.py` | 248 | audit_append_call | `lines.append("- None")` |
| `scripts/popia_route_tx_gap_plan.py` | 73 | audit_append_call | `problems.append("no POPIA service delegate call found")` |
| `scripts/popia_route_tx_gap_plan.py` | 75 | audit_append_call | `problems.append("direct DB mutations present")` |
| `scripts/popia_route_tx_gap_plan.py` | 91 | audit_append_call | `actions.append(` |
| `scripts/popia_route_tx_gap_plan.py` | 154 | audit_append_call | `lines.append(` |
| `scripts/popia_route_tx_gap_plan.py` | 159 | audit_append_call | `lines.append("\| `-` \| 0 \| `none` \| No local source gaps detected \| False \|")` |
| `scripts/popia_route_tx_gap_plan.py` | 174 | audit_append_call | `lines.append("- No POPIA route-source implementation gaps detected by the current report.")` |
| `scripts/popia_sweep.py` | 111 | audit_append_call | `self.issues.append(issue)` |
| `scripts/popia_sweep.py` | 131 | audit_append_call | `files.append(path)` |
| `scripts/popia_sweep.py` | 228 | audit_append_call | `decorator_names.append(decorator.attr)` |
| `scripts/popia_sweep.py` | 230 | audit_append_call | `decorator_names.append(decorator.id)` |
| `scripts/popia_sweep.py` | 298 | audit_log_identifier | `kw in func_source for kw in ["audit_log", "fourth_estate", "AuditLog", "log_action"]` |
| `scripts/popia_sweep.py` | 375 | audit_append_call | `by_severity.setdefault(issue.severity, []).append(issue)` |
| `scripts/populate_md_with_pdfs.py` | 41 | audit_append_call | `matched_pdfs.append(pdf)` |
| `scripts/prepare_training_data.py` | 59 | audit_append_call | `pairs.append({` |
| `scripts/prepare_training_data.py` | 65 | audit_append_call | `pairs.append({` |
| `scripts/prepare_training_data.py` | 71 | audit_append_call | `pairs.append({` |
| `scripts/prepare_training_data.py` | 77 | audit_append_call | `pairs.append({` |
| `scripts/prepare_training_data.py` | 83 | audit_append_call | `pairs.append({` |
| `scripts/prepare_training_data.py` | 105 | audit_append_call | `pairs.append({` |
| `scripts/prepare_training_data.py` | 117 | audit_append_call | `pairs.append({` |
| `scripts/prepare_training_data.py` | 125 | audit_append_call | `pairs.append({` |
| `scripts/prod_frontend_deployment.py` | 163 | audit_append_call | `lines.append(f"\| `{check.name}` \| {check.passed} \| {check.detail} \|")` |
| `scripts/prod_frontend_deployment.py` | 169 | audit_append_call | `lines.append("- None")` |
| `scripts/prod_frontend_runtime.py` | 290 | audit_append_call | `fields.append(RuntimeEvidenceField(name, value, False, "pending"))` |
| `scripts/prod_frontend_runtime.py` | 300 | audit_append_call | `fields.append(RuntimeEvidenceField(name, value, False, "must be pass/passed/green/ok/success"))` |
| `scripts/prod_frontend_runtime.py` | 304 | audit_append_call | `fields.append(RuntimeEvidenceField(name, value, False, "must be URL"))` |
| `scripts/prod_frontend_runtime.py` | 308 | audit_append_call | `fields.append(RuntimeEvidenceField(name, value, False, "must look like git SHA"))` |
| `scripts/prod_frontend_runtime.py` | 311 | audit_append_call | `fields.append(RuntimeEvidenceField(name, value, True, "ok"))` |
| `scripts/prod_frontend_runtime.py` | 352 | audit_append_call | `blockers.append("docker compose config failed")` |
| `scripts/prod_frontend_runtime.py` | 411 | audit_append_call | `lines.append(f"\| `{check.name}` \| {check.passed} \| {check.detail} \|")` |
| `scripts/prod_frontend_runtime.py` | 415 | audit_append_call | `lines.append(f"\| `{field.name}` \| `{field.value}` \| {field.valid} \| {field.reason} \|")` |
| `scripts/prod_frontend_runtime.py` | 421 | audit_append_call | `lines.append("- None")` |
| `scripts/project_assistance_status.py` | 119 | audit_append_call | `lines.append(f"\| `{source}` \| {_path_status(source)} \|")` |
| `scripts/project_assistance_status.py` | 131 | audit_append_call | `lines.append(f"\| {lane.number} \| {lane.name} \| {lane.output} \| `{lane.commands[0]}` \|")` |
| `scripts/reconcile_agent_roadmap.py` | 69 | audit_append_call | `lines.append(f"\| {task.id} \| {task.priority} \| {task.area} \| {task.status} \| {task.title} \| {task.next_action} \|")` |
| `scripts/refresh_current_state_doc.py` | 358 | audit_append_call | `results.append(r)` |
| `scripts/release_go_no_go.py` | 88 | audit_append_call | `items.append(current)` |
| `scripts/release_go_no_go.py` | 99 | audit_append_call | `items.append(current)` |
| `scripts/release_go_no_go.py` | 160 | audit_append_call | `findings.append(finding)` |
| `scripts/release_go_no_go.py` | 162 | audit_append_call | `blockers.append(f"{finding.id}: {finding.reason}")` |
| `scripts/release_go_no_go.py` | 171 | audit_append_call | `actions.append("Attach a passing GitHub Actions run URL for CI-001.")` |
| `scripts/release_go_no_go.py` | 173 | audit_append_call | `actions.append("Complete external approval files for legal, security, content, and staging gates.")` |
| `scripts/release_go_no_go.py` | 175 | audit_append_call | `actions.append("Resolve remaining beta-blocking engineering evidence items.")` |
| `scripts/release_go_no_go.py` | 177 | audit_append_call | `actions.append("Review release_decision_log.md and obtain explicit release-owner sign-off.")` |
| `scripts/release_go_no_go.py` | 258 | audit_append_call | `lines.append(` |
| `scripts/release_go_no_go.py` | 267 | audit_append_call | `lines.append("- None")` |
| `scripts/remove_proven_dead_backend_consolidation_artifacts.py` | 9 | audit_append_call | `skipped.append(f"{p.relative_to(ROOT)}: active/protected"); continue` |
| `scripts/remove_proven_dead_backend_consolidation_artifacts.py` | 12 | audit_append_call | `skipped.append(f"{p.relative_to(ROOT)}: referenced"); continue` |
| `scripts/remove_proven_dead_backend_consolidation_artifacts.py` | 13 | audit_append_call | `p.unlink(); removed.append(str(p.relative_to(ROOT)))` |
| `scripts/rename_metaphor_layers.py` | 90 | audit_append_call | `hits.append((path, lineno, match.group(0).lower(), line.rstrip()))` |
| `scripts/repair_arq_dependency_worker_import.py` | 46 | audit_append_call | `changed.append(str(path.relative_to(ROOT)))` |
| `scripts/repair_arq_dependency_worker_import.py` | 53 | audit_append_call | `changed.append(str(path.relative_to(ROOT)))` |
| `scripts/repair_arq_dependency_worker_import.py` | 98 | audit_append_call | `changed.append(str(path.relative_to(ROOT)))` |
| `scripts/repair_auth_forward_refs.py` | 72 | audit_append_call | `chunks.append("\n".join(lines[start:end]))` |
| `scripts/repair_auth_forward_refs.py` | 125 | audit_append_call | `candidates.append(base)` |
| `scripts/repair_auth_forward_refs.py` | 191 | audit_append_call | `unresolved.append(symbol)` |
| `scripts/repair_auth_forward_refs.py` | 193 | audit_append_call | `imports_by_module.setdefault(module, []).append(symbol)` |
| `scripts/repair_auth_lifecycle_method_extraction.py` | 76 | audit_append_call | `chunks.append("\n".join(source_lines[start:end]))` |
| `scripts/repair_auth_lifecycle_method_extraction.py` | 109 | audit_append_call | `found.append((node, method))` |
| `scripts/repair_auth_lifecycle_method_extraction.py` | 143 | audit_append_call | `names.append("auth_service")` |
| `scripts/repair_auth_lifecycle_method_extraction.py` | 158 | audit_append_call | `helper_header.append(re.sub(r"\bdef\s+" + re.escape(node.name) + r"\b", f"def {helper_name}", line, count=1))` |
| `scripts/repair_auth_lifecycle_method_extraction.py` | 161 | audit_append_call | `helper_header.append(line)` |
| `scripts/repair_auth_lifecycle_method_extraction.py` | 211 | audit_append_call | `replacements.append((start, end, _route_replacement(lines, node, method)))` |
| `scripts/repair_auth_lifecycle_method_extraction.py` | 282 | audit_append_call | `failures.append(f"auth.py does not delegate {method}")` |
| `scripts/repair_auth_lifecycle_method_extraction.py` | 284 | audit_append_call | `failures.append(f"AuthApplicationService missing assigned {method} method")` |
| `scripts/repair_auth_repository_fixture_proof.py` | 32 | audit_repository | `"app.repositories.repositories.AuditRepository",` |
| `scripts/repair_auth_repository_fixture_proof.py` | 33 | audit_repository | `"app.repositories.audit_repository.AuditRepository",` |
| `scripts/repair_auth_router_boundary.py` | 60 | audit_append_call | `updated_lines.append(line.split("import", 1)[0] + "import " + ", ".join(kept) + "\n")` |
| `scripts/repair_auth_router_boundary.py` | 67 | audit_append_call | `updated_lines.append(line.split("import", 1)[0] + "import " + ", ".join(kept) + "\n")` |
| `scripts/repair_auth_router_boundary.py` | 70 | audit_append_call | `updated_lines.append(line)` |
| `scripts/repair_auth_router_boundary.py` | 148 | audit_append_call | `patches.append((header_start, body_start, [replaced]))` |
| `scripts/repair_auth_router_boundary.py` | 159 | audit_append_call | `patches.append((close_index, close_index, [f"{close_indent}    {param},"]))` |
| `scripts/repair_auth_service_extraction.py` | 21 | audit_repository | `"AuditRepository",` |
| `scripts/repair_auth_service_extraction.py` | 31 | audit_repository | `"AuditRepository": "audit_repo",` |
| `scripts/repair_auth_service_extraction.py` | 86 | audit_append_call | `lines.append(line)` |
| `scripts/repair_auth_service_extraction.py` | 90 | audit_append_call | `lines.append(line)` |
| `scripts/repair_auth_service_extraction.py` | 100 | audit_append_call | `lines.append(before + "import " + ", ".join(kept) + "\n")` |
| `scripts/repair_auth_service_extraction.py` | 137 | audit_append_call | `insertions.append((idx, f"{indent}    {param},"))` |
| `scripts/repair_auth_service_extraction.py` | 156 | audit_append_call | `removed.append(line.strip())` |
| `scripts/repair_auth_service_extraction.py` | 158 | audit_append_call | `lines.append(line)` |
| `scripts/repair_beta_evidence_integrity.py` | 129 | audit_append_call | `blockers.append("invalid_or_synthetic_evidence")` |
| `scripts/repair_beta_evidence_integrity.py` | 164 | audit_append_call | `lines.append(` |
| `scripts/repair_diagnostics_data_integrity.py` | 114 | audit_append_call | `insertions.append((first.lineno - 1, snippet))` |
| `scripts/repair_diagnostics_data_integrity.py` | 118 | audit_append_call | `insertions.append((first.lineno - 1, snippet))` |
| `scripts/repair_diagnostics_data_integrity.py` | 121 | audit_append_call | `blockers.append("No diagnostics submit/answer/response/mastery candidate function with payload-like argument was found.")` |
| `scripts/repair_lesson_object_authorization.py` | 110 | audit_append_call | `blockers.append(f"{node.name}: missing db/session or current_user-like argument for read authz")` |
| `scripts/repair_lesson_object_authorization.py` | 112 | audit_append_call | `insertions.append((node.body[0].lineno - 1, f"{indent}{MARKER_READ}\n{indent}await require_lesson_read_access_for_current_user({db}, {user}, lesson_id)"))` |
| `scripts/repair_lesson_object_authorization.py` | 115 | audit_append_call | `blockers.append(f"{node.name}: missing db/session or current_user-like argument for write authz")` |
| `scripts/repair_lesson_object_authorization.py` | 117 | audit_append_call | `insertions.append((node.body[0].lineno - 1, f"{indent}{MARKER_WRITE}\n{indent}await require_lesson_write_access_for_current_user({db}, {user}, lesson_id)"))` |
| `scripts/repair_lesson_object_authorization.py` | 121 | audit_append_call | `blockers.append(f"{node.name}: missing db/current_user/payload argument for sync authz")` |
| `scripts/repair_lesson_object_authorization.py` | 128 | audit_append_call | `insertions.append((node.body[0].lineno - 1, snippet))` |
| `scripts/repair_popia_consent_lifecycle.py` | 215 | audit_append_call | `blocks.append(node)` |
| `scripts/repair_popia_consent_lifecycle.py` | 253 | audit_append_call | `insertions.append((insertion_line, snippet))` |
| `scripts/repair_runtime_blockers_after_followup_audit.py` | 96 | audit_append_call | `lines.append(line.split("import", 1)[0] + "import " + ", ".join(kept) + "\n")` |
| `scripts/repair_runtime_blockers_after_followup_audit.py` | 98 | audit_append_call | `lines.append(line)` |
| `scripts/repair_runtime_blockers_after_followup_audit.py` | 145 | audit_append_call | `ranges.append((node.lineno - 1, node.end_lineno or node.lineno))` |
| `scripts/repair_runtime_blockers_after_followup_audit.py` | 156 | audit_repository | `if stripped.startswith("from app.repositories") and any(name in line for name in ("ConsentRepository", "AuditRepository")):` |
| `scripts/repair_runtime_blockers_after_followup_audit.py` | 158 | audit_append_call | `new_lines.append(line)` |
| `scripts/route_tx_auth_slice.py` | 107 | audit_append_call | `parts.append(value.attr)` |
| `scripts/route_tx_auth_slice.py` | 110 | audit_append_call | `parts.append(value.id)` |
| `scripts/route_tx_auth_slice.py` | 130 | audit_append_call | `mutations.append(name)` |
| `scripts/route_tx_auth_slice.py` | 142 | audit_append_call | `chunks.append(path.read_text(encoding="utf-8", errors="ignore"))` |
| `scripts/route_tx_auth_slice.py` | 219 | audit_append_call | `blockers.append(f"{name} is pending")` |
| `scripts/route_tx_auth_slice.py` | 221 | audit_append_call | `blockers.append("Live DB evidence URL must be a URL")` |
| `scripts/route_tx_auth_slice.py` | 223 | audit_append_call | `blockers.append("Test result must be passed/pass/green/ok")` |
| `scripts/route_tx_auth_slice.py` | 225 | audit_append_call | `blockers.append("Commit SHA must look like a git SHA")` |
| `scripts/route_tx_auth_slice.py` | 234 | audit_append_call | `blockers.append("auth router file missing")` |
| `scripts/route_tx_auth_slice.py` | 254 | audit_append_call | `findings.append(finding)` |
| `scripts/route_tx_auth_slice.py` | 255 | audit_append_call | `blockers.append(f"{route_name}: route function missing")` |
| `scripts/route_tx_auth_slice.py` | 268 | audit_append_call | `missing.append(f"expected delegate {expected_delegate} missing")` |
| `scripts/route_tx_auth_slice.py` | 270 | audit_append_call | `missing.append("auth_service dependency missing")` |
| `scripts/route_tx_auth_slice.py` | 272 | audit_append_call | `missing.append("direct db mutations present: " + ", ".join(mutations))` |
| `scripts/route_tx_auth_slice.py` | 274 | audit_append_call | `blockers.append(f"{route_name}: {reason}")` |
| `scripts/route_tx_auth_slice.py` | 276 | audit_append_call | `findings.append(` |
| `scripts/route_tx_auth_slice.py` | 291 | audit_append_call | `blockers.append("no auth transactional service markers found in app/services")` |
| `scripts/route_tx_auth_slice.py` | 334 | audit_append_call | `lines.append(` |
| `scripts/route_tx_auth_slice.py` | 344 | audit_append_call | `lines.append("- None")` |
| `scripts/route_tx_auth_slice.py` | 350 | audit_append_call | `lines.append("- None")` |
| `scripts/route_tx_diagnostics_slice.py` | 140 | audit_append_call | `chunks.append("\n".join(lines[start:end]))` |
| `scripts/route_tx_diagnostics_slice.py` | 154 | audit_append_call | `parts.append(value.attr)` |
| `scripts/route_tx_diagnostics_slice.py` | 157 | audit_append_call | `parts.append(value.id)` |
| `scripts/route_tx_diagnostics_slice.py` | 170 | audit_append_call | `mutations.append(name)` |
| `scripts/route_tx_diagnostics_slice.py` | 181 | audit_append_call | `calls.append(name)` |
| `scripts/route_tx_diagnostics_slice.py` | 195 | audit_append_call | `chunks.append(path.read_text(encoding="utf-8", errors="ignore"))` |
| `scripts/route_tx_diagnostics_slice.py` | 270 | audit_append_call | `blockers.append(f"{name} is pending")` |
| `scripts/route_tx_diagnostics_slice.py` | 272 | audit_append_call | `blockers.append("Live DB evidence URL must be a URL")` |
| `scripts/route_tx_diagnostics_slice.py` | 274 | audit_append_call | `blockers.append("Test result must be passed/pass/green/ok")` |
| `scripts/route_tx_diagnostics_slice.py` | 276 | audit_append_call | `blockers.append("Commit SHA must look like a git SHA")` |
| `scripts/route_tx_diagnostics_slice.py` | 284 | audit_append_call | `funcs.append(node)` |
| `scripts/route_tx_diagnostics_slice.py` | 294 | audit_append_call | `blockers.append("diagnostics router file missing")` |
| `scripts/route_tx_diagnostics_slice.py` | 318 | audit_append_call | `reasons.append("no diagnostics service delegate call found")` |
| `scripts/route_tx_diagnostics_slice.py` | 320 | audit_append_call | `reasons.append("direct db mutations present: " + ", ".join(mutations))` |
| `scripts/route_tx_diagnostics_slice.py` | 322 | audit_append_call | `blockers.append(f"{node.name}: {reason}")` |
| `scripts/route_tx_diagnostics_slice.py` | 323 | audit_append_call | `findings.append(DiagnosticsRouteSliceFinding(` |
| `scripts/route_tx_diagnostics_slice.py` | 334 | audit_append_call | `blockers.append("selected diagnostics routes were not found in router source")` |
| `scripts/route_tx_diagnostics_slice.py` | 338 | audit_append_call | `blockers.append("no diagnostics transactional service markers found")` |
| `scripts/route_tx_diagnostics_slice.py` | 382 | audit_append_call | `lines.append(` |
| `scripts/route_tx_diagnostics_slice.py` | 391 | audit_append_call | `lines.append("- None")` |
| `scripts/route_tx_diagnostics_slice.py` | 396 | audit_append_call | `lines.append("- None")` |
| `scripts/route_tx_diagnostics_slice.py` | 410 | audit_append_call | `actions.append(DiagnosticsRouteTxGapAction(` |
| `scripts/route_tx_diagnostics_slice.py` | 465 | audit_append_call | `lines.append(f"\| `{action.route_function}` \| {action.line} \| `{action.current_status}` \| {action.blocker_reason} \| {action.can_be_closed_by_current_report} \|")` |
| `scripts/route_tx_diagnostics_slice.py` | 467 | audit_append_call | `lines.append("\| `-` \| 0 \| `none` \| No local source gaps detected \| False \|")` |
| `scripts/route_tx_impl_plan.py` | 143 | audit_append_call | `actions.append(` |
| `scripts/route_tx_impl_plan.py` | 206 | audit_append_call | `lines.append(` |
| `scripts/route_tx_impl_plan.py` | 226 | audit_append_call | `lines.append("- No unproven mutation routes detected by the current inventory.")` |
| `scripts/route_tx_popia_slice.py` | 131 | audit_append_call | `chunks.append("\n".join(lines[start:end]))` |
| `scripts/route_tx_popia_slice.py` | 145 | audit_append_call | `parts.append(value.attr)` |
| `scripts/route_tx_popia_slice.py` | 148 | audit_append_call | `parts.append(value.id)` |
| `scripts/route_tx_popia_slice.py` | 161 | audit_append_call | `mutations.append(name)` |
| `scripts/route_tx_popia_slice.py` | 172 | audit_append_call | `calls.append(name)` |
| `scripts/route_tx_popia_slice.py` | 186 | audit_append_call | `chunks.append(path.read_text(encoding="utf-8", errors="ignore"))` |
| `scripts/route_tx_popia_slice.py` | 263 | audit_append_call | `blockers.append(f"{name} is pending")` |
| `scripts/route_tx_popia_slice.py` | 265 | audit_append_call | `blockers.append("Live DB evidence URL must be a URL")` |
| `scripts/route_tx_popia_slice.py` | 267 | audit_append_call | `blockers.append("Test result must be passed/pass/green/ok")` |
| `scripts/route_tx_popia_slice.py` | 269 | audit_append_call | `blockers.append("Commit SHA must look like a git SHA")` |
| `scripts/route_tx_popia_slice.py` | 277 | audit_append_call | `funcs.append(node)` |
| `scripts/route_tx_popia_slice.py` | 287 | audit_append_call | `blockers.append("POPIA router file missing")` |
| `scripts/route_tx_popia_slice.py` | 316 | audit_append_call | `reasons.append("no POPIA service delegate call found")` |
| `scripts/route_tx_popia_slice.py` | 318 | audit_append_call | `reasons.append("direct db mutations present: " + ", ".join(mutations))` |
| `scripts/route_tx_popia_slice.py` | 320 | audit_append_call | `blockers.append(f"{node.name}: {reason}")` |
| `scripts/route_tx_popia_slice.py` | 322 | audit_append_call | `findings.append(` |
| `scripts/route_tx_popia_slice.py` | 335 | audit_append_call | `blockers.append("selected POPIA routes were not found in router source")` |
| `scripts/route_tx_popia_slice.py` | 339 | audit_append_call | `blockers.append("no POPIA transactional service markers found")` |
| `scripts/route_tx_popia_slice.py` | 385 | audit_append_call | `lines.append(` |
| `scripts/route_tx_popia_slice.py` | 395 | audit_append_call | `lines.append("- None")` |
| `scripts/route_tx_popia_slice.py` | 401 | audit_append_call | `lines.append("- None")` |
| `scripts/route_tx_slice_rollup.py` | 144 | audit_append_call | `slice_blockers.append("slice report missing")` |
| `scripts/route_tx_slice_rollup.py` | 146 | audit_append_call | `slice_blockers.append(f"{local_gaps} local route-source gap(s) remain")` |
| `scripts/route_tx_slice_rollup.py` | 148 | audit_append_call | `slice_blockers.append("live DB rollback evidence missing")` |
| `scripts/route_tx_slice_rollup.py` | 151 | audit_append_call | `blockers.append(f"{slice_id}: not release-ready")` |
| `scripts/route_tx_slice_rollup.py` | 152 | audit_append_call | `slices.append(` |
| `scripts/route_tx_slice_rollup.py` | 217 | audit_append_call | `lines.append(` |
| `scripts/run_database_backup.py` | 50 | audit_append_call | `results.append(` |
| `scripts/run_database_backup.py` | 78 | audit_append_call | `lines.append(f"- `{name}`")` |
| `scripts/run_database_backup.py` | 143 | audit_append_call | `results.append(validate_backup_tool())` |
| `scripts/run_database_restore.py` | 40 | audit_append_call | `results.append(` |
| `scripts/run_database_restore.py` | 133 | audit_append_call | `results.append(validate_target_environment(args.target_environment, args.allow_production_target))` |
| `scripts/run_database_restore.py` | 134 | audit_append_call | `results.append(validate_restore_confirmation(args.target_environment, args.confirm_restore))` |
| `scripts/run_database_restore.py` | 136 | audit_append_call | `results.append(validate_restore_tool(args.backup_artifact))` |
| `scripts/run_disposable_schema_drift_proof.py` | 79 | audit_append_call | `failures.append("DATABASE_URL is required")` |
| `scripts/run_disposable_schema_drift_proof.py` | 81 | audit_append_call | `failures.append("DATABASE_URL does not look disposable/test-like")` |
| `scripts/run_disposable_schema_drift_proof.py` | 83 | audit_append_call | `failures.append("DATABASE_URL contains placeholder credentials")` |
| `scripts/run_disposable_schema_drift_proof.py` | 94 | audit_append_call | `drift_cmd.append("--ignore-consolidation-tables")` |
| `scripts/run_disposable_schema_drift_proof.py` | 95 | audit_append_call | `commands.append(("schema_drift_db", drift_cmd))` |
| `scripts/run_disposable_schema_drift_proof.py` | 113 | audit_append_call | `lines.append(f"\| {result['name']} \| {result['return_code']} \| {result['passed']} \|")` |
| `scripts/run_live_ingestion.py` | 77 | audit_append_call | `self.metrics["confidence_scores"].append(data["confidence"])` |
| `scripts/run_staging_smoke.py` | 186 | audit_append_call | `rows.append(` |
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
| `scripts/scrape_teaching_materials.py` | 40 | audit_append_call | `links.append({"url": full_url, "text": text})` |
| `scripts/seed_item_bank.py` | 109 | audit_append_call | `failing.append({"item": item, "errors": errors})` |
| `scripts/seed_item_bank.py` | 119 | audit_append_call | `passing.append(item)` |
| `scripts/staging_acceptance_evidence.py` | 192 | audit_append_call | `lines.append(f"\| `{field.name}` \| `{field.value}` \| {field.valid} \| {field.reason} \|")` |
| `scripts/staging_acceptance_evidence.py` | 198 | audit_append_call | `lines.append("- None")` |
| `scripts/staging_smoke.py` | 60 | audit_append_call | `results.append({"path": check.path, "status": status, "passed": passed})` |
| `scripts/staging_smoke_evidence_acceptance.py` | 189 | audit_append_call | `blockers.append("GitHub CLI is unavailable or not authenticated")` |
| `scripts/staging_smoke_evidence_acceptance.py` | 194 | audit_append_call | `blockers.append("STAGING_SMOKE_RUN_ID is not numeric")` |
| `scripts/staging_smoke_evidence_acceptance.py` | 198 | audit_append_call | `blockers.append(f"unable to read GitHub Actions run {requested_run_id}")` |
| `scripts/staging_smoke_evidence_acceptance.py` | 202 | audit_append_call | `blockers.append(` |
| `scripts/staging_smoke_evidence_acceptance.py` | 224 | audit_append_call | `blockers.append("run ID is missing or non-numeric")` |
| `scripts/staging_smoke_evidence_acceptance.py` | 227 | audit_append_call | `blockers.append("run URL does not contain the numeric run ID")` |
| `scripts/staging_smoke_evidence_acceptance.py` | 230 | audit_append_call | `blockers.append("run URL contains placeholder evidence")` |
| `scripts/staging_smoke_evidence_acceptance.py` | 233 | audit_append_call | `blockers.append(f"GitHub Actions run status is {run_status or 'missing'}, expected completed")` |
| `scripts/staging_smoke_evidence_acceptance.py` | 236 | audit_append_call | `blockers.append(f"GitHub Actions run conclusion is {conclusion or 'missing'}, expected success")` |
| `scripts/staging_smoke_evidence_acceptance.py` | 239 | audit_append_call | `blockers.append(f"GitHub Actions run SHA {head_sha or 'missing'} does not match current commit {sha}")` |
| `scripts/staging_smoke_evidence_acceptance.py` | 242 | audit_append_call | `blockers.append("workflow name is missing")` |
| `scripts/staging_smoke_evidence_acceptance.py` | 245 | audit_append_call | `blockers.append(` |
| `scripts/staging_smoke_evidence_acceptance.py` | 250 | audit_append_call | `blockers.append("auth refresh DB proof workflow is not valid staging smoke evidence")` |
| `scripts/staging_smoke_evidence_acceptance.py` | 253 | audit_append_call | `blockers.append("staging base URL is missing, non-HTTPS, localhost/example, or placeholder")` |
| `scripts/staging_smoke_evidence_acceptance.py` | 256 | audit_append_call | `blockers.append("staging smoke test command is missing or placeholder")` |
| `scripts/staging_smoke_evidence_acceptance.py` | 259 | audit_append_call | `blockers.append("STAGING_SMOKE_RESULT must be passed")` |
| `scripts/staging_smoke_evidence_acceptance.py` | 262 | audit_append_call | `blockers.append("STAGING_SMOKE_HEALTHCHECK_RESULT must be passed")` |
| `scripts/staging_smoke_evidence_acceptance.py` | 265 | audit_append_call | `blockers.append("STAGING_SMOKE_API_RESULT must be passed")` |
| `scripts/staging_smoke_evidence_acceptance.py` | 268 | audit_append_call | `blockers.append("STAGING_SMOKE_FRONTEND_RESULT must be passed or omitted")` |
| `scripts/staging_smoke_evidence_acceptance.py` | 341 | audit_append_call | `lines.append("- None")` |
| `scripts/staging_smoke_probe.py` | 130 | audit_append_call | `blockers.append("staging base URL must be real, HTTPS, and non-placeholder")` |
| `scripts/staging_smoke_probe.py` | 137 | audit_append_call | `probes.append(smoke_get("healthcheck", build_url(base_url, health_path)))` |
| `scripts/staging_smoke_probe.py` | 138 | audit_append_call | `probes.append(smoke_get("api", build_url(base_url, api_path)))` |
| `scripts/staging_smoke_probe.py` | 140 | audit_append_call | `probes.append(smoke_get("frontend", build_url(base_url, frontend_path)))` |
| `scripts/staging_smoke_probe.py` | 144 | audit_append_call | `blockers.append(f"{probe.name} probe failed: {probe.detail}")` |
| `scripts/staging_smoke_probe.py` | 196 | audit_append_call | `lines.append(` |
| `scripts/staging_smoke_probe.py` | 204 | audit_append_call | `lines.append("- None")` |
| `scripts/stamp_evidence_registry_commit.py` | 34 | audit_append_call | `output.append(line)` |
| `scripts/stamp_evidence_registry_commit.py` | 37 | audit_append_call | `output.append(f"    last_verified_commit: {sha}")` |
| `scripts/stamp_evidence_registry_commit.py` | 39 | audit_append_call | `output.append(line)` |
| `scripts/sync_caps_r2.py` | 58 | audit_append_call | `items.append(SyncItem(path, f"{prefix.rstrip('/')}/{rel}"))` |
| `scripts/sync_caps_r2.py` | 95 | audit_append_call | `synced.append({"local_path": str(item.local_path), "key": item.key})` |
| `scripts/sync_caps_r2.py` | 112 | audit_append_call | `synced.append({"local_path": str(local_path), "key": key})` |
| `scripts/sync_git_to_redmine.py` | 13 | audit_events_table | `"fourth estate": 5, "estate": 5, "audit_events": 5,` |
| `scripts/train_qlora.py` | 41 | audit_append_call | `records.append(json.loads(line))` |
| `scripts/transaction_boundary_inventory.py` | 102 | audit_append_call | `found.append(marker)` |
| `scripts/transaction_boundary_inventory.py` | 111 | audit_append_call | `areas.append(area)` |
| `scripts/transaction_boundary_inventory.py` | 128 | audit_append_call | `calls.append(name)` |
| `scripts/transaction_boundary_inventory.py` | 169 | audit_append_call | `findings.append(finding)` |
| `scripts/transaction_boundary_inventory.py` | 199 | audit_append_call | `lines.append(` |
| `scripts/transaction_rollback_rollup.py` | 73 | audit_append_call | `proofs.append(` |
| `scripts/transaction_rollback_rollup.py` | 116 | audit_append_call | `lines.append(` |
| `scripts/tx_route_wiring_inventory.py` | 63 | audit_append_call | `chunks.append("\n".join(lines[start:end]))` |
| `scripts/tx_route_wiring_inventory.py` | 109 | audit_append_call | `rows.append(` |
| `scripts/tx_route_wiring_inventory.py` | 160 | audit_append_call | `lines.append(` |
| `scripts/validate_ai_output_fixtures.py` | 50 | audit_append_call | `results.append(` |
| `scripts/validate_ai_output_fixtures.py` | 58 | audit_append_call | `results.append(` |
| `scripts/validate_ai_output_fixtures.py` | 67 | audit_append_call | `results.append(` |
| `scripts/validate_ai_output_fixtures.py` | 101 | audit_append_call | `results.append(` |
| `scripts/validate_ai_output_fixtures.py` | 122 | audit_append_call | `results.append(` |
| `scripts/validate_ai_output_fixtures.py` | 149 | audit_append_call | `results.append(FixtureValidationResult(path.name, False, f"unsupported type {output_type!r}"))` |
| `scripts/validate_ai_output_fixtures.py` | 159 | audit_append_call | `results.append(FixtureValidationResult(fixture, False, "fixture missing"))` |
| `scripts/validate_item_bank.py` | 205 | audit_append_call | `failure_log.append({` |
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
| `scripts/verify_api_health.py` | 151 | audit_append_call | `results.append(("health", verify_health(args.base_url)))` |
| `scripts/verify_api_health.py` | 152 | audit_append_call | `results.append(("ready", verify_ready(args.base_url)))` |
| `scripts/verify_api_health.py` | 153 | audit_append_call | `results.append(("metrics", verify_metrics(args.base_url)))` |
| `scripts/verify_api_health.py` | 154 | audit_append_call | `results.append(("docs", verify_docs(args.base_url)))` |
| `scripts/verify_api_health.py` | 155 | audit_append_call | `results.append(("openapi", verify_openapi(args.base_url)))` |
| `scripts/verify_audit_chain.py` | 5 | audit_events_table | `Walks the audit_events table and checks hash/HMAC integrity.` |
| `scripts/verify_audit_chain.py` | 28 | audit_repository | `from app.repositories.audit_repository import AuditRepository, configure_hmac_secret` |
| `scripts/verify_audit_chain.py` | 40 | audit_repository | `repo = AuditRepository(pool)` |
| `scripts/verify_migration_graph.py` | 71 | audit_append_call | `migrations.append(Migration(file=file, revision=str(revision), down_revisions=down_revisions))` |
| `scripts/verify_migration_graph.py` | 84 | audit_append_call | `errors.append(f"duplicate revision id: {migration.revision}")` |
| `scripts/verify_migration_graph.py` | 90 | audit_append_call | `errors.append(` |
| `scripts/verify_migration_graph.py` | 94 | audit_append_call | `errors.append(` |
| `scripts/verify_migration_graph.py` | 102 | audit_append_call | `bases.append(migration.revision)` |
| `scripts/verify_migration_graph.py` | 104 | audit_append_call | `children.setdefault(down_revision, []).append(migration.revision)` |
| `scripts/verify_migration_graph.py` | 108 | audit_append_call | `errors.append(f"expected exactly one base revision, found {bases}")` |
| `scripts/verify_migration_graph.py` | 110 | audit_append_call | `errors.append(f"expected exactly one head revision, found {heads}")` |
| `tests/ci/test_item_bank_ci_jobs.py` | 180 | audit_append_call | `failures.append(f"{item.get('item_id', '?')}: missing {missing}")` |
| `tests/ci/test_item_bank_ci_jobs.py` | 184 | audit_append_call | `failures.append(` |
| `tests/ci/test_item_bank_ci_jobs.py` | 253 | audit_append_call | `latencies.append(lat)` |
| `tests/integration/conftest.py` | 60 | audit_append_call | `results.append(await self._incr_immediate(*args))` |
| `tests/integration/conftest.py` | 62 | audit_append_call | `results.append(await self._expire_immediate(*args))` |
| `tests/integration/conftest.py` | 68 | audit_append_call | `self._queue.append(("incr", (key,)))` |
| `tests/integration/conftest.py` | 79 | audit_append_call | `self._queue.append(("expire", (key, seconds)))` |
| `tests/integration/test_assessment_production_path.py` | 32 | audit_append_call | `self.submit_calls.append(` |
| `tests/integration/test_audit_immutability.py` | 12 | audit_events_table | `Verify that audit_events cannot be updated or deleted due to DB rules.` |
| `tests/integration/test_audit_immutability.py` | 34 | audit_events_table | `"UPDATE audit_events SET payload = '{\"key\": \"tampered\"}' "` |
| `tests/integration/test_audit_immutability.py` | 43 | audit_events_table | `text("SELECT payload FROM audit_events WHERE id = :id"),` |
| `tests/integration/test_audit_immutability.py` | 55 | audit_events_table | `text("DELETE FROM audit_events WHERE id = :id"),` |
| `tests/integration/test_audit_immutability.py` | 62 | audit_events_table | `text("SELECT COUNT(*) FROM audit_events WHERE id = :id"),` |
| `tests/integration/test_auth_lifecycle_http_success_scope.py` | 174 | audit_append_call | `routes.append((combined, route))` |
| `tests/integration/test_auth_lifecycle_http_success_scope.py` | 204 | audit_append_call | `self.calls.append(("register", kwargs))` |
| `tests/integration/test_auth_lifecycle_http_success_scope.py` | 212 | audit_append_call | `self.calls.append(("login", kwargs))` |
| `tests/integration/test_auth_lifecycle_http_success_scope.py` | 220 | audit_append_call | `self.calls.append(("refresh", kwargs))` |
| `tests/integration/test_auth_lifecycle_http_success_scope.py` | 230 | audit_append_call | `self.calls.append(("create_dev_session", kwargs))` |
| `tests/integration/test_auth_repository_fixture_proof.py` | 47 | audit_append_call | `stored_tokens.append(token)` |
| `tests/integration/test_auth_transactional_db_lifecycle_proof.py` | 107 | audit_append_call | `rows.append((f"{lowered} {endpoint} {route_name}", route))` |
| `tests/integration/test_diagnostic_session.py` | 88 | audit_append_call | `items.append(_make_item(difficulty_b=b, caps_ref=caps_ref))` |
| `tests/integration/test_diagnostic_session.py` | 191 | audit_append_call | `served_item_ids.append(item.item_id)` |
| `tests/integration/test_diagnostic_session.py` | 247 | audit_append_call | `served_ids.append(item.item_id)` |
| `tests/integration/test_diagnostics_transaction_rollback_proof.py` | 44 | audit_events_table | `audit_events = __import__("sqlalchemy").Table(` |
| `tests/integration/test_diagnostics_transaction_rollback_proof.py` | 78 | audit_events_table | `audit_events_table=audit_events,` |
| `tests/integration/test_diagnostics_transaction_rollback_proof.py` | 103 | audit_events_table | `assert await _count(session, audit_events) == 1` |
| `tests/integration/test_diagnostics_transaction_rollback_proof.py` | 118 | audit_events_table | `assert await _count(session, audit_events) == 0` |
| `tests/integration/test_diagnostics_transaction_rollback_proof.py` | 131 | audit_events_table | `assert await _count(session, audit_events) == 1` |
| `tests/integration/test_lesson_authorization_negative_contract.py` | 39 | audit_append_call | `read_routes.append(block)` |
| `tests/integration/test_lesson_authorization_negative_contract.py` | 41 | audit_append_call | `write_routes.append(block)` |
| `tests/integration/test_lesson_authorization_negative_contract.py` | 43 | audit_append_call | `sync_routes.append(block)` |
| `tests/integration/test_lesson_gamification_transaction_rollback_proof.py` | 36 | audit_events_table | `audit_events = __import__("sqlalchemy").Table(` |
| `tests/integration/test_lesson_gamification_transaction_rollback_proof.py` | 80 | audit_events_table | `result = await session.execute(select(func.count()).select_from(audit_events))` |
| `tests/integration/test_lesson_gamification_transaction_rollback_proof.py` | 89 | audit_events_table | `audit_events_table=audit_events,` |
| `tests/integration/test_lesson_sync.py` | 54 | audit_append_call | `calls.append(("complete", lesson_id, None))` |
| `tests/integration/test_lesson_sync.py` | 57 | audit_append_call | `calls.append(("feedback", lesson_id, score))` |
| `tests/integration/test_popia_lifecycle_response_contract.py` | 35 | audit_append_call | `self.events.append("consent.granted")` |
| `tests/integration/test_popia_lifecycle_response_contract.py` | 47 | audit_append_call | `self.events.append(f"consent.{reason}")` |
| `tests/integration/test_popia_lifecycle_response_contract.py` | 51 | audit_append_call | `self.events.append("consent.renewed")` |
| `tests/integration/test_popia_lifecycle_runtime_contract.py` | 14 | audit_append_call | `self.calls.append(("grant", guardian_id, learner_id, consent_version, actor_id))` |
| `tests/integration/test_popia_lifecycle_runtime_contract.py` | 18 | audit_append_call | `self.calls.append(("revoke", guardian_id, learner_id, actor_id, reason))` |
| `tests/integration/test_stripe_webhooks.py` | 32 | audit_append_call | `calls.append(guardian_id)` |
| `tests/legacy/integration/test_api_contracts.py` | 114 | audit_events_table | `assert "audit_events" in payload` |
| `tests/legacy/integration/test_five_pillar_pipeline.py` | 121 | audit_append_call | `captured_calls.append({"args": args, "kwargs": kwargs})` |
| `tests/legacy/integration/test_lesson_api.py` | 59 | audit_append_call | `captured_prompts.append({"system": system, "user": user})` |
| `tests/legacy/popia/test_popia_compliance.py` | 237 | audit_log_identifier | `from app.models import AuditLog` |
| `tests/legacy/popia/test_popia_compliance.py` | 239 | audit_log_identifier | `log = AuditLog()` |
| `tests/legacy/unit/test_irt_benchmarks.py` | 27 | audit_append_call | `session.responses.append(Response(item.item_id, is_correct, 5000))` |
| `tests/legacy/unit/test_irt_benchmarks.py` | 43 | audit_append_call | `bank.append(Item(` |
| `tests/legacy/unit/test_irt_benchmarks.py` | 57 | audit_append_call | `estimates.append(est)` |
| `tests/legacy/unit/test_irt_benchmarks.py` | 61 | audit_append_call | `results.append((true_theta, avg_est, error))` |
| `tests/legacy/unit/test_profiler.py` | 21 | audit_append_call | `events.append({` |
| `tests/test_entrypoints.py` | 94 | audit_append_call | `missing.append(f"{prefix}{fragment}")` |
| `tests/unit/modules/lessons/test_lesson_generation_perf.py` | 182 | audit_append_call | `latencies.append(elapsed)` |
| `tests/unit/modules/lessons/test_lesson_generation_perf.py` | 227 | audit_append_call | `latencies.append(elapsed * 1000)  # convert to ms` |
| `tests/unit/modules/lessons/test_lesson_generation_perf.py` | 268 | audit_append_call | `latencies.append((time.perf_counter() - start) * 1000)` |
| `tests/unit/test_api_v2_router_contract.py` | 51 | audit_append_call | `missing.append(f"{router_name}:{expected_prefix}")` |
| `tests/unit/test_arq_worker_import_contract.py` | 22 | audit_append_call | `matching.append(path)` |
| `tests/unit/test_assessments_router_contract.py` | 27 | audit_append_call | `self.list_calls.append({"limit": limit, "offset": offset})` |
| `tests/unit/test_assessments_router_contract.py` | 37 | audit_append_call | `self.submit_calls.append(` |
| `tests/unit/test_audit_callsite_inventory_and_adapter.py` | 44 | audit_append_call | `self.calls.append(kwargs)` |
| `tests/unit/test_audit_callsite_inventory_and_adapter.py` | 50 | audit_append_call | `result = await adapter.append(action="x", resource_id="r1")` |
| `tests/unit/test_audit_repository.py` | 4 | audit_repository | `Task 23: AuditRepository unit tests` |
| `tests/unit/test_audit_repository.py` | 8 | audit_events_table | `- UPDATE on audit_events is a no-op (PostgreSQL RULE)` |
| `tests/unit/test_audit_repository.py` | 9 | audit_events_table | `- DELETE on audit_events is a no-op (PostgreSQL RULE)` |
| `tests/unit/test_audit_repository.py` | 24 | audit_repository | `from app.repositories.audit_repository import AuditRepository` |
| `tests/unit/test_audit_repository.py` | 32 | audit_repository | `repo = AuditRepository(db_session)` |
| `tests/unit/test_audit_repository.py` | 36 | audit_append_call | `event = await repo.append(` |
| `tests/unit/test_audit_repository.py` | 52 | audit_repository | `repo = AuditRepository(db_session)` |
| `tests/unit/test_audit_repository.py` | 53 | audit_append_call | `event = await repo.append(` |
| `tests/unit/test_audit_repository.py` | 63 | audit_repository | `repo = AuditRepository(db_session)` |
| `tests/unit/test_audit_repository.py` | 64 | audit_append_call | `event = await repo.append(` |
| `tests/unit/test_audit_repository.py` | 73 | audit_repository | `repo = AuditRepository(db_session)` |
| `tests/unit/test_audit_repository.py` | 75 | audit_append_call | `await repo.append(event_type="", payload={})` |
| `tests/unit/test_audit_repository.py` | 80 | audit_repository | `repo = AuditRepository(db_session)` |
| `tests/unit/test_audit_repository.py` | 83 | audit_append_call | `await repo.append(` |
| `tests/unit/test_audit_repository.py` | 89 | audit_append_call | `await repo.append(` |
| `tests/unit/test_audit_repository.py` | 95 | audit_append_call | `await repo.append(` |
| `tests/unit/test_audit_repository.py` | 109 | audit_repository | `repo = AuditRepository(db_session)` |
| `tests/unit/test_audit_repository.py` | 110 | audit_append_call | `event = await repo.append(` |
| `tests/unit/test_audit_repository.py` | 117 | audit_events_table | `text("UPDATE audit_events SET event_type = 'tampered' WHERE id = :id"),` |
| `tests/unit/test_audit_repository.py` | 128 | audit_events_table | `"UPDATE on audit_events must be a no-op due to PostgreSQL RULE"` |
| `tests/unit/test_audit_repository.py` | 137 | audit_repository | `repo = AuditRepository(db_session)` |
| `tests/unit/test_audit_repository.py` | 138 | audit_append_call | `event = await repo.append(` |
| `tests/unit/test_audit_repository.py` | 145 | audit_events_table | `text("DELETE FROM audit_events WHERE id = :id"),` |
| `tests/unit/test_audit_repository.py` | 156 | audit_events_table | `"DELETE on audit_events must be a no-op due to PostgreSQL RULE"` |
| `tests/unit/test_audit_repository.py` | 164 | audit_repository | `repo = AuditRepository(db_session)` |
| `tests/unit/test_audit_repository.py` | 168 | audit_append_call | `await repo.append("consent.granted", payload={}, resource_id=resource_id)` |
| `tests/unit/test_audit_repository.py` | 169 | audit_append_call | `await repo.append("consent.revoked", payload={}, resource_id=resource_id)` |
| `tests/unit/test_audit_repository.py` | 170 | audit_append_call | `await repo.append("consent.granted", payload={}, resource_id=other_resource_id)` |
| `tests/unit/test_audit_repository.py` | 178 | audit_repository | `repo = AuditRepository(db_session)` |
| `tests/unit/test_audit_repository.py` | 181 | audit_append_call | `await repo.append("consent.granted", payload={}, resource_id=resource_id)` |
| `tests/unit/test_audit_repository.py` | 182 | audit_append_call | `await repo.append("consent.revoked", payload={}, resource_id=resource_id)` |
| `tests/unit/test_audit_repository.py` | 190 | audit_repository | `repo = AuditRepository(db_session)` |
| `tests/unit/test_audit_repository.py` | 193 | audit_append_call | `await repo.append("consent.granted", payload={}, actor_id=actor_id)` |
| `tests/unit/test_audit_repository.py` | 194 | audit_append_call | `await repo.append("consent.revoked", payload={}, actor_id=actor_id)` |
| `tests/unit/test_backend_consolidation_implementation_foundation.py` | 32 | audit_append_call | `self.calls.append(kwargs)` |
| `tests/unit/test_backend_consolidation_implementation_foundation.py` | 54 | audit_append_call | `self.calls.append(kwargs)` |
| `tests/unit/test_backend_runtime_enablement_pack.py` | 23 | audit_logs_table | `assert "`audit_logs` deletion: blocked" in text` |
| `tests/unit/test_backend_runtime_wiring_preflight.py` | 24 | audit_logs_table | `assert "`audit_logs` deletion allowed" in text` |
| `tests/unit/test_billing_monetization_production_readiness.py` | 69 | audit_log_identifier | `assert "processed:evt_1:invoice.created:1" in store.audit_log` |
| `tests/unit/test_billing_monetization_production_readiness.py` | 70 | audit_log_identifier | `assert "duplicate:evt_1:invoice.created" in store.audit_log` |
| `tests/unit/test_billing_router_contract.py` | 25 | audit_append_call | `self.checkout_calls.append({"guardian_id": guardian_id, "email_plaintext": email_plaintext})` |
| `tests/unit/test_billing_router_contract.py` | 29 | audit_append_call | `self.webhook_calls.append({"payload_len": len(payload), "signature": signature})` |
| `tests/unit/test_billing_router_contract.py` | 38 | audit_append_call | `self.records.append((event_type, payload))` |
| `tests/unit/test_consent_policy.py` | 75 | audit_append_call | `self.events.append(kwargs)` |
| `tests/unit/test_content_bulk_review.py` | 35 | audit_append_call | `self.approved.append(artifact_id)` |
| `tests/unit/test_content_bulk_review.py` | 38 | audit_append_call | `self.rejected.append(artifact_id)` |
| `tests/unit/test_content_bulk_review.py` | 42 | audit_append_call | `self.quarantined.append(artifact_id)` |
| `tests/unit/test_content_bulk_review.py` | 50 | audit_append_call | `self.added.append(obj)` |
| `tests/unit/test_content_factory_route_security.py` | 27 | audit_append_call | `deps.append(dep.call)` |
| `tests/unit/test_content_factory_route_security.py` | 97 | audit_append_call | `missing.append(f"{list(route.methods)} {route.path}")` |
| `tests/unit/test_content_factory_table_reconciliation.py` | 68 | audit_append_call | `missing.append(model_name)` |
| `tests/unit/test_content_factory_table_reconciliation.py` | 84 | audit_append_call | `mismatches.append(` |
| `tests/unit/test_content_factory_table_reconciliation.py` | 98 | audit_append_call | `undeclared.append(` |
| `tests/unit/test_content_factory_table_reconciliation.py` | 125 | audit_append_call | `missing.append(table_name)` |
| `tests/unit/test_content_file_review_workflow.py` | 175 | audit_append_call | `self.added.append(obj)` |
| `tests/unit/test_content_generation_executor.py` | 32 | audit_append_call | `self.added.append(obj)` |
| `tests/unit/test_content_generation_planner.py` | 32 | audit_append_call | `self.added.append(obj)` |
| `tests/unit/test_content_generation_runs.py` | 22 | audit_append_call | `self.objects.append(obj)` |
| `tests/unit/test_content_reviewer_assignment.py` | 33 | audit_append_call | `self.added.append(obj)` |
| `tests/unit/test_content_staging_readiness.py` | 36 | audit_append_call | `self.added.append(obj)` |
| `tests/unit/test_content_staging_seed_executor.py` | 43 | audit_append_call | `self.added.append(obj)` |
| `tests/unit/test_db_backup_restore_rollback_evidence.py` | 32 | audit_events_table | `source = {"key_table_counts": {"audit_events": 6, "irt_items": 1600}}` |
| `tests/unit/test_db_backup_restore_rollback_evidence.py` | 33 | audit_events_table | `restore = {"key_table_counts": {"audit_events": 6, "irt_items": 1599}}` |
| `tests/unit/test_db_backup_restore_rollback_evidence.py` | 36 | audit_events_table | `assert "audit_events" not in mismatches` |
| `tests/unit/test_db_migration_seed_repeatability.py` | 90 | audit_events_table | `'CREATE TABLE public."audit_events" (',` |
| `tests/unit/test_db_migration_seed_repeatability.py` | 102 | audit_events_table | `assert presence['audit_events'] is True` |
| `tests/unit/test_diagnostics_scoring_snapshot.py` | 67 | audit_append_call | `captured.append([float(getattr(item, "difficulty_b", getattr(item, "b_param", 0.0))) for item, _ in responses])` |
| `tests/unit/test_envelope_route_background.py` | 12 | audit_append_call | `calls.append("ran")` |
| `tests/unit/test_etl_mcp_server_startup.py` | 22 | audit_append_call | `self.calls.append(kwargs)` |
| `tests/unit/test_etl_mcp_server_startup.py` | 30 | audit_append_call | `called.append((mcp_server, host, port))` |
| `tests/unit/test_lesson_object_authorization_contracts.py` | 48 | audit_append_call | `candidates.append(node)` |
| `tests/unit/test_lesson_object_authorization_contracts.py` | 62 | audit_append_call | `candidates.append(node)` |
| `tests/unit/test_no_raw_dict_responses.py` | 74 | audit_append_call | `violations.append(` |
| `tests/unit/test_phase6_durable_jobs.py` | 31 | audit_append_call | `self.calls.append(` |
| `tests/unit/test_popia_erasure_safety.py` | 46 | audit_events_table | `"audit_events",` |
| `tests/unit/test_popia_erasure_safety.py` | 47 | audit_logs_table | `"audit_logs",` |
| `tests/unit/test_popia_erasure_safety.py` | 157 | audit_append_call | `execute_calls.append(stmt)` |
| `tests/unit/test_popia_erasure_safety.py` | 214 | audit_append_call | `execute_calls.append(stmt)` |
| `tests/unit/test_popia_erasure_safety.py` | 271 | audit_append_call | `execute_calls.append(str(stmt))` |
| `tests/unit/test_popia_erasure_safety.py` | 282 | audit_events_table | `assert "audit_events" not in call.lower()` |
| `tests/unit/test_popia_erasure_safety.py` | 283 | audit_logs_table | `assert "audit_logs" not in call.lower()` |
| `tests/unit/test_popia_erasure_safety.py` | 299 | audit_append_call | `execute_calls.append(str(stmt))` |
| `tests/unit/test_popia_erasure_safety.py` | 327 | audit_append_call | `execute_calls.append(str(stmt))` |
| `tests/unit/test_popia_erasure_safety.py` | 385 | audit_append_call | `execute_calls.append(str(stmt))` |
| `tests/unit/test_popia_export_completeness.py` | 330 | audit_events_table | `"audit_events",` |
| `tests/unit/test_popia_service_authority.py` | 34 | audit_append_call | `violations.append((str(router_file.relative_to(repo_root)), pattern))` |
| `tests/unit/test_popia_service_authority.py` | 62 | audit_append_call | `violations.append((str(service_file.relative_to(repo_root)), pattern))` |
| `tests/unit/test_practice_session_authorization.py` | 81 | audit_append_call | `consent_calls.append((db, current_user, checked_learner_id))` |
| `tests/unit/test_practice_session_authorization.py` | 168 | audit_append_call | `consent_calls.append((db, current_user, checked_learner_id))` |
| `tests/unit/test_readonly_deep_readiness_runtime.py` | 7 | audit_append_call | `async def execute(self, statement): self.statements.append(str(statement)); return R()` |
| `tests/unit/test_real_audit_runtime_facade.py` | 6 | audit_append_call | `async def record(self, **kw): self.events.append(kw); return {"ok": True}` |
| `tests/unit/test_real_consent_runtime_facade.py` | 5 | audit_append_call | `async def record(self, **kw): self.events.append(kw); return {"ok": True}` |
| `tests/unit/test_runtime_blockers_after_followup_audit.py` | 16 | audit_append_call | `self.calls.append(("grant", guardian_id, learner_id, consent_version, actor_id))` |
| `tests/unit/test_runtime_blockers_after_followup_audit.py` | 20 | audit_append_call | `self.calls.append(("revoke", guardian_id, learner_id, actor_id, reason))` |
| `tests/unit/test_schema_drift_deep_readiness_audit_slice.py` | 48 | audit_events_table | `for bad in ["session.commit()", "INSERT INTO audit_events", "alembic stamp head"]:` |
| `tests/unit/test_schema_drift_deep_readiness_audit_slice.py` | 65 | audit_append_call | `self.calls.append(kwargs)` |
| `tests/unit/test_seed_staging_review_scopes.py` | 35 | audit_append_call | `self.added.append(obj)` |
| `tests/unit/test_sprint3_popia_router_data_rights.py` | 24 | audit_append_call | `self.calls.append(("export", {"learner_id": learner_id, "current_user": current_user}))` |
| `tests/unit/test_sprint3_popia_router_data_rights.py` | 28 | audit_append_call | `self.calls.append(("erasure", {"learner_id": learner_id, "current_user": current_user, "reason": reason}))` |
| `tests/unit/test_sprint3_popia_router_data_rights.py` | 32 | audit_append_call | `self.calls.append(("cancel_erasure", {"learner_id": learner_id, "current_user": current_user}))` |
| `tests/unit/test_sprint3_popia_router_data_rights.py` | 36 | audit_append_call | `self.calls.append(("correction", {"learner_id": learner_id, "current_user": current_user, "fields": fields, "reason": reason}))` |
| `tests/unit/test_sprint3_popia_router_data_rights.py` | 40 | audit_append_call | `self.calls.append(("restriction", {"learner_id": learner_id, "current_user": current_user, "reason": reason}))` |
| `tests/unit/test_v2_services.py` | 6 | audit_log_identifier | `from app.domain.entities import AuditLog, LearnerProfile` |
| `tests/unit/test_v2_services.py` | 35 | audit_log_identifier | `repo.append.return_value = AuditLog(` |
| `tests/unit/test_v2_services_full.py` | 15 | audit_log_identifier | `from app.domain.entities import LearnerProfile, AuditLog` |
| `tests/unit/test_v2_services_full.py` | 29 | audit_log_identifier | `def _audit_log(event_type: str = "TEST") -> AuditLog:` |
| `tests/unit/test_v2_services_full.py` | 30 | audit_log_identifier | `return AuditLog(event_id=str(uuid.uuid4()), learner_id=LEARNER_ID, event_type=event_type,` |
| `tests/unit/test_v2_services_full.py` | 403 | audit_append_call | `learners.append(m)` |

## Review checklist

- [ ] Confirm canonical append-only audit table.
- [ ] Confirm all security/POPIA-sensitive actions emit canonical audit events.
- [ ] Identify legacy `append` call sites that need adapter migration.
- [ ] Identify any `audit_logs` data-retention requirement.
- [ ] Delete legacy audit code only after adapter migration and full-suite evidence.
