# Maintenance archive package preview

`forge maintenance-archive-package-preview` previews package metadata for a copied maintenance archive root without creating a compressed archive.

The command is intentionally read-only. It reuses the written-manifest and archive-copy verification chain, then compares the copied archive-root contents with the manifest entries before reporting the intended package path, format, entry list, total bytes, blockers, and next step.

```bash
forge maintenance-archive-package-preview \
  --manifest .ai/archives/AUTO-120-manifest.json \
  --archive-root .ai/archive-copies/AUTO-120 \
  --package .ai/archive-packages/AUTO-120.tar.gz \
  --require-ready
```

Use `--format json` for machine-readable output.

## Safety boundary

The preview verifies copied evidence existence, byte counts, SHA-256 values, package destination safety, and unmanifested archive-root files. It does not create tar/zip files, copy files, write manifests, stage, commit, push, poll workflows, rerun validation, or prove signer identity.

## Readiness rules

The preview is ready only when:

- the written archive manifest is still ready;
- the copied archive root verifies against manifest hashes and byte counts;
- the future package path is repository-local and uses `.tar.gz`, `.tgz`, `.tar`, or `.zip`;
- the package path is not inside the archive root;
- the package parent directory already exists;
- the package destination does not already exist; and
- the archive root contains no unmanifested files.

A future package writer should reuse this evidence and add an explicit confirmation flag before writing any compressed archive.
