# Autonomous Decisions

## DEC-108 — 2026-07-09 — Completed bundles need run-history links

Context: AUTO-099 through AUTO-103 created complete maintenance evidence bundles, source-report hash verification, and replay summaries, but a completed pushed bundle still had to be discovered by knowing the exact persisted bundle path. The roadmap after AUTO-107 identified durable run-history linkage for completed pushed bundles as the next safe step.
Decision: Extend `forge maintenance-evidence-bundle` with optional `--history-link`, `--confirm-history-link`, and `--require-history-linked` support. The command writes one small `maintenance-bundle-history-link/v1` JSON pointer under `.ai/run-history/` only after the bundle itself is complete and already written.
Alternatives considered: Copy the full bundle into multiple run-history files, modify the legacy run-history schema, add a separate command first, auto-write links without confirmation, overwrite an existing latest pointer, or defer all discovery until a future index command exists.
Consequences: Maintainers can now preserve a lightweight durable pointer to completed pushed bundles without duplicating the full bundle. The link records bundle hash/size, commit, branch, reviewed paths, validation steps, and source-report fingerprints, but it does not verify hashes, sign evidence, prove remote state, or replace bundle verification/replay commands.
Human decision still required: No.

## DEC-107 — 2026-07-09 — Push handoff must enforce branch-policy evidence

Context: AUTO-106 made `forge push-readiness` branch-protection aware, but the push-capable `forge push-handoff` boundary still needed to reject older ready reports that predated protected-branch/status-context evidence. Without that explicit check, stale ready JSON could reach the local git inspection and confirmed push path.
Decision: Harden `forge push-handoff` so it requires branch-protection-aware push-readiness fields: clear branch-protection status, protected branch name, strict required status checks, at least one required status context, observed status contexts, and no missing required contexts. The handoff also compares the protected branch with the requested push branch before any confirmed push.
Alternatives considered: Trust only `push_ready=true`, add a separate push-policy command, move branch-policy checks only into post-push verification, call GitHub APIs directly from push-handoff, or disable the push handoff until live branch polling exists.
Consequences: The push-capable boundary now fails closed on legacy/stale branch-policy evidence while preserving the no-force, no-tags, no-remote-configuration, no-branch-protection-mutation, no-shell, no-environment-read boundary. The command still trusts supplied JSON and exact status-context names.
Human decision still required: No.

## DEC-106 — 2026-07-09 — Push-readiness should include branch protection policy

Context: `forge push-readiness` already required commit verification, commit trust, and clear status evidence, but a ready report could still advance toward push handoff without proving that the target branch was protected or that every required branch status context had been observed as clear in the supplied status review.
Decision: Require `forge push-readiness` to consume `--branch-protection` JSON for the target branch. The command now checks that the supplied branch is protected, that required status checks are strict/up-to-date, that required contexts or checks are present, and that every required context appears in the supplied clear status-review evidence.
Alternatives considered: Add a separate branch-protection-review command first, call GitHub APIs directly from push-readiness, leave branch policy to manual review, push first and rely on GitHub rejection, or defer branch protection until a full remote policy model exists.
Consequences: Push-readiness now encodes a stronger branch-policy gate without adding git execution, network calls, pushes, remote mutation, workflow reruns, branch-protection changes, environment reads, or working-tree writes. The gate trusts supplied JSON and exact status-context names; it does not prove the branch policy is current.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history.
