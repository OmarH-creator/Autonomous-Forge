# Autonomous Changelog

## 2026-08-15 — AUTO-144 verified guarded patch apply

- Task ID: AUTO-144 — Verify the actual tracked diff after guarded patch apply
- Summary: Extended the existing write-capable `forge patch-apply` path with optional `--verify-live-diff`. A confirmed replacement write can now be followed immediately by bounded target-scoped `git diff --no-ext-diff --no-textconv HEAD -- <target>` capture, policy review, exact one-file/one-target verification, and automatic rollback to the original target contents if live diff verification fails.
- Branch and PR assessment: Inspected README/docs/examples, source/tests/config/CI, `.forge/policy.md`, roadmap/state/changelog/decisions, recent commits, open issues, all visible branches, and PR history. Work stayed directly on `main`; historical branches remain stale or superseded and no PR required integration or replacement.
- Validation completed: GitHub Actions run `31891899123` on implementation/test head `5c726ae297ddd3f524eb547512f60cb4a8985153` completed successfully across Python 3.10, 3.11, and 3.12, including package installation, source compilation, installed CLI smoke, roadmap lint, and pytest. Regression coverage verifies successful target-scoped live review and rollback when the post-write tracked diff cannot be established.
- Product commits: `1c351e5c56e5e4b9e749e794f472b80a8ae51f10` (safe path-scoped live diff capture), `f2f5cf2fc097819069ea4a18b2130b441a01ab53` (verified apply + rollback), `b71c4e7d8243139c6b87218d6703486386381043` (CLI gate), `5c726ae297ddd3f524eb547512f60cb4a8985153` (regression coverage), plus docs/project-memory commits.
- Follow-up notes: Continue the same end-to-end maintenance milestone by carrying verified apply evidence directly into the existing validation execution/result handoff and then commit verification. Do not add another isolated read-only audit surface.

## 2026-08-15 — AUTO-143 live tracked diff inspection

- Task ID: AUTO-143 — Inspect the actual current tracked repository diff
- Summary: Extended the existing `forge git-diff-review` surface with `--current`, allowing policy-aware inspection of the repository's real tracked staged and unstaged changes relative to `HEAD` without first exporting a patch file. Current-mode capture runs exactly `git diff --no-ext-diff --no-textconv HEAD --` with `shell=False`, a 15-second timeout, and a 1 MB output bound, then reuses the existing diff parser and policy/path gates. Clean tracked state is clear but explicitly warns that untracked files are outside scope.
- Branch and PR assessment: Inspected README/docs/examples, source/tests/config/CI, policy, roadmap/state/changelog/decisions, recent commits, open issues, all visible branches, and PR history. Work stayed directly on `main`; historical branches remain stale or superseded and no PR required integration or replacement.
- Validation completed: GitHub Actions run `31881238816` on regression-test head `b23ff40455104322dc078f649b92f748c6e987ef` completed successfully across Python 3.10, 3.11, and 3.12, including package installation, source compilation, installed CLI smoke, roadmap lint, and pytest. Deterministic tests assert the exact git argv, configured working directory, `shell=False`, timeout, clean-state handling, and primary CLI `--current` routing.
- Commits: `41ce7536e57ccea7196ca82e154885b5cea809c8` (bounded live-diff capture), `52e0e8c5c573cfd83933d578588fe494b973fc52` (existing CLI integration), `b23ff40455104322dc078f649b92f748c6e987ef` (regression coverage), `25928c61642de5a10043f764076459a481cf6b57` (CLI documentation), plus roadmap/state/decision bookkeeping.
- Follow-up notes: Continue the same end-to-end maintenance milestone by carrying live reviewed diff evidence into guarded patch-generation/application and validation handoffs. Do not create another isolated review/audit surface unless it resolves a concrete blocker.

## 2026-08-15 — AUTO-142 green-baseline completion

