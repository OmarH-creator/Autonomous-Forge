# AUTO-190 — Crash-safe guarded patch replacement

## Inspection

Inspected the current `main` README/docs, guarded patch source/tests, `.forge` policy, CI/config, autonomous state/roadmap records, recent commits, open issues, all visible branches, and PR history. The original policy-aware `forge plan` milestone is already shipped. Historical non-main branches remain diverged and no PR contains newer applicable guarded-patch work.

AUTO-189's final combined-status lookup still exposed no checks. No evidence justified claiming that matrix green.

## Objective and rationale

Harden the write-capable patch boundary itself. `_apply_prepared_patch()` wrote both the replacement and rollback with `Path.write_text()`. Because that truncates the existing file in place, interruption or I/O failure could leave a partially written working file before live-diff verification or rollback could protect the repository.

## Work

- Added same-directory temporary-file preparation for target replacements.
- Preserved the target permission mode on the prepared replacement.
- Flushed and fsynced the complete replacement before publication.
- Switched the target atomically with `os.replace`.
- Fsynced the target directory after replacement.
- Reused the same atomic path for rollback after failed live-diff verification.
- Added truthful failure semantics for pre-replace failures versus post-replace directory-sync failures.
- Added deterministic regression coverage and updated patch-apply documentation.

## Safety

Existing preview reproduction, ready change evidence, explicit apply confirmation, repository/symlink containment, secret-marker checks, target-scoped live-diff review, and rollback gates remain in force. No network, new external command, workflow mutation, force-push, tag push, remote mutation, protection change, telemetry, or new persistence authority was introduced.

## Validation

Deterministic tests cover successful atomic replacement, permission preservation, temporary cleanup, failed replacement preserving original bytes, file/directory fsync, and post-replace directory-sync failure reporting. Full checkout/full pytest is unavailable from the automation runtime because `github.com` DNS resolution fails. Final-head GitHub CI must be inspected when observable; this record does not fabricate a green matrix.

## Branch / PR disposition

Worked directly on `main`. No branch or PR was created or merged. Historical branches/PRs remain inspect-only evidence and none warranted integration.

## Visuals

No visual update was warranted; the lifecycle architecture is unchanged.

## Next action

Inspect AUTO-190 CI when observable. Any failure takes priority. If green, continue only with another concrete end-to-end mutation/persistence integrity defect or a meaningful reduction in caller-managed handoffs.
