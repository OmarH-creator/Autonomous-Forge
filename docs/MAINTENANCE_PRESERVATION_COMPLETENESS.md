# Maintenance preservation completeness

`forge maintenance-preservation-completeness` summarizes the final preservation state for a completed maintenance evidence set.

The command is read-only. It verifies three already-written/local evidence layers and reports one final `complete` or `blocked` status:

- the written archive manifest;
- the copied archive root;
- the written archive package.

```bash
forge maintenance-preservation-completeness \
  --manifest .ai/archives/AUTO-120-manifest.json \
  --archive-root .ai/archive-copies/AUTO-120 \
  --package .ai/archive-packages/AUTO-120.tar.gz \
  --require-complete
```

Use JSON output for follow-on tooling:

```bash
forge maintenance-preservation-completeness \
  --manifest .ai/archives/AUTO-120-manifest.json \
  --archive-root .ai/archive-copies/AUTO-120 \
  --package .ai/archive-packages/AUTO-120.zip \
  --require-complete \
  --format json
```

The compatibility script is also available:

```bash
forge-maintenance-preservation-completeness --help
```

## What is checked

- the written manifest still verifies current evidence hashes and byte counts;
- the copied archive root still verifies against the manifest entries;
- the written tar/zip package still verifies against the copied archive root;
- manifest, copied-root, expected package, and verified package entry counts match;
- stage gates summarize manifest, copied-root, and package readiness in one place.

## Safety boundary

The completeness summary reads repository-local manifest, archive-root, and package files only. It does not write files, copy evidence, create packages, stage, commit, push, poll workflows, rerun validation, change remotes, or prove signer identity.

## Exit codes

- `0`: completeness was reported. With `--require-complete`, this means all preservation gates were clean.
- `2`: inputs were invalid/missing/unsafe, or `--require-complete` was supplied and the preservation summary found blockers.
