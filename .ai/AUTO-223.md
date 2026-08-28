# AUTO-223 — Bound immutable validation-attachment inputs

## Objective

Close the resource-bound gap left after AUTO-222 by ensuring direct immutable validation-attachment construction and verification cannot read arbitrarily large source or attachment files into memory.

## Repository assessment

- Baseline `main` head `02c193cb19a1a8ec5fce0600c65bfcb9c6a4215b` was green in Actions run `33166352930`.
- Inspected README/docs/examples, validation attachment source/tests, run-history reader/writer paths, `.forge/policy.md`, `.ai` state/roadmap/changelog/decisions context, recent commits, open issues, all eight visible branches, and recent PR history.
- Seven non-main branches remain historical/diverged. Recent PRs are merged, closed, obsolete, or unrelated; none warranted integration.
- Open issues #1, #6, and #9 are broader project/discussion requests rather than blockers for this integrity slice.

## Rationale

AUTO-222 bounded validation-sidecar discovery, but `validation_result_attachment.py` still used unbounded source `read_bytes()` calls and direct attachment `read_text()` during construction, stale-source rechecks, and verification. An oversized stable input could therefore consume unbounded memory before the immutable-evidence checks ran.

## Work

- Added a fixed 1 MiB `MAX_VALIDATION_ATTACHMENT_BYTES` contract.
- Added bounded binary reads that consume at most the limit plus one sentinel byte.
- Applied the ceiling to source snapshots before payload construction, the pre-publication stale-source recheck, direct immutable attachment verification, and source fingerprint recomputation during verification.
- Added deterministic regression coverage for oversized source input, oversized direct attachment input, source growth after receipt creation, and source growth during a confirmed write.
- Updated immutable validation-attachment documentation and README status/safety text.

## Safety

- Existing `--confirm-write`, repository/path/symlink confinement, no-clobber atomic publication, fsync durability, SHA-256/byte binding, and stale-source refusal remain intact.
- No validation command, Git operation, network call, workflow mutation, push authority, remote mutation, or protection change was added.
- Changed paths remain within repository policy's allowed `src/**`, `tests/**`, `docs/**`, README, and `.ai/**` areas; prohibited workflow/secret paths were untouched.

## Validation

Substantive product/test/docs head `b83ff59c90a5e4d82357b54c62e47b092e39be70` passed GitHub Actions run `33183703391`. Python 3.10, 3.11, and 3.12 each passed checkout/install, source compilation, installed CLI smoke tests, roadmap validation, and pytest.

## Limitations

The 1 MiB ceiling is a fixed local fail-closed contract rather than streaming validation. The historical validation-result payload builder remains reused for compatibility after the source passes the immutable attachment stage's initial bound; the writer rechecks the source through the same ceiling immediately before publication.

## Next action

Inspect the remaining authoritative run-history read/write paths for the same concrete unbounded-input class, or choose another meaningful cross-stage integrity defect. Any fresh CI failure takes priority.