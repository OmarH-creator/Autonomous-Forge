# Autonomous Decisions

## DEC-147 — 2026-08-15 — Preservation ranking must use retained review values, not a lossy summary

Context: After deterministic fixture collisions and replay-policy inconsistencies were repaired, the maintenance-review comparison ranking test exposed a product defect rather than a stale assertion. `maintenance_history_link_review` intentionally summarizes retained validation context into presence/count metadata. `maintenance_review_compare` ranks preservation candidates partly by the richness of retained validation context, but `maintenance_review_handoff` was forwarding the summary object. Every candidate therefore appeared to contain zero retained context items even when one had materially richer review evidence.

Decision: Keep the public history-link quality summary unchanged, but have maintenance-review handoff expose the already safety-validated raw retained validation-context lists for downstream comparison/ranking. Continue using the existing raw-value comparison against replayed bundle context, and keep replay-policy, bundle-hash, reviewed-path, validation-step, malformed-evidence, and handoff gates fail-closed. Update stale tests to assert the current enriched structured contracts and normalized validation steps rather than reverting product output to older weaker shapes.

Alternatives considered: Rank the history-review count summary directly, remove retained-context richness from ranking, expand the public history-review summary into raw values, or change the ranking expectation to accept a weaker candidate. Ranking counts from the lossy shape cannot distinguish richer evidence; removing the signal would make candidate selection less useful; changing the public review contract creates unnecessary surface churn; and weakening the test would preserve a real selection defect.

Consequences: Ready preservation candidates are now ranked using actual retained review context while blocked handoffs remain excluded. The baseline-recovery run also corrected the primary replay-policy help identity, repaired replay-policy-valid comparison fixtures, and aligned stale planning/validation/executor tests to the stronger enriched context contract. GitHub Actions run `31871553378` passed installation, compilation, installed CLI smoke, roadmap lint, and all 655 tests on Python 3.10, 3.11, and 3.12. No write, remote, force-push, branch-protection, uncontrolled execution, workflow-rerun, or evidence-integrity safeguard was weakened.

Human decision still required: No.

## DEC-146 — 2026-08-15 — Equivalent validation steps should collapse at the shared planning boundary

Context: The remaining baseline failures showed that a roadmap validation step such as `Run python -m pytest` and a policy/task form such as `Run python -m pytest.` could survive as distinct validation steps. Downstream validation previews then emitted duplicate command candidates for the same executable command, creating redundant review evidence and stale executor expectations.

Decision: Normalize validation steps only for duplicate comparison by collapsing whitespace and ignoring terminal periods. Preserve the first documented spelling and original order in output. Apply the rule once in the shared validation-plan builder so downstream review, orchestration, and executor surfaces inherit the same deterministic set.

Alternatives considered: Deduplicate only command candidates, strip punctuation from all emitted steps, or update tests to accept duplicates. Command-only deduplication would leave contradictory validation-plan evidence; rewriting emitted text would create unnecessary contract churn; and accepting duplicates would preserve a real product defect.

Consequences: Semantically duplicate validation steps no longer create duplicate downstream command candidates. Distinct steps remain distinct, first-source wording is retained, and no execution, policy, parser, integrity, write, commit, push, or remote safety boundary is weakened. GitHub Actions run `31861022809` improved the inspected Python 3.11 suite from 631 passed / 23 failed to 633 passed / 22 failed.

Human decision still required: No.

## DEC-145 — 2026-08-15 — Archive destinations must derive from canonical repository-relative source paths

Context: After handoff-context recovery, the remaining archive pipeline reached destination mapping and failed broadly. Written manifests can contain absolute paths that are still valid because they resolve inside the configured repository root. `pathlib` discards a left-hand prefix when the right-hand operand is absolute, so both archive-copy preview and copied-root verification could unintentionally map a valid absolute source back to its live repository location instead of beneath the requested archive root. Existing collision and archive-root containment guards correctly blocked the result, causing the downstream package and preservation chain to fail.

Decision: After verifying that every archive entry source resolves inside the configured repository root, canonicalize it to a repository-relative path before joining it beneath the selected archive root. Apply the same canonicalization rule in both copy-preview destination planning and copied-root verification. Keep all existing repository-root containment, archive-root containment, duplicate-destination, source-equals-destination, existing-destination, byte-count, and SHA-256 checks fail-closed.

Alternatives considered: Allow absolute manifest paths to pass through unchanged, weaken destination-collision checks, change every manifest producer to emit only relative paths, or special-case `.ai/run-history`. Passing absolute paths through preserves the pathlib prefix-discard bug; weakening collision checks risks copying over live evidence; changing only producers leaves existing valid written manifests incompatible; and special-casing one directory would not establish a general path invariant.

Consequences: Valid repository-contained evidence now maps deterministically beneath the requested archive root regardless of whether the written manifest retained an absolute or relative source path. The inspected Python 3.11 matrix improved from 57 failed / 597 passed at cycle start to 23 failed / 631 passed after the preview and verifier fixes, with the archive-copy/verify/package/preservation cluster absent. No overwrite, path escape, remote, workflow-rerun, commit, push, or branch-protection authority was added.

