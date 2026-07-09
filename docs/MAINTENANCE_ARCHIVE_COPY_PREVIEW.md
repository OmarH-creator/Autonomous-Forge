# Maintenance archive-copy preview

`forge maintenance-archive-copy-preview` reads a previously written maintenance archive manifest, verifies it with the same integrity checks as `forge maintenance-archive-manifest --manifest`, and plans where each verified evidence file would be copied under a repository-local archive root.

The command is intentionally read-only. It does not create directories, copy files, overwrite files, create archives, stage, commit, push, poll workflows, rerun validation, or prove signer identity.

## Usage

Preview a future copy layout from a written manifest:

```bash
forge maintenance-archive-copy-preview \
  --manifest .ai/archives/AUTO-120-manifest.json \
  --archive-root .ai/archive-copies/AUTO-120
```

Use `--require-ready` when automation should fail closed unless the manifest is verified and every planned destination is safe:

```bash
forge maintenance-archive-copy-preview \
  --manifest .ai/archives/AUTO-120-manifest.json \
  --archive-root .ai/archive-copies/AUTO-120 \
  --require-ready
```

Use JSON output for review tooling:

```bash
forge maintenance-archive-copy-preview \
  --manifest .ai/archives/AUTO-120-manifest.json \
  --archive-root .ai/archive-copies/AUTO-120 \
  --format json
```

The compatibility script is also available:

```bash
forge-maintenance-archive-copy-preview --help
```

## Readiness gates

A ready copy preview requires:

- the written manifest verifies as ready;
- the archive root stays inside the configured repository root;
- every planned destination stays inside the configured repository root;
- no planned destination duplicates another destination;
- no destination matches its source path;
- no destination already exists.

The archive root itself does not need to exist for preview mode. Missing destination parents are reported in JSON as `destination_parent_exists`, allowing a future confirmed copy command to decide whether directory creation should be permitted.

## Output

Text output includes the copy status, manifest path, archive root, copy entry count, planned source-to-destination mappings, blockers, next step, and safety boundary.

JSON output includes the same data plus machine-readable `copy_plan` entries with source path, destination path, byte count, optional SHA-256, and destination existence flags.

## Safety boundary

The command verifies one written manifest and maps each evidence entry to a repository-local destination. It only reports a plan. It does not mutate files or create archive contents.

## Exit codes

- `0`: the copy preview completed.
- `2`: inputs were invalid or unsafe, manifest verification failed, or `--require-ready` was supplied and the copy plan was blocked.
