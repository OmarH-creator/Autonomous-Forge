# AUTO-244 — Push-evidence publication durability rollback

## Repository assessment
Inspected `main`, README/docs/examples, source/tests/config/CI, `.forge` policy, autonomous plan/state/changelog/decisions, recent commits and Actions, all eight visible branches, open issues, and PR history. The policy-aware `forge plan` milestone and the later guarded end-to-end maintenance workflow are already shipped. Seven non-main branches remain historical/diverged and no open PR requires integration; issues #1, #6, and #9 are broader product/discussion requests rather than blockers for this repair.

## Objective and rationale
Close a concrete write-integrity defect in the existing `forge verified-full-maintenance-run` path. Its immutable push-evidence writer could hard-link the final JSON successfully, then fail parent-directory `fsync` and return an error while leaving the destination published. That creates ambiguous durable evidence at the boundary immediately before maintenance-bundle construction.

## Change
`src/autonomous_forge/verified_full_maintenance_run.py` now SHA-256 binds the exact serialized push-evidence payload before publication. After hard-link publication, a directory-sync failure triggers ownership-checked rollback: Forge removes the destination only if its current digest still equals this invocation's payload, then syncs the parent directory again. If another process changed the destination, Forge preserves those bytes rather than deleting data it no longer owns.

Deterministic tests in `tests/test_auto244_push_evidence_durability.py` cover rollback of unchanged bytes and preservation of a destination mutated during the failure window. `docs/PUSH_EVIDENCE_DURABILITY_ROLLBACK.md` documents the contract and residual filesystem-concurrency limits.

## Safety and validation
No authority boundary was weakened. Explicit push-evidence write confirmation, repository confinement, `.json` enforcement, no-clobber hard-link publication, same-directory temporary-file `fsync`, downstream bundle verification, non-force push behavior, and independent later confirmations remain unchanged. No workflows, secrets, remotes, branch protections, or branch/PR state were modified.

Direct checkout execution is unavailable because outbound DNS to github.com is blocked in this runtime, so GitHub Actions on the final pushed head is the authoritative full validation. The final run report must not claim success unless the supported Python 3.10/3.11/3.12 workflow is green.

## Limitations and next action
Rollback cannot execute after `SIGKILL`, host/interpreter failure, or power loss. A second directory-sync failure leaves durability uncertain, and no shared filesystem lock closes the narrow race after the final ownership digest check. Next, harden the shared maintenance-evidence bundle/history-link no-clobber publication helper against the same post-link durability ambiguity unless a fresh CI failure takes priority.
