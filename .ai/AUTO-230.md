# AUTO-230 — Stream and reverify confirmed archive-package writes

## Repository assessment

Inspected the current `main` baseline and canonical Actions result, README/docs/examples, archive/package source and tests, configuration and CI, policy, `.ai/AUTONOMOUS_PLAN.md`, `.ai/AUTONOMOUS_STATE.md`, `.ai/AUTONOMOUS_CHANGELOG.md`, `.ai/DECISIONS.md`, recent commits, open issues, all eight visible branches, and recent/open/merged/closed pull requests. AUTO-229 was green before work began. The seven non-main branches remain historical/diverged; open issues are broader project requests; inspected PRs are merged, closed, obsolete, superseded, or unrelated. No branch or PR warranted integration.

## Objective and rationale

Continue the same preservation milestone by fixing the next concrete write-path defect rather than creating another read-only surface. `forge maintenance-archive-package` still materialized complete ZIP source files with `Path.read_bytes()` and materialized the complete finished package again to calculate its SHA-256. The preview also occurred before the actual archive write, leaving digest-bound evidence exposed to source drift between review and publication.

## Work completed

- Added 64 KiB incremental SHA-256 hashing for completed package files.
- ZIP package construction now streams source bytes through `ZipFile.open(..., "w")` instead of `read_bytes()`/`writestr()`.
- Tar package construction now hashes and counts the exact bytes consumed by `tarfile` through a bounded reader wrapper.
- Every entry with an expected byte count is checked against the reviewed package preview while writing.
- Every entry with an expected preview SHA-256 must retain that digest on the exact streamed bytes before publication.
- Same-size digest-bound source drift after preview fails closed and the temporary package is discarded.
- Advisory entries whose authoritative upstream evidence intentionally has no expected SHA remain advisory; they are byte-count checked but are not promoted into invented digest-bound evidence.
- Updated `docs/MAINTENANCE_ARCHIVE_PACKAGE.md` and README safety/status text.

## Validation and correction

The first product head `d4c59a4b95cc5ccf89640ffcc54560cdff3850fd` passed installation, compilation, CLI smoke, and roadmap validation but failed pytest across the supported matrix because the first implementation treated a missing advisory `run_history_link` SHA as a digest mismatch. This exposed a compatibility mistake in the new guard rather than a pre-existing failure.

The correction enforces SHA only when the reviewed preview supplies one while preserving byte-count checks. Focused regression coverage now proves the writer succeeds without `Path.read_bytes()` on archive-root/package paths and refuses same-size mutation of a digest-bound source after preview. Corrected product head `8d3d1a034fe485dc52fb630d4ed708d3e2423264` passed Actions run `33270213540`; Python 3.10, 3.11, and 3.12 all passed package installation, source compilation, installed CLI smoke tests, roadmap validation, and pytest.

## Safety and diff review

Existing explicit `--confirm-package`, ready-preview gating, repository containment, same-directory temporary creation, completed-package fsync, atomic hard-link no-clobber publication, parent-directory fsync, and downstream verification remain unchanged. No staging, commit-generation, push, workflow mutation, network collection, remote change, protection change, force-push, branch, or PR capability was added.

The run changed only the intended archive-package implementation, focused tests, archive-package documentation, README status/safety description, autonomous state, and this run record. No workflow, secret, generated, or unrelated path was intentionally changed. `AUTONOMOUS_PLAN.md`, `AUTONOMOUS_CHANGELOG.md`, and `DECISIONS.md` were inspected; this is an implementation hardening within the existing roadmap and safety architecture, so no artificial semantic rewrite was made.

## Limitations and next action

Exact archive construction and hashing still read every source byte, so runtime and disk I/O remain proportional to evidence size. Advisory archive entries without an upstream expected SHA can only be byte-count checked during this confirmed write; synthesizing a digest here would change their trust semantics.

Next autonomous objective: inspect whether that advisory entry can acquire a trustworthy digest at its authoritative upstream boundary without changing its provenance class. If not, continue to the next concrete preservation write/integrity defect. Any fresh CI failure takes priority.