Human decision still required: No.

## DEC-144 — 2026-08-15 — Handoff context consistency must compare retained values, not summary counts

Context: Actionable pytest annotations exposed a large archive-manifest and archive-copy failure cluster. Tracing the shared path showed that `maintenance_history_link_review` intentionally summarizes retained validation context into presence/count metadata, while `maintenance_review_handoff` later treated that summary object as though it still contained the original `expected_file_changes`, `implementation_steps`, `validation_steps`, and `risk_register` lists. Consequently, valid history links with retained context were classified as mismatched before archive construction.

Decision: Keep the public history-link review summary contract unchanged, but have maintenance-review handoff reread the same repository-local history link through the existing safety-validated `_read_history_link` helper and compare its raw retained validation-context lists against replayed bundle context. Preserve exact mismatch blocking, reviewed-path checks, validation-step checks, bundle hash verification, and replay-policy gates. Align archive test fixtures with generated source-report evidence and reviewed-path-derived expected-change text rather than fabricated metadata.

Alternatives considered: Remove the handoff context gate, teach the summary object to masquerade as raw context, expand the public history-review output with retained values, or update only downstream archive assertions. Removing the gate would weaken evidence integrity; treating counts as values is semantically incorrect; expanding public output would create avoidable contract churn; and assertion-only changes would hide a real product defect.

Consequences: Valid retained context can now pass handoff consistency while explicit context drift still blocks. The fix adds no new write, execution, commit, push, remote, workflow-rerun, or branch-protection authority. The post-fix matrix no longer reports the earlier archive-manifest preview/source-report verification failures; remaining archive failures have advanced to the later archive-copy destination-mapping guard.

Human decision still required: No.

## DEC-143 — 2026-08-15 — CI must expose exact pytest failure identities while preserving failure semantics

Context: Issue #13 requires repairing the remaining red-baseline test clusters without weakening safety contracts. The connected GitHub checks surface exposed only a generic `Process completed with exit code 1` annotation for the pytest step, and direct repository cloning is unavailable in this automation runtime because outbound DNS to github.com is blocked. Continuing from aggregate historical counts would force subsequent cycles to guess which tests still fail.

Decision: Wrap the existing pytest invocation in bash, capture output with `tee`, retain pytest's original status from `PIPESTATUS[0]`, emit up to 80 standard `FAILED ...` summary lines as a GitHub Actions error annotation when pytest fails, delete the temporary output file, and exit with the original pytest status. Do not add a new dependency, artifact upload, retry, test filter, or failure suppression.

Alternatives considered: Guess from historical failure counts, add an artifact-upload action, weaken or skip failing tests, or create another diagnostic command. Guessing risks incorrect changes; an upload action adds an external workflow dependency when annotations are sufficient; weakening/skipping tests violates baseline-recovery safety; and another product command would be unrelated surface area.

Consequences: Subsequent autonomous runs can retrieve exact failing test node IDs through check annotations and target the largest deterministic failure cluster. CI semantics remain unchanged: any pytest failure still fails the job with pytest's own non-zero status. No product runtime, repository policy, write capability, test selection, or side-effect boundary changes.

Human decision still required: No.

## DEC-142 — 2026-08-15 — Omitted optional expected-change context is absence, not contradiction

Context: Replay consistency compared every reviewed path against retained `expected_file_changes`. Older but otherwise valid evidence can retain only a subset of supported validation context, such as `validation_steps`. When `expected_file_changes` was omitted, the replay summary still populated every reviewed path as lacking expected-change context and classified the supplied context as inconsistent, despite having no contradictory expected-change evidence.

Decision: Enforce reviewed-path coverage only when `expected_file_changes` is actually supplied. If that optional context field is absent, do not synthesize path mismatches from its absence. Continue to fail closed when a supplied expected-change list omits reviewed paths, when retained validation steps do not match bundle validation steps, or when context is malformed.

Alternatives considered: Make `expected_file_changes` mandatory retroactively, remove context consistency checks, or update only old fixtures. Making the field mandatory would invalidate historical partial context that the bundle schema currently permits; removing consistency checks would weaken safety; fixture-only changes would hide a real semantic contradiction between optional-field handling and replay policy.

Consequences: Partial retained context remains replay-compatible without fabricating evidence, while explicit contradictory context still blocks. This is a compatibility correction inside the existing read-only replay contract; it adds no write, execution, commit, push, remote, workflow-rerun, or branch-protection authority.

Human decision still required: No.

## DEC-141 — 2026-08-15 — Normalize only successful argparse exits at the primary extension router

Context: The repository's red baseline includes two router-help failures because extension CLIs use argparse, whose successful `--help` path raises `SystemExit(0)`, while the importable `forge` router contract expects an integer return code.

