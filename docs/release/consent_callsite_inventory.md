# Consent Call-Site Inventory

This inventory supports consent service/table consolidation. It is diagnostic only.

| Path | Line | Category | Text |
|---|---:|---|---|
| `alembic/versions/0001_v2_consolidated_schema.py` | 13 | parental_consents_table | `3. parental_consents — POPIA consent records with expiry/revocation` |
| `alembic/versions/0001_v2_consolidated_schema.py` | 92 | parental_consents_table | `"parental_consents",` |
| `alembic/versions/0001_v2_consolidated_schema.py` | 105 | parental_consents_table | `op.create_index("ix_parental_consent_guardian", "parental_consents", ["guardian_id"])` |
| `alembic/versions/0001_v2_consolidated_schema.py` | 106 | parental_consents_table | `op.create_index("ix_parental_consent_learner", "parental_consents", ["learner_id"])` |
| `alembic/versions/0001_v2_consolidated_schema.py` | 250 | parental_consents_table | `op.drop_table("parental_consents")` |
| `alembic/versions/20260505_1734_add_missing_production_indexes.py` | 30 | parental_consents_table | `"parental_consents",` |
| `alembic/versions/20260505_1734_add_missing_production_indexes.py` | 37 | parental_consents_table | `op.drop_index("ix_active_parental_consents", "parental_consents")` |
| `alembic/versions/20260507_1200_popia_consent_audit_hardening.py` | 32 | parental_consents_table | `"parental_consents",` |
| `alembic/versions/20260507_1200_popia_consent_audit_hardening.py` | 35 | parental_consents_table | `op.create_index("ix_parental_consents_status", "parental_consents", ["status"])` |
| `alembic/versions/20260507_1200_popia_consent_audit_hardening.py` | 48 | parental_consents_table | `op.drop_index("ix_parental_consents_status", table_name="parental_consents")` |
| `alembic/versions/20260507_1200_popia_consent_audit_hardening.py` | 49 | parental_consents_table | `op.drop_column("parental_consents", "status")` |
| `alembic/versions/20260507_1330_database_integrity_constraints.py` | 28 | parental_consents_table | `"parental_consents",` |
| `alembic/versions/20260507_1330_database_integrity_constraints.py` | 32 | parental_consents_table | `"parental_consents",` |
| `alembic/versions/20260507_1330_database_integrity_constraints.py` | 70 | parental_consents_table | `"parental_consents",` |
| `alembic/versions/20260507_1330_database_integrity_constraints.py` | 75 | parental_consents_table | `"parental_consents",` |
| `alembic/versions/20260507_1330_database_integrity_constraints.py` | 111 | parental_consents_table | `"parental_consents",` |
| `alembic/versions/20260507_1330_database_integrity_constraints.py` | 116 | parental_consents_table | `"parental_consents",` |
| `alembic/versions/20260507_1330_database_integrity_constraints.py` | 214 | parental_consents_table | `op.drop_constraint("ck_parental_consents_revoked_after_grant", "parental_consents", type_="check")` |
| `alembic/versions/20260507_1330_database_integrity_constraints.py` | 215 | parental_consents_table | `op.drop_constraint("ck_parental_consents_expiry_after_grant", "parental_consents", type_="check")` |
| `alembic/versions/20260507_1330_database_integrity_constraints.py` | 224 | parental_consents_table | `op.drop_index("ix_parental_consents_active_status", table_name="parental_consents")` |
| `alembic/versions/20260507_1330_database_integrity_constraints.py` | 225 | parental_consents_table | `op.drop_index("ix_parental_consents_guardian_learner_status", table_name="parental_consents")` |
| `alembic/versions/20260507_1330_database_integrity_constraints.py` | 232 | parental_consents_table | `op.drop_column("parental_consents", "updated_at")` |
| `alembic/versions/20260507_1330_database_integrity_constraints.py` | 233 | parental_consents_table | `op.drop_column("parental_consents", "created_at")` |
| `alembic/versions/20260510_0300_popia_consent_audit_dsr.py` | 43 | consent_records_table | `"consent_records",` |
| `alembic/versions/20260510_0300_popia_consent_audit_dsr.py` | 56 | consent_records_table | `op.create_index("ix_consent_records_learner_id", "consent_records", ["learner_id"])` |
| `alembic/versions/20260510_0300_popia_consent_audit_dsr.py` | 127 | consent_records_table | `"consent_records", "audit_events",` |
| `alembic/versions/_deprecated/0001_initial_consolidated_schema.py` | 102 | parental_consents_table | `# ── parental_consents ─────────────────────────────────────────────────` |
| `alembic/versions/_deprecated/0001_initial_consolidated_schema.py` | 104 | parental_consents_table | `"parental_consents",` |
| `alembic/versions/_deprecated/0001_initial_consolidated_schema.py` | 132 | parental_consents_table | `op.create_index("ix_consents_learner_id", "parental_consents", ["learner_id"])` |
| `alembic/versions/_deprecated/0001_initial_consolidated_schema.py` | 133 | parental_consents_table | `op.create_index("ix_consents_status", "parental_consents", ["status"])` |
| `alembic/versions/_deprecated/0001_initial_consolidated_schema.py` | 208 | parental_consents_table | `for table in ("guardians", "learners", "parental_consents", "study_plans"):` |
| `alembic/versions/_deprecated/0001_initial_consolidated_schema.py` | 217 | parental_consents_table | `for table in ("guardians", "learners", "parental_consents", "study_plans"):` |
| `alembic/versions/_deprecated/0001_initial_consolidated_schema.py` | 224 | parental_consents_table | `op.drop_table("parental_consents")` |
| `alembic/versions/_deprecated/0001_schema_from_technical_report.py` | 68 | parental_consents_table | `# ── parental_consents ────────────────────────────────────────────────────` |
| `alembic/versions/_deprecated/0001_schema_from_technical_report.py` | 70 | parental_consents_table | `"parental_consents",` |
| `alembic/versions/_deprecated/0001_schema_from_technical_report.py` | 81 | parental_consents_table | `op.create_index("ix_consents_learner_id", "parental_consents", ["learner_id"])` |
| `alembic/versions/_deprecated/0001_schema_from_technical_report.py` | 187 | parental_consents_table | `"parental_consents",` |
| `app/api_v2_deps/consent_lifecycle.py` | 11 | consent_service | `from app.modules.consent.service import ConsentService` |
| `app/api_v2_deps/consent_lifecycle.py` | 12 | consent_repository | `from app.repositories.consent_repository import ConsentRepository` |
| `app/api_v2_deps/consent_lifecycle.py` | 72 | consent_service | `def get_canonical_consent_service(db: AsyncSession = Depends(get_db)) -> ConsentService:` |
| `app/api_v2_deps/consent_lifecycle.py` | 74 | consent_service | `params = inspect.signature(ConsentService).parameters` |
| `app/api_v2_deps/consent_lifecycle.py` | 77 | consent_service | `return POPIAConsentLifecycleAdapter(ConsentService(session=db))` |
| `app/api_v2_deps/consent_lifecycle.py` | 79 | consent_service | `return POPIAConsentLifecycleAdapter(ConsentService(db=db))` |
| `app/api_v2_deps/consent_lifecycle.py` | 81 | consent_repository | `if "consent_repository" in params or "consent_repo" in params:` |
| `app/api_v2_deps/consent_lifecycle.py` | 82 | consent_repository | `repo = ConsentRepository(db)` |
| `app/api_v2_deps/consent_lifecycle.py` | 84 | consent_service | `return POPIAConsentLifecycleAdapter(ConsentService(consent_repository=repo))` |
| `app/api_v2_deps/consent_lifecycle.py` | 85 | consent_service | `return POPIAConsentLifecycleAdapter(ConsentService(consent_repo=repo))` |
| `app/api_v2_deps/consent_lifecycle.py` | 85 | consent_repository | `return POPIAConsentLifecycleAdapter(ConsentService(consent_repo=repo))` |
| `app/api_v2_deps/consent_lifecycle.py` | 88 | consent_service | `return POPIAConsentLifecycleAdapter(ConsentService(db))` |
| `app/api_v2_deps/consent_lifecycle.py` | 91 | consent_service | `"Cannot construct canonical ConsentService from AsyncSession. "` |
| `app/api_v2_deps/consent_lifecycle.py` | 92 | consent_service | `"Align app.modules.consent.service.ConsentService constructor before using POPIA lifecycle routes."` |
| `app/api_v2_routers/consent.py` | 18 | consent_service | `from app.modules.consent.service import ConsentService` |
| `app/api_v2_routers/consent.py` | 47 | consent_service | `# AuditLog emission is handled inside ConsentService.grant().` |
| `app/api_v2_routers/consent.py` | 47 | consent_grant | `# AuditLog emission is handled inside ConsentService.grant().` |
| `app/api_v2_routers/consent.py` | 48 | consent_service | `consent = await ConsentService(db).grant(` |
| `app/api_v2_routers/consent.py` | 48 | consent_grant | `consent = await ConsentService(db).grant(` |
| `app/api_v2_routers/consent.py` | 80 | consent_service | `# AuditLog emission is handled inside ConsentService.revoke().` |
| `app/api_v2_routers/consent.py` | 80 | consent_revoke | `# AuditLog emission is handled inside ConsentService.revoke().` |
| `app/api_v2_routers/consent.py` | 81 | consent_service | `await ConsentService(db).revoke(` |
| `app/api_v2_routers/consent.py` | 81 | consent_revoke | `await ConsentService(db).revoke(` |
| `app/api_v2_routers/consent.py` | 104 | consent_service | `consent = await ConsentService(db).get_status(str(learner_id))` |
| `app/api_v2_routers/learners.py` | 143 | consent_service | `consent_svc = ConsentService(db)` |
| `app/api_v2_routers/parents.py` | 23 | consent_service | `from app.services.consent import ConsentService` |
| `app/api_v2_routers/parents.py` | 282 | consent_service | `consent_service = ConsentService(db)` |
| `app/api_v2_routers/popia.py` | 4 | require_active_consent | `All learner-data routes use the require_active_consent dependency (§4.2).` |
| `app/api_v2_routers/popia.py` | 23 | consent_service | `from app.modules.consent.service import ConsentService` |
| `app/api_v2_routers/popia.py` | 105 | consent_service | `consent_svc: ConsentService = Depends(get_canonical_consent_service),` |
| `app/api_v2_routers/popia.py` | 111 | consent_grant | `return await consent_svc.grant(` |
| `app/api_v2_routers/popia.py` | 123 | consent_service | `consent_svc: ConsentService = Depends(get_canonical_consent_service),` |
| `app/api_v2_routers/popia.py` | 141 | consent_service | `consent_svc: ConsentService = Depends(get_canonical_consent_service),` |
| `app/api_v2_routers/popia.py` | 156 | consent_service | `consent_svc: ConsentService = Depends(get_canonical_consent_service),` |
| `app/core/consent_gate.py` | 10 | require_active_consent | `_: ConsentRecord = Depends(require_active_consent),` |
| `app/core/consent_gate.py` | 26 | consent_service | `from app.services.consent_service import ConsentService` |
| `app/core/consent_gate.py` | 52 | require_active_consent | `async def require_active_consent(` |
| `app/core/consent_gate.py` | 54 | consent_service | `consent_service: ConsentService = Depends(),` |
| `app/core/consent_gate.py` | 71 | require_active_consent | `ActiveConsent = Annotated[ConsentRecord, Depends(require_active_consent)]` |
| `app/core/dependencies.py` | 21 | consent_repository | `from app.repositories.consent_repository import ConsentRepository` |
| `app/core/dependencies.py` | 28 | consent_repository | `async def get_consent_repo() -> ConsentRepository:` |
| `app/core/dependencies.py` | 29 | consent_repository | `return ConsentRepository()` |
| `app/core/dependencies.py` | 59 | require_active_consent | `async def require_active_consent(` |
| `app/core/dependencies.py` | 62 | consent_repository | `repo: ConsentRepository = Depends(get_consent_repo),` |
| `app/core/dependencies.py` | 71 | require_active_consent | `dependencies=[Depends(require_active_consent)],` |
| `app/core/dependencies.py` | 94 | consent_repository | `repo: ConsentRepository = Depends(get_consent_repo),` |
| `app/core/dependencies.py` | 106 | require_active_consent | `await require_active_consent(learner_id, db, repo)` |
| `app/domain/consent.py` | 68 | consent_grant | `def grant(self, privacy_notice_version: str) -> "ConsentRecord":` |
| `app/models/__init__.py` | 132 | parental_consent_model | `consents: Mapped[list[ParentalConsent]] = relationship("ParentalConsent", back_populates="guardian")` |
| `app/models/__init__.py` | 158 | parental_consent_model | `consents: Mapped[list[ParentalConsent]] = relationship("ParentalConsent", back_populates="learner")` |
| `app/models/__init__.py` | 180 | parental_consent_model | `class ParentalConsent(Base):` |
| `app/models/__init__.py` | 181 | parental_consents_table | `__tablename__ = "parental_consents"` |
| `app/modules/consent/__init__.py` | 3 | consent_service | `Provides the :class:`~app.modules.consent.service.ConsentService` for` |
| `app/modules/consent/service.py` | 15 | consent_service | `from app.modules.consent.service import ConsentService` |
| `app/modules/consent/service.py` | 17 | consent_service | `svc = ConsentService(db)` |
| `app/modules/consent/service.py` | 18 | require_active_consent | `await svc.require_active_consent("learner-uuid", actor_id="user-uuid")` |
| `app/modules/consent/service.py` | 29 | consent_repository | `from app.repositories.repositories import ConsentRepository` |
| `app/modules/consent/service.py` | 32 | consent_service | `class ConsentService:` |
| `app/modules/consent/service.py` | 43 | consent_service | `svc = ConsentService(db)` |
| `app/modules/consent/service.py` | 44 | consent_grant | `consent = await svc.grant(` |
| `app/modules/consent/service.py` | 55 | consent_repository | `consent_repo: ConsentRepository \| None = None,` |
| `app/modules/consent/service.py` | 63 | consent_repository | `consent_repo: Optional :class:`~app.repositories.consent_repository.ConsentRepository`` |
| `app/modules/consent/service.py` | 75 | consent_service | `svc = ConsentService(db)  # auto-creates repos` |
| `app/modules/consent/service.py` | 76 | consent_service | `svc = ConsentService(consent_repo=repo)  # explicit repo` |
| `app/modules/consent/service.py` | 76 | consent_repository | `svc = ConsentService(consent_repo=repo)  # explicit repo` |
| `app/modules/consent/service.py` | 78 | consent_repository | `if consent_repo is None:` |
| `app/modules/consent/service.py` | 80 | consent_service | `raise ValueError("ConsentService requires a db session or consent_repo")` |
| `app/modules/consent/service.py` | 80 | consent_repository | `raise ValueError("ConsentService requires a db session or consent_repo")` |
| `app/modules/consent/service.py` | 81 | consent_repository | `consent_repo = ConsentRepository(db)` |
| `app/modules/consent/service.py` | 86 | consent_repository | `self._repo = consent_repo` |
| `app/modules/consent/service.py` | 94 | require_active_consent | `async def require_active_consent(self, learner_id: str, actor_id: str \| None = None) -> ConsentPolicyDecision:` |
| `app/modules/consent/service.py` | 113 | consent_grant | `async def grant(` |
| `app/modules/consent/service.py` | 125 | consent_repository | `:meth:`~app.repositories.consent_repository.ConsentRepository.grant`` |
| `app/modules/consent/service.py` | 142 | consent_grant | `consent = await svc.grant(` |
| `app/modules/consent/service.py` | 147 | consent_grant | `consent = await self._repo.grant(` |
| `app/modules/consent/service.py` | 163 | consent_revoke | `async def revoke(self, learner_id: str, guardian_id: str \| None = None, reason: str = "revoked") -> int:` |
| `app/modules/consent/service.py` | 181 | consent_revoke | `count = await svc.revoke("l-001", guardian_id="g-001")` |
| `app/modules/consent/service.py` | 186 | consent_revoke | `count = await self._repo.revoke(str(learner_id), reason=reason)` |
| `app/modules/consent/service.py` | 251 | consent_revoke | `await self.revoke(str(learner_id), guardian_id=guardian_id, reason="erasure_requested")` |
| `app/modules/diagnostics/service.py` | 3 | consent_service | `Provides a :class:`ConsentService` used by diagnostic flows to enforce` |
| `app/modules/diagnostics/service.py` | 22 | parental_consent_model | `from app.models import ParentalConsent` |
| `app/modules/diagnostics/service.py` | 23 | consent_repository | `from app.repositories import ConsentRepository, LearnerRepository` |
| `app/modules/diagnostics/service.py` | 25 | consent_repository | `_consent_repo = ConsentRepository()` |
| `app/modules/diagnostics/service.py` | 29 | consent_service | `class ConsentService:` |
| `app/modules/diagnostics/service.py` | 42 | consent_service | `svc = ConsentService()` |
| `app/modules/diagnostics/service.py` | 43 | require_active_consent | `consent = await svc.require_active_consent(learner_id, db)` |
| `app/modules/diagnostics/service.py` | 54 | parental_consent_model | `) -> ParentalConsent:` |
| `app/modules/diagnostics/service.py` | 58 | parental_consent_model | `:class:`~app.models.ParentalConsent` record, and writes an` |
| `app/modules/diagnostics/service.py` | 70 | parental_consent_model | `ParentalConsent: The newly created consent record.` |
| `app/modules/diagnostics/service.py` | 88 | consent_grant | `consent = await _consent_repo.grant(` |
| `app/modules/diagnostics/service.py` | 148 | consent_revoke | `count = await _consent_repo.revoke(learner_id, db, reason=reason)` |
| `app/modules/diagnostics/service.py` | 161 | require_active_consent | `async def require_active_consent(` |
| `app/modules/diagnostics/service.py` | 163 | parental_consent_model | `) -> ParentalConsent:` |
| `app/modules/diagnostics/service.py` | 174 | parental_consent_model | `ParentalConsent: The active :class:`~app.models.ParentalConsent`` |
| `app/modules/diagnostics/service.py` | 184 | require_active_consent | `consent = await svc.require_active_consent(learner_id, db)` |
| `app/modules/diagnostics/service.py` | 195 | parental_consent_model | `) -> list[ParentalConsent]:` |
| `app/modules/diagnostics/service.py` | 206 | parental_consent_model | `list[ParentalConsent]: Consent records expiring within the` |
| `app/modules/jobs.py` | 206 | parental_consent_model | `consent: A :class:`~app.models.ParentalConsent` record with` |
| `app/modules/lessons/service.py` | 11 | consent_service | `:meth:`~app.modules.consent.service.ConsentService.require_active_consent`` |
| `app/modules/lessons/service.py` | 11 | require_active_consent | `:meth:`~app.modules.consent.service.ConsentService.require_active_consent`` |
| `app/modules/lessons/service.py` | 39 | consent_service | `from app.services.consent import ConsentService` |
| `app/modules/lessons/service.py` | 82 | consent_service | `self._consent_service = ConsentService(db)` |
| `app/modules/lessons/service.py` | 93 | consent_service | `:meth:`~app.modules.consent.service.ConsentService.require_active_consent`.` |
| `app/modules/lessons/service.py` | 93 | require_active_consent | `:meth:`~app.modules.consent.service.ConsentService.require_active_consent`.` |
| `app/modules/lessons/service.py` | 121 | require_active_consent | `await self._consent_service.require_active_consent(` |
| `app/repositories/__init__.py` | 6 | consent_repository | `from app.repositories.consent_repository import ConsentRepository` |
| `app/repositories/__init__.py` | 16 | consent_repository | `"ConsentRepository",` |
| `app/repositories/consent_repository.py` | 17 | consent_repository | `class ConsentRepository:` |
| `app/repositories/consent_repository.py` | 26 | consent_records_table | `SELECT * FROM consent_records` |
| `app/repositories/consent_repository.py` | 37 | consent_records_table | `"SELECT * FROM consent_records WHERE id = $1", record_id` |
| `app/repositories/consent_repository.py` | 44 | consent_records_table | `INSERT INTO consent_records (` |
| `app/repositories/consent_repository.py` | 60 | consent_records_table | `UPDATE consent_records SET` |
| `app/repositories/consent_repository.py` | 76 | consent_records_table | `SELECT * FROM consent_records` |
| `app/repositories/parent_report_repository.py` | 15 | parental_consent_model | `from app.models import ParentalConsent, SubjectMastery` |
| `app/repositories/parent_report_repository.py` | 24 | parental_consent_model | `select(ParentalConsent).where(` |
| `app/repositories/parent_report_repository.py` | 25 | parental_consent_model | `ParentalConsent.learner_id == learner_id,` |
| `app/repositories/parent_report_repository.py` | 26 | parental_consent_model | `ParentalConsent.guardian_id == guardian_id,` |
| `app/repositories/repositories.py` | 21 | parental_consent_model | `ParentalConsent,` |
| `app/repositories/repositories.py` | 123 | parental_consent_model | `await self.db.execute(delete(ParentalConsent).where(ParentalConsent.learner_id == learner_id))` |
| `app/repositories/repositories.py` | 131 | consent_repository | `class ConsentRepository:` |
| `app/repositories/repositories.py` | 135 | parental_consent_model | `async def create(self, **kwargs) -> ParentalConsent:` |
| `app/repositories/repositories.py` | 136 | parental_consent_model | `consent = ParentalConsent(**kwargs)` |
| `app/repositories/repositories.py` | 141 | parental_consent_model | `async def get_active(self, learner_id: str) -> ParentalConsent \| None:` |
| `app/repositories/repositories.py` | 143 | parental_consent_model | `select(ParentalConsent).where(` |
| `app/repositories/repositories.py` | 144 | parental_consent_model | `ParentalConsent.learner_id == learner_id,` |
| `app/repositories/repositories.py` | 145 | parental_consent_model | `ParentalConsent.revoked_at == None,  # noqa: E711` |
| `app/repositories/repositories.py` | 146 | parental_consent_model | `ParentalConsent.expires_at > datetime.now(UTC),` |
| `app/repositories/repositories.py` | 151 | parental_consent_model | `async def get_latest_for_learner(self, learner_id: str) -> ParentalConsent \| None:` |
| `app/repositories/repositories.py` | 153 | parental_consent_model | `select(ParentalConsent)` |
| `app/repositories/repositories.py` | 154 | parental_consent_model | `.where(ParentalConsent.learner_id == learner_id)` |
| `app/repositories/repositories.py` | 155 | parental_consent_model | `.order_by(ParentalConsent.created_at.desc())` |
| `app/repositories/repositories.py` | 160 | consent_grant | `async def grant(` |
| `app/repositories/repositories.py` | 168 | parental_consent_model | `) -> ParentalConsent:` |
| `app/repositories/repositories.py` | 169 | parental_consent_model | `consent = ParentalConsent(` |
| `app/repositories/repositories.py` | 180 | consent_revoke | `async def revoke(self, learner_id: str, reason: str = "revoked") -> int:` |
| `app/repositories/repositories.py` | 182 | parental_consent_model | `update(ParentalConsent)` |
| `app/repositories/repositories.py` | 184 | parental_consent_model | `ParentalConsent.learner_id == learner_id,` |
| `app/repositories/repositories.py` | 185 | parental_consent_model | `ParentalConsent.revoked_at == None,` |
| `app/repositories/repositories.py` | 191 | parental_consent_model | `async def renew(self, learner_id: str, guardian_id: str, consent_version: str) -> tuple[ParentalConsent \| None, ParentalConsent]:` |
| `app/repositories/repositories.py` | 194 | consent_revoke | `await self.revoke(learner_id, reason="renewed")` |
| `app/repositories/repositories.py` | 195 | consent_grant | `renewed = await self.grant(` |
| `app/repositories/repositories.py` | 203 | parental_consent_model | `async def get_expiring_soon(self, db: AsyncSession \| None = None, days: int = 30) -> list[ParentalConsent]:` |
| `app/repositories/repositories.py` | 207 | parental_consent_model | `select(ParentalConsent).where(` |
| `app/repositories/repositories.py` | 208 | parental_consent_model | `ParentalConsent.status == "granted",` |
| `app/repositories/repositories.py` | 209 | parental_consent_model | `ParentalConsent.expires_at <= datetime.now(UTC) + timedelta(days=days),` |
| `app/repositories/repositories.py` | 210 | parental_consent_model | `ParentalConsent.expires_at > datetime.now(UTC)` |
| `app/security/dependencies.py` | 150 | consent_service | `from app.modules.consent.service import ConsentService` |
| `app/security/dependencies.py` | 295 | consent_service | `return await ConsentService(db).require_active_consent(` |
| `app/security/dependencies.py` | 295 | require_active_consent | `return await ConsentService(db).require_active_consent(` |
| `app/services/auth_application_service.py` | 22 | consent_repository | `"consent_repo": (` |
| `app/services/auth_application_service.py` | 23 | consent_repository | `"app.repositories.repositories.ConsentRepository",` |
| `app/services/auth_application_service.py` | 24 | consent_repository | `"app.repositories.consent_repository.ConsentRepository",` |
| `app/services/auth_application_service.py` | 110 | consent_repository | `def consent_repo(self) -> Any:` |
| `app/services/auth_application_service.py` | 111 | consent_repository | `return self._repo("consent_repo")` |
| `app/services/auth_application_service.py` | 148 | consent_repository | `def consent_repo(self) -> Any:` |
| `app/services/auth_application_service.py` | 149 | consent_repository | `return self.repositories.consent_repo` |
| `app/services/auth_lifecycle_impl.py` | 72 | consent_repository | `consent_repo = auth_runtime.consent_repo` |
| `app/services/auth_lifecycle_impl.py` | 94 | consent_repository | `if await consent_repo.get_active(learner.id) is None:` |
| `app/services/auth_lifecycle_impl.py` | 95 | consent_repository | `await consent_repo.create(` |
| `app/services/auth_runtime_boundary.py` | 60 | consent_repository | `consent_repo: Any \| None = None` |
| `app/services/auth_runtime_boundary.py` | 94 | consent_repository | `_import_symbol("app.repositories.repositories.ConsentRepository")` |
| `app/services/auth_runtime_boundary.py` | 95 | consent_repository | `or _import_symbol("app.repositories.consent_repository.ConsentRepository")` |
| `app/services/auth_runtime_boundary.py` | 103 | consent_repository | `consent_repo = _construct_repository(consent_repo_cls, db) if consent_repo_cls is not None else None` |
| `app/services/auth_runtime_boundary.py` | 105 | consent_repository | `return AuthRuntimeContext(db=db, learner_repo=learner_repo, consent_repo=consent_repo, guardian_repo=guardian_repo)` |
| `app/services/consent.py` | 1 | consent_service | `from app.modules.consent.service import ConsentService` |
| `app/services/consent.py` | 3 | consent_service | `__all__ = ["ConsentService"]` |
| `app/services/consent_renewal_service.py` | 5 | parental_consent_model | `This service queries for ParentalConsent records expiring within 30 days` |
| `app/services/consent_renewal_service.py` | 29 | parental_consent_model | `"""Structural typing — matches the SQLAlchemy ParentalConsent ORM model."""` |
| `app/services/consent_renewal_service.py` | 194 | parental_consent_model | `Queries for ParentalConsent records expiring within ``days_threshold``` |
| `app/services/consent_renewal_service.py` | 280 | parental_consent_model | `from app.models import ParentalConsent  # type: ignore[import]` |
| `app/services/consent_renewal_service.py` | 289 | parental_consent_model | `sa_select(ParentalConsent).where(` |
| `app/services/consent_renewal_service.py` | 291 | parental_consent_model | `ParentalConsent.revoked_at.is_(None),` |
| `app/services/consent_renewal_service.py` | 292 | parental_consent_model | `ParentalConsent.expires_at > datetime.now(tz=timezone.utc),` |
| `app/services/consent_renewal_service.py` | 294 | parental_consent_model | `ParentalConsent.expires_at <= cutoff,` |
| `app/services/consent_runtime_compatibility.py` | 10 | consent_service | `"app.services.consent_service.ConsentService",` |
| `app/services/consent_runtime_compatibility.py` | 11 | consent_service | `"app.modules.consent.service.ConsentService",` |
| `app/services/consent_service.py` | 2 | consent_service | `# Canonical consent service: app.modules.consent.service.ConsentService` |
| `app/services/consent_service.py` | 26 | consent_repository | `from app.repositories.consent_repository import ConsentRepository` |
| `app/services/consent_service.py` | 29 | consent_service | `class ConsentService:` |
| `app/services/consent_service.py` | 32 | consent_repository | `consent_repo: ConsentRepository,` |
| `app/services/consent_service.py` | 35 | consent_repository | `self._consent = consent_repo` |
| `app/services/consent_service.py` | 42 | consent_grant | `async def grant(` |
| `app/services/consent_service.py` | 56 | consent_grant | `updated = existing.grant(privacy_notice_version)` |
| `app/services/consent_service.py` | 64 | consent_grant | `).grant(privacy_notice_version)` |
| `app/services/data_subject_rights_service.py` | 220 | consent_records_table | `"DELETE FROM consent_records WHERE learner_id = $1", learner_id` |
| `app/services/data_subject_rights_service.py` | 379 | consent_records_table | `"FROM consent_records WHERE learner_id=$1",` |
| `app/services/job_dependency_factory.py` | 56 | consent_service | `service_cls = _import_symbol("app.modules.consent.service.ConsentService")` |
| `app/services/job_dependency_factory.py` | 57 | consent_repository | `consent_repo_cls = _import_symbol("app.repositories.consent_repository.ConsentRepository")` |
| `app/services/job_dependency_factory.py` | 60 | consent_service | `raise RuntimeError("Canonical ConsentService not found")` |
| `app/services/job_dependency_factory.py` | 62 | consent_repository | `consent_repo = _construct(consent_repo_cls, session) if consent_repo_cls is not None else None` |
| `app/services/job_dependency_factory.py` | 70 | consent_repository | `if consent_repo is not None:` |
| `app/services/job_dependency_factory.py` | 72 | consent_repository | `kwargs["consent_repository"] = consent_repo` |
| `app/services/job_dependency_factory.py` | 73 | consent_repository | `if "consent_repo" in params:` |
| `app/services/job_dependency_factory.py` | 74 | consent_repository | `kwargs["consent_repo"] = consent_repo` |
| `app/services/popia_consent_lifecycle_adapter.py` | 215 | consent_grant | `async def grant(self, *args: Any, **kwargs: Any) -> ConsentRecord:` |
| `app/services/popia_consent_lifecycle_adapter.py` | 234 | consent_revoke | `async def revoke(self, *args: Any, **kwargs: Any) -> ConsentRecord:` |
| `app/services/popia_service.py` | 21 | parental_consent_model | `from app.models import DiagnosticSession, KnowledgeGap, LearnerProfile, Lesson, ParentalConsent` |
| `app/services/popia_service.py` | 24 | consent_service | `from app.services.consent import ConsentService` |
| `app/services/popia_service.py` | 56 | consent_service | `self.consent = ConsentService(db)` |
| `app/services/popia_service.py` | 81 | require_active_consent | `await self.consent.require_active_consent(learner_id, actor_id=requester_id)` |
| `app/services/popia_service.py` | 201 | consent_revoke | `await self.consent.revoke(learner_id, guardian_id=requester_id, reason="processing_restricted")` |
| `app/services/popia_service.py` | 221 | parental_consent_model | `consents = list((await self.db.scalars(select(ParentalConsent).where(ParentalConsent.learner_id == learner_id))).all())` |
| `app/services/popia_service.py` | 249 | parental_consents_table | `"parental_consents": [` |
| `app/services/popia_service.py` | 261 | parental_consents_table | `for section in ("diagnostic_sessions", "lessons", "knowledge_gaps", "parental_consents"):` |
| `app/services/popia_transactional_lifecycle.py` | 101 | consent_grant | `async def grant(self, **kwargs: Any) -> Any:` |
| `scripts/check_active_consent_route_sources.py` | 63 | consent_service | `"ConsentService(db).require_active_consent" not in source,` |
| `scripts/check_active_consent_route_sources.py` | 63 | require_active_consent | `"ConsentService(db).require_active_consent" not in source,` |
| `scripts/check_active_consent_route_sources.py` | 64 | consent_service | `"does not bypass central adapter" if "ConsentService(db).require_active_consent" not in source else "bypasses central adapter",` |
| `scripts/check_active_consent_route_sources.py` | 64 | require_active_consent | `"does not bypass central adapter" if "ConsentService(db).require_active_consent" not in source else "bypasses central adapter",` |
| `scripts/check_audit_event_contracts.py` | 22 | require_active_consent | `"require_active_consent",` |
| `scripts/check_audit_event_contracts.py` | 31 | consent_service | `"ConsentService(db).grant",` |
| `scripts/check_audit_event_contracts.py` | 32 | consent_service | `"ConsentService(db).revoke",` |
| `scripts/check_audit_event_contracts.py` | 33 | consent_service | `"AuditLog emission is handled inside ConsentService",` |
| `scripts/check_auth_lifecycle_method_extraction.py` | 34 | consent_repository | `for constructor in ("UserRepository(", "GuardianRepository(", "LearnerRepository(", "ConsentRepository("):` |
| `scripts/check_auth_repository_fixture_proof.py` | 38 | consent_repository | `("app.repositories.repositories.ConsentRepository", "app.repositories.consent_repository.ConsentRepository"),` |
| `scripts/check_auth_service_extraction.py` | 18 | consent_repository | `"ConsentRepository",` |
| `scripts/check_backend_consolidation_dragons.py` | 53 | consent_records_table | `"consent_records": _scan(r"\bconsent_records\b"),` |
| `scripts/check_backend_consolidation_dragons.py` | 54 | parental_consents_table | `"parental_consents": _scan(r"\bparental_consents\b"),` |
| `scripts/check_backend_consolidation_execution_packet.py` | 20 | consent_service | `"ConsentService",` |
| `scripts/check_consent_rejection_audit.py` | 12 | require_active_consent | `"require_active_consent",` |
| `scripts/check_database_persistence_production_readiness.py` | 106 | consent_repository | `"class ConsentRepository",` |
| `scripts/check_diagnostics_jobs_integrity.py` | 46 | consent_service | `if "ConsentService()" in jobs_text:` |
| `scripts/check_diagnostics_jobs_integrity.py` | 47 | consent_service | `failures.append("ConsentService empty constructor")` |
| `scripts/check_diagnostics_jobs_integrity.py` | 48 | consent_service | `print("- FAIL jobs module still contains ConsentService()")` |
| `scripts/check_diagnostics_jobs_integrity.py` | 50 | consent_service | `print("- PASS no ConsentService() empty constructor in jobs module")` |
| `scripts/check_diagnostics_jobs_integrity.py` | 52 | consent_repository | `for token in ("AsyncSessionLocal", "ConsentRepository", "validate_arq_job_payload"):` |
| `scripts/check_first_audit_runtime_wiring_no_destructive_actions.py` | 19 | consent_records_table | `"merge consent_records",` |
| `scripts/check_first_audit_runtime_wiring_no_destructive_actions.py` | 20 | parental_consents_table | `"merge parental_consents",` |
| `scripts/check_popia_consent_audit_evidence.py` | 95 | consent_service | `"ConsentService(db).require_active_consent",` |
| `scripts/check_popia_consent_audit_evidence.py` | 95 | require_active_consent | `"ConsentService(db).require_active_consent",` |
| `scripts/check_popia_consent_audit_evidence.py` | 149 | require_active_consent | `"require_active_consent",` |
| `scripts/check_popia_consent_audit_evidence.py` | 150 | require_active_consent | `"await self.consent.require_active_consent(learner_id, actor_id=requester_id)",` |
| `scripts/check_popia_consent_boundary_matrix.py` | 39 | require_active_consent | `row.marker in {"require_active_consent_for_current_user", "require_active_consent"},` |
| `scripts/check_runtime_blockers_after_followup_audit.py` | 30 | consent_repository | `for token in ("LearnerRepository(", "ConsentRepository(", "GuardianRepository("):` |
| `scripts/check_runtime_blockers_after_followup_audit.py` | 40 | consent_service | `for token in ("AsyncSessionLocal", "ConsentService("):` |
| `scripts/check_runtime_wiring_no_destructive_actions.py` | 20 | consent_records_table | `"merge consent_records",` |
| `scripts/check_runtime_wiring_no_destructive_actions.py` | 21 | parental_consents_table | `"merge parental_consents",` |
| `scripts/compare_orm_tables_to_database.py` | 94 | consent_records_table | `"consent_records",` |
| `scripts/generate_backend_deletion_candidate_inventory.py` | 14 | parental_consents_table | `("legacy_consent", re.compile(r"parental_consents\|ParentalConsent\|legacy consent", re.IGNORECASE)),` |
| `scripts/generate_backend_deletion_candidate_inventory.py` | 14 | parental_consent_model | `("legacy_consent", re.compile(r"parental_consents\|ParentalConsent\|legacy consent", re.IGNORECASE)),` |
| `scripts/generate_backend_deletion_candidate_inventory.py` | 15 | consent_repository | `("duplicate_repository", re.compile(r"class\s+\w*Repository\|AuditRepository\|ConsentRepository")),` |
| `scripts/generate_consent_callsite_inventory.py` | 28 | require_active_consent | `("require_active_consent", re.compile(r"\brequire_active_consent\b")),` |
| `scripts/generate_consent_callsite_inventory.py` | 89 | consent_records_table | `"- [ ] Identify whether `consent_records` is current state, event history, or both.",` |
| `scripts/generate_consent_callsite_inventory.py` | 90 | parental_consents_table | `"- [ ] Identify whether `parental_consents` is current state, relationship consent, or legacy.",` |
| `scripts/generate_consent_gate_inventory.py` | 18 | consent_service | `"ConsentService.require_active_consent",` |
| `scripts/generate_consent_gate_inventory.py` | 18 | require_active_consent | `"ConsentService.require_active_consent",` |
| `scripts/generate_consent_gate_inventory.py` | 76 | require_active_consent | `function="require_active_consent",` |
| `scripts/generate_consent_gate_inventory.py` | 78 | consent_service | `marker="ConsentService require_active_consent",` |
| `scripts/generate_consent_gate_inventory.py` | 78 | require_active_consent | `marker="ConsentService require_active_consent",` |
| `scripts/generate_popia_consent_boundary_matrix.py` | 92 | require_active_consent | `if "require_active_consent" in source:` |
| `scripts/generate_popia_consent_boundary_matrix.py` | 93 | require_active_consent | `return "require_active_consent"` |
| `scripts/inspect_diagnostics_and_jobs_integrity.py` | 52 | consent_service | `"consent_service_empty_constructor_count": jobs_text.count("ConsentService()"),` |
| `scripts/inspect_diagnostics_and_jobs_integrity.py` | 69 | consent_service | `f"\| ConsentService() empty constructor count in jobs \| {payload['consent_service_empty_constructor_count']} \|",` |
| `scripts/patch_popia_router_boundary.py` | 23 | consent_repository | `"from app.repositories.consent_repository import ConsentRepository",` |
| `scripts/popia_sweep.py` | 12 | consent_service | `ConsentService.require_active_consent() before any DB access.` |
| `scripts/popia_sweep.py` | 12 | require_active_consent | `ConsentService.require_active_consent() before any DB access.` |
| `scripts/popia_sweep.py` | 211 | require_active_consent | `learner data without calling require_active_consent().` |
| `scripts/popia_sweep.py` | 256 | require_active_consent | `"require_active_consent" in direct_body_source` |
| `scripts/popia_sweep.py` | 257 | consent_service | `or "ConsentService.require_active_consent" in direct_body_source` |
| `scripts/popia_sweep.py` | 257 | require_active_consent | `or "ConsentService.require_active_consent" in direct_body_source` |
| `scripts/popia_sweep.py` | 273 | consent_service | `"calling ConsentService.require_active_consent(). "` |
| `scripts/popia_sweep.py` | 273 | require_active_consent | `"calling ConsentService.require_active_consent(). "` |
| `scripts/popia_sweep.py` | 297 | consent_grant | `kw in func_source for kw in ["mark_granted", "mark_revoked", "execute_erasure", "grant(", "revoke("]` |
| `scripts/popia_sweep.py` | 297 | consent_revoke | `kw in func_source for kw in ["mark_granted", "mark_revoked", "execute_erasure", "grant(", "revoke("]` |
| `scripts/repair_arq_consent_reminder_job.py` | 42 | consent_repository | `repo = ConsentRepository(session)` |
| `scripts/repair_arq_consent_reminder_job.py` | 43 | consent_service | `params = inspect.signature(ConsentService).parameters` |
| `scripts/repair_arq_consent_reminder_job.py` | 45 | consent_repository | `if "consent_repo" in params:` |
| `scripts/repair_arq_consent_reminder_job.py` | 46 | consent_repository | `kwargs["consent_repo"] = repo` |
| `scripts/repair_arq_consent_reminder_job.py` | 53 | consent_service | `service = ConsentService(**kwargs) if kwargs else ConsentService(session)` |
| `scripts/repair_arq_consent_reminder_job.py` | 114 | consent_service | `text = _ensure_import(text, "from app.modules.consent.service import ConsentService")` |
| `scripts/repair_arq_consent_reminder_job.py` | 115 | consent_repository | `text = _ensure_import(text, "from app.repositories.consent_repository import ConsentRepository")` |
| `scripts/repair_arq_consent_reminder_job.py` | 119 | consent_service | `if "ConsentService()" in text:` |
| `scripts/repair_arq_consent_reminder_job.py` | 121 | consent_service | `"# ARQ Consent Job Repair Blocker\n\n`ConsentService()` empty constructor still appears in `app/modules/jobs.py`.\n",` |
| `scripts/repair_arq_consent_reminder_job.py` | 124 | consent_service | `print("ConsentService() empty constructor remains")` |
| `scripts/repair_arq_consent_reminder_job.py` | 141 | consent_repository | `"- Consent reminder job constructs `ConsentRepository(session)`.",` |
| `scripts/repair_arq_consent_reminder_job.py` | 142 | consent_service | `"- Consent reminder job constructs `ConsentService` with explicit dependencies.",` |
| `scripts/repair_arq_dependency_worker_import.py` | 93 | consent_service | `text = text.replace("assert \"ConsentService\" in source", "assert \"job_dependency_factory\" in source or \"run_consent_reminder_cycle\" in source")` |
| `scripts/repair_arq_dependency_worker_import.py` | 94 | consent_repository | `text = text.replace("assert \"ConsentRepository\" in source", "assert \"job_dependency_factory\" in source or \"run_consent_reminder_cycle\" in source")` |
| `scripts/repair_auth_repository_fixture_proof.py` | 27 | consent_repository | `"consent_repo": (` |
| `scripts/repair_auth_repository_fixture_proof.py` | 28 | consent_repository | `"app.repositories.repositories.ConsentRepository",` |
| `scripts/repair_auth_repository_fixture_proof.py` | 29 | consent_repository | `"app.repositories.consent_repository.ConsentRepository",` |
| `scripts/repair_auth_repository_fixture_proof.py` | 81 | consent_repository | `_import_symbol("app.repositories.repositories.ConsentRepository")` |
| `scripts/repair_auth_repository_fixture_proof.py` | 82 | consent_repository | `or _import_symbol("app.repositories.consent_repository.ConsentRepository")` |
| `scripts/repair_auth_repository_fixture_proof.py` | 90 | consent_repository | `consent_repo = _construct_repository(consent_repo_cls, db) if consent_repo_cls is not None else None` |
| `scripts/repair_auth_repository_fixture_proof.py` | 92 | consent_repository | `return AuthRuntimeContext(db=db, learner_repo=learner_repo, consent_repo=consent_repo, guardian_repo=guardian_repo)` |
| `scripts/repair_auth_repository_fixture_proof.py` | 94 | consent_repository | `pattern = r'def build_auth_runtime_context\(db: Any\) -> AuthRuntimeContext:\n(?:.\|\n)*?\n    return AuthRuntimeContext\(db=db, learner_repo=learner_repo, consent_repo=consent_repo, guardian_repo=guardian_repo\)\n'` |
| `scripts/repair_auth_service_extraction.py` | 20 | consent_repository | `"ConsentRepository",` |
| `scripts/repair_auth_service_extraction.py` | 30 | consent_repository | `"ConsentRepository": "consent_repo",` |
| `scripts/repair_popia_consent_lifecycle.py` | 126 | consent_service | `"from app.services.consent_service import ConsentService",` |
| `scripts/repair_popia_consent_lifecycle.py` | 127 | consent_service | `"from app.modules.consent.service import ConsentService",` |
| `scripts/repair_popia_consent_lifecycle.py` | 184 | consent_service | `def get_canonical_consent_service(db: AsyncSession = Depends(get_db)) -> ConsentService:` |
| `scripts/repair_popia_consent_lifecycle.py` | 186 | consent_service | `params = inspect.signature(ConsentService).parameters` |
| `scripts/repair_popia_consent_lifecycle.py` | 188 | consent_service | `return ConsentService(session=db)` |
| `scripts/repair_popia_consent_lifecycle.py` | 190 | consent_service | `return ConsentService(db=db)` |
| `scripts/repair_popia_consent_lifecycle.py` | 191 | consent_repository | `if "consent_repository" in params or "consent_repo" in params:` |
| `scripts/repair_popia_consent_lifecycle.py` | 192 | consent_repository | `repo = ConsentRepository(db)` |
| `scripts/repair_popia_consent_lifecycle.py` | 194 | consent_service | `return ConsentService(consent_repository=repo)` |
| `scripts/repair_popia_consent_lifecycle.py` | 195 | consent_service | `return ConsentService(consent_repo=repo)` |
| `scripts/repair_popia_consent_lifecycle.py` | 195 | consent_repository | `return ConsentService(consent_repo=repo)` |
| `scripts/repair_popia_consent_lifecycle.py` | 197 | consent_service | `return ConsentService(db)` |
| `scripts/repair_popia_consent_lifecycle.py` | 200 | consent_service | `"Cannot construct canonical ConsentService from AsyncSession. "` |
| `scripts/repair_popia_consent_lifecycle.py` | 201 | consent_service | `"Align app.modules.consent.service.ConsentService constructor before using POPIA lifecycle routes."` |
| `scripts/repair_popia_consent_lifecycle.py` | 262 | consent_service | `r":\s*ConsentService\s*=\s*Depends\([^)]*\)",` |
| `scripts/repair_popia_consent_lifecycle.py` | 263 | consent_service | `": ConsentService = Depends(get_canonical_consent_service)",` |
| `scripts/repair_popia_consent_lifecycle.py` | 276 | consent_service | `"# Canonical consent service: app.modules.consent.service.ConsentService\n"` |
| `scripts/repair_popia_consent_lifecycle.py` | 317 | consent_repository | `text = _ensure_import(text, "from app.repositories.consent_repository import ConsentRepository")` |
| `scripts/repair_popia_consent_lifecycle.py` | 351 | consent_service | `"\| Canonical ConsentService helper inserted \| true \|",` |
| `scripts/repair_runtime_blockers_after_followup_audit.py` | 40 | consent_service | `"return ConsentService(session=db)": "return POPIAConsentLifecycleAdapter(ConsentService(session=db))",` |
| `scripts/repair_runtime_blockers_after_followup_audit.py` | 41 | consent_service | `"return ConsentService(db=db)": "return POPIAConsentLifecycleAdapter(ConsentService(db=db))",` |
| `scripts/repair_runtime_blockers_after_followup_audit.py` | 42 | consent_service | `"return ConsentService(consent_repository=repo)": "return POPIAConsentLifecycleAdapter(ConsentService(consent_repository=repo))",` |
| `scripts/repair_runtime_blockers_after_followup_audit.py` | 43 | consent_service | `"return ConsentService(consent_repo=repo)": "return POPIAConsentLifecycleAdapter(ConsentService(consent_repo=repo))",` |
| `scripts/repair_runtime_blockers_after_followup_audit.py` | 43 | consent_repository | `"return ConsentService(consent_repo=repo)": "return POPIAConsentLifecycleAdapter(ConsentService(consent_repo=repo))",` |
| `scripts/repair_runtime_blockers_after_followup_audit.py` | 44 | consent_service | `"return ConsentService(db)": "return POPIAConsentLifecycleAdapter(ConsentService(db))",` |
| `scripts/repair_runtime_blockers_after_followup_audit.py` | 61 | consent_repository | `if "consent_repo:" not in text:` |
| `scripts/repair_runtime_blockers_after_followup_audit.py` | 64 | consent_repository | `"learner_repo: Any \| None = None\n    consent_repo: Any \| None = None\n    guardian_repo: Any \| None = None\n",` |
| `scripts/repair_runtime_blockers_after_followup_audit.py` | 69 | consent_repository | `"consent_repo_cls = (\n        _import_symbol(\"app.repositories.consent_repository.ConsentRepository\")\n        or _import_symbol(\"app.repositories.repositories.ConsentRepository\")\n    )\n    guardian_repo_cls = (\n` |
| `scripts/repair_runtime_blockers_after_followup_audit.py` | 85 | consent_repository | `text = re.sub(r"ConsentRepository\(\s*(?:db\|session\|database)\s*\)", "auth_runtime.consent_repo", text)` |
| `scripts/repair_runtime_blockers_after_followup_audit.py` | 89 | consent_repository | `for repo_name in ("ConsentRepository", "GuardianRepository", "LearnerRepository"):` |
| `scripts/repair_runtime_blockers_after_followup_audit.py` | 154 | consent_service | `if stripped.startswith("from app.modules.consent.service import ConsentService"):` |
| `scripts/repair_runtime_blockers_after_followup_audit.py` | 156 | consent_repository | `if stripped.startswith("from app.repositories") and any(name in line for name in ("ConsentRepository", "AuditRepository")):` |
| `scripts/validate_schema_integrity.py` | 27 | parental_consents_table | `"parental_consents",` |
| `scripts/validate_schema_integrity.py` | 45 | parental_consents_table | `"parental_consents": {` |
| `scripts/validate_schema_integrity.py` | 63 | parental_consents_table | `"parental_consents": {` |
| `scripts/validate_schema_integrity.py` | 101 | parental_consents_table | `if table_name in {"learner_profiles", "parental_consents", "diagnostic_sessions", "knowledge_gaps", "lessons"} and fk_count == 0:` |
| `tests/integration/test_auth_repository_fixture_proof.py` | 60 | consent_repository | `assert service.consent_repo.__class__.__module__ == "app.repositories.repositories"` |
| `tests/integration/test_consent_grant_authorization.py` | 38 | consent_grant | `async def grant(self, guardian_id: str, learner_id: str, consent_version: str, ip_hash: str \| None = None):` |
| `tests/integration/test_consent_grant_authorization.py` | 61 | consent_service | `monkeypatch.setattr(consent_router, "ConsentService", FakeConsentService)` |
| `tests/integration/test_consent_revoke_authorization.py` | 36 | consent_revoke | `async def revoke(self, learner_id: str, guardian_id: str, reason: str) -> None:` |
| `tests/integration/test_consent_revoke_authorization.py` | 54 | consent_service | `monkeypatch.setattr(consent_router, "ConsentService", FakeConsentService)` |
| `tests/integration/test_consent_status_authorization.py` | 58 | consent_service | `monkeypatch.setattr(consent_router, "ConsentService", FakeConsentService)` |
| `tests/integration/test_diagnostic_items_authorization.py` | 22 | require_active_consent | `async def require_active_consent(self, learner_id: str, actor_id: str \| None = None) -> None:` |
| `tests/integration/test_diagnostic_submit_authorization.py` | 22 | require_active_consent | `async def require_active_consent(self, learner_id: str, actor_id: str \| None = None) -> None:` |
| `tests/integration/test_gamification_award_xp_authorization.py` | 51 | require_active_consent | `async def require_active_consent(self, learner_id: str, actor_id: str \| None = None) -> None:` |
| `tests/integration/test_gamification_profile_authorization.py` | 32 | require_active_consent | `async def require_active_consent(self, learner_id: str, actor_id: str \| None = None) -> None:` |
| `tests/integration/test_learner_mastery_authorization.py` | 23 | require_active_consent | `async def require_active_consent(self, learner_id: str, actor_id: str \| None = None) -> None:` |
| `tests/integration/test_learner_read_authorization.py` | 23 | require_active_consent | `async def require_active_consent(self, learner_id: str, actor_id: str \| None = None) -> None:` |
| `tests/integration/test_parent_erasure_authorization.py` | 76 | consent_service | `monkeypatch.setattr(parents_router, "ConsentService", FakeConsentService)` |
| `tests/integration/test_parent_export_authorization.py` | 50 | require_active_consent | `async def require_active_consent(self, learner_id: str, actor_id: str \| None = None) -> None:` |
| `tests/integration/test_parent_progress_authorization.py` | 77 | require_active_consent | `async def require_active_consent(self, learner_id: str, actor_id: str \| None = None) -> None:` |
| `tests/integration/test_parent_trust_dashboard.py` | 84 | require_active_consent | `async def require_active_consent(self, _learner_id, actor_id=None):` |
| `tests/integration/test_popia_lifecycle_response_contract.py` | 34 | consent_grant | `async def grant(self, learner_id: uuid.UUID, guardian_id: uuid.UUID, consent_version: str, **_: Any) -> ConsentRecord:` |
| `tests/integration/test_popia_lifecycle_response_contract.py` | 46 | consent_revoke | `async def revoke(self, learner_id: uuid.UUID, guardian_id: uuid.UUID \| None = None, reason: str = "revoked") -> int:` |
| `tests/integration/test_popia_lifecycle_runtime_contract.py` | 13 | consent_grant | `async def grant(self, guardian_id, learner_id, consent_version, actor_id=None):` |
| `tests/integration/test_popia_lifecycle_runtime_contract.py` | 17 | consent_revoke | `async def revoke(self, guardian_id=None, learner_id=None, actor_id=None, reason=None):` |
| `tests/integration/test_popia_lifecycle_runtime_contract.py` | 27 | consent_grant | `await adapter.grant(` |
| `tests/integration/test_popia_lifecycle_runtime_contract.py` | 54 | consent_repository | `def __init__(self, db=None, session=None, consent_repo=None, consent_repository=None):` |
| `tests/integration/test_popia_lifecycle_runtime_contract.py` | 57 | consent_repository | `self.consent_repo = consent_repo or consent_repository` |
| `tests/integration/test_popia_lifecycle_runtime_contract.py` | 59 | consent_grant | `async def grant(self, guardian_id, learner_id, consent_version):` |
| `tests/integration/test_popia_lifecycle_runtime_contract.py` | 66 | consent_service | `monkeypatch.setattr(deps, "ConsentService", FakeCanonicalConsentService, raising=False)` |
| `tests/integration/test_popia_lifecycle_runtime_contract.py` | 67 | consent_repository | `monkeypatch.setattr(deps, "ConsentRepository", FakeConsentRepository, raising=False)` |
| `tests/integration/test_popia_transaction_rollback_proof.py` | 57 | consent_grant | `async def grant(self, *, guardian_id, learner_id, privacy_notice_version="v1", **kwargs):` |
| `tests/integration/test_popia_transaction_rollback_proof.py` | 110 | consent_grant | `await service.grant(guardian_id=uuid.uuid4(), learner_id=uuid.uuid4(), privacy_notice_version="v1")` |
| `tests/integration/test_popia_transaction_rollback_proof.py` | 125 | consent_grant | `await service.grant(guardian_id=uuid.uuid4(), learner_id=uuid.uuid4(), privacy_notice_version="v1")` |
| `tests/integration/test_popia_transaction_rollback_proof.py` | 140 | consent_grant | `await service.grant(guardian_id=uuid.uuid4(), learner_id=uuid.uuid4(), privacy_notice_version="v1")` |
| `tests/integration/test_rate_limits.py` | 30 | require_active_consent | `async def require_active_consent(self, _learner_id):` |
| `tests/legacy/integration/test_api_contracts.py` | 113 | consent_records_table | `assert "consent_records" in payload` |
| `tests/legacy/integration/test_consent_enforcement.py` | 21 | consent_service | `from app.api.services.consent_service import ConsentService, ConsentNotGrantedError` |
| `tests/legacy/integration/test_consent_enforcement.py` | 236 | consent_service | `# ── Unit tests for ConsentService ─────────────────────────────────────────────` |
| `tests/legacy/integration/test_consent_enforcement.py` | 239 | consent_service | `"""Fast unit tests for ConsentService logic — no DB required."""` |
| `tests/legacy/integration/test_parent_portal_integration.py` | 407 | consent_records_table | `consent_records = [mock_consent_granted]` |
| `tests/legacy/integration/test_parent_portal_integration.py` | 426 | consent_records_table | `consent_records_result.scalars.return_value.all.return_value = consent_records` |
| `tests/legacy/popia/test_popia_compliance.py` | 160 | parental_consent_model | `from app.models import ParentalConsent` |
| `tests/legacy/popia/test_popia_compliance.py` | 162 | parental_consent_model | `consent = ParentalConsent()` |
| `tests/legacy/popia/test_popia_compliance.py` | 176 | parental_consent_model | `from app.models import ParentalConsent` |
| `tests/legacy/popia/test_popia_compliance.py` | 177 | parental_consent_model | `consent = ParentalConsent()` |
| `tests/legacy/popia/test_popia_compliance.py` | 187 | parental_consent_model | `from app.models import ParentalConsent` |
| `tests/legacy/popia/test_popia_compliance.py` | 188 | parental_consent_model | `consent = ParentalConsent()` |
| `tests/legacy/popia/test_popia_compliance.py` | 196 | parental_consent_model | `from app.models import ParentalConsent` |
| `tests/legacy/popia/test_popia_compliance.py` | 197 | parental_consent_model | `consent = ParentalConsent()` |
| `tests/popia/test_consent_audit_trail.py` | 12 | consent_service | `from app.modules.consent.service import ConsentService` |
| `tests/popia/test_consent_audit_trail.py` | 53 | consent_service | `service = ConsentService(db_session)` |
| `tests/popia/test_consent_audit_trail.py` | 54 | consent_grant | `await service.grant(guardian.id, learner.id, "2.0", ip_hash="hashed-ip")` |
| `tests/popia/test_consent_audit_trail.py` | 65 | consent_service | `service = ConsentService(db_session)` |
| `tests/popia/test_consent_audit_trail.py` | 66 | consent_grant | `await service.grant(guardian.id, learner.id, "2.0")` |
| `tests/popia/test_consent_audit_trail.py` | 67 | consent_revoke | `await service.revoke(learner.id, guardian_id=guardian.id, reason="guardian_request")` |
| `tests/popia/test_consent_audit_trail.py` | 80 | consent_service | `service = ConsentService(db_session)` |
| `tests/popia/test_consent_audit_trail.py` | 81 | consent_grant | `await service.grant(guardian.id, learner.id, "2.0")` |
| `tests/popia/test_consent_audit_trail.py` | 95 | consent_service | `service = ConsentService(db_session)` |
| `tests/popia/test_consent_audit_trail.py` | 96 | consent_grant | `await service.grant(guardian.id, learner.id, "2.0")` |
| `tests/popia/test_consent_audit_trail.py` | 109 | consent_service | `service = ConsentService(db_session)` |
| `tests/popia/test_consent_audit_trail.py` | 112 | require_active_consent | `await service.require_active_consent(learner.id, actor_id=guardian.id)` |
| `tests/unit/test_arq_worker_import_contract.py` | 43 | consent_service | `assert "ConsentService(" not in source` |
| `tests/unit/test_auth_repository_fixture_proof_contracts.py` | 14 | consent_repository | `assert source.index("app.repositories.repositories.ConsentRepository") < source.index("app.repositories.consent_repository.ConsentRepository")` |
| `tests/unit/test_auth_repository_fixture_proof_contracts.py` | 21 | consent_repository | `assert source.index("app.repositories.repositories.ConsentRepository") < source.index("app.repositories.consent_repository.ConsentRepository")` |
| `tests/unit/test_auth_service_extraction_contracts.py` | 50 | consent_repository | `for token in ("UserRepository(", "GuardianRepository(", "LearnerRepository(", "ConsentRepository("):` |
| `tests/unit/test_consent_dependency_adapter.py` | 18 | consent_service | `assert "ConsentService(db).require_active_consent" in source` |
| `tests/unit/test_consent_dependency_adapter.py` | 18 | require_active_consent | `assert "ConsentService(db).require_active_consent" in source` |
| `tests/unit/test_consent_dependency_denial_paths.py` | 31 | consent_service | `It delegates directly to ConsentService.require_active_consent, whose` |
| `tests/unit/test_consent_dependency_denial_paths.py` | 31 | require_active_consent | `It delegates directly to ConsentService.require_active_consent, whose` |
| `tests/unit/test_consent_dependency_denial_paths.py` | 41 | consent_service | `assert "ConsentService(db).require_active_consent" in source` |
| `tests/unit/test_consent_dependency_denial_paths.py` | 41 | require_active_consent | `assert "ConsentService(db).require_active_consent" in source` |
| `tests/unit/test_consent_lifecycle.py` | 15 | consent_service | `from app.services.consent_service import ConsentService` |
| `tests/unit/test_consent_lifecycle.py` | 31 | consent_grant | `return _pending_record().grant("v1.0")` |
| `tests/unit/test_consent_lifecycle.py` | 44 | consent_grant | `r = _pending_record().grant("v1.0")` |
| `tests/unit/test_consent_lifecycle.py` | 50 | consent_grant | `r = _pending_record().grant("v1.0")` |
| `tests/unit/test_consent_lifecycle.py` | 85 | consent_grant | `r = _pending_record().deny().grant("v1.0")` |
| `tests/unit/test_consent_lifecycle.py` | 124 | consent_service | `def _service(self, has_consent: bool) -> ConsentService:` |
| `tests/unit/test_consent_lifecycle.py` | 125 | consent_repository | `consent_repo = MagicMock()` |
| `tests/unit/test_consent_lifecycle.py` | 127 | consent_service | `svc = ConsentService(consent_repo, audit_repo)` |
| `tests/unit/test_consent_lifecycle.py` | 127 | consent_repository | `svc = ConsentService(consent_repo, audit_repo)` |
| `tests/unit/test_consent_lifecycle.py` | 129 | consent_repository | `consent_repo.get_active_for_learner = AsyncMock(` |
| `tests/unit/test_consent_lifecycle.py` | 133 | consent_repository | `consent_repo.get_active_for_learner = AsyncMock(return_value=None)` |
| `tests/unit/test_consent_policy.py` | 10 | consent_service | `from app.modules.consent.service import ConsentService` |
| `tests/unit/test_consent_policy.py` | 81 | consent_service | `service = ConsentService(consent_repo=FakeRepo(None), audit_repo=audit)` |
| `tests/unit/test_consent_policy.py` | 81 | consent_repository | `service = ConsentService(consent_repo=FakeRepo(None), audit_repo=audit)` |
| `tests/unit/test_consent_policy.py` | 84 | require_active_consent | `await service.require_active_consent("learner-1", actor_id="guardian-1")` |
| `tests/unit/test_consent_policy.py` | 93 | consent_service | `service = ConsentService(` |
| `tests/unit/test_consent_policy.py` | 94 | consent_repository | `consent_repo=FakeRepo(consent(expires_at=datetime(2020, 1, 1, tzinfo=UTC))),` |
| `tests/unit/test_consent_policy.py` | 99 | require_active_consent | `await service.require_active_consent("learner-1", actor_id="guardian-1")` |
| `tests/unit/test_diagnostics_central_consent_source.py` | 17 | consent_service | `assert "ConsentService(db).require_active_consent" not in source` |
| `tests/unit/test_diagnostics_central_consent_source.py` | 17 | require_active_consent | `assert "ConsentService(db).require_active_consent" not in source` |
| `tests/unit/test_diagnostics_central_consent_source.py` | 18 | consent_service | `assert "from app.services.consent import ConsentService" not in source` |
| `tests/unit/test_diagnostics_jobs_integrity_contracts.py` | 71 | consent_service | `# Assert that ConsentService is not constructed directly in jobs.py` |
| `tests/unit/test_diagnostics_jobs_integrity_contracts.py` | 72 | consent_service | `assert "ConsentService()" not in jobs_source` |
| `tests/unit/test_diagnostics_jobs_integrity_contracts.py` | 77 | consent_repository | `# Assert that actual database session factory and ConsentRepository are in the dependency factory` |
| `tests/unit/test_diagnostics_jobs_integrity_contracts.py` | 79 | consent_repository | `assert "ConsentRepository" in factory_source` |
| `tests/unit/test_gamification_consent_gate_wiring.py` | 17 | consent_service | `assert "from app.services.consent import ConsentService" not in source` |
| `tests/unit/test_generate_consent_gate_inventory.py` | 14 | consent_service | `assert any("ConsentService" in row.marker for row in rows)` |
| `tests/unit/test_learner_read_consent_gate_wiring.py` | 17 | consent_service | `assert "from app.services.consent import ConsentService" not in source` |
| `tests/unit/test_parent_routes_consent_gate_wiring.py` | 25 | require_active_consent | `assert "await consent_service.require_active_consent" not in source` |
| `tests/unit/test_parent_routes_consent_gate_wiring.py` | 45 | consent_service | `assert "consent_service = ConsentService(db)" in block` |
| `tests/unit/test_popia_data_rights_consent_boundary.py` | 16 | require_active_consent | `assert "await self.consent.require_active_consent" in source` |
| `tests/unit/test_popia_data_rights_consent_boundary.py` | 25 | require_active_consent | `assert "await self.consent.require_active_consent(learner_id, actor_id=requester_id)" in block` |
| `tests/unit/test_popia_data_rights_consent_boundary.py` | 27 | require_active_consent | `"await self.consent.require_active_consent(learner_id, actor_id=requester_id)"` |
| `tests/unit/test_popia_data_rights_consent_boundary.py` | 46 | require_active_consent | `assert "self.consent.require_active_consent" not in dsr_section` |
| `tests/unit/test_runtime_blockers_after_followup_audit.py` | 15 | consent_grant | `async def grant(self, guardian_id, learner_id, consent_version, actor_id=None):` |
| `tests/unit/test_runtime_blockers_after_followup_audit.py` | 19 | consent_revoke | `async def revoke(self, guardian_id=None, learner_id=None, actor_id=None, reason=None):` |
| `tests/unit/test_runtime_blockers_after_followup_audit.py` | 28 | consent_grant | `await adapter.grant(guardian_id="guardian-1", learner_id="learner-1", privacy_notice_version="v1", actor_id="actor-1")` |
| `tests/unit/test_runtime_blockers_after_followup_audit.py` | 47 | consent_repository | `assert "ConsentRepository(" not in source` |
| `tests/unit/test_runtime_blockers_after_followup_audit.py` | 56 | consent_service | `assert "ConsentService(" not in source` |

## Review checklist

- [ ] Identify the canonical active-consent runtime service.
- [ ] Identify whether `consent_records` is current state, event history, or both.
- [ ] Identify whether `parental_consents` is current state, relationship consent, or legacy.
- [ ] Confirm POPIA routes keep explicit read/write authorization boundaries.
- [ ] Do not merge/drop consent tables without ADR and data-retention decision.