- Task ID: AUTO-142 — Restore green main baseline, phase 2: replay/context, comparison, and enriched-contract recovery
- Summary: Completed issue #13. Fixed the primary replay-policy help identity; made multi-bundle maintenance-review comparison fixtures deterministic and replay-policy-valid; fixed a real preservation-ranking defect by exposing the already validated raw retained history-link context through maintenance review handoff instead of ranking the lossy count summary; and updated stale planning/validation/executor assertions to the current enriched safety contract rather than weakening runtime safeguards.
- Branch and PR assessment: Inspected README/docs/examples, source/tests/config/CI, policy, roadmap/state/changelog/decisions, issue #13, recent commits, all visible branches, and PR history. Work stayed directly on `main`; historical branches remain stale or superseded and no PR required integration.
- Validation completed: The run started from 633 passed / 22 failed on the inspected Python 3.11 suite. Intermediate CI reduced that to 637/18 and then 647/8. Run `31871534812` reached 654 passed / 1 failed, isolating the final normalized validation-expectation assertion. After commit `f3864ca164728ed6b5bdf760504385b345c29b9d`, GitHub Actions run `31871553378` passed package installation, source compilation, installed CLI smoke, roadmap lint, and all 655 pytest tests on Python 3.10, 3.11, and 3.12.
- Product commits: replay-policy help identity; `fd20a5c86422ba288d9db0bce65b35551f879b84` (raw retained review context for preservation ranking); `703d677de0f05054e02e092306b9bac6615455c1` (replay-policy-valid comparison ranking fixture); `f3864ca164728ed6b5bdf760504385b345c29b9d` (last stale normalized validation expectation), plus focused contract-test alignment commits.
- Follow-up notes: Issue #13 exit criteria are satisfied. Resume feature delivery only while the full Python 3.10/3.11/3.12 matrix remains green; prefer integration of the existing guarded planning→diff→patch→validation→commit/push→evidence capabilities over another standalone read-only review command.

## 2026-08-15 — AUTO-142 validation-step normalization

- Task ID: AUTO-142 — Restore green main baseline, phase 2: semantic validation-step deduplication
- Summary: Fixed a shared validation-plan defect where semantically identical validation steps differing only by whitespace or a trailing period survived as separate entries. The validation-plan boundary now deduplicates those cosmetic variants while preserving the first documented spelling and order, preventing duplicate downstream command candidates without weakening execution or evidence safeguards.
- Branch and PR assessment: Inspected README/docs/source/tests/config/CI, roadmap/state/changelog/decisions, issue #13, recent commits, all visible branches, and PR history. Work stayed directly on `main`; historical branches remain stale or superseded and no PR required integration.
- Validation completed: Added deterministic regression coverage in `tests/test_validation_step_dedup.py`. GitHub Actions run `31861022809` passed install, compile, installed CLI smoke, and roadmap lint on Python 3.10, 3.11, and 3.12. Python 3.11 pytest improved from 631 passed / 23 failed to 633 passed / 22 failed. The remaining failures are separate stale enriched-contract assertions, one replay-policy help assertion, and four maintenance-review-compare fixture/output failures.
- Commits: `d9a51b68089eec7926ce6d5310e232b61f6c54cb` (normalization), `43a74adf533239a1c52b5509bd10e25f97be8865` (regression coverage), plus project-memory follow-up commits.
- Follow-up notes: Continue issue #13 with the stale enriched planning/validation/executor assertions, then the replay-policy help assertion and maintenance-review-compare failures. Do not resume feature work until all matrix jobs are green.

## 2026-08-15 — AUTO-142 archive-path recovery

