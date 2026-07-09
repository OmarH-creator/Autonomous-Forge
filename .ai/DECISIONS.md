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

## Historical note

Older autonomous decision entries remain available in repository history.
