# Longitudinal Controlled Impact Study Protocol (LEV-WS10)

## 1. Study Overview
- **Primary Design**: Multi-site Cluster-Randomized Trial (Cluster-RCT).
- **Randomization Unit**: School cluster level (to prevent teacher/learner contamination within schools).
- **Target Population**: Grade 4-6 Mathematics learners across South African DBE Quintiles 1–5.
- **Primary Analysis**: Intent-to-Treat (ITT) baseline-covariate-adjusted ANCOVA / Linear Mixed Model accounting for Intra-Cluster Correlation (ICC).
- **Secondary / Fallback Analysis**: Propensity Score Matching (PSM) paired with Difference-in-Differences (DiD) estimation for observational and non-randomized scale-up cohorts.

## 2. Statistical Hypotheses
- **Null Hypothesis ($H_0$)**: $\beta_{\text{treatment}} = 0$ (Adjusted post-test mathematics score gain of EduBoost V2 learners is equal to business-as-usual controls).
- **Alternative Hypothesis ($H_1$)**: $\beta_{\text{treatment}} > 0$ with minimum detectable effect size (MDES) Hedges' $g \ge 0.20$.

## 3. Clustering & Power Sizing
- Expected ICC: $\rho = 0.08$.
- Cluster size: $m = 50$ learners per school.
- Variance Inflation Factor: $\text{VIF} = 1 + (m - 1)\rho = 1 + (49 \times 0.08) = 4.92$.
- Target Sample: 20 schools (10 treatment, 10 control), $N = 1,000$ learners.
- Target Statistical Power: $1 - \beta \ge 0.80$ at $\alpha = 0.05$ (two-tailed).

## 4. POPIA & Research Ethics Guardrails
- Written parental consent and child assent obtained prior to baseline assessment.
- Zero raw child PII committed to source control; data stored with SHA-256 pseudonyms.
- All evaluation runs recorded immutably in `lev_validation_runs`.