Decision: Add a narrow extension-dispatch helper that converts only `SystemExit(0)` and `SystemExit(None)` into return code `0`, normalizes a `None` extension return to `0`, and re-raises every non-zero `SystemExit` so parser errors remain failures. Add regression coverage proving non-zero parser exits are not swallowed.

Alternatives considered: Change every extension CLI, change the tests to expect `SystemExit`, or catch all `SystemExit` values. Updating every CLI would duplicate compatibility glue, changing tests would preserve an inconsistent importable router contract, and swallowing all exits would hide invalid CLI usage.

Consequences: Process-level help behavior remains successful, direct callers of `main([...])` receive the documented numeric success code for extension help, and invalid arguments continue to fail. No side-effect capability or safety gate changes.

Human decision still required: No.

## DEC-140 — 2026-07-10 — Compatibility commands must also be reachable through primary `forge`

Context: `forge-maintenance-replay-policy-summary` was exposed through `pyproject.toml`, but `cli_entry_patch.py` did not route `forge maintenance-replay-policy-summary`, and CI smoke coverage did not check either replay-policy route.

Decision: Add the missing `maintenance-replay-policy-summary` primary route to the installed `forge` router, preserve the existing compatibility script, and smoke-test both routes in CI.

Alternatives considered: Leave the compatibility script as the only entry point, document only the compatibility script, or add another standalone command. Compatibility-only behavior creates an inconsistent user-facing release surface, documentation-only mitigation would not prevent regressions, and another command would duplicate the existing replay-policy capability.

Consequences: Users can reach the replay-policy summary from the primary `forge <command>` surface and release smoke checks now guard both route forms. The change adds no write behavior and does not run validation commands, stage files, create commits, push, rerun workflows, poll remote status, change remotes, or alter branch protections.

Human decision still required: No.

## DEC-139 — 2026-07-10 — Final preservation review needs optional workflow freshness

Context: AUTO-138 could prove manifest, copied-root, and archive-package completeness, but a preserved package could still be considered complete without checking whether supplied workflow/status evidence was successful for the same commit.

Decision: Extend `forge maintenance-preservation-completeness` and `forge-maintenance-preservation-completeness` with `--status-evidence` and `--require-workflow-fresh`. The command reuses the existing commit-status review contract, requires the supplied evidence to be successful, compares its commit SHA with the written manifest commit SHA, and reports a `workflow_status` stage gate.

Alternatives considered: Create another standalone freshness command, always require status evidence, or poll GitHub workflows directly. A standalone command would fragment the final preservation decision, always requiring status evidence would break older local-only evidence sets, and polling workflows would expand the command beyond repository-local deterministic evidence review.

Consequences: Maintainers can make preservation completeness stricter when workflow evidence exists, while the default local-only preservation check remains backward compatible. The gate trusts supplied JSON and does not write files, poll GitHub, rerun workflows, prove signer identity, prove package provenance, or prove validation coverage.

Human decision still required: No.

## DEC-138 — 2026-07-10 — Preservation needs one final completeness gate

Context: AUTO-137 could verify a written archive package, but maintainers still had to inspect separate manifest, copied-root, and package verification outputs to decide whether preservation was complete.
Decision: Add `forge maintenance-preservation-completeness` and `forge-maintenance-preservation-completeness` as read-only final review commands. The command combines written manifest verification, copied archive-root verification, archive-package verification, and entry-count consistency into one `complete` or `blocked` status with `--require-complete` fail-closed behavior.
Alternatives considered: Leave final review manual, extend the package verifier with more summary fields, or create another write-capable preservation command. Manual review is avoidably error-prone, expanding package verification would blur its focused contract, and a write-capable command is unnecessary because preservation completeness is a review decision.
Consequences: Maintainers can now review preservation readiness from one deterministic artifact while the command remains local-first and read-only. It does not write files, copy evidence, create packages, stage, commit, push, rerun validation, poll workflows, change remotes, prove signer identity, or prove validation coverage.
Human decision still required: No.

## DEC-137 — 2026-07-10 — Written archive packages need read-only verification before preservation

Context: AUTO-136 created confirmed tar/zip archive packages from verified copied archive roots, but there was no separate command to reopen a package later and prove its entries still matched the manifest-backed evidence.
Decision: Add `forge maintenance-archive-package-verify` and `forge-maintenance-archive-package-verify` as read-only package verification commands. The command reuses the manifest/copy/package-preview verification chain, constrains the package path to the repository root, opens `.tar.gz`, `.tgz`, `.tar`, and `.zip` files, and compares package entry paths, byte counts, and SHA-256 values against the expected copied archive entries.
Alternatives considered: Trust package writer output, rely on manual tar/zip inspection, or fold verification into the writer only. Trusting writer output misses later package drift/deletion, manual inspection is error-prone, and writer-only verification does not support independent preservation review after time has passed.
Consequences: Maintainers can now verify a written evidence package before treating it as preserved. The command remains read-only and does not stage, commit, push, rerun validation, poll workflows, change remotes, or prove signer identity.
Human decision still required: No.

## Historical decisions

Older autonomous decision entries remain available in repository history.