# Phase 2R Gate 2R.1 Status Correction

**Status:** In Progress — closure not established

The earlier Gate 2R.1 closure claim is superseded. Its evidence was collected
from a dirty worktree and did not prove the source catalogue, per-use rights
model, frozen completeness register, or independent review decisions.

Gate 2R.1 has candidate evidence collected and committed. Gate 2R.1 is not
closed. Independent approvals and a separate Gate 2R.2 authorisation commit
remain required.

Current candidate evidence:

- source commit: `e6e43df45e4e990e9914a55134742b68c500ddd5`;
- evidence commit: `57f8a3c4ea51a19cd3601cdf5f3ae29753548644`;
- evidence pack: `docs/release-evidence/atlas/phase-02r/gate-2r1/`;
- raw checksum index: `docs/release-evidence/atlas/phase-02r/gate-2r1/raw/SHA256SUMS.txt`.

Closure remains blocked until:

- rights, curriculum, engineering, evidence, and release approvals are signed;
- a separate approval commit authorises Gate 2R.2.

As of 2026-06-21, implementation-level verification has exercised the authority
migration against disposable PostgreSQL, proved append-only update/delete
rejection, frozen the source-completeness register, and loaded the real
first-slice source authority/per-use rights records into the disposable
database. Candidate evidence has since been collected from a clean committed
source state, but it remains candidate evidence only because independent
approvals have not been signed and no separate Gate 2R.2 transition commit
exists.

The later-gate implementation bundle for Gates 2R.2-2R.8 has also been
applied, but it does not alter the Gate 2R.1 closure status or authorise Gate
2R.2.
