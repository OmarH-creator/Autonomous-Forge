# AUTO-184 — Harden archive-manifest persistence against races

## Objective

Close a concrete durability gap in confirmed archive-manifest writes: preflight already refused an existing output, but the final `Path.write_text()` could still overwrite a file created by another process between the preflight check and publication.

## Inspection

Inspected README/docs/examples, archive and preservation implementation/tests, repository policy/config/CI, roadmap/state/changelog/decisions, recent commits, open issues, every visible branch, and PR history. Historical non-main branches remain stale/diverged; reviewed PRs are merged, closed, obsolete, or unrelated and no integration was warranted.

## Change

`write_maintenance_archive_manifest()` now publishes the serialized manifest with a same-directory temporary file, flush + file `fsync`, atomic no-clobber hard-link publication, parent-directory `fsync`, and guaranteed temporary-file cleanup. A target created after preflight causes a fail-closed `MaintenanceArchiveManifestError` instead of being replaced.

Focused regression coverage proves both successful file/directory durability syncing and preservation of bytes written by a simulated racing process.

## Safety

The existing ready-manifest requirement, repository-root confinement, explicit `--confirm-write` gate, and existing-output refusal remain unchanged. No overwrite escape hatch, network access, external command execution, Git mutation, force-push, remote/protection mutation, or workflow change was added.

## Validation

Added deterministic tests for successful durable publication and the TOCTOU collision path. The changed implementation and tests were reviewed for Python syntax and use only standard-library `os`/`tempfile` primitives. Full checkout/full pytest is unavailable in this runtime because `github.com` DNS resolution fails. Final GitHub status is inspected separately; no green Python matrix is claimed without evidence.

## Diff / noise review

Intended AUTO-184 paths are limited to archive-manifest implementation, focused tests, dedicated docs, README current status, autonomous state, and this run record. Repository policy permits these areas and prohibited workflow/secret paths were not touched.

## Next action

Inspect AUTO-184 CI when observable. Any failure takes priority. If green, continue only with a concrete end-to-end persistence/provenance integrity defect or a meaningful reduction in caller-managed handoffs.