- Task ID: AUTO-142 — Restore green main baseline, phase 2: canonical archive destination mapping
- Summary: Fixed the shared archive-copy path defect exposed after handoff-context recovery. Valid manifest entries can retain absolute paths that are still valid because they resolve inside the repository. Both copy preview and copied-root verification previously joined those absolute paths directly to the requested archive root; `pathlib` then discarded the archive-root prefix. The fix verifies repository containment first, canonicalizes each source to a repository-relative path, and only then joins it beneath the archive root. Existing containment, collision, overwrite, byte-count, and SHA-256 safeguards remain intact.
- Branch and PR assessment: Inspected README/docs/source/tests/config/CI, roadmap/state/changelog/decisions, issue #13, recent commits, all visible branches, and PR history. Work stayed directly on `main`; historical branches remain stale or superseded and no PR required integration.
- Validation completed: At cycle start the annotated matrix reported 57 failed / 597 passed. Commit `bedb09e77ab672e8716ab1fc3910a06549afd478` fixed copy-preview mapping and the inspected Python 3.11 job improved to 51 failed / 603 passed. Commit `8160132ad188033d66a6290c180bbd718fe42952` fixed copied-root verification using the same canonical path invariant; Python 3.11 then reached 23 failed / 631 passed. No archive-copy, archive-copy-verify, archive-package, or preservation-completeness tests remain in the failure summary. Python 3.10, 3.11, and 3.12 all pass install, compile, installed CLI smoke, and roadmap lint before pytest; pytest remains red, so feature delivery stays paused.
- Commits: `bedb09e77ab672e8716ab1fc3910a06549afd478` (copy-preview canonicalization), `8160132ad188033d66a6290c180bbd718fe42952` (copy-verifier canonicalization), plus project-memory follow-up commits.
- Follow-up notes: Continue issue #13 with the remaining 23 failures, prioritizing stale enriched planning/validation/executor output-contract assertions, then the replay-policy help assertion and maintenance-review-compare fixture/output failures. Do not resume feature work until all matrix jobs are green.

## 2026-08-15 — AUTO-142 handoff-context recovery

- Task ID: AUTO-142 — Restore green main baseline, phase 2: handoff context consistency and archive recovery
- Summary: Used the new actionable pytest annotation to trace a large archive-manifest and archive-copy failure cluster through maintenance review handoff. Found a real internal contract defect: history-link review intentionally returns validation-context summary counts, while handoff consistency treated that summary as the original retained context lists. Handoff now rereads the already safety-validated repository-local history link and compares its raw retained context against replayed bundle context. Public history-review output remains unchanged. Shared archive fixtures were also aligned with generated source-report metadata and reviewed-path-derived expected-change context rather than fabricated evidence.
- Branch and PR assessment: Inspected README/docs/source/tests/config/CI, roadmap/state/changelog/decisions, issue #13, all visible branches, recent commits, and PR history. Work stayed directly on `main`; historical branches remain stale or superseded and no PR required integration.
- Validation completed: Python 3.10/3.11/3.12 runs continued to pass install, compile, installed CLI smoke, and roadmap lint. Before the handoff fix, the annotation showed archive-manifest preview/source-report verification failures and many downstream archive-copy failures. After `f03aed1c34285c041f02afa236898090ad8d9022`, the archive-manifest failures disappeared and several archive-copy guard failures disappeared; remaining archive failures advanced to the later archive-copy destination-mapping guard. Pytest remains red, so baseline recovery continues and feature delivery remains paused.
- Commits: `80efd9c4423cc7208891533a0c55ddc4ec0fb657` (actionable pytest diagnostics), `f01a9c7f2d83f7d6c6a5673cfdaac926d0842713` and `9f30db304460e6f2f1466ad8efbdec8659e07eba` (fixture alignment), `f03aed1c34285c041f02afa236898090ad8d9022` (raw history-context handoff comparison), plus project-memory follow-up commits.
- Follow-up notes: Repair the archive-copy destination mapping cluster next, then stale command/executor output expectations and the replay-policy primary-router help assertion. Do not resume feature work until all matrix jobs are green.

## 2026-08-15 — AUTO-142 diagnostic slice

