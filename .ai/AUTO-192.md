# AUTO-192 — Bind validated target bytes through commit creation

## Repository assessment

Inspected README/docs, verified commit-readiness/change-run/commit-create implementation and tests, repository policy/config/CI visibility, recent commits, open issues, all eight visible branches, and recent PR history. The policy-aware `forge plan` milestone and the integrated guarded maintenance chain are already shipped. The seven non-main branches remain historical/diverged, and recent PRs are merged, closed, obsolete, or unrelated.

## Objective and rationale

The highest-value concrete defect was a validation-to-commit integrity gap. Forge proved that retained validation commands passed and later verified the created commit's changed paths, but it did not prove that the target bytes staged by `git add` were still the same bytes that validation observed. A local edit after validation could therefore enter a supposedly verified commit.

## Change

- Verified commit readiness can now carry `validated_target_sha256`, a SHA-256 over the exact bounded target bytes observed after all required validations pass.
- Repository-local `verified-commit-readiness` generation binds that target digest automatically.
- `verified-change-run` captures the digest after every retained validation succeeds and passes it through the in-memory readiness handoff.
- `verified-commit-create` requires a valid target digest, re-hashes the target immediately before any Git status/staging command, and blocks before Git is invoked if the bytes drifted.
- Target hashing is bounded to 1 MB and refuses symlinks, missing/non-regular files, and repository-root escapes.

## Validation

Added deterministic regression coverage for readiness digest capture, change-run propagation, and post-validation drift refusal before any Git runner invocation. Existing commit-creation tests were updated to construct target bytes consistent with the readiness digest. Full checkout/full pytest remains unavailable because this runtime cannot resolve `github.com`, and the connected combined-status surface has not exposed checks for the new code/test head, so no green Python 3.10/3.11/3.12 claim is fabricated.

## Safety and limitations

No new side-effect authority was added. Validation and commit confirmations remain separate, reviewed-path staging remains constrained, and created commits are still checked for SHA, summary, and exact changed paths. This is a fail-closed staleness check rather than a shared filesystem lock; a concurrent writer can still race in the narrow interval between the final SHA-256 comparison and `git add`.

## Branch/PR disposition

Work stayed directly on `main`. No branch or PR was created or merged. Historical branches remain inspect-only evidence.

## Next action

Inspect AUTO-192 CI when observable; any failure takes priority. If green, continue the same end-to-end milestone with another concrete cross-stage integrity defect or a meaningful caller-managed evidence-handoff reduction.