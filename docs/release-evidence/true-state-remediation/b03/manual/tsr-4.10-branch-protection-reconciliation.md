# TSR-4.10 Branch Protection and Hosted Configuration Reconciled

## Policy Definition
1. **Target Branch**: `master`.
2. **Protected Settings**:
   - Direct push prohibited; all changes must arrive via pull request.
   - Required status checks bound exclusively to canonical jobs defined in `docs/ci/ci_authority_matrix.json`.
   - Linear history enforced (squash-and-merge or rebase).
   - Admin bypass prohibited for release gate compliance.
