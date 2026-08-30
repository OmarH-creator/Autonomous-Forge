# Preservation receipt publication binding

`forge maintenance-preservation-receipt` creates an immutable receipt for one already-complete preservation artifact.

AUTO-233 strengthens the confirmed write boundary so the authoritative preservation-completeness source must still match the exact path, byte count, and SHA-256 captured by the receipt both immediately before publication and immediately after the no-clobber hard-link publication step.

If the completeness source changes while publication is in progress, the write fails closed. If the change is detected after the destination link exists, Forge removes that destination and fsyncs the receipt directory before returning the error. A successful write therefore cannot report success for stale completeness bytes.

The source remains subject to the fixed 1 MiB completeness-input ceiling. The existing explicit confirmation gate, repository containment, symlink refusal, no-clobber publication, temporary-file fsync, directory fsync, and verification semantics remain unchanged.

This check is an integrity continuity guard, not a provenance upgrade. It does not rerun archive verification or validation, does not make informational workflow status authoritative, and grants no Git, network, workflow, overwrite, remote, or branch-protection authority.
