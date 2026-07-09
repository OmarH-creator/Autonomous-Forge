# Maintenance archive copy verification

`forge maintenance-archive-copy-verify` reopens a repository-local archive root after `forge maintenance-archive-copy` and verifies every copied evidence file against the written archive manifest.

The command is read-only. It reads one written manifest, verifies that the source evidence listed by the manifest is still ready, maps every manifest entry into the supplied archive root, and recomputes copied file byte counts and SHA-256 values where expected digests are available.

## Usage

```bash
forge maintenance-archive-copy-verify \
  --manifest .ai/archives/AUTO-120-manifest.json \
  --archive-root .ai/archive-copies/AUTO-120 \
  --require-verified
```

Use JSON output for dashboards or later archive-packaging handoffs:

```bash
forge maintenance-archive-copy-verify \
  --manifest .ai/archives/AUTO-120-manifest.json \
  --archive-root .ai/archive-copies/AUTO-120 \
  --format json \
  --require-verified
```

The compatibility script is also available:

```bash
forge-maintenance-archive-copy-verify --help
```

## Verification gates

A verified copy requires:

- the written manifest itself to verify ready;
- the archive root to exist and be a directory under `--root`;
- every manifest entry to exist at `ARCHIVE_ROOT/<manifest entry path>`;
- copied byte counts to match the manifest entry byte counts when present;
- copied SHA-256 values to match expected manifest digests when present.

Missing copied files, byte-count drift, SHA-256 drift, blocked manifest verification, or an unsafe path blocks `copy_verified`.

## Safety boundary

The command reads one repository-local written manifest and one repository-local archive root. It does not copy files, write archives, create compressed bundles, stage, commit, push, poll workflows, rerun validation, change remotes, or prove signer identity.

## Exit codes

- `0`: verification completed. With `--require-verified`, all copied entries verified.
- `2`: an input was invalid, unsafe, unreadable, or `--require-verified` was supplied and copied evidence was missing or drifted.
