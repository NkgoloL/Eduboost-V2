from __future__ import annotations
import csv, re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TODO = ROOT/'TODO.md'
OUT = ROOT/'docs'/'backlog'; OUT.mkdir(parents=True, exist_ok=True)
EXCLUDE_DIRS={'.git','.venv','__pycache__','node_modules','.tmp','temp'}
EXCLUDE_FILES={'coverage.xml','package-lock.json','TODO.md'}
texts={}
paths=[]
for p in ROOT.rglob('*'):
    if not p.is_file(): continue
    rel=p.relative_to(ROOT)
    if set(rel.parts)&EXCLUDE_DIRS or p.name in EXCLUDE_FILES: continue
    paths.append(str(rel))
    if p.suffix.lower() in {'.py','.md','.yml','.yaml','.json','.js','.ts','.tsx','.css','.ini','.txt','.sh','.bicep','.env','.example'} or p.name in {'Makefile','Dockerfile'}:
        try: texts[str(rel)]=p.read_text(errors='ignore')[:40000].lower()
        except Exception: pass
pathset=set(paths)
combined_by_path={rel:(rel.lower()+'\n'+txt) for rel,txt in texts.items()}

STOP=set('the and for with from into every such only should must add ensure confirm verify define implement create build use using current before after all are not cannot has have this that when where why how what which every such local ci staging production supported optional dependencies tests test workflow workflows status states policy policies paths path fields field data docs document documented versioning review reviews queue queues service services endpoint endpoints'.split())

def exists(p):
    return (ROOT/p).exists() or any(x.startswith(p.rstrip('/')+'/') for x in paths)

def search_terms(terms, limit=8):
    hits=[]
    terms=[t.lower().replace('-','_') for t in terms if len(t)>=4]
    for rel, blob in combined_by_path.items():
        if any(t in blob.replace('-','_') for t in terms):
            hits.append(rel)
            if len(hits)>=limit: break
    return hits

def generic_evidence(task):
    terms=[]
    terms += re.findall(r'`([^`]+)`', task)
    terms += [w for w in re.findall(r'[A-Za-z][A-Za-z0-9_-]{3,}', task.lower()) if w not in STOP]
    return search_terms(terms[:12])

def parse_tasks():
    tasks=[]; section=''; subsection=''; idx=0
    for lineno,line in enumerate(TODO.read_text().splitlines(),1):
        if line.startswith('# '): section=line.strip('# ').strip(); subsection=''
        elif line.startswith('## '): subsection=line.strip('# ').strip()
        m=re.match(r'\s*- \[([ x])\] `\[([^\]]+)\]` (.*)', line)
        if m:
            idx+=1
            tasks.append({'id':f'TODO-{idx:03d}','line':lineno,'section':section,'subsection':subsection,'todo_checked':'x' if m.group(1)=='x' else '', 'priority':m.group(2),'task':m.group(3).strip()})
    return tasks

def infer_owner(s):
    if any(x in s for x in ['frontend','next.js','ux','mobile','accessibility','pwa','dashboard','browser']): return 'frontend'
    if any(x in s for x in ['auth','jwt','security','cookie','cors','password','rbac','rate limit','secret']): return 'security/backend'
    if any(x in s for x in ['popia','consent','privacy','erasure','export','retention','data subject','audit integrity']): return 'compliance/backend'
    if any(x in s for x in ['llm','ai','lesson generation','caps','curriculum','prompt','hallucination']): return 'ai/curriculum/backend'
    if any(x in s for x in ['database','alembic','postgres','repository','migration','index','constraint']): return 'backend/data'
    if any(x in s for x in ['docker','kubernetes','azure','ci','deployment','observability','prometheus','grafana','backup','restore']): return 'devops'
    if any(x in s for x in ['billing','subscription','pricing','email','notification']): return 'product/integrations'
    if any(x in s for x in ['analytics','experimentation','data science']): return 'analytics/data'
    if any(x in s for x in ['growth','launch','support','legal','business','partnership']): return 'product/ops'
    return 'backend/product'

# ordered curated rules: marker substring -> expected paths, status, note
RULES=[]
def add(marker, paths, status='Partial', note='Repo contains related evidence; completion needs targeted validation/tests.'):
    RULES.append((marker.lower(),paths,status,note))
