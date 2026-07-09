# Autonomous Decisions

## DEC-105 — 2026-07-09 — Commit trust can require an allowed signer

Context: `forge commit-trust-review` already inspected local git signature metadata and blocked unsigned, bad, expired, revoked, uncheckable, or mismatched commits before push-readiness. However, a trusted git signature code alone did not let maintainers express a repository-specific identity policy for which signer names or key fingerprints are allowed to advance toward push handoff.
Decision: Add optional allowed-signer policy support to `forge commit-trust-review`. The command accepts `--allowed-signers` for one repository-local JSON policy with a non-empty `allowed_signers` list. Entries match exact signer, exact key fingerprint, or both; wildcard identity values are refused. When the policy is supplied, otherwise trusted signatures block unless the inspected signer/key fingerprint matches at least one allowlist entry.
Alternatives considered: Keep signer review manual, make all trusted local git signatures pass, require a default checked-in allowlist before adding the feature, move allowlist checks into push-readiness, call GitHub signing APIs, or defer until a full cryptographic attestation model exists.
Consequences: The push-readiness evidence chain can now include repository-specific maintainer identity policy without adding staging, commit creation, push execution, network calls, remote mutation, workflow reruns, environment reads, or branch-protection changes. The feature still relies on local `git show` signature metadata and exact policy strings; it does not manage keys or prove organization membership.
Human decision still required: No.

## DEC-104 — 2026-07-09 — Push handoff must preflight fast-forward ancestry

Context: `forge push-handoff` was already explicitly confirmed, non-force, branch/upstream checked, and limited to one verified commit pushed to one branch, but it did not explicitly verify that the current remote-tracking branch tip was an ancestor of the verified commit before attempting the push. A normal `git push` would reject many non-fast-forward updates, but the safe maintenance workflow benefits from reporting that blocker deterministically before remote mutation is attempted.
Decision: Add a fast-forward guard to `forge push-handoff`. After readiness, branch, HEAD, upstream, and remote-ref checks pass, the command runs `git merge-base --is-ancestor <remote-sha> <verified-commit>` and blocks confirmed pushes when the verified commit is not a descendant of the current remote branch tip. The report exposes `fast_forward_checked` for review.
Alternatives considered: Rely on non-force `git push` rejection, require users to run fetch manually without a tool-level check, move the check into post-push verification only, add branch-protection API checks first, or disable the push-capable handoff until a larger remote policy model exists.
Consequences: Confirmed pushes now fail earlier and more clearly on stale or divergent remote history while preserving the existing no-force, no-tags, no-remote-configuration, no-branch-protection-mutation boundary. The guard still relies on local remote-tracking refs, so maintainers should refresh refs before using the handoff when remote state may have changed.
Human decision still required: No.

## DEC-103 — 2026-07-09 — Persisted bundles need a replay summary

Context: AUTO-101 can verify that a persisted maintenance evidence bundle still matches its source-report hashes, but maintainers still lacked one compact command that explains whether the saved patch, validation, commit, push, and post-push chain is internally complete and replayable.
Decision: Add `forge maintenance-replay-summary` plus compatibility `forge-maintenance-replay-summary`. The command consumes one persisted bundle, reuses the bundle verifier to detect source-report drift, checks the bundle completion fields, safe reviewed paths, target path, validation steps, and expected evidence-chain stages, then reports `replayable` or `blocked` with blockers.
Alternatives considered: Leave replay decisions to manual review, add replay output to `maintenance-bundle-verify`, require rerunning validation/workflows, poll GitHub Actions, inspect branch protection remotely, or defer this until a cryptographic attestation model exists.
Consequences: Maintainers now have a deterministic local replay decision for saved maintenance evidence without adding writes, patch application, validation execution, commits, pushes, remote mutation, workflow reruns, polling, or environment reads. This is still evidence replay, not proof of current remote state, signer identity, or branch-protection compliance.
Human decision still required: No.

## DEC-102 — 2026-07-09 — Push-readiness should require commit trust evidence

Context: AUTO-102 added a local `forge commit-trust-review` checkpoint, but leaving `forge push-readiness` dependent only on commit verification and status evidence would let a ready push ignore unsigned, bad, expired, revoked, uncheckable, mismatched, or path-mismatched trust evidence.
Decision: Require `forge push-readiness` to consume `--commit-trust` JSON in addition to `--commit-verify` and `--status-review`. Push-readiness reports ready only when the verified commit, trusted commit, status-review commit, and reviewed paths all match, the trust report is trusted with signature code `G` or `U`, and status evidence is clear.
Alternatives considered: Keep commit trust as an optional side report, make push-readiness run `git show` directly, merge commit trust into commit verification, require full allowed-signer policy before integration, or defer trust to human review only.
Consequences: Push readiness now encodes a stronger pre-push evidence chain without adding git execution, network calls, writes, commits, pushes, remote changes, workflow reruns, or branch-protection changes to the push-readiness command. This still is not a full identity policy or cryptographic attestation system.
Human decision still required: No.

