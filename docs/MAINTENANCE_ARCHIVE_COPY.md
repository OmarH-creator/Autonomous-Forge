# Maintenance archive copy

`forge maintenance-archive-copy` is the first write-capable evidence-preservation step after archive-manifest verification and archive-copy preview.

It reads one written maintenance archive manifest, verifies it through the same manifest and copy-preview gates, and then copies the verified repository-local evidence files into a repository-local archive root only when explicitly confirmed.

The command is intentionally narrow. It does not create compressed archives, stage files, commit, push, poll workflows, rerun validation, change remotes, or prove signer identity.

## Usage

Preview the copy layout first:

```bash
forge maintenance-archive-copy-preview \
  --manifest .ai/archives/AUTO-120-manifest.json \
  --archive-root .ai/archive-copies/AUTO-120 \
  --require-ready
```

Then perform the local copy only after reviewing the plan:

```bash
forge maintenance-archive-copy \
  --manifest .ai/archives/AUTO-120-manifest.json \
  --archive-root .ai/archive-copies/AUTO-120 \
  --confirm-copy \
  --create-parents
```

Use JSON output for downstream review tooling:

```bash
forge maintenance-archive-copy \
  --manifest .ai/archives/AUTO-120-manifest.json \
  --archive-root .ai/archive-copies/AUTO-120 \
  --confirm-copy \
  --create-parents \
  --format json
```

The compatibility script is also available:

```bash
forge-maintenance-archive-copy --help
```

## Safety gates

A copy run requires:

- `--confirm-copy`;
- a written manifest that verifies as ready;
- a copy preview that verifies as ready;
- source and destination paths constrained to the configured repository root;
- no destination that already exists;
- no destination that matches its source;
- unique destination paths;
- existing destination parents, unless `--create-parents` is explicitly supplied.

All blockers are checked before copying begins. Missing parent directories are only created after the full preflight passes.

Each evidence file is then copied into a same-directory temporary file rather than directly into the final archive destination. Forge recomputes the temporary copy's byte count and SHA-256 and requires them to match the verified copy preview before publication. It flushes and file-fsyncs the temporary copy, publishes it with a no-clobber hard link, fsyncs the destination directory, and removes the temporary name. If another writer creates the final destination after preflight, Forge preserves that competing file and refuses publication. If source bytes drift after preview, Forge refuses to publish the drifted copy.

This is per-file durability rather than a cross-file transaction. If a later entry fails after earlier entries were safely published, the earlier copied entries remain for inspection and a retry must use a clean destination set rather than overwrite them.

## Output

Text output includes copy status, manifest path, archive root, copied entry count, per-entry source-to-destination mappings, blockers, next step, and safety boundary.

JSON output includes the same data plus machine-readable `copied_entries` with source path, destination path, byte count, SHA-256, and optional stage metadata.

## Exit codes

- `0`: verified evidence files were copied.
- `2`: inputs were invalid or unsafe, confirmation was missing, manifest/copy-preview verification failed, destination parents were missing without `--create-parents`, a destination already existed or won a publication race, source evidence drifted after preview, or durable publication failed.