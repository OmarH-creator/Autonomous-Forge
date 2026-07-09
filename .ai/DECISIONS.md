# Autonomous Decisions

## DEC-137 — 2026-07-10 — Written archive packages need read-only verification before preservation

Context: AUTO-136 created confirmed tar/zip archive packages from verified copied archive roots, but there was no separate command to reopen a package later and prove its entries still matched the manifest-backed evidence.
Decision: Add `forge maintenance-archive-package-verify` and `forge-maintenance-archive-package-verify` as read-only package verification commands. The command reuses the manifest/copy/package-preview verification chain, constrains the package path to the repository root, opens `.tar.gz`, `.tgz`, `.tar`, and `.zip` files, and compares package entry paths, byte counts, and SHA-256 values against the expected copied archive entries.
Alternatives considered: Trust package writer output, rely on manual tar/zip inspection, or fold verification into the writer only. Trusting writer output misses later package drift/deletion, manual inspection is error-prone, and writer-only verification does not support independent preservation review after time has passed.
Consequences: Maintainers can now verify a written evidence package before treating it as preserved. The command remains read-only and does not stage, commit, push, rerun validation, poll workflows, change remotes, or prove signer identity.
Human decision still required: No.

## DEC-136 — 2026-07-10 — Archive package writing must reuse ready previews and require confirmation

Context: AUTO-135 made archive-package metadata reviewable but did not create compressed archives. The next safe product step is a bounded package writer that does not bypass the preview, manifest, copy-verification, destination, and overwrite gates already established.
Decision: Add `forge maintenance-archive-package` and `forge-maintenance-archive-package` as explicitly confirmed local package-writing commands. The command reuses the ready archive-package preview, requires `--confirm-package`, refuses unready previews and existing package destinations, constrains package paths to the repository root, and writes exactly one `.tar.gz`, `.tgz`, `.tar`, or `.zip` archive from the verified archive root.
Alternatives considered: Keep packaging manual, let the preview command write with another flag, or silently overwrite existing packages. Manual packaging leaves avoidable preservation mistakes, mixing preview and write behavior would blur the safety boundary, and overwriting packages would undermine durable evidence preservation.
Consequences: Maintainers can now create one bounded archive package after reviewing a ready preview. The command still does not stage, commit, push, rerun validation, poll workflows, change remotes, or prove signer identity.
Human decision still required: No.

## DEC-135 — 2026-07-09 — Archive packaging needs a verified metadata preview before writing archives

Context: AUTO-134 made copied archive roots re-verifiable, but moving directly to tar/zip creation would introduce package path, format, overwrite, extra-file, and parent-directory risks before reviewers can inspect the intended archive metadata.
Decision: Add `forge maintenance-archive-package-preview` and `forge-maintenance-archive-package-preview` as read-only package-preview commands. The command verifies the written manifest and copied archive root, constrains the future package path to the repository, accepts only `.tar.gz`, `.tgz`, `.tar`, or `.zip`, blocks existing package destinations and package paths inside the archive root, compares archive-root contents with manifested entries, and reports package entries and total bytes without creating an archive.
Alternatives considered: Create compressed archives immediately, leave packaging manual, or fold package planning into copy verification. Immediate writing is premature before package metadata is reviewable, manual packaging keeps avoidable evidence-drift and extra-file risks, and copy verification should remain focused on the copied root rather than future package destination metadata.
Consequences: Maintainers can now review exact package metadata before any writer exists. The command does not create compressed archives, copy files, write manifests, stage, commit, push, rerun validation, poll workflows, change remotes, or prove signer identity.
Human decision still required: No.

## Historical decisions

Older autonomous decision entries remain available in repository history.
