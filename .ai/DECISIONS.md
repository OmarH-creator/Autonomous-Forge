# Autonomous Decisions

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

## DEC-130 — 2026-07-09 — Archive manifests may be written only through a narrow confirmed JSON writer

Context: AUTO-129 made archive-manifest previews verify source-report hashes and byte counts, leaving the next preservation step manual. Reviewers still needed a durable manifest file that records the selected ready preservation candidate without copying evidence or creating an archive.
Decision: Extend `forge maintenance-archive-manifest` with `--output` and `--confirm-write`. The command still previews by default, writes exactly one repository-local JSON manifest only when the manifest is ready and explicitly confirmed, and refuses blocked manifests, outside-root outputs, missing parent directories, and overwrites.
Alternatives considered: Keep the command preview-only, add a full archive-copy writer, or silently overwrite manifests. Preview-only keeps extra manual work, archive copying is premature before manifest verification exists, and overwrites would undermine durable evidence records.
Consequences: Maintainers can persist a compact preservation manifest while the workflow remains local-first and bounded. The command does not copy evidence files, create archives, change source evidence, stage, commit, push, rerun validation, poll workflows, or prove signer identity.
Human decision still required: No.

## DEC-129 — 2026-07-09 — Archive manifests must verify evidence hashes before archive writes exist

Context: AUTO-128 listed the files that should be preserved for a selected maintenance candidate, but the manifest mostly exposed current path existence and byte counts. A future archive writer would need stronger evidence that the source reports still match the bundle metadata at preview time.
Decision: Harden `forge maintenance-archive-manifest` so read-only manifest output recomputes source-report SHA-256 values and byte counts, exposes compact archive-integrity gates, and blocks readiness when listed evidence is missing or drifted. Keep the command preview-only.
Alternatives considered: Move directly to a write-capable archive command, rely on replay summaries alone, or leave integrity checking to reviewers. Immediate writes are premature, replay summaries are not as archive-entry focused, and manual checking keeps avoidable preservation mistakes.
Consequences: Reviewers can see whether the selected archive set is currently intact before any writer exists. The command remains local-first and read-only; it does not copy files, write archives, change files, stage, commit, push, rerun validation, poll workflows, or prove signer identity.
Human decision still required: No.

## Historical decisions

Older autonomous decision entries remain available in repository history.
