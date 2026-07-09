# Maintenance preservation completeness

`forge maintenance-preservation-completeness` summarizes the final preservation state for a completed maintenance evidence set.

The command is read-only. It verifies three already-written/local evidence layers and can optionally add a supplied workflow-status freshness gate:

- the written archive manifest;
- the copied archive root;
- the written archive package;
- optional commit/workflow status JSON that must be successful and match the manifest commit when `--require-workflow-fresh` is used.

```bash
forge maintenance-preservation-completeness \
  --manifest .ai/archives/AUTO-120-manifest.json \
  --archive-root .ai/archive-copies/AUTO-120 \
  --package .ai/archive-packages/AUTO-120.tar.gz \
  --require-complete
```

Add workflow freshness evidence when the preserved package should also prove that the archived run belongs to a successful status/check/workflow result for the same commit:

```bash
forge maintenance-preservation-completeness \
  --manifest .ai/archives/AUTO-120-manifest.json \
  --archive-root .ai/archive-copies/AUTO-120 \
  --package .ai/archive-packages/AUTO-120.tar.gz \
  --status-evidence .ai/status/AUTO-120-workflows.json \
  --require-workflow-fresh \
  --require-complete
```

Use JSON output for follow-on tooling:

```bash
forge maintenance-preservation-completeness \
  --manifest .ai/archives/AUTO-120-manifest.json \
  --archive-root .ai/archive-copies/AUTO-120 \
  --package .ai/archive-packages/AUTO-120.zip \
  --status-evidence .ai/status/AUTO-120-workflows.json \
  --require-workflow-fresh \
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
- stage gates summarize manifest, copied-root, package, and optional workflow-status readiness in one place;
- when workflow freshness is required, supplied status evidence must be successful and its commit SHA must match the written manifest commit SHA.

## Status evidence format

The optional `--status-evidence` file uses the same JSON shapes accepted by `forge commit-status-review`: `statuses`, `check_runs`, `workflow_runs`, or a combined `state`. It must be a repository-local JSON object. The freshness gate is clear only when all supplied contexts are successful and the status evidence commit SHA matches the archive manifest commit SHA.

## Safety boundary

The completeness summary reads repository-local manifest, archive-root, package, and optional status-evidence files only. It does not write files, copy evidence, create packages, stage, commit, push, poll workflows, rerun validation, change remotes, or prove signer identity.

## Exit codes

- `0`: completeness was reported. With `--require-complete` and `--require-workflow-fresh`, this means all preservation and workflow freshness gates were clean.
- `2`: inputs were invalid/missing/unsafe, or a strict flag was supplied and the preservation summary found blockers.
