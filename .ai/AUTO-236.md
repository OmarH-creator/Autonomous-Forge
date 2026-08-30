# AUTO-236 — Core archive-manifest publication binding

Date: 2026-08-30
Status: DONE
Branch: `main`

## Objective

Move the already-shipped archive-manifest post-publication continuity guarantee into the core `write_maintenance_archive_manifest(...)` API so direct Python callers cannot bypass immediate evidence verification and ownership-checked rollback.

## Repository inspection

The cycle started from AUTO-235 head `fd582df1b85588b0857bc3aec8e071d4a02becf4`, whose GitHub Actions run `33318984421` was green. Inspection covered README/docs, source/tests/config/CI, `.forge/policy.md`, `.ai/AUTONOMOUS_PLAN.md`, `.ai/AUTONOMOUS_STATE.md`, `.ai/AUTONOMOUS_CHANGELOG.md`, `.ai/DECISIONS.md`, recent commits and Actions, open issues, all eight visible branches, and PR history.

The roadmap confirms the requested policy-aware `forge plan` milestone and later guarded maintenance workflow are already shipped. AUTO-235 explicitly identified the remaining archive-manifest gap: the installed command used a verified wrapper, while the historical core writer could still return immediately after publication.

Open issues #1, #6, and #9 are broader project requests rather than release blockers. The seven non-`main` branches are historical/diverged: `auto/auto-015-json-run-summary`, `auto/auto-017-json-run-summary-rebase`, `auto/auto-018-policy-aware-plan`, `auto/ci-package-smoke`, `codex/replace-readme-report`, `maintenance/ci-concurrency-guard`, and `maintenance/fix-plan-priority-lint`. Inspected PRs are merged, closed, obsolete, superseded, or unrelated; none warranted integration.

## Rationale

AUTO-234 and AUTO-235 protected installed confirmed archive-manifest writes by placing immediate verification and interruption-safe rollback in `write_verified_maintenance_archive_manifest(...)`. That left a concrete API-level integrity discrepancy: callers importing `write_maintenance_archive_manifest(...)` directly could publish a manifest and receive success without current evidence being reverified.

The highest-value safe continuation was to establish the same invariant at the core write boundary rather than add another read-only command or documentation-only task.

## Work completed

- `src/autonomous_forge/maintenance_archive_manifest.py`
  - moved post-publication verification and rollback into `write_maintenance_archive_manifest(...)`;
  - computes the intended serialized manifest SHA-256 before publication;
  - preserves the existing no-clobber temporary-file/hard-link publication and fsync behavior;
  - immediately verifies the written manifest against current listed evidence;
  - re-hashes the final manifest after verification and requires it to match the exact intended output SHA-256;
  - on ordinary failures or Python-level interruptions, removes only the exact output bytes owned by this invocation and fsyncs the directory;
  - refuses rollback if the published path is no longer a regular file or its bytes changed;
  - successful direct calls report `publication_verified=true` and `publication_verification_status=ready`.
- `src/autonomous_forge/maintenance_archive_manifest_publication.py`
  - retained the historical verified wrapper for compatibility;
  - returns immediately when the core writer already reports successful publication verification, avoiding duplicate full evidence verification;
  - preserves the previous wrapper-level verification/rollback fallback for legacy or monkeypatched core writers.
- `tests/test_auto236_archive_manifest_core_publication.py`
  - deterministic direct-core tests cover successful immediate verification, blocked verification rollback, `KeyboardInterrupt`/`SystemExit` rollback and re-raise, and refusal to delete output changed during verification.
- `docs/ARCHIVE_MANIFEST_CORE_PUBLICATION.md`
  - documents the core publication contract, compatibility behavior, safety boundary, and limitations.
- `README.md`
  - updated evidence/preservation behavior, safety boundary, limitations, and replaced `## Current Autonomous Status` with AUTO-236.

No new visual was needed because the maintenance/preservation workflow topology did not change; only ownership of an existing integrity invariant moved from a wrapper into the core writer.

## Validation

The implementation commit `9d7887fafba5d20dbf859f8050843f37bd72edf3` passed GitHub Actions run `33330003958`. The product/test integration head `ae3e5b4562d6559750c69fd0e856224f8f231c5d` passed GitHub Actions run `33330033154`; Python 3.10, 3.11, and 3.12 all passed package installation, source compilation, installed CLI smoke tests, roadmap validation, and pytest.

The final documentation/project-memory head is checked again before the cycle is reported complete.

## Safety and policy

All changed paths are permitted by `.forge/policy.md`: `src/**`, `tests/**`, `docs/**`, `README.md`, and `.ai/**`. No `.github/workflows/**`, secret/token/key material, network access, external service call, new Git authority, force-push behavior, remote mutation, branch-protection mutation, overwrite authority, or workflow control was added.

Existing explicit confirmation, repository containment, no-clobber publication, incremental SHA-256 hashing, file/directory fsync, and fail-closed output-ownership checks remain intact.

## Project-memory disposition

`AUTONOMOUS_PLAN.md`, `AUTONOMOUS_CHANGELOG.md`, and `DECISIONS.md` were inspected. The roadmap direction and architectural safety decision did not change: AUTO-236 completes the already-recorded continuation from AUTO-235 by moving the same verified-publication invariant to the core boundary. No semantic roadmap or architecture rewrite was warranted merely to create status churn.

## Limitations

Immediate verification is not a permanent filesystem lock. Evidence changed after a successful return is detected by ordinary written-manifest verification. Cleanup also cannot run after abrupt termination that prevents Python execution entirely, including `SIGKILL`, host failure, interpreter crash, or power loss.

The compatibility wrapper remains because existing external callers may import it; normal core-verified writes no longer repeat the verification there.

## Next highest-value opportunity

Inspect the remaining preservation writers for a direct Python API whose guarantees are weaker than its installed/verified publication path, prioritizing a concrete post-publication continuity or cross-stage integrity gap. Any fresh CI failure takes priority.
