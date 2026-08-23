# Stale patch target protection

AUTO-191 hardens the guarded patch-apply mutation boundary against concurrent edits.

## Behavior

Before an atomic replacement is published, Forge re-reads the target and requires it to match the exact text that authorized the write:

- the initial confirmed apply expects the original text captured while reproducing the patch preview;
- rollback after failed live-diff verification expects the replacement text that Forge itself just published.

If the target no longer matches, Forge refuses the replacement instead of overwriting the newer bytes.

This matters most during rollback. A third party may edit the file after Forge applies its replacement but before live-diff verification finishes. In that case Forge reports that rollback could not safely proceed and preserves the third-party edit for inspection rather than restoring stale original content over it.

## Safety boundary

The protection is local and fail-closed. It does not add a shared inter-process lock or claim a filesystem-level compare-and-swap primitive; another writer could still race in the narrow interval between the final text check and `os.replace`. Existing preview reproduction, path/symlink containment, explicit `--confirm-apply`, file/directory fsync, live-diff verification, and validation/commit/push gates remain unchanged.
