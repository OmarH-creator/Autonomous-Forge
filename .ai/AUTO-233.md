# AUTO-233 — Bind preservation-receipt publication to current completeness bytes

## Objective
Close a concrete preview-to-publication integrity gap in the confirmed preservation-receipt writer. A receipt already captured the authoritative preservation-completeness path, byte count, and SHA-256, but the writer did not prove that those source bytes still matched at the moment the immutable receipt was published.

## Repository inspection
Started from `main` at AUTO-232 head `c8981675b2263f2e69a556f852e4742728af1e8c`, whose Test workflow run `33289553743` was green. Inspected README/docs/examples, preservation/archive source and tests, `.forge` policy, CI, `.ai/AUTONOMOUS_PLAN.md`, `.ai/AUTONOMOUS_STATE.md`, `.ai/AUTONOMOUS_CHANGELOG.md`, `.ai/DECISIONS.md`, recent Actions, all eight visible branches, open issues, and PR history.

Seven non-`main` branches remain historical/diverged. Open issues #1, #6, and #9 are broad project requests rather than blockers for the current maintenance-workflow milestone. The inspected PRs are merged, closed, obsolete, superseded, or unrelated. No branch or PR work warranted integration, and the cycle remained main-only.

## Rationale
`write_maintenance_preservation_receipt(...)` built a hash-bound receipt and then persisted it with explicit confirmation and no-clobber hard-link publication. However, the completeness source could change after receipt construction and before or during publication. Later verification would detect the mismatch, but the write itself could still report success for evidence that was already stale by the time it was published.

## Work
- Added a fixed-bound source-binding recheck that reloads the authoritative completeness file through the existing 1 MiB ceiling and requires canonical path, exact byte count, and SHA-256 continuity.
- Recheck immediately before the destination hard link is created.
- Recheck again immediately after the hard link exists.
- If post-link drift is observed, remove the destination receipt, fsync the receipt directory, and fail closed.
- Preserve explicit write confirmation, repository containment, symlink refusal, immutable no-clobber publication, file/directory fsync, informational receipt semantics, and later read-only verification.
- Added deterministic tests covering same-size source drift before publication and during the hard-link publication step, including assertion that no stale receipt remains published.
- Added `docs/PRESERVATION_RECEIPT_PUBLICATION_BINDING.md`.

## Validation
The AUTO-232 starting head was green. AUTO-233 Actions runs are checked before the cycle is reported complete. The strongest repository validation remains the existing Python 3.10/3.11/3.12 workflow covering install, source compilation, installed CLI smoke tests, roadmap validation, and pytest.

## Safety and limitations
This is a local integrity-continuity improvement, not a provenance upgrade. It grants no product-side Git, network, workflow, overwrite, remote, force-push, or branch-protection authority. It does not rerun archive checks or validation and does not elevate informational workflow/external evidence.

The writer cannot lock the source against unrelated processes forever. A source may change after a successful write; durable receipt verification remains responsible for detecting later drift. AUTO-233 ensures the writer does not return success when source drift is observed immediately around its publication boundary.

## Visuals
None. The preservation workflow topology is unchanged; the change strengthens one existing write boundary rather than adding a new stage.

## Next action
If final-head CI is green, inspect remaining preservation writers for another concrete preview-to-publication continuity gap or cross-stage integrity defect. Any fresh CI failure takes priority.
