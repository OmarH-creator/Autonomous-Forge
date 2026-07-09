# Autonomous Decisions

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

## DEC-132 — 2026-07-09 — Archive-copy behavior needs a read-only destination preview first

Context: AUTO-131 made written archive manifests re-verifiable, but moving directly to file copying would introduce destination path, collision, parent-directory, and overwrite risks before reviewers can inspect the planned layout.
Decision: Add `forge maintenance-archive-copy-preview` and `forge-maintenance-archive-copy-preview` as read-only commands. The command verifies one written manifest first, maps every evidence entry under a repository-local `--archive-root`, blocks outside-root destinations, duplicate destinations, source-equals-destination mappings, and existing destination files, and reports text/JSON copy plans without copying anything.
Alternatives considered: Add a confirmed copy command immediately, require manual destination planning, or fold destination mapping into manifest verification. Immediate copying is premature before the destination contract is visible, manual planning keeps avoidable preservation mistakes, and folding copy planning into manifest verification would blur evidence integrity checks with destination layout checks.
Consequences: Maintainers can review an exact future copy layout before any write-capable archive-copy command exists. The command does not create directories, copy files, overwrite files, create archives, stage, commit, push, rerun validation, poll workflows, or prove signer identity.
Human decision still required: No.

## DEC-131 — 2026-07-09 — Written archive manifests must be re-verifiable before archive-copy behavior

Context: AUTO-130 made ready archive manifests durable by writing one repository-local JSON file, but a written manifest can become stale if listed evidence files are edited, deleted, or moved before preservation.
Decision: Extend `forge maintenance-archive-manifest` with `--manifest` verification mode. The command reads one written manifest, requires `manifest_written=true`, refuses link/write flag combinations, constrains listed entries to the repository root, recomputes current SHA-256 values and byte counts, and fails closed with `--require-ready` when evidence has drifted.
Alternatives considered: Move directly to archive-copy behavior, trust the written manifest forever, or add a separate standalone verifier command. Copy behavior is premature before verification exists, trusting old manifests would preserve stale evidence, and a separate command would duplicate the existing archive-manifest output/format contract.
Consequences: Maintainers can verify a persisted manifest immediately before manual preservation or future copy planning while the workflow remains bounded. The command does not copy evidence files, create archives, mutate evidence, stage, commit, push, rerun validation, poll workflows, or prove signer identity.
Human decision still required: No.

## Historical decisions

Older autonomous decision entries remain available in repository history.