## DEC-101 — 2026-07-09 — Persisted bundles need a local drift verifier

Context: AUTO-100 added SHA-256 source-report fingerprints to durable maintenance evidence bundles, but the repository still lacked a command that could later recompute those fingerprints and report whether the persisted bundle still matched its local source evidence files.
Decision: Add `forge maintenance-bundle-verify` plus compatibility `forge-maintenance-bundle-verify`. The command reads one persisted bundle, validates that all expected source-report stages are present, recomputes byte counts and SHA-256 hashes for each repository-local source report path, and reports `verified` or `drifted` with blockers. `--require-verified` fails closed on drift.
Alternatives considered: Leave verification to manual scripts, add verification back into the bundle builder, hash only the final persisted bundle, require signed artifacts, rerun workflows, or verify commit signatures as part of the bundle verifier.
Consequences: Maintainers now have a deterministic local drift check for persisted bundle provenance without widening the write, commit, push, remote, or workflow authority boundary. This is still not a signature system, author identity proof, workflow rerun proof, or cryptographic trust model.
Human decision still required: No.

## DEC-100 — 2026-07-09 — Durable bundles need source-report fingerprints

Context: AUTO-099 created one portable maintenance evidence bundle after patch apply, validation, commit verification, push handoff, and post-push verification. The bundle linked semantic evidence but did not preserve fingerprints of the exact source JSON reports used to build it, so later report edits or swaps would be harder to detect.
Decision: Extend `forge maintenance-evidence-bundle` to record a `source_reports` array containing stage, path, byte count, and SHA-256 digest for each source evidence file. The command validates supplied hash metadata when building from in-memory data and computes fingerprints automatically when reading repository-local JSON reports from the CLI path.
Alternatives considered: Add a separate verification command first, rely only on commit SHA and reviewed paths, hash only the final bundle output, use non-cryptographic checksums, or turn the bundle into a signed trust artifact.
Consequences: Persisted bundles now carry enough local provenance to detect stale, edited, swapped, or regenerated source reports by recomputing SHA-256 later. This is not signed evidence, identity verification, workflow rerun proof, or a cryptographic trust model.
Human decision still required: No.

## DEC-099 — 2026-07-09 — Completed maintenance loops need one durable evidence bundle

Context: The workflow can now apply a reviewed patch, record supplied post-apply validation, verify a created commit, push through an explicitly confirmed non-force handoff, and verify post-push remote reachability. Those reports remained separate, making it harder to preserve one portable end-to-end maintenance artifact.
Decision: Add `forge maintenance-evidence-bundle` plus compatibility `forge-maintenance-evidence-bundle`. The command consumes completed patch-apply, post-apply validation, commit-verify, push-handoff, and post-push verification JSON reports, validates that the same commit and reviewed paths flow through the commit/push/post-push stages, reports blockers for stale or inconsistent evidence, and can persist one bounded JSON bundle only with `--output` plus `--confirm-write`.
Alternatives considered: Leave bundling to manual documentation, add bundle writing inside post-push verification, write automatically without confirmation, include workflow reruns or polling, or make the bundle a cryptographic trust artifact.
Consequences: Maintainers now have a durable evidence handoff for completed maintenance loops. The command trusts supplied JSON evidence and does not yet verify commit signatures, rerun workflows, apply patches, create commits, push, or mutate remotes.
Human decision still required: No.

## DEC-098 — 2026-07-09 — Pushed commits need explicit post-push verification

Context: The workflow can now create, verify, mark ready, and push one reviewed commit through an explicitly confirmed non-force handoff, but it still had no concrete checkpoint confirming that the pushed commit is reachable from the intended remote branch with clear status evidence.
Decision: Add `forge post-push-verify` plus compatibility `forge-post-push-verify`. The command consumes pushed push-handoff JSON and clear commit-status-review JSON for the same commit, validates safe reviewed paths, branch, and remote labels, optionally runs one bounded `git fetch --prune <remote> <branch>`, checks the local remote-tracking ref, and reports verified only when `git merge-base --is-ancestor <commit> <remote>/<branch>` confirms reachability.
Alternatives considered: Treat successful `git push` as enough, add verification inside push-handoff, poll/rerun GitHub workflows, trust status evidence without matching the pushed commit, require the commit to be exactly the branch head, or add remote/protection management.
Consequences: Maintainers now have a concrete post-push completion gate while avoiding force-pushes, tag pushes, remote mutation, workflow reruns, and branch-protection mutation. The command trusts supplied handoff/status evidence and local git remote-tracking output; `--fetch` refreshes only the requested remote branch.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history.