- Task ID: AUTO-142 — Restore green main baseline, phase 2: actionable pytest failure diagnostics
- Summary: Resolved a concrete baseline-recovery blocker in CI. The test workflow now captures pytest output, preserves pytest's original exit status, and emits up to 80 standard `FAILED ...` summary lines as a GitHub Actions error annotation when the suite fails. This makes exact failing node IDs visible through the connected checks API instead of exposing only a generic exit-code annotation.
- Branch and PR assessment: Inspected README/docs/source/tests/config/CI, roadmap/state/changelog/decisions, issue #13, all visible branches, recent commits, and PR history. Work stayed directly on `main`; historical branches remain stale or superseded and no PR required integration.
- Validation completed: The preceding Python 3.10/3.11/3.12 matrix passed install, compile, CLI smoke, and roadmap lint and failed only at pytest. Static review of commit `80efd9c4423cc7208891533a0c55ddc4ec0fb657` confirms the wrapper retains `${PIPESTATUS[0]}`, reports failures, removes its temporary log, and exits with the original pytest status. Direct checkout execution was blocked by outbound DNS in this runtime.
- Commits: `80efd9c4423cc7208891533a0c55ddc4ec0fb657` plus project-memory follow-up commits.
- Follow-up notes: Consume the next workflow annotation and repair the highest-volume deterministic failure cluster under issue #13. Do not resume feature work until all matrix jobs are green.

## 2026-08-15 — AUTO-142

- Task ID: AUTO-142 — Restore green main baseline, phase 2: partial replay-context compatibility
- Summary: Fixed a concrete replay consistency defect so retained validation context that omits optional `expected_file_changes` is not treated as contradictory path evidence. Explicit expected-change mismatches and retained validation-step mismatches still fail closed. Added deterministic regression coverage for the compatible partial-context case.
- Branch and PR assessment: Inspected README, roadmap/state/changelog/decisions, current source/tests, GitHub Actions, issue #13, all visible branches, and PR history. Work stayed directly on `main`; historical branches are stale or superseded and no PR required integration.
- Validation completed: Local three-case logic probe passed for partial compatible context, explicit reviewed-path mismatch, and validation-step mismatch. GitHub Actions for commit `9fd663f71ea3058654dc476141980b66ae82a063` completed with the repository-wide pytest step still failing across the matrix, so the baseline is not claimed green. Full diff review from pre-run head showed only the replay-summary logic, focused regression test, and run-state changes before README/changelog bookkeeping.
- Commits: `0f9af30bfa58d8967c5bf9de24a2cfd57da052a4`, `9fd663f71ea3058654dc476141980b66ae82a063`, `6f2e4ce0c41cbf52b7a13b65570460e9e29ce48f`, `6359e1a8086145bfe6ba1a7ae481f23608bc426b`.
- Follow-up notes: Continue issue #13 against the next observed deterministic compatibility/fixture cluster. Do not resume feature work until Python 3.10, 3.11, and 3.12 are green.

## 2026-08-15 — AUTO-141

- Task ID: AUTO-141 — Restore router help contract on red main
- Summary: Fixed the importable primary `forge` router so successful argparse help exits from extension commands normalize to return code `0`, while non-zero parser exits still propagate. Added regression coverage for the non-zero case.
- Branch and PR assessment: Inspected README, roadmap/state/changelog/decisions, recent commits, open issues, all visible branches, PR history, router source, focused tests, and current commit status. Stayed directly on `main`; no stale branch or PR contained work that should be merged for this defect.
- Validation completed: Reviewed the complete committed diff from pre-run main; only `src/autonomous_forge/cli_entry_patch.py` and `tests/test_cli_entry_patch.py` changed in the product slice. The router change is limited to extension dispatch semantics. Fresh GitHub status checks were not yet visible at inspection time.
- Commits: `e2184b2b87592fbc98a85712e42e3865d49944a8`, `2bbe729b21f3d6555f43d50adcc0b46ad4ab4e68`.
- Follow-up notes: Continue issue #13 and repair the remaining red-baseline clusters before any new feature work.

## 2026-07-10 — AUTO-140

