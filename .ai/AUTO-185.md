# AUTO-185 — Harden run-history record persistence against races

## Inspection

Reviewed README/docs/examples, run-history source/tests, policy/config/CI, `.ai` roadmap/state/changelog/decisions, recent commits, issues, all visible branches, and PR history. Historical branches remain stale/diverged and no PR contains newer applicable work. PR #8's original silent-overwrite concern is already superseded on `main`; the current writer still had a narrower time-of-check/time-of-use race because it checked for existence and later called `Path.write_text()`.

## Objective

Make durable `run-history-write` publication fail closed when another process creates the requested output after preflight but before the final write.

## Change

- Write JSON bytes to a same-directory temporary file.
- Flush and `fsync` the temporary file.
- Publish with `os.link()` so the target is created atomically without replacing an existing path.
- `fsync` the parent directory before reporting success.
- Clean temporary files on success and failure.
- Preserve the existing explicit confirmation, preflight readiness, repository/history-directory containment, JSON extension, and immutable-output checks.

## Validation

The changed source and focused test file syntax-compiled in the available Python environment. Deterministic tests cover normal file/directory fsync and a simulated competing writer that creates the destination immediately before publication; the writer must raise, retain the competing bytes, and leave no temporary file behind. Full checkout/full pytest is unavailable because this runtime cannot resolve `github.com`; final supported-version CI must be inspected when exposed by GitHub.

## Safety and limitations

No network access, validation execution, Git mutation, push, force-push, remote/protection mutation, or workflow change was added. The no-clobber publication relies on normal same-filesystem hard-link support; the temporary file is deliberately created in the output directory.

## Next action

Inspect AUTO-185 CI when observable. Any failure takes priority; if green, continue only with another concrete persistence/provenance integrity defect or meaningful caller-handoff reduction.
