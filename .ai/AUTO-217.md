# AUTO-217 — Carry verified live-status provenance into preservation receipts

## Objective

Continue the end-to-end preservation provenance milestone by allowing immutable preservation receipts to expose the live workflow-status proof already retained by a complete preservation artifact, without creating another workflow-status contract or preservation gate.

## Repository inspection

Inspected README/docs/examples, preservation receipt/completeness source and tests, policy/config/CI, `.ai` state and roadmap direction, recent commits, open issues, all eight visible branches, and recent PR history. Seven non-main branches remain historical/diverged; recent PRs are merged, closed, obsolete, or unrelated. No branch or PR warranted integration.

## Work

- Added normalized `live_status_provenance` to receipt preview/write/verification data.
- Preserved exact requested commit, bounded workflow-run limit, collection-completeness proof, per-run commit binding, evidence SHA-256, and fixed informational semantics.
- Receipt verification rebuilds the live-status summary from the exact hash-bound completeness artifact and rejects field drift.
- Verified receipt discovery rows expose the retained summary so reviewers do not need to reopen the completeness JSON merely to inspect status provenance.
- Added deterministic regression coverage for propagation, verification, discovery visibility, and tamper refusal.
- Updated receipt documentation and autonomous status.

## Safety

Evidence propagation only. Receipt live status is forced to `review_effect=informational_only`, `preservation_gate_effect=none`, `affects_preservation_completeness=false`, and `affects_preservation_integrity=false`. Receipt presence remains optional and informational. No network access, validation execution, workflow rerun, push authority, force-push/tag-push behavior, remote mutation, branch-protection mutation, or additional persistence authority was added.

## Validation

AUTO-216 baseline head `c30f23bd25fca53aa5099c228be0f5f844104012` passed Actions run `33066076904` on Python 3.10, 3.11, and 3.12. AUTO-217 focused deterministic tests are committed; fresh Actions validation is required before the task is marked DONE because direct local checkout is unavailable in this execution environment.

## Visuals

None. The lifecycle topology is unchanged; this extends an existing evidence field through the existing immutable receipt boundary.

## Next action

Confirm the Python 3.10/3.11/3.12 matrix. Any failure takes priority. If green, continue only with another concrete end-to-end preservation/provenance integrity gap or meaningful evidence-handoff reduction.