# Governance / repo
add('repository_governance',['docs/repository_governance.md'],'Partial','Doc exists and names canonical repo; mirror/security authority details are skeletal.')
add('canonical repository',['docs/repository_governance.md'],'Human-decision','Doc names NkgoloL/Eduboost-V2, but upstream authority must be confirmed by owner.')
add('protect `master`',['.github/workflows/ci-cd.yml'],'Blocked','Branch protection is a GitHub setting, not verifiable from the ZIP.')
add('protect `main`',['.github/workflows/ci-cd.yml'],'Blocked','Branch protection is a GitHub setting, not verifiable from the ZIP.')
add('codeowners',['.github/CODEOWNERS'],'Partial','CODEOWNERS exists but coverage is narrow.')
add('issue templates',['.github/ISSUE_TEMPLATE/bug_report.yml','.github/ISSUE_TEMPLATE/feature_request.yml'],'Partial','Bug/feature templates exist; security/compliance/accessibility/curriculum/incident templates missing.')
add('pr template',['.github/PULL_REQUEST_TEMPLATE.md'],'Partial','Template exists but lacks full requested checklist.')
add('dependabot',['.github/dependabot.yml'],'Done','Dependabot covers pip, npm, Docker, and GitHub Actions.')
add('canonical dependency',['requirements/base.txt','requirements/dev.txt','requirements/docs.txt','requirements/ml.txt'],'Partial','Canonical requirements directory exists; root aliases need explicit policy.')
add('duplicate or stale root dependency',['requirements.txt','requirements-dev.txt','requirements-docs.txt','requirements-ml.txt'],'Partial','Root dependency aliases still exist.')
add('makefile',['Makefile'],'Partial','Makefile exists but lacks e2e/security/release-check/smoke targets.')
add('docs/adr',['docs/adr'],'Partial','ADR directory exists but requested ADR set incomplete.')
add('markdown linting',['.github/workflows/ci-cd.yml'],'Partial','Markdown lint exists; docs link checker not evident.')
# Runtime/API
add('app/api_v2.py',['app/api_v2.py'],'Partial','V2 entrypoint exists; deployment and legacy-shim guarantees remain incomplete.')
add('compatibility shim',['app/api/main.py'],'Missing','app/api/main.py is absent in the snapshot.')
add('deployment command',['tests/test_entrypoints.py','.github/workflows/ci-cd.yml'],'Partial','Entrypoint import smoke exists; all documented commands not proven.')
add('legacy-only routes',['tests/legacy'],'Partial','Legacy tests exist; route-exposure proof not complete.')
add('openapi schema',['docs/openapi.json'],'Done','docs/openapi.json exists.')
add('openapi diff',['.github/workflows/ci-cd.yml'],'Missing','No explicit OpenAPI diff gate found.')
add('routers are thin',['app/api_v2_routers'],'Partial','Routers exist, but several contain business/audit logic directly.')
add('business logic out of routers',['app/api_v2_routers','app/services','app/modules'],'Partial','Services/modules exist; router/service separation remains inconsistent.')
add('service contracts',['app/services','app/modules'],'Partial','Many services exist, but contracts/interfaces are inconsistent.')
add('duplicate service concepts',['app/services','app/modules'],'Partial','Both service_v2 and module services exist; consolidation still needed.')
add('business-logic location',['app/services','app/modules'],'Human-decision','Architecture decision required before consolidation.')
add('metaphor-layer',['app/services/ether.py','app/services/judiciary.py','app/services/fourth_estate.py','app/services/executive.py'],'Partial','Metaphor services still exist in active code.')
add('import boundaries',['.importlinter','.github/workflows/ci-cd.yml'],'Partial','Import-linter exists; boundaries need enforcement/cleanup.')
add('fastapi dependencies',['app/core/dependencies.py','app/core/security.py'],'Partial','Dependency helpers exist, not yet standardized across routers.')
add('ad-hoc service construction',['app/api_v2_routers'],'Partial','Routers still instantiate services/repositories directly.')
add('test dependency overrides',['tests/conftest.py'],'Partial','Test scaffolding exists; not all providers covered.')
add('correlation id',['app/core/middleware.py','app/core/logging.py','app/frontend/src/lib/api/client.ts'],'Partial','RequestID middleware and client exist; audit/tracing propagation requires validation.')
# Data/migrations
add('primary keys',['app/models','alembic/versions'],'Partial','Models/migrations exist; full schema audit required.')
add('indexes',['alembic/versions/20260505_1734_add_missing_production_indexes.py'],'Partial','Index migration exists; full checklist still needs verification.')
add('database-level constraints',['alembic/versions','app/models'],'Partial','Some constraints exist; full sensitive workflow constraint audit required.')
add('partial indexes',['alembic/versions/20260505_1734_add_missing_production_indexes.py'],'Partial')
add('transaction boundaries',['app/services','app/api_v2_routers'],'Partial')
add('slow-query',['app/core/database.py'],'Missing')
add('performance tests',['tests'],'Missing','No obvious performance test suite found.')
add('rollback strategy',['docs/db_rollback.md'],'Partial','Rollback doc exists; per-destructive-migration rollback plans incomplete.')
add('migration naming convention',['alembic/versions/20260505_1734_add_missing_production_indexes.py'],'Partial','One timestamped migration exists; older files use mixed naming.')
add('staging dry-run',['scripts/smoke_test_migrations.sh','.github/workflows/ci-cd.yml'],'Blocked','Needs staging environment and backup workflow validation.')
add('migration smoke',['scripts/smoke_test_migrations.sh','.github/workflows/ci-cd.yml'],'Partial')
add('synthetic seed',['scripts/seed_irt_items.py','scripts/seed_item_bank.py','tests/fixtures'],'Partial')
add('repository tests',['tests/unit/test_audit_repository.py','tests/unit/test_v2_services_full.py'],'Partial')
add('raw orm',['app/repositories','app/api_v2_routers'],'Partial')
add('repository method names',['app/repositories'],'Partial')
add('pagination',['app/api_v2_routers','app/repositories'],'Partial')
add('cursor pagination',['app/api_v2_routers/audit.py'],'Missing')
# Auth/privacy/security
add('signup, login, refresh',['app/api_v2_routers/auth.py','app/modules/auth/service.py','tests'],'Partial')
add('password hashing',['app/services/auth_service.py','app/core/security.py','tests/unit/test_v2_services_full.py'],'Partial')
add('password strength',['app/modules/auth/service.py','app/services/auth_service.py'],'Missing')
add('rate limiting',['app/core/rate_limit.py','app/api_v2.py','app/api_v2_routers/lessons.py'],'Partial')
add('account lockout',['app/modules/auth/service.py'],'Missing')
add('session inventory',['app/modules/auth/service.py'],'Missing')
add('mfa',['app/modules/auth/service.py'],'Missing')
add('passkeys',['app/modules/auth/service.py'],'Missing')
add('access-token ttl',['app/core/config.py'],'Partial')
add('refresh-token ttl',['app/core/config.py'],'Partial')
add('refresh tokens hashed',['app/modules/auth/service.py','app/services/auth_service.py'],'Partial')
add('refresh-token reuse',['app/modules/auth/service.py','app/services/auth_service.py'],'Partial')
add('redis-backed revocation',['app/core/security.py','app/core/redis.py','.env.example'],'Partial')
add('jwt signing-key rotation',['app/core/secret_rotation.py'],'Partial')
add('cookie settings',['app/api_v2_routers/auth.py','app/core/config.py'],'Partial')
add('define roles',['app/core/security.py','app/core/dependencies.py','app/domain/schemas.py'],'Partial')
add('object-level authorization',['app/api_v2_routers/learners.py','app/core/security.py'],'Partial')
add('policy helpers',['app/core/security.py','app/core/dependencies.py'],'Partial')
add('policy tests',['tests'],'Partial')
add('admin impersonation',['app'],'Missing')
add('consent states',['app/services/consent.py','app/modules/consent','app/domain/schemas.py'],'Partial')
add('parent/guardian consent',['app/services/consent.py','tests/popia'],'Partial')
add('declarative',['app/services/consent.py','app/api_v2_routers'],'Partial','Consent checks exist but are not consistently declarative dependencies.')
add('negative tests',['tests/popia','tests/test_popia_end_to_end.py'],'Partial')
add('consent renewal',['app/services/consent_renewal_service.py','app/api_v2_routers/consent_renewal.py'],'Partial')
add('consent withdrawal',['app/services/consent.py','app/api_v2_routers/consent.py'],'Partial')
add('consent versioning',['app/services/consent.py','docs/POPIA_COMPLIANCE.md'],'Partial')
add('school-mediated',['docs'],'Human-decision','Requires institutional deployment scope decision.')
add('export workflow',['app/api_v2_routers/popia.py','app/services/popia_service.py'],'Partial')
add('erasure workflow',['app/api_v2_routers/popia.py','app/services/popia_service.py','docs/popia_erasure.md'],'Partial')
add('correction/update',['app/services/popia_service.py','app/api_v2_routers/popia.py'],'Missing')
add('processing restriction',['app/services/popia_service.py','app/api_v2_routers/popia.py'],'Missing')
add('sla targets',['docs/POPIA_COMPLIANCE.md'],'Missing')
add('admin review queue',['app/api_v2_routers/popia.py'],'Missing')
add('machine-readable export',['app/services/popia_service.py'],'Partial')
add('data_retention_policy',['docs/data_retention_policy.md'],'Missing')
add('subprocessor_register',['docs/subprocessor_register.md'],'Missing')
add('audit events',['app/services/fourth_estate.py','app/services/audit_service.py','app/repositories/audit_repository.py'],'Partial')
add('tamper-evident',['app/repositories/audit_repository.py','alembic/versions/0006_v2_audit_events.py'],'Missing','Append-only exists; hash-chain/HMAC not evident.')
add('immutable retention',['docs/POPIA_COMPLIANCE.md'],'Missing')
add('audit dashboard',['app/api_v2_routers/audit.py','app/frontend/src'],'Partial')
add('audit completeness',['tests/unit/test_audit_repository.py'],'Partial')
# AI/CAPS/diagnostics/frontend/API/integrations/devops broad evidence
add('llm gateway',['app/modules/lessons/llm_gateway.py','app/services/lesson_service_v2.py'],'Partial')
add('pii-redaction',['app/services/pii_sweep.py','scripts/popia_sweep.py','tests/popia'],'Partial')
add('pii redaction',['app/services/pii_sweep.py','scripts/popia_sweep.py','tests/popia'],'Partial')
add('structured json',['app/domain/schemas.py','app/domain/api_v2_models.py'],'Partial')
add('circuit breaker',['app/modules/lessons/llm_gateway.py'],'Partial')
add('budget guardrails',['app/services/quota_service.py'],'Partial')
add('llm metadata',['app/services/telemetry.py','app/services/fourth_estate.py'],'Partial')
add('prompt-template',['app/modules/lessons','docs/llm'],'Partial')
add('golden prompt',['docs/LLM_Test_Gating.md','tests'],'Partial')
add('lesson output contract',['app/domain/schemas.py','app/domain/api_v2_models.py'],'Partial')
add('answer keys',['app/services/caps_validator.py','app/modules/lessons'],'Partial')
add('validators',['app/services/caps_validator.py','tests'],'Partial')
add('human review queue',['app/api_v2_routers','app/frontend/src'],'Missing')
add('content quality score',['app/services/caps_validator.py'],'Partial')
add('lesson regression',['tests'],'Partial')
add('model comparison',['scripts/evaluate_pedagogy.py','docs/LLM_Test_Gating.md'],'Partial')
add('caps topic map',['data','app/services/caps_validator.py','docs/launch_scope.md'],'Partial')
add('valid CAPS topic',['app/services/caps_validator.py'],'Partial')
add('coverage dashboards',['app/frontend/src','app/api_v2_routers'],'Missing')
add('curriculum coverage',['app/frontend/src','app/api_v2_routers'],'Missing')
add('alignment confidence',['app/services/caps_validator.py'],'Partial')
add('lesson variants',['app/modules/lessons','app/frontend/src'],'Partial')
add('adaptive remediation',['app/services/diagnostic_service_v2.py','app/services/study_plan_service_v2.py'],'Partial')
add('parent explanation mode',['app/services/parent_report_service_v2.py','app/frontend/src/components/eduboost/ParentDashboard.tsx'],'Partial')
add('teacher insight',['app/frontend/src'],'Missing')
add('low-bandwidth',['app/frontend/src/lib/api/offlineSync.ts','app/frontend/src/components/ServiceWorkerRegistration.tsx'],'Partial')
add('retrieval-augmented',['docs/LLM_Integration_Roadmap.md'],'Human-decision')
add('local/smaller models',['LLM_Integration_Roadmap.md','docs/LLM_Test_Gating.md'],'Human-decision')
add('diagnostic item schema',['app/modules/diagnostics','alembic/versions/0007_caps_irt_item_bank.py'],'Partial')
add('irt parameters',['app/modules/diagnostics/irt_engine.py','tests'],'Partial')
add('fisher information',['app/modules/diagnostics/irt_engine.py','tests'],'Partial')
add('item calibration',['scripts/seed_irt_items.py','scripts/seed_item_bank.py'],'Partial')
add('exposure limits',['app/modules/diagnostics'],'Missing')
add('session recovery',['app/modules/diagnostics','app/api_v2_routers/diagnostics.py'],'Partial')
add('confidence intervals',['app/modules/diagnostics'],'Missing')
add('item bank',['alembic/versions/0005_seed_irt_items.py','alembic/versions/0007_caps_irt_item_bank.py'],'Partial')
add('review status',['app/models','app/domain/schemas.py'],'Partial')
add('distractor',['app/modules/diagnostics','alembic/versions/0007_caps_irt_item_bank.py'],'Partial')
add('misconception',['app/repositories','app/modules/diagnostics'],'Partial')
add('spaced repetition',['app/services/study_plan_service_v2.py'],'Missing')
add('mastery model',['app/api_v2_routers/learners.py','app/services/study_plan_service_v2.py'],'Partial')
add('progress timelines',['app/frontend/src','app/api_v2_routers/learners.py'],'Partial')
add('subject-level',['app/api_v2_routers/learners.py'],'Partial')
add('bayesian knowledge',['docs'],'Human-decision')
# Frontend
add('environment variables',['app/frontend/next.config.js','.env.example','docs/environment_variables.md'],'Partial')
add('NEXT_PUBLIC',['app/frontend','docs/environment_variables.md'],'Partial')
add('error boundaries',['app/frontend/src/components/ui/ErrorMessage.tsx'],'Partial')
add('loading, empty',['app/frontend/src/components/ui/LoadingSpinner.tsx','app/frontend/src/components/ui/ErrorMessage.tsx'],'Partial')
add('typed api client',['app/frontend/src/lib/api/client.ts','app/frontend/src/lib/api/types.ts','app/frontend/src/lib/api/services.ts'],'Partial')
add('protected route guards',['app/frontend/src/app/(auth)/layout.tsx','app/frontend/src/app/(learner)/layout.tsx'],'Partial')
add('bundle analysis',['app/frontend/next.config.js'],'Missing')
add('signup/onboarding',['app/api_v2_routers/onboarding.py','app/frontend/src/components/eduboost/EntryScreens.tsx'],'Partial')
add('login, logout',['app/frontend/src/components/eduboost/EntryScreens.tsx','app/api_v2_routers/auth.py'],'Partial')
add('learner dashboard',['app/frontend/src/components/eduboost','app/frontend/src/app/page.tsx'],'Partial')
add('parent dashboard',['app/frontend/src/components/eduboost/ParentDashboard.tsx','app/frontend/src/app/parent-portal/page.tsx'],'Partial')
add('diagnostic ux',['app/frontend/src/components/eduboost/InteractiveDiagnostic.tsx'],'Partial')
add('lesson ux',['app/frontend/src/components/eduboost/InteractiveLesson.tsx'],'Partial')
add('study-plan ux',['app/frontend/src'],'Partial')
add('wcag',['app/frontend/src','playwright.config.ts'],'Missing','No explicit WCAG/a11y gate detected.')
add('keyboard navigation',['app/frontend/src/__tests__','playwright.config.ts'],'Missing')
add('color contrast',['app/frontend/src/app/globals.css','app/frontend/src/components/eduboost/styles.ts'],'Partial')
add('semantic headings',['app/frontend/src'],'Partial')
add('reduced-motion',['app/frontend/src/app/globals.css'],'Partial')
add('mobile',['app/frontend/src/app/globals.css','app/frontend/src/components/eduboost/styles.ts'],'Partial')
add('responsive layout',['app/frontend/src/__tests__'],'Missing')
add('pwa/low-data',['app/frontend/src/components/ServiceWorkerRegistration.tsx','app/frontend/src/lib/api/offlineSync.ts'],'Partial')
# API/integrations
add('response envelopes',['app/core/exceptions.py','app/domain/api_v2_models.py'],'Partial')
add('error shape',['app/core/exceptions.py'],'Partial')
add('openapi tags',['docs/openapi.json','app/api_v2_routers'],'Partial')
add('idempotency',['app/api_v2_routers/billing.py','app/api_v2_routers/lessons.py'],'Partial')
add('pagination metadata',['app/api_v2_routers','app/repositories'],'Partial')
add('billing provider',['app/services/stripe_service.py'],'Human-decision','Stripe service exists, but production provider choice must be approved.')
add('webhook signature',['app/api_v2_routers/billing.py','app/services/stripe_service.py'],'Partial')
add('subscription states',['app/services/subscription_service.py','app/domain/schemas.py'],'Partial')
add('pricing',['docs/launch_scope.md'],'Human-decision')
add('billing lifecycle',['tests'],'Missing')
add('invoices',['app/services/stripe_service.py'],'Partial')
add('email provider',['.env.example','app/core/config.py'],'Human-decision','Provider selection required; implementation not evident.')
add('transactional templates',['app/services','docs'],'Missing')
add('notification preferences',['app/services','app/api_v2_routers'],'Missing')
add('sms/whatsapp',['docs'],'Human-decision')
add('notification rate limits',['app/core/rate_limit.py'],'Missing')
# DevOps/ops
add('dockerfile builds',['docker/Dockerfile.v2','docker/Dockerfile.api','docker/Dockerfile.frontend','docker/Dockerfile.inference'],'Partial')
add('ci image build paths',['.github/workflows/ci-cd.yml','docker/Dockerfile.v2'],'Partial')
add('non-root',['docker/Dockerfile.v2','docker/Dockerfile.api','docker/Dockerfile.frontend'],'Partial')
add('pin base images',['docker'],'Partial')
add('multi-stage',['docker/Dockerfile.v2','docker/Dockerfile.frontend'],'Partial')
add('runtime images',['docker'],'Partial')
add('image labels',['docker'],'Missing')
add('production target explicitly',['bicep/container_apps.bicep','k8s/api-deployment.yml'],'Human-decision')
add('deployment assets match',['docker-compose.yml','docker-compose.prod.yml','k8s','bicep'],'Blocked')
add('manifests',['k8s/api-deployment.yml','bicep/container_apps.bicep'],'Partial')
add('horizontal autoscaling',['k8s'],'Missing')
add('environment variable inventory',['docs/environment_variables.md','.env.example'],'Partial')
add('secret management',['app/core/secret_rotation.py','.env.example'],'Partial')
add('release evidence bundle',['docs/release_checklist.md','.github/workflows/ci-cd.yml'],'Partial')
add('staging smoke',['tests/smoke','.github/workflows/ci-cd.yml'],'Partial')
add('logs, metrics, traces',['app/core/logging.py','app/core/metrics.py','prometheus.yml'],'Partial')
add('prometheus',['prometheus.yml','prometheus/alerts.yml','app/core/metrics.py'],'Partial')
add('grafana',['grafana/dashboards.yml','grafana/datasources.yml'],'Partial')
add('alertmanager',['alertmanager/alertmanager.yml','prometheus/alerts.yml'],'Partial')
add('incident response',['docs/incident_response.md','SECURITY.md'],'Partial')
add('backup',['scripts/backup_postgres.sh','scripts/db_backup.sh','scripts/db_restore.sh'],'Partial')
add('restore',['scripts/db_restore.sh','docs/db_rollback.md'],'Partial')
# default docs/general
add('release checklist',['docs/release_checklist.md'],'Done')
add('launch scope',['docs/launch_scope.md'],'Done')
add('data_inventory',['docs/data_inventory.md'],'Done')
add('data inventory',['docs/data_inventory.md'],'Done')
add('api reference',['docs/API_REFERENCE.md','docs/api_v2.md','docs/openapi.json'],'Partial')
add('architecture docs',['docs/architecture.md','docs/architecture'],'Partial')
add('security disclosure',['SECURITY.md'],'Partial')

