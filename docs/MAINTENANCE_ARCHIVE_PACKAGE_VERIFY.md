# Maintenance archive package verification

`forge maintenance-archive-package-verify` reopens a written repository-local tar/zip package and verifies it against the manifest-backed copied archive root.

The command is read-only. It first reuses the package preview chain so the written manifest and copied archive root are still verified, then reads the package entries and compares package paths, byte counts, and SHA-256 values with the expected copied evidence entries.

```bash
forge maintenance-archive-package-verify \
  --manifest .ai/archives/AUTO-120-manifest.json \
  --archive-root .ai/archive-copies/AUTO-120 \
  --package .ai/archive-packages/AUTO-120.tar.gz \
  --require-verified
```

Use JSON output for follow-on tooling:

```bash
forge maintenance-archive-package-verify \
  --manifest .ai/archives/AUTO-120-manifest.json \
  --archive-root .ai/archive-copies/AUTO-120 \
  --package .ai/archive-packages/AUTO-120.zip \
  --require-verified \
  --format json
```

The compatibility script is also available:

```bash
forge-maintenance-archive-package-verify --help
```

## What is checked

- the manifest and copied archive root still pass the package-preview verification chain;
- the package file exists, is inside the repository root, and can be opened as `.tar.gz`, `.tgz`, `.tar`, or `.zip`;
- every expected copied evidence path is present in the package;
- unmanifested package entries are reported as blockers;
- each matched entry has the expected byte count and SHA-256 value when available.

## Safety boundary

The verifier reads repository-local manifest, archive-root, and package files only. It does not write files, copy evidence, create packages, stage, commit, push, poll workflows, rerun validation, change remotes, or prove signer identity.

## Exit codes

- `0`: verification was reported. With `--require-verified`, this means the package matched all expected entries.
- `2`: inputs were invalid/missing/unsafe, or `--require-verified` was supplied and verification found blockers.
