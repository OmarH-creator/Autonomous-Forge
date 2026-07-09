# Maintenance archive manifest

`forge maintenance-archive-manifest` builds an archive manifest for the strongest ready preservation candidate selected from one or more `.ai/run-history/` links. It can also verify a previously written manifest before any evidence-copy/archive step exists.

By default, link-based operation remains a preview. With both `--output` and `--confirm-write`, it writes one repository-local JSON manifest that lists the evidence files that should be preserved together. With `--manifest`, it reopens that written JSON and recomputes the listed evidence hashes/byte counts without writing anything.

The command reuses `forge maintenance-review-compare`, selects the best ready candidate, reads the linked bundle, and lists:

- the selected run-history link;
- the selected maintenance bundle;
- each source evidence report referenced by the bundle;
- current existence and byte counts for those repository-local files;
- current SHA-256 verification for the maintenance bundle and source evidence reports;
- archive integrity gate totals and per-entry pass/fail/advisory reasons;
- the pushed commit, remote, and branch target;
- blockers and next preservation guidance.

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

The command recomputes local SHA-256 values for the selected maintenance bundle and source reports. Source reports also compare current byte counts to the values recorded in the bundle or written manifest. The output includes an `archive_integrity` object in JSON and an `Archive integrity` line in text output.

A ready manifest requires zero failed integrity gates. Missing files, source-report hash drift, or byte-count drift block readiness before the manifest can be written or verified ready.

The run-history link is still listed as an advisory entry when it lacks an expected digest because the linked bundle and replay gates already verify the hash-linked evidence chain. The command does not invent a new expected digest for the link itself.

## Confirmed write behavior

Writing requires all of the following:

- `--output` must point to a repository-local JSON path under `--root`;
- the output parent directory must already exist;
- the output file must not already exist;
- the manifest must be ready;
- `--confirm-write` must be supplied.

The written JSON contains the same selected candidate, archive entries, integrity gates, blockers, and preservation guidance as the preview, plus `manifest_written: true` and `manifest_path`.

## Written manifest verification

`--manifest` is mutually exclusive with `--link`, `--output`, and `--confirm-write`. It reads one existing written manifest, requires `manifest_written: true`, verifies that every listed entry stays inside `--root`, recomputes current SHA-256 values where the manifest carries expected digests, recomputes byte counts, and returns a blocked status if any listed evidence is missing or drifted.

Verification does not mutate the manifest. It is intended as the safety gate immediately before manual preservation or any future archive-copy command.

## Safety boundary

The command reads repository-local history links, linked bundle JSON, written manifest JSON, and source-report metadata. It recomputes local path existence, byte counts, and source-report hashes. With `--output --confirm-write`, it writes exactly one manifest JSON file. It does not copy evidence files, create archives, change source evidence, stage, commit, push, poll workflows, inspect live remotes, rerun validation, or prove signer identity.

## Exit codes

- `0`: the manifest preview, confirmed write, or written-manifest verification completed.
- `2`: an input was invalid, unsafe, unreadable, a write was requested without confirmation, `--manifest` was combined with link/write options, or `--require-ready` was supplied and the manifest was blocked.
