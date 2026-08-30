# AUTO-234 — Verify archive-manifest publication against current evidence

## Inspection

The cycle started from `main` at `89a90e28032e9619d29878ec9adf7b36b5053a89`, whose Test workflow was green. Inspection covered README/docs/examples, source/tests/config/CI, `.forge/policy.md`, `.ai/AUTONOMOUS_PLAN.md`, `.ai/AUTONOMOUS_STATE.md`, `.ai/AUTONOMOUS_CHANGELOG.md`, `.ai/DECISIONS.md`, recent commits and Actions, all eight visible branches, open issues, and PR history.

Seven non-main branches remain historical/diverged and inspected PRs are merged, closed, obsolete, superseded, or unrelated. Open issues #1, #6, and #9 are broader product requests rather than a concrete release blocker. No old branch/PR work warranted integration under the main-only workflow.

## Objective and rationale

AUTO-233 closed the equivalent publication race for immutable preservation receipts. Inspection found the next concrete write-path continuity gap in archive-manifest creation: the existing writer built a byte/SHA-bound snapshot and durably published it, but the installed CLI returned success without immediately re-verifying the just-published manifest against current evidence. A source report, selected maintenance bundle, or run-history link could change after snapshot construction and before publication completed; later verification would catch that drift, but the write itself could already have reported success.

## Implementation

Added `maintenance_archive_manifest_publication.py` and routed confirmed CLI archive-manifest writes through `write_verified_maintenance_archive_manifest(...)`.

The wrapper:

- delegates preview/build/no-clobber persistence to the existing writer and preserves its explicit `--confirm-write` gate;
- resolves the writer-reported manifest path inside the configured repository root;
- hashes the exact published manifest bytes incrementally in 64 KiB chunks;
- immediately runs the existing written-manifest verifier against current listed evidence;
- returns success only when that verification remains ready;
- rolls back a newly published stale manifest and fsyncs the parent directory when verification fails or raises;
- removes the output only when its current SHA-256 still equals the exact bytes this invocation observed after publication, refusing destructive rollback if another writer changed the output itself.

The core historical writer remains independently callable for compatibility; the installed CLI and the new reusable wrapper now provide the stronger publication-bound contract.

## Tests and documentation

Added deterministic coverage for successful immediate verification, rollback on detected evidence drift, and refusal to delete output bytes changed by another writer after publication. Added `docs/ARCHIVE_MANIFEST_PUBLICATION_BINDING.md` documenting behavior, safety, and the remaining post-return drift limitation. README Current Autonomous Status and autonomous state were updated during run finalization.

No visual change was needed because archive/preservation topology did not change.

## Validation

Local scratch `py_compile` succeeded for the new publication module, modified CLI, and focused regression test. Product/test head `5e0a0cacdc11f049936798fa0a19558e9392741b` passed GitHub Actions run `33308380858` across Python 3.10, 3.11, and 3.12, including installation, source compilation, installed CLI smoke tests, roadmap validation, and pytest. The final README/project-memory head is checked separately before the cycle is reported complete.

## Safety and diff review

All changed paths are permitted by `.forge/policy.md`: `src/**`, `tests/**`, `docs/**`, README, and `.ai/**`. No prohibited workflow, secret, token, key, environment, generated-noise, remote, branch-protection, or unrelated paths were changed. Work remained a fast-forward main-only sequence with no branch, PR, merge, or force-push.

## Limitations and next action

The stronger CLI contract closes the known build-to-return publication race but is not a permanent filesystem lock; evidence may still change after a successful command returns, and ordinary written-manifest verification remains the durable later check. The historical core Python writer is retained for compatibility and does not automatically opt direct callers into the new wrapper.

Next highest-value objective: move the same immediate publication-continuity guarantee into the core archive-manifest writer without breaking direct-call compatibility, or inspect the next confirmed preservation writer for an equivalent preview-to-publication integrity gap. Any fresh CI failure takes priority.