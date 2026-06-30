# Phase <NN> Evidence Index — <Phase Title>

**Evidence-pack version:** 1.0  
**Phase:** <NN>  
**Status:** Draft | Collecting | Frozen for Audit | Superseded  
**Evidence custodian:** <name/role>  
**Phase owner:** <name/role>  
**Execution-plan version:** <version/path>  
**Implementation-report version:** <version/path>  
**Canonical branch:** <branch>  
**Base commit:** <SHA>  
**Merge commit:** <SHA>  
**Build/image digest:** <digest or N/A>  
**Environment identity:** <environment/version>  
**Collection window:** <UTC start–end>  
**Freeze timestamp:** <UTC>  
**Evidence directory:** `docs/release-evidence/atlas/phase-<NN>/`

> This index is the authoritative manifest for the phase evidence pack. Evidence not listed here is contextual only and cannot close a mandatory criterion.

## 1. Evidence Completeness Summary

| Measure | Count |
|---|---:|
| Roadmap exit criteria | |
| Execution-plan criteria | |
| Criteria with evidence | |
| Criteria missing evidence | |
| Passing items | |
| Failing items | |
| Contextual-only items | |
| Restricted items | |

## 2. Criterion-to-Evidence Matrix

| Criterion ID | Criterion | Evidence IDs | Result | Blocking | Report section | Audit procedure |
|---|---|---|---|---|---|---|
| ... | ... | E-<NN>-001 | Pass/Fail | Yes/No | ... | ... |

## 3. Evidence Inventory

| Evidence ID | Title | Type | File / immutable link | Source commit | Environment | Tool/version | Operator | Timestamp | Exit code/result | Hash | Sensitivity | Retention |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E-<NN>-001 | ... | Raw log/Test report/Signed review/... | ... | ... | ... | ... | ... | ... | ... | ... | Public/Internal/Restricted | ... |

## 4. Test and Verification Totals

| Suite / review | Expected minimum | Passed | Failed | Skipped | XFailed | Warnings | Collection errors | Retries/flakes | Duration | Evidence ID |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

## 5. External and Manual Evidence

| Evidence ID | Reviewer/vendor | Scope | Qualification/authority | Signed/date | Release-candidate identity | Expiry/revalidation |
|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... | ... |

## 6. Defects, Exceptions, and Amendments Referenced

| ID | Type | Description | Approval | Status | Evidence IDs | Revalidation trigger |
|---|---|---|---|---|---|---|
| ... | Defect/Exception/Plan amendment | ... | ... | ... | ... | ... |

## 7. Sensitive Evidence Controls

Document redaction, encryption, access control, personal-data minimisation, secrets handling, retention, and deletion requirements. Evidence containing learner or guardian data must be de-identified unless the approved review requires otherwise.

## 8. Reproduction Instructions

Provide exact prerequisites and commands needed to reproduce the critical evidence from a clean checkout or approved environment.

## 9. Missing, Contextual, or Non-Reproducible Evidence

List every limitation. Missing mandatory evidence prevents the pack from being frozen.

## 10. Evidence Freeze Checklist

- [ ] Every roadmap and plan criterion is mapped.
- [ ] Raw or machine-readable outputs are retained where practical.
- [ ] Source commit, environment, tools, operator, timestamps, and results are recorded.
- [ ] Test counts, warnings, skips, xfails, collection errors, and retries are complete.
- [ ] Hashes or immutable links are recorded.
- [ ] Sensitive evidence is classified and protected.
- [ ] Contextual evidence is not used as closure proof without approved equivalence.
- [ ] Defects, exceptions, and amendments are linked.
- [ ] Reproduction instructions are tested.
- [ ] The implementation report references this exact evidence-pack version.

## 11. Evidence Completeness Declaration

| Role | Name | Decision | Date | Signature / immutable reference |
|---|---|---|---|---|
| Evidence Custodian | | Complete / Incomplete | | |
| Phase Owner | | Accept / Reject | | |
| Release Manager | | Frozen for audit / Returned | | |
