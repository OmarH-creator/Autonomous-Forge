# AUTO-186 — Harden durable maintenance evidence persistence

## Inspection

Reviewed `main`, README/docs/examples, maintenance evidence and history-link implementation/tests, config/CI, `.forge/policy.md`, autonomous roadmap/state/changelog/decisions, recent commits, open issues, all visible branches, and PR history. Historical non-main branches remain stale/diverged; reviewed PRs are merged, closed, obsolete, or unrelated.

## Objective

Close the remaining time-of-check/time-of-use overwrite window in maintenance bundle and maintenance history-link persistence. Both writers already refused outputs that existed at preflight but still used direct `Path.write_text()` for final publication.

## Change

Both persistence boundaries now create a same-directory temporary file, flush and fsync it, publish with atomic no-clobber `os.link`, fsync the parent directory, and clean the temporary file. If another writer creates the target after preflight, Forge reports a blocked result and preserves the competing bytes.

## Validation

Added deterministic coverage for bundle and history-link racing writers, temporary-file cleanup, and successful file/directory fsync. Full repository checkout/pytest is unavailable in this runtime because `github.com` cannot be resolved; final-head CI must be inspected when observable before claiming the supported Python matrix green.

## Safety

No overwrite escape hatch, network access, external command execution, force-push, tag push, remote mutation, branch-protection mutation, or workflow mutation was added. Existing explicit confirmations and path/readiness gates remain unchanged. Publication relies on normal same-filesystem hard-link support, with temporary files created in the destination directory.

## Branch / PR disposition

Work stayed directly on `main`. No branch or pull request was created or merged.

## Next

Inspect AUTO-186 CI when observable. Any failure takes priority; if green, continue only with another concrete end-to-end persistence/provenance integrity defect or a meaningful reduction in caller-managed handoffs.