HUMAN_MARKERS=['decide ','choose ','define pricing','legal review','privacy impact review','validate workflow with real','conduct user interviews','user interview','educator review','partnership','ngo/community','sponsored learner model','roadmap for future expansion']
BLOCKED_MARKERS=['verified in staging','staging and production','live before real learner data','before real learner data','enabled, encrypted, monitored','restore-tested','production branch','production promotion','real learner traffic','customer support','tax','company registration']

def classify(t):
    s=f"{t['section']} {t['subsection']} {t['task']}".lower(); owner=infer_owner(s)
    if t['todo_checked']:
        ev=generic_evidence(t['task'])
        return 'Done','TODO is already checked; evidence not exhaustively revalidated.' if not ev else 'TODO checked and supporting evidence found.',ev,owner
    if t['priority']=='research' or any(m in s for m in HUMAN_MARKERS):
        return 'Human-decision','Requires product/legal/business/education decision or empirical validation before implementation.',generic_evidence(t['task']),owner
    if any(m in s for m in BLOCKED_MARKERS):
        return 'Blocked','Cannot be fully verified from repository snapshot; needs GitHub/cloud/staging/operations access.',generic_evidence(t['task']),owner
    for marker, pths, status, note in RULES:
        if marker in s:
            present=[p for p in pths if exists(p)]
            if status=='Missing':
                if present: return 'Partial','Related file(s) exist, but requested capability was not evident/complete.',present,owner
                return 'Missing',note,[],owner
            if present: return status,note,present,owner
            return 'Missing',f'Expected evidence path(s) not found: {", ".join(pths)}',[],owner
    ev=generic_evidence(t['task'])
    if ev: return 'Missing','Only weak/indirect search hits were found; no specific implementation evidence was confirmed.',ev,owner
    return 'Missing','No meaningful implementation/config/doc evidence found in repository snapshot.',[],owner

