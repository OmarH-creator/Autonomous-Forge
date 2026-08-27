# Archive Live-Status Provenance

AUTO-215 carries the existing verified live workflow-status proof beyond the archive manifest into copied-root and package review surfaces.

## What is preserved

`forge maintenance-archive-copy-verify`, archive package preview, and `forge maintenance-archive-package-verify` expose the normalized live-status provenance already stored in a verified archive manifest:

- `source`
- `requested_commit`
- `workflow_run_limit`
- `collection_complete`
- `commit_binding_complete`
- `evidence_sha256`
- verification status

Stable text output shows the same proof so reviewers do not need to reopen the manifest JSON merely to confirm which bounded workflow-status evidence accompanied the preserved package.

## Safety semantics

This is evidence propagation only. Live-status provenance is forced to `review_effect=informational_only` at the copied-root boundary. It cannot make copy verification pass or fail, cannot make package preview ready or blocked, and cannot make package verification pass or fail. The archive-integrity result remains based on the manifest, copied bytes, and package contents.

The downstream surfaces therefore expose explicit non-gating fields such as `affects_copy_verification=false`, `affects_package_readiness=false`, `affects_package_verification=false`, and `affects_archive_integrity=false`.

No GitHub query, workflow rerun, validation execution, file copy, package write, Git mutation, push, remote mutation, or branch-protection mutation is added by AUTO-215.

## Compatibility

Legacy manifests without `live_status_provenance` remain valid. Downstream review surfaces report a not-present live-status summary instead of inventing proof.

The linked maintenance bundle and linked-bundle verification remain authoritative for the origin of live workflow-status evidence; archive surfaces preserve that already-verified reviewer context only.
