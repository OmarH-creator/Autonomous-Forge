# Maintenance archive package

`forge maintenance-archive-package` creates one repository-local tar/zip package from a verified copied maintenance archive root after explicit confirmation.

The command reuses `forge maintenance-archive-package-preview` as its safety gate. A package can only be written when the preview is ready, the destination parent already exists, the destination package does not already exist, and `--confirm-package` is supplied.

```bash
mkdir -p .ai/archive-packages
forge maintenance-archive-package \
  --manifest .ai/archives/AUTO-120-manifest.json \
  --archive-root .ai/archive-copies/AUTO-120 \
  --package .ai/archive-packages/AUTO-120.tar.gz \
  --confirm-package
```

Use JSON output for follow-on tooling:

```bash
forge maintenance-archive-package \
  --manifest .ai/archives/AUTO-120-manifest.json \
  --archive-root .ai/archive-copies/AUTO-120 \
  --package .ai/archive-packages/AUTO-120.zip \
  --confirm-package \
  --format json
```

The compatibility script is also available:

```bash
forge-maintenance-archive-package --help
```

## Supported formats

The package path must end with one of:

- `.tar.gz`
- `.tgz`
- `.tar`
- `.zip`

The package entries come directly from the ready package preview. Tar entries are written with stable metadata, and zip entries use a fixed timestamp, so repeated packaging of the same copied archive root avoids avoidable metadata noise.

## Streaming source verification

Confirmed package construction streams source evidence in 64 KiB chunks. Zip entries are written through `ZipFile.open(..., "w")` instead of `read_bytes()`/`writestr()`, tar entries are hashed through the exact reader consumed by `tarfile`, and the finished package SHA-256 is also computed incrementally.

Forge compares every source entry's byte count against the already-reviewed package preview while those exact bytes are being written. When the preview supplies an expected SHA-256, Forge also requires the streamed digest to match before publication. Advisory entries whose upstream manifest intentionally has no expected digest remain advisory: they are still streamed and byte-count checked, but are not promoted into digest-bound evidence by the package writer.

If a digest-bound source changes after preview but before or during packaging—even without changing size—construction fails closed and the temporary package is discarded rather than publishing an artifact that no longer matches the reviewed evidence. This bounds peak memory for large evidence while strengthening the preview-to-write integrity handoff. Exact packaging and hashing still read every source byte, so runtime and I/O remain proportional to archive size.

## Durable no-clobber publication

Confirmed packaging is built in a same-directory temporary file first. Forge closes the archive, fsyncs the completed temporary package, publishes it with an atomic no-clobber hard link, fsyncs the destination directory, and then removes the temporary name.

This means two important failure cases stay safe:

- if package construction or source-integrity verification fails, no partial final package is published;
- if another process creates the final destination after preview/preflight but before publication, Forge refuses the publish and preserves the competing bytes.

The normal writer never replaces an existing package. A later preservation run must choose a new package path.

## Safety boundary

The writer verifies the written manifest, verifies the copied archive root, checks package destination safety, refuses overwrites, requires `--confirm-package`, revalidates every source entry's expected byte count and any available expected digest while streaming it into the package, and writes exactly one repository-local package file. Package publication is same-directory, fsynced, and no-clobber. It does not create manifests, copy evidence files, stage, commit, push, poll workflows, rerun validation, change remotes, or prove signer identity.

No-clobber publication relies on ordinary same-filesystem hard-link support. A failure after the hard link is created but during parent-directory durability sync is reported as a published-but-not-fully-synced package and requires inspection before retrying.

## Exit codes

- `0`: the package was written and reported.
- `2`: inputs were invalid, missing, unsafe, unready, package creation was not explicitly confirmed, digest-bound source evidence changed during packaging, package construction failed, or race-safe publication could not complete.
