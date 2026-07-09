# Autonomous Decisions

## DEC-135 — 2026-07-09 — Archive packaging needs a verified metadata preview before writing archives

Context: AUTO-134 made copied archive roots re-verifiable, but moving directly to tar/zip creation would introduce package path, format, overwrite, extra-file, and parent-directory risks before reviewers can inspect the intended archive metadata.
Decision: Add `forge maintenance-archive-package-preview` and `forge-maintenance-archive-package-preview` as read-only package-preview commands. The command verifies the written manifest and copied archive root, constrains the future package path to the repository, accepts only `.tar.gz`, `.tgz`, `.tar`, or `.zip`, blocks existing package destinations and package paths inside the archive root, compares archive-root contents with manifested entries, and reports package entries and total bytes without creating an archive.
Alternatives considered: Create compressed archives immediately, leave packaging manual, or fold package planning into copy verification. Immediate writing is premature before package metadata is reviewable, manual packaging keeps avoidable evidence-drift and extra-file risks, and copy verification should remain focused on the copied root rather than future package destination metadata.
Consequences: Maintainers can now review exact package metadata before any writer exists. The command does not create compressed archives, copy files, write manifests, stage, commit, push, rerun validation, poll workflows, change remotes, or prove signer identity.
Human decision still required: No.

## DEC-134 — 2026-07-09 — Copied archive roots must be verified before packaging

Context: AUTO-133 added a bounded archive-copy command, but after copying there was no dedicated way to reopen the archive root and prove the copied evidence still matched the written manifest before preservation or packaging.
Decision: Add `forge maintenance-archive-copy-verify` and `forge-maintenance-archive-copy-verify` as read-only post-copy verification commands. The command first verifies the written manifest, constrains the archive root to the repository, maps each manifest entry to `ARCHIVE_ROOT/<entry path>`, recomputes copied file byte counts and SHA-256 values where expected digests are present, and fails closed with `--require-verified` when copied evidence is missing or drifted.
Alternatives considered: Trust copy output, move directly to compressed archive packaging, or fold verification into the copy command only. Trusting copy output misses later drift/deletion, packaging is premature without a stable verification surface, and copy-only verification would not help reviewers recheck archives after time has passed.
Consequences: Maintainers can now verify a copied evidence root before any archive-package writer exists. The command does not copy files, write archives, stage, commit, push, rerun validation, poll workflows, change remotes, or prove signer identity.
Human decision still required: No.

## DEC-133 — 2026-07-09 — Archive-copy execution must be confirmation-gated and overwrite-safe

Context: AUTO-132 made archive-copy destination layouts reviewable, but preservation still required manual copying after a ready preview. The next useful step is bounded local copy execution that gathers verified evidence files together without becoming an uncontrolled archive writer.
Decision: Add `forge maintenance-archive-copy` and `forge-maintenance-archive-copy` as explicitly confirmed local copy commands. The command reuses written-manifest verification and archive-copy-preview readiness, requires `--confirm-copy`, refuses blocked previews, refuses existing destinations, constrains all source and destination paths to the repository root, and only creates missing destination parents when `--create-parents` is explicitly supplied.
Alternatives considered: Keep copying manual, create compressed archives immediately, or silently create parents and overwrite files. Manual copying keeps avoidable preservation mistakes, compressed archives are premature before post-copy verification exists, and implicit directory creation/overwrites would undermine safety and evidence durability.
Consequences: Maintainers can now perform a bounded local evidence copy after reviewing a ready plan. The command still does not create compressed archives, stage, commit, push, rerun validation, poll workflows, change remotes, or prove signer identity.
Human decision still required: No.

## Historical decisions

Older autonomous decision entries remain available in repository history.