- Task ID: AUTO-140 — Primary replay-policy route and smoke coverage
- Summary: Fixed a release-surface blocker by routing `forge maintenance-replay-policy-summary` through the installed primary `forge` entry point while preserving the existing `forge-maintenance-replay-policy-summary` compatibility script.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent commits, recent PRs, open issues, router implementation, replay-policy CLI, focused tests, docs, and workflow smoke coverage. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; no open PR or branch required integration.
- Validation completed: Static source/test/docs/workflow review completed through the GitHub repository API. Added focused router help coverage and CI smoke coverage for both primary and compatibility replay-policy summary routes. Local scratch syntax compilation passed for the changed router and focused router test file. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a reviewer checklist or provenance/signature review for storing or transferring verified preservation packages.

## 2026-07-10 — AUTO-139

- Task ID: AUTO-139 — Preservation workflow-status freshness gate
- Summary: Extended `forge maintenance-preservation-completeness` and `forge-maintenance-preservation-completeness` with optional `--status-evidence` and `--require-workflow-fresh` support. The final preservation gate can now require successful supplied workflow/status JSON whose commit SHA matches the archive manifest commit.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent commits, recent PRs, open issues, branch search, preservation-completeness implementation, focused tests, docs, and workflow smoke coverage. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; branch search returned no open branch work requiring integration.
- Validation completed: Static source/test/docs/workflow review completed through the GitHub repository API. Local scratch syntax compilation passed for the changed preservation-completeness core, CLI module, and focused test file. Added deterministic coverage for matching workflow status, stale workflow status, required-missing workflow evidence, and CLI strict workflow freshness. Direct full checkout/full pytest execution remained unavailable from this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a reviewer checklist or provenance/signature review for storing or transferring verified preservation packages.

## 2026-07-10 — AUTO-138

- Task ID: AUTO-138 — Maintenance preservation completeness summary
- Summary: Added `forge maintenance-preservation-completeness` and `forge-maintenance-preservation-completeness`, a read-only final review command that combines written archive-manifest verification, copied archive-root verification, and archive-package verification into one `complete` or `blocked` preservation status.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent commits, recent PRs, branch search, archive manifest/copy/package verification implementation, focused tests, docs, and workflow smoke coverage. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; branch search returned no open branch work requiring integration.
- Validation completed: Static source/test/docs/workflow review completed through the GitHub repository API. Local scratch syntax compilation passed for the changed preservation-completeness core, CLI module, and focused test file. Added deterministic coverage for clean completeness, missing package blocking, JSON CLI success, and fail-closed `--require-complete` behavior on package drift. Static review also corrected the package verifier's expected-existing-package blocker so a written package can be verified after package creation. Direct full checkout/full pytest execution remained unavailable from this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a read-only evidence provenance/signature review or workflow-freshness gate if a concrete safe local contract is identified.

## 2026-07-10 — AUTO-137

- Task ID: AUTO-137 — Archive-package verification
- Summary: Added `forge maintenance-archive-package-verify` and `forge-maintenance-archive-package-verify`, a read-only verifier that reopens a written repository-local `.tar.gz`, `.tgz`, `.tar`, or `.zip` archive package and compares entry paths, byte counts, and SHA-256 values against the manifest-backed copied archive root.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent PRs, archive package writer/preview implementation, archive copy verification helper tests, package scripts, docs, and workflow smoke coverage. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; no open PR or branch required integration.
- Validation completed: Static source/test/docs/workflow review completed through the GitHub repository API. Local scratch syntax compilation passed for the new verifier module, CLI module, and focused test file. Added deterministic coverage for verified `.tar.gz`, verified `.zip`, missing package blocking, drifted package-entry blocking, JSON CLI success, and fail-closed `--require-verified` behavior. Direct full checkout/full pytest execution remained unavailable from this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a preservation-completeness summary that combines manifest verification, copied archive-root verification, and archive-package verification into one final review artifact.

## Historical note

Older autonomous run entries remain available in repository history.