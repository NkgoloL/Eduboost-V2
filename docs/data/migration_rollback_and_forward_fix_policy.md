# Migration Rollback and Forward-Fix Policy (TSR-7.6)

## Policy Directives
1. **Single Linear Migration Head:**
   - Multiple heads in Alembic are strictly prohibited.
   - All migrations must have explicit `upgrade()` and `downgrade()` routines.
2. **Forward-Fix Principle for Production:**
   - Once a migration is applied in a release environment, schema modifications must be applied via forward-fix migrations rather than editing historical files.
3. **Pre-Deployment Dry Run Requirements:**
   - Migrations must be validated against empty-database spinup (`alembic upgrade head`) and tested for schema drift (`alembic check`).
4. **Data Preservation Safeguards:**
   - Additive operations (`ADD COLUMN`, `CREATE TABLE`) are favored over destructive drops.
   - Any column drop requires a two-step deprecation cycle.
