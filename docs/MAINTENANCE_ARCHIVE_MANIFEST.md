# Maintenance archive manifest preview

`forge maintenance-archive-manifest` builds a read-only archive manifest preview for the strongest ready preservation candidate selected from one or more `.ai/run-history/` links.

It is intended for reviewers who already have completed maintenance evidence bundles and want one compact list of the files that should be preserved together before any write-capable archive step exists. The command reuses `forge maintenance-review-compare`, selects the best ready candidate, reads the linked bundle, and lists:

- the selected run-history link;
- the selected maintenance bundle;
- each source evidence report referenced by the bundle;
- current existence and byte counts for those repository-local files;
- current SHA-256 verification for the maintenance bundle and source evidence reports;
- archive integrity gate totals and per-entry pass/fail/advisory reasons;
- the pushed commit, remote, and branch target;
- blockers and next preservation guidance.

## Usage

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

Use JSON output for local dashboards or follow-on review tooling:

```bash
forge maintenance-archive-manifest \
  --link .ai/run-history/AUTO-120-link.json \
  --format json
```

The compatibility script is also available:

```bash
forge-maintenance-archive-manifest --help
```

## Integrity gates

The manifest preview recomputes local SHA-256 values for the selected maintenance bundle and source reports. Source reports also compare current byte counts to the values recorded in the bundle. The output includes an `archive_integrity` object in JSON and an `Archive integrity` line in text output.

A ready manifest requires zero failed integrity gates. Missing files, source-report hash drift, or byte-count drift block readiness before a future archive writer can safely use the manifest.

The run-history link is still listed as an advisory entry because the linked bundle and replay gates already verify the hash-linked evidence chain. The preview does not invent a new expected digest for the link itself.

## Safety boundary

The command reads repository-local history links, linked bundle JSON, and source-report metadata. It recomputes local path existence, byte counts, and source-report hashes, but it does not copy files, write archive manifests, create archives, change files, stage, commit, push, poll workflows, inspect live remotes, or prove signer identity.

## Exit codes

- `0`: the manifest preview was generated.
- `2`: an input was invalid, unsafe, unreadable, or `--require-ready` was supplied and the preview was blocked.
