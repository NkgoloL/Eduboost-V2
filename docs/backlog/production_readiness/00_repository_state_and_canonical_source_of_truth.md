# 0. Repository state and canonical source of truth

## 0.1 Canonical repo, fork, and branch policy

- [verify] `P0` Confirm canonical source repo in `docs/repository_governance.md`. Evidence: `docs/repository_governance.md`, `scripts/verify_repo_state.py`.
- [verify] `P0` Confirm active branch is `master`. Evidence: `docs/repository_governance.md`, `scripts/verify_repo_state.py`; verification gap: branch protection must be confirmed in GitHub settings.
- [verify] `P0` Confirm latest valid repo state is identified by the commit message containing `Merge pull request #52`. Evidence: `scripts/verify_repo_state.py`.
- [verify] `P0` Document relationship between `NkgoloL/Eduboost-V2` and `userxrebornbackup-ux/Eduboost-V2`. Evidence: `docs/repository_governance.md`.
- [verify] `P0` Document which repo produces official releases. Evidence: `docs/repository_governance.md`.
- [verify] `P0` Document which repo is allowed to receive production hotfixes. Evidence: `docs/repository_governance.md`.
- [verify] `P0` Document whether the backup fork is temporary, permanent mirror, or recovery source. Evidence: `docs/repository_governance.md`; verification gap: owner approval record still required.
- [verify] `P0` Stop using raw commit count as the canonical freshness signal. Evidence: `scripts/verify_repo_state.py`.
- [verify] `P0` Use head SHA + merge marker + release tag + CI evidence as freshness criteria. Evidence: `scripts/verify_repo_state.py`, `.github/workflows/repo-state.yml`; verification gap: release tag evidence still required at release time.
- [ ] `P1` Add mirror-sync policy.
- [ ] `P1` Add fork divergence-detection policy.
- [ ] `P1` Add fork recovery procedure.
- [ ] `P1` Add release authority section.
- [ ] `P1` Add security patch authority section.
- [ ] `P1` Add archive/deprecation policy for stale forks.
- [ ] `P2` Add branch naming conventions.
- [ ] `P2` Add PR naming conventions.
- [ ] `P2` Add issue labels for `backend`, `frontend`, `security`, `compliance`, `ai`, `curriculum`, `devops`, `docs`, `qa`, `ops`, and `product`.

## 0.2 Repo-state verification automation

- [verify] `P0` Add `scripts/verify_repo_state.py`. Evidence: `scripts/verify_repo_state.py`, `tests/unit/test_verify_repo_state.py`.
- [verify] `P0` Script must verify current git branch is `master`. Evidence: `scripts/verify_repo_state.py`; verification gap: release branch check runs strictly only on release branches.
- [verify] `P0` Script must verify remote URL matches accepted canonical or recovery repo. Evidence: `scripts/verify_repo_state.py`, `tests/unit/test_verify_repo_state.py`.
- [verify] `P0` Script must verify latest commit message contains the accepted freshness marker. Evidence: `scripts/verify_repo_state.py`, `tests/unit/test_verify_repo_state.py`.
- [verify] `P0` Script must print current head SHA. Evidence: `scripts/verify_repo_state.py`.
- [verify] `P0` Script must fail if working tree is dirty unless `--allow-dirty` is passed. Evidence: `scripts/verify_repo_state.py`, `tests/unit/test_verify_repo_state.py`.
- [verify] `P0` Script must fail if run from the wrong repo. Evidence: `scripts/verify_repo_state.py`.
- [verify] `P1` Add `make verify-repo-state`. Evidence: `Makefile`.
- [verify] `P1` Add CI step for repo-state verification. Evidence: `.github/workflows/repo-state.yml`.
- [ ] `P1` Add repo-state verification output to release evidence bundle.
- [ ] `P2` Add JSON output mode to `scripts/verify_repo_state.py`.

## 0.3 Branch protection and governance

- [ ] `P0` Protect `master`.
- [ ] `P0` Require pull request review before merge to `master`.
- [ ] `P0` Require required checks before merge to `master`.
- [ ] `P0` Disable force-push on `master`.
- [ ] `P0` Disable branch deletion on `master`.
- [ ] `P1` Require signed commits where feasible.
- [ ] `P1` Require linear history or document why merge commits are accepted.
- [ ] `P1` Add CODEOWNERS for backend.
- [ ] `P1` Add CODEOWNERS for frontend.
- [ ] `P1` Add CODEOWNERS for infrastructure.
- [ ] `P1` Add CODEOWNERS for security.
- [ ] `P1` Add CODEOWNERS for compliance.
- [ ] `P1` Add CODEOWNERS for curriculum/CAPS.
- [ ] `P1` Add CODEOWNERS for AI safety.
- [ ] `P1` Add CODEOWNERS for docs.
- [ ] `P1` Require security owner review for auth, secrets, crypto, authorization, and infra changes.
- [ ] `P1` Require compliance owner review for consent, POPIA, audit, export, erasure, and learner data changes.
- [ ] `P1` Require AI safety owner review for LLM prompts, lesson generation, RLHF, and content validation.
- [ ] `P1` Require curriculum owner review for CAPS map and diagnostic content.

---

