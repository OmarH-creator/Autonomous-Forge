# Autonomous Decisions

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

## DEC-128 — 2026-07-09 — Selected preservation candidates need a read-only archive manifest before archive writes

Context: AUTO-127 made `forge maintenance-review-compare` select the strongest ready preservation candidate, but the next preservation step still required reviewers to infer which files should be kept together from the history link, bundle, and source-report metadata.
Decision: Add `forge maintenance-archive-manifest` and `forge-maintenance-archive-manifest` as read-only preview commands. The preview reuses the comparison workflow, requires a selected ready candidate, reads the linked bundle, and lists the run-history link, bundle, source reports, commit target, blockers, and next preservation guidance without copying or writing archive files.
Alternatives considered: Add a write-capable archive command immediately, keep archive selection manual, or fold manifest output into comparison. Immediate writes are premature before the manifest schema is reviewed, manual selection keeps avoidable preservation mistakes, and folding the behavior into comparison would blur candidate ranking with archive packaging.
Consequences: Reviewers can audit exactly which evidence files belong together before any archive writer exists. The command remains local-first and read-only; it does not copy files, write archives, change files, stage, commit, push, rerun validation, poll workflows, or prove signer identity.
Human decision still required: No.

## Historical decisions

Older autonomous decision entries remain available in repository history.
