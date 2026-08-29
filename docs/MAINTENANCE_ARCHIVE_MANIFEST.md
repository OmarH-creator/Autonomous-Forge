# Maintenance archive manifest

`forge maintenance-archive-manifest` builds an archive manifest for the strongest ready preservation candidate selected from one or more `.ai/run-history/` links. It can also verify a previously written manifest before any evidence-copy/archive step exists.

By default, link-based operation remains a preview. With both `--output` and `--confirm-write`, it writes one repository-local JSON manifest that lists the evidence files that should be preserved together. With `--manifest`, it reopens that written JSON and recomputes the listed evidence hashes/byte counts without writing anything.

The command reuses `forge maintenance-review-compare`, selects the best ready candidate, reads the linked bundle, and lists:

- the selected run-history link;
- the selected maintenance bundle;
- each source evidence report referenced by the bundle;
- current existence and byte counts for those repository-local files;
- current SHA-256 verification for the run-history link, maintenance bundle, and source evidence reports;
- archive integrity gate totals and per-entry pass/fail/advisory reasons;
- the pushed commit, remote, and branch target;
- verified live workflow-status provenance already carried by the selected preservation candidate, when present;
- blockers and next preservation guidance.

## Live workflow-status provenance

When the selected preservation candidate carries the normalized live workflow-status proof established by linked-bundle review and reviewer comparison, the manifest preserves it as `live_status_provenance` across preview, confirmed write, written-manifest verification, JSON output, and stable text output.

The retained fields are:

- `present` and `status`;
- `verified`;
- `source`;
- `requested_commit`;
- `workflow_run_limit`;
- `collection_complete`;
- `commit_binding_complete`;
- `evidence_sha256`;
- `review_effect: informational_only`;
- `affects_manifest_readiness: false`;
- `affects_archive_integrity: false`.

This is evidence continuity, not a new archive gate. Missing or unverified live-status provenance does not make an otherwise ready manifest blocked and does not change archive-integrity scoring. The authoritative trust remains the linked durable bundle plus `forge maintenance-history-link-review --verify-linked-bundle`; the archive manifest does not query GitHub or independently prove workflow sufficiency.

Legacy candidates and written manifests without live-status provenance remain compatible and are reported as `present=false`, `status=not_present`.

## Usage

Preview a manifest:

```bash
forge maintenance-archive-manifest \
  --link .ai/run-history/AUTO-120-link.json \
  --link .ai/run-history/AUTO-121-link.json
```

Use `--require-ready` when the preview should fail closed unless the comparison is ready, a selected candidate exists, all listed archive entries are present, and hash/byte-count integrity gates pass:

```bash
forge maintenance-archive-manifest \
  --link .ai/run-history/AUTO-120-link.json \
  --require-ready
```

Write a ready manifest only after explicit confirmation:

```bash
mkdir -p .ai/archives
forge maintenance-archive-manifest \
  --link .ai/run-history/AUTO-120-link.json \
  --output .ai/archives/AUTO-120-manifest.json \
  --confirm-write \
  --require-ready
```

Verify a written manifest before preserving or copying evidence:

```bash
forge maintenance-archive-manifest \
  --manifest .ai/archives/AUTO-120-manifest.json \
  --require-ready
```

Preview where the verified manifest entries would be copied without copying them:

```bash
forge maintenance-archive-copy-preview \
  --manifest .ai/archives/AUTO-120-manifest.json \
  --archive-root .ai/archive-copies/AUTO-120 \
  --require-ready
```

Copy verified entries after explicit confirmation, then verify the copied archive root:

```bash
forge maintenance-archive-copy \
  --manifest .ai/archives/AUTO-120-manifest.json \
  --archive-root .ai/archive-copies/AUTO-120 \
  --confirm-copy \
  --create-parents
forge maintenance-archive-copy-verify \
  --manifest .ai/archives/AUTO-120-manifest.json \
  --archive-root .ai/archive-copies/AUTO-120 \
  --require-verified
```

See `docs/MAINTENANCE_ARCHIVE_COPY_PREVIEW.md` for the dedicated copy-preview contract and `docs/MAINTENANCE_ARCHIVE_COPY_VERIFY.md` for the post-copy verification contract.

Use JSON output for local dashboards or follow-on review tooling:

```bash
forge maintenance-archive-manifest \
  --manifest .ai/archives/AUTO-120-manifest.json \
  --format json
```

The compatibility script is also available:

```bash
forge-maintenance-archive-manifest --help
```

## Integrity gates

The command computes local SHA-256 values for the selected run-history link and maintenance bundle and recomputes the expected source-report SHA-256 values recorded in the bundle. Source reports also compare current byte counts to the values recorded in the bundle or written manifest. The output includes an `archive_integrity` object in JSON and an `Archive integrity` line in text output.

A ready newly generated manifest requires zero failed integrity gates. Missing files, run-history-link drift after a manifest has been written, source-report hash drift, or byte-count drift block readiness before preservation can continue.

The selected run-history link receives a SHA-256 content binding at the archive-manifest boundary. That digest records the exact link bytes that were reviewed when the manifest was created, so downstream manifest verification, archive-copy verification, and archive-package stages can reject same-size link drift instead of relying on byte count alone. This is a content-integrity guarantee only: it does not promote the link into executor validation evidence, change external-validation provenance, make live workflow status authoritative, or prove signer identity.

Legacy written manifests that predate this binding and therefore carry no expected SHA-256 for the run-history link remain readable. Their link entry retains the older advisory integrity behavior rather than receiving an invented historical digest.

Live workflow-status provenance is not an integrity gate. It is carried only to keep already-verified workflow evidence reviewable through the preservation path.

## Confirmed write behavior

Writing requires all of the following:

- `--output` must point to a repository-local JSON path under `--root`;
- the output parent directory must already exist;
- the output file must not already exist;
- the manifest must be ready;
- `--confirm-write` must be supplied.

The written JSON contains the same selected candidate, archive entries, integrity gates, provenance summaries, blockers, and preservation guidance as the preview, plus `manifest_written: true` and `manifest_path`.

## Written manifest verification

`--manifest` is mutually exclusive with `--link`, `--output`, and `--confirm-write`. It reads one existing written manifest, requires `manifest_written: true`, verifies that every listed entry stays inside `--root`, recomputes current SHA-256 values where the manifest carries expected digests, recomputes byte counts, and returns a blocked status if any listed evidence is missing or drifted.

For newly generated manifests, that expected-digest set includes the selected run-history link as well as the bundle and source reports. Verification preserves the manifest's normalized live-status summary for review; it does not turn that informational provenance into an archive gate or re-query GitHub.

Verification does not mutate the manifest. It is intended as the safety gate immediately before manual preservation or any future archive-copy command.

## Safety boundary

The command reads repository-local history links, linked bundle JSON, written manifest JSON, and source-report metadata. It recomputes local path existence, byte counts, and evidence hashes. With `--output --confirm-write`, it writes exactly one manifest JSON file. It does not copy evidence files, create archives, change source evidence, stage, commit, push, poll workflows, inspect live remotes, rerun validation, or prove signer identity.

## Exit codes

- `0`: the manifest preview, confirmed write, or written-manifest verification completed.
- `2`: an input was invalid, unsafe, unreadable, a write was requested without confirmation, `--manifest` was combined with link/write options, or `--require-ready` was supplied and the manifest was blocked.
