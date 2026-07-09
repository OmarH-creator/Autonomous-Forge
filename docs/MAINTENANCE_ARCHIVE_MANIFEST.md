# Maintenance archive manifest preview

`forge maintenance-archive-manifest` builds a read-only archive manifest preview for the strongest ready preservation candidate selected from one or more `.ai/run-history/` links.

It is intended for reviewers who already have completed maintenance evidence bundles and want one compact list of the files that should be preserved together before any write-capable archive step exists. The command reuses `forge maintenance-review-compare`, selects the best ready candidate, reads the linked bundle, and lists:

- the selected run-history link;
- the selected maintenance bundle;
- each source evidence report referenced by the bundle;
- current existence and byte counts for those repository-local files;
- the pushed commit, remote, and branch target;
- blockers and next preservation guidance.

## Usage

```bash
forge maintenance-archive-manifest \
  --link .ai/run-history/AUTO-120-link.json \
  --link .ai/run-history/AUTO-121-link.json
```

Use `--require-ready` when the preview should fail closed unless the comparison is ready, a selected candidate exists, and all listed archive entries are present:

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

## Safety boundary

The command reads repository-local history links, linked bundle JSON, and source-report metadata. It recomputes local path existence and byte counts, but it does not copy files, write archive manifests, create archives, change files, stage, commit, push, poll workflows, inspect live remotes, or prove signer identity.

## Exit codes

- `0`: the manifest preview was generated.
- `2`: an input was invalid, unsafe, unreadable, or `--require-ready` was supplied and the preview was blocked.
