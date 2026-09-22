# Independent Review Dossier Specification (LEV-WS14)

## 1. Governance & Purpose
This evidence dossier structure facilitates independent panel review (psychometricians, subject matter specialists, and ethics boards) before any commercial or high-stakes use authorization is granted.

## 2. Dossier Component Index
1. **Construct Validity**: Mastery claims inventory and operational definitions (`docs/roadmap/production_readiness/lev/templates/MASTERY_INTERPRETATION_AND_USE_SPECIFICATION.md`).
2. **Curriculum Alignment**: CAPS concept and knowledge graph mapping rubrics (`docs/research/longitudinal_validation/caps_validation_blueprint.md`).
3. **Psychometrics & Calibration**: Item difficulty, discrimination, and Expected Calibration Error reports (`docs/roadmap/production_readiness/lev/templates/CALIBRATION_REPORT.md`).
4. **False-Mastery Risk**: Confusion matrices with Wilson score confidence intervals and error cost models (`docs/roadmap/production_readiness/lev/templates/CLASSIFICATION_RISK_REPORT.md`).
5. **Contextual Fairness**: Demographic parity bands across South African Quintiles 1-5 and official language groups (`docs/roadmap/production_readiness/lev/templates/FAIRNESS_AND_CONTEXT_VALIDITY_REPORT.md`).
6. **Controlled Impact**: Cluster-Randomized Trial (Cluster-RCT) report and Difference-in-Differences fallback analysis (`docs/research/longitudinal_validation/impact_study_protocol.md`).
7. **Adverse Consequence Mitigation**: Cognitive overload monitors and teacher escalation logs (`docs/research/longitudinal_validation/adverse_consequence_monitoring_plan.md`).

## 3. Reviewer Attestation Protocol
- Requires unanimous sign-off by:
  - Lead Psychometrician (external independent)
  - Mathematics Education Specialist (external independent)
  - Information Officer / POPIA Compliance Lead
- Attested signatures recorded in `LEVValidationRun` and cryptographically signed manifests.
