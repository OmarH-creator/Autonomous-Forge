# AUTO-240 — Validation-attachment durability rollback

## Objective

Close the confirmed post-publication durability gap in immutable validation-result attachment creation without adding a new command or widening authority.

## Repository assessment

The run started from green AUTO-239 on `main` (`eea3d820d2f267e18097ddc1782ac704376b6af2`). Inspection covered README and documentation/examples, source and tests, `.forge/policy.md`, CI configuration, `.ai/AUTONOMOUS_PLAN.md`, `.ai/AUTONOMOUS_STATE.md`, changelog/decisions, recent commits and Actions, all eight visible branches, open issues, and PR history.

The policy-aware `forge plan` milestone requested by the stewardship prompt is already shipped and documented, together with later guarded change, validation, commit, push, and preservation stages. The next concrete integrity defect identified from AUTO-239's handoff was in `validation_result_attachment.py`: after the sidecar hard-link had succeeded, a parent-directory `fsync` failure raised an error while leaving the new destination visible.

## Branch and PR assessment

Work remained directly on `main`. The seven non-main branches are historical/diverged or contain already-integrated/superseded work; no branch warranted integration. There are no open PRs requiring merge. Open issues #1, #6, and #9 are broader product/discussion requests and do not block this fix. No branch, PR, merge, force-push, remote change, workflow permission change, or protection change was used.

## Change

`_atomic_create_text()` now computes the SHA-256 of the exact serialized sidecar before no-clobber publication. If the parent-directory durability `fsync` fails after publication, Forge hashes the current destination incrementally:

- when it still matches the bytes this invocation published, Forge removes it and fsyncs the directory again before failing;
- when it no longer matches, Forge preserves it for inspection rather than risking deletion of another writer's bytes;
- when durable rollback itself fails, Forge reports that uncertainty explicitly.

Existing confirmation, repository containment, source size bounds, source byte/SHA binding, same-directory temporary-file fsync, and no-clobber hard-link behavior remain unchanged.

## Deterministic tests

`tests/test_auto240_validation_attachment_durability_rollback.py` covers:

1. a synthetic first parent-directory sync failure followed by successful ownership-checked rollback; and
2. mutation of the published sidecar immediately before the synthetic sync failure, proving changed bytes are preserved.

## Documentation

`docs/VALIDATION_RESULT_ATTACHMENTS.md` now records the rollback contract and its limits. README's `## Current Autonomous Status` records AUTO-240, validation scope, safety boundary, branch/PR disposition, limitations, visual disposition, and next objective. No new visual was needed because workflow topology did not change.

## Validation

Strongest practical validation is the repository's push-triggered GitHub Actions matrix: Python 3.10, 3.11, and 3.12 package installation, source compilation, installed CLI smoke testing, roadmap validation, and full pytest. Final workflow evidence is recorded in `.ai/AUTONOMOUS_STATE.md` after the completed head is green.

## Limitations

Ownership-checked rollback is not a filesystem transaction or permanent lock. `SIGKILL`, interpreter/host failure, or power loss can prevent cleanup. A second directory-fsync failure while recording rollback leaves durability uncertain and requires inspection.

## Next action

Inspect the historical in-place validation-result writer for a safe recovery strategy when `os.replace()` succeeds but its parent-directory durability sync fails. Because that path can replace pre-existing authoritative record bytes, any rollback must avoid restoring or deleting stale data unless ownership and prior-state continuity can be proven.