def pr_bucket(t,status):
    if status=='Done': return 'none'
    sec=t['section'].lower()
    sub=t['subsection'].lower()
    s=f"{sec} {sub} {t['task']}".lower()
    # Primary bucketing follows TODO section numbers to avoid keyword leakage.
    if sec.startswith('1. '): return 'PR-001 Repo governance and backlog hygiene'
    if sec.startswith('2. ') or sub.startswith('9.1') or 'response envelopes' in s or 'error shape' in s: return 'PR-002 Backend runtime/API contract baseline'
    if sec.startswith('4. ') or 'jwt' in s or 'password' in s or 'rbac' in s: return 'PR-003 Auth/session/RBAC hardening'
    if sec.startswith('5. ') or 'popia' in s or 'consent' in s or 'erasure' in s or 'data subject' in s or 'audit integrity' in s: return 'PR-004 POPIA consent/data-rights/audit'
    if sec.startswith('3. '): return 'PR-005 Database/migration integrity'
    if sec.startswith('6. ') or sec.startswith('7. ') or sec.startswith('23. ') or ('caps' in s and not sec.startswith('26.')): return 'PR-006 AI/CAPS/diagnostics safety'
    if sec.startswith('8. '): return 'PR-007 Frontend core flows and accessibility'
    if sec.startswith('10. ') or sec.startswith('11. ') or sec.startswith('12. ') or sec.startswith('13. ') or sec.startswith('14. '): return 'PR-008 DevOps/observability/DR'
    return 'PR-009 Product/ops/future differentiation'

