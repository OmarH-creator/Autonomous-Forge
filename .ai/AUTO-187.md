# AUTO-187 — Harden verified full-maintenance push-evidence persistence against races

## Inspection

Reviewed README/docs/examples, the verified full-maintenance orchestrator and focused tests, repository policy, CI configuration, roadmap/state/changelog/decisions, recent commits, open issues/TODO-oriented records, all visible branches, and recent PR history. Historical non-main branches remain stale or superseded; no reviewed PR contains newer applicable work.

## Objective and rationale

Close the remaining time-of-check/time-of-use overwrite window when `forge verified-full-maintenance-run` persists its post-push-verified JSON before durable bundle construction. That evidence is part of the provenance chain and must not be silently replaced by a racing writer.

## Work

- Replaced direct push-evidence `Path.write_text()` with same-directory temporary-file persistence.
- Flush and file-fsync the payload before publication.
- Publish using an atomic no-clobber hard link.
- Fsync the parent directory after successful publication.
- Return a blocked result if another writer creates the target first, preserving competing bytes.
- Clean temporary files on both success and failure.
- Added focused deterministic regression coverage and dedicated documentation.

## Safety

Existing post-push verification, independent push-evidence write confirmation, repository containment, JSON-extension enforcement, existing-output refusal, and downstream bundle verification remain unchanged. No force-push, tag push, network access, remote mutation, branch-protection mutation, workflow mutation, or overwrite escape hatch was added.

## Validation

Focused tests cover successful file/directory fsync and a simulated racing writer that creates the output immediately before publication. Full local checkout/full pytest is unavailable because this runtime cannot resolve `github.com`; final-head CI must be inspected when it becomes observable before claiming the supported Python matrix green.

## Branch/PR disposition

Work stayed directly on `main`. No branch, PR, merge, force-push, or protection change was created.

## Next action

Inspect AUTO-187 CI when observable. Any failure takes priority; if green, continue only with another concrete end-to-end persistence/provenance integrity defect or a meaningful reduction in caller-managed evidence handoffs.
