# Autonomous Decisions

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

## DEC-127 — 2026-07-09 — Comparison output should identify the strongest ready preservation candidate

Context: AUTO-125 introduced multi-handoff comparison and AUTO-126 made individual handoffs fail closed when history pointers drift from replayed bundles. The comparison could show ready and blocked records, but reviewers still had to manually decide which ready evidence record should be preserved first.
Decision: Extend `forge maintenance-review-compare` with deterministic `preservation_candidates` and a `selected_preservation_candidate`. The ranking only considers ready handoffs with no failed handoff or replay-policy gates, then favors verified linked-bundle replay, fewer blockers, more reviewed paths, more validation steps, richer retained validation context, and stable commit/bundle/link tie-breakers.
Alternatives considered: Leave selection to manual review, select the newest commit only, or add a write-capable archive immediately. Manual review keeps avoidable friction, newest-commit selection can ignore evidence quality, and writing archives is premature before a reviewable candidate-selection surface exists.
Consequences: Reviewers get a compact recommendation while blocked records and blockers remain visible. The command remains read-only and still does not rerun validation, poll workflows, inspect live remotes, change files, stage, commit, push, write archive manifests, or prove signer identity.
Human decision still required: No.

## Historical decisions

Older autonomous decision entries remain available in repository history.
