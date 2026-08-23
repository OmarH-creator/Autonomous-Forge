# AUTO-191 — Refuse stale guarded-patch apply and rollback writes

## Repository assessment

Inspected README/docs, guarded patch source/tests, policy/config/CI, current autonomous state, recent commits, open issues, all eight visible branches, and recent PR history. The policy-aware `forge plan` milestone is already shipped, the seven non-main branches remain historical/diverged, issue #13 remains resolved, and no reviewed PR contained newer applicable patch-mutation work.

## Objective and rationale

AUTO-190 made target replacement crash-safe, but the mutation path still trusted target text captured earlier while reproducing the patch preview. A concurrent edit after that capture could be silently overwritten by the initial apply. More seriously, a third party could edit the file after Forge applied its replacement and then have that edit overwritten by automatic rollback if live-diff verification failed.

## Change

`_replace_target_atomically()` now accepts optional expected current text. After the replacement temporary file is fully written and fsynced, Forge re-reads the target immediately before `os.replace` and refuses publication if the bytes no longer match the evidence that authorized the write.

- Initial apply requires the target to still equal the preview-matched original text.
- Automatic rollback requires the target to still equal Forge's just-applied replacement text.
- A stale apply or rollback preserves the newer concurrent edit and reports a blocked/error result for inspection.

## Validation

Added deterministic regression coverage for stale initial-apply refusal and for live-diff failure followed by a third-party edit, proving rollback fails closed rather than overwriting that newer edit. Full checkout/full pytest is unavailable because the execution runtime cannot resolve `github.com`. Combined-status lookups currently expose no checks for the new head, so no green Python 3.10/3.11/3.12 result is claimed without evidence.

## Safety and limitations

Existing preview reproduction, change-readiness, explicit `--confirm-apply`, path/symlink containment, simple secret-marker checks, atomic/fsynced replacement, target-scoped live-diff verification, and later validation/commit/push gates remain unchanged. This is a stale-state recheck rather than a filesystem-level compare-and-swap or shared cross-process lock; another writer can still race in the narrow interval between the final comparison and `os.replace`.

## Branch/PR disposition

Work stayed directly on `main`. No branch or PR was created or merged. Historical non-main branches remain inspect-only evidence.

## Next action

Inspect AUTO-191 CI when observable. Any failure takes priority. If green, continue the same end-to-end milestone with another concrete mutation/persistence integrity defect or a meaningful caller-managed evidence-handoff reduction.
