# Autonomous Decisions

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

## Historical note

Older autonomous decision entries remain available in repository history.