priority_score={'critical':100,'high':70,'medium':40,'low':20,'research':10}; status_score={'Partial':30,'Missing':25,'Blocked':10,'Human-decision':5,'Done':0}
def rank(t,status):
    s=f"{t['section']} {t['subsection']} {t['task']}".lower(); bonus=0
    if any(x in s for x in ['auth','jwt','security','popia','consent','erasure','learner data','audit','database','ready','backup']): bonus+=20
    if any(x in s for x in ['production','staging','real learner','billing']): bonus+=10
    if status=='Blocked': bonus-=10
    if status=='Human-decision': bonus-=20
    return priority_score.get(t['priority'],0)+status_score.get(status,0)+bonus

rows=[]
for t in parse_tasks():
    st,note,ev,owner=classify(t)
    rows.append({**t,'repo_status':st,'owner':owner,'evidence_paths':'; '.join(ev),'audit_note':note,'pr_bucket':pr_bucket(t,st),'rank_score':rank(t,st)})

with (OUT/'task_matrix.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

counts=Counter(r['repo_status'] for r in rows)
md=['# TODO.md Repository Audit\n','Generated from `TODO.md` against the current uploaded repository snapshot. Ignored `.git`, `.venv`, caches, frontend `node_modules`, lockfiles, temp files, and coverage artifacts.\n','## Status semantics\n','- **Done**: strong repo evidence or TODO already checked.\n- **Partial**: related implementation/config/docs exist, but scope is incomplete or unverified.\n- **Missing**: no meaningful evidence found.\n- **Blocked**: needs GitHub/cloud/staging/ops access.\n- **Human-decision**: requires product/legal/business/education decision or research.\n','## Summary\n','| Status | Count |\n|---|---:|']
for st in ['Done','Partial','Missing','Blocked','Human-decision']: md.append(f'| {st} | {counts[st]} |')
md += ['\n## Priority × repo status\n','| Priority | Done | Partial | Missing | Blocked | Human-decision | Total |\n|---|---:|---:|---:|---:|---:|---:|']
for p in ['critical','high','medium','research']:
    sub=[r for r in rows if r['priority']==p]
    md.append(f"| {p} | {sum(r['repo_status']=='Done' for r in sub)} | {sum(r['repo_status']=='Partial' for r in sub)} | {sum(r['repo_status']=='Missing' for r in sub)} | {sum(r['repo_status']=='Blocked' for r in sub)} | {sum(r['repo_status']=='Human-decision' for r in sub)} | {len(sub)} |")
md += ['\n## Highest-risk open items\n','| Rank | ID | Priority | Status | Owner | Task | Evidence |\n|---:|---|---|---|---|---|---|']
for i,r in enumerate([r for r in sorted(rows,key=lambda r:(-r['rank_score'],r['id'])) if r['repo_status']!='Done'][:40],1):
    md.append(f"| {i} | {r['id']} | {r['priority']} | {r['repo_status']} | {r['owner']} | {r['task'].replace('|','\\|')} | {(r['evidence_paths'] or '—').replace('|','\\|')} |")
md.append('\n## PR-sized backlog buckets\n')
by_pr=defaultdict(list)
for r in sorted(rows,key=lambda r:(-r['rank_score'],r['id'])): by_pr[r['pr_bucket']].append(r)
for bucket in ['PR-001 Repo governance and backlog hygiene','PR-002 Backend runtime/API contract baseline','PR-003 Auth/session/RBAC hardening','PR-004 POPIA consent/data-rights/audit','PR-005 Database/migration integrity','PR-006 AI/CAPS/diagnostics safety','PR-007 Frontend core flows and accessibility','PR-008 DevOps/observability/DR','PR-009 Product/ops/future differentiation']:
    open_items=[r for r in by_pr[bucket] if r['repo_status']!='Done']
    if not open_items: continue
    c=Counter(r['repo_status'] for r in open_items)
    md.append(f'\n### {bucket}\n')
    md.append(f"Open items: {len(open_items)} — Partial {c['Partial']}, Missing {c['Missing']}, Blocked {c['Blocked']}, Human-decision {c['Human-decision']}.\n")
    md.append('| ID | Priority | Status | Task | Evidence |\n|---|---|---|---|---|')
    for r in open_items[:18]: md.append(f"| {r['id']} | {r['priority']} | {r['repo_status']} | {r['task'].replace('|','\\|')} | {(r['evidence_paths'] or '—').replace('|','\\|')} |")
    if len(open_items)>18: md.append(f'\n_Additional items in CSV: {len(open_items)-18}._\n')
(OUT/'backlog_audit.md').write_text('\n'.join(md),encoding='utf-8')

cp=['# Critical Path\n','This sequence is optimized to reduce implementation risk, not checkbox velocity.\n','## Phase order\n']
for i,b in enumerate(['PR-001 Repo governance and backlog hygiene','PR-002 Backend runtime/API contract baseline','PR-003 Auth/session/RBAC hardening','PR-004 POPIA consent/data-rights/audit','PR-005 Database/migration integrity','PR-006 AI/CAPS/diagnostics safety','PR-007 Frontend core flows and accessibility','PR-008 DevOps/observability/DR','PR-009 Product/ops/future differentiation'],1):
    oi=[r for r in rows if r['pr_bucket']==b and r['repo_status']!='Done']; crit=sum(r['priority']=='critical' for r in oi)
    cp.append(f'{i}. **{b}** — {len(oi)} open, {crit} critical.')
cp += ['\n## External blockers / human decisions\n','| ID | Priority | Status | Task |\n|---|---|---|---|']
for r in sorted([r for r in rows if r['repo_status'] in {'Blocked','Human-decision'}],key=lambda r:(-priority_score.get(r['priority'],0),r['id']))[:90]:
    cp.append(f"| {r['id']} | {r['priority']} | {r['repo_status']} | {r['task'].replace('|','\\|')} |")
(OUT/'critical_path.md').write_text('\n'.join(cp),encoding='utf-8')

first=sorted([r for r in rows if r['pr_bucket']=='PR-001 Repo governance and backlog hygiene' and r['repo_status']!='Done'],key=lambda r:(-r['rank_score'],r['id']))
fb=['# First PR-sized Batch: Repository Governance and Backlog Hygiene\n','## Objective\nMake the repository easier to operate before touching high-risk auth/POPIA/AI code. This PR is intentionally low-runtime-risk and creates guardrails for later PRs.\n','## Included TODO items\n','| ID | Priority | Status | Task | Current evidence |\n|---|---|---|---|---|']
for r in first: fb.append(f"| {r['id']} | {r['priority']} | {r['repo_status']} | {r['task'].replace('|','\\|')} | {(r['evidence_paths'] or '—').replace('|','\\|')} |")
fb += ['\n## Concrete patch plan\n','1. Expand `.github/CODEOWNERS` to cover backend, frontend, infrastructure, security, compliance, curriculum, docs, and tests.','2. Add missing issue templates: security redirect, compliance concern, accessibility issue, curriculum/content issue, incorrect content, and production incident.','3. Expand `.github/PULL_REQUEST_TEMPLATE.md` with migration, POPIA, security, accessibility, analytics, deployment, rollback, and evidence-bundle checkboxes.','4. Update `docs/repository_governance.md` to cover mirrors, branch policy, release authority, secret rotation authority, security patch process, and archive policy.','5. Normalize dependency-file intent: `requirements/base.txt`, `dev.txt`, `docs.txt`, `ml.txt` as canonical; root files as compatibility aliases unless deleted by owner decision.','6. Add missing `Makefile` targets: `e2e`, `security`, `release-check`, and `smoke`.','7. Add ADR stubs for PostgreSQL audit ledger, Redis revocation, LLM provider abstraction, POPIA-first design, and CAPS alignment.','8. Add docs-link checking to CI or document it as a follow-up if dependency install is too heavy.','\n## Acceptance criteria\n','- Governance docs and templates exist in deterministic paths.','- Makefile help lists all required commands.','- Dependency hierarchy is unambiguous.','- PR template forces future security/privacy/accessibility/migration/deployment/rollback disclosure.','- No application runtime behavior changes.']
(OUT/'first_pr_batch.md').write_text('\n'.join(fb),encoding='utf-8')
print('Wrote', OUT/'task_matrix.csv')
print('Wrote', OUT/'backlog_audit.md')
print('Wrote', OUT/'critical_path.md')
print('Wrote', OUT/'first_pr_batch.md')
print('Counts', dict(counts))
