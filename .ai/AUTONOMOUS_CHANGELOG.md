# Autonomous Changelog

## 2026-07-09 — AUTO-105

- Task ID: AUTO-105 — Maintainer allowed-signer trust policy
- Summary: Added optional allowed-signer policy support to `forge commit-trust-review`. The command now accepts `--allowed-signers` pointing to one repository-local JSON policy, validates a non-empty `allowed_signers` list, refuses wildcard identity values, and blocks otherwise trusted signatures when the inspected signer/key fingerprint is not allowlisted.
- Branch and PR assessment: Inspected repository metadata, recent commits, branch search results, recent PRs, open issues, README/status, roadmap, state, changelog, decisions, commit trust implementation, CLI, tests, and docs. Work stayed directly on `main`. Branch search returned no active branch results. PR #11 is merged; PR #10 is closed and superseded by direct `main` updates; PR #4 was already merged; PRs #2, #3, and #5 were closed or obsolete. Open issues #1, #6, and #9 did not supersede this concrete trust-policy hardening.
- Validation completed: Static source/test/docs review completed through the GitHub repository API. Scratch syntax compilation covered the updated module, CLI, and tests. Focused scratch pytest for `tests/test_commit_trust_review.py` passed with 8 tests covering allowed-signer match, mismatch, malformed policy, unsigned commit, mismatched commit, bad signature, and unverified evidence. Direct local checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add branch-protection/status-policy inspection before push handoff.

## 2026-07-09 — AUTO-104

- Task ID: AUTO-104 — Fast-forward-only push handoff guard
- Summary: Hardened `forge push-handoff` so the explicitly confirmed push path now checks `git merge-base --is-ancestor <remote-sha> <verified-commit>` before any `git push` is attempted. Ready handoffs now report `fast_forward_checked`, confirmed pushes remain non-force, and non-fast-forward candidates are blocked deterministically before remote mutation.
- Branch and PR assessment: Inspected repository metadata, recent commits, branch search results, recent PRs, open issues, README/status, roadmap, state, changelog, decisions, push handoff implementation, tests, and focused docs. Work stayed directly on `main`. Branch search returned no active branch results. PR #11 is merged; PR #10 is closed and superseded by direct `main` updates; PR #4 was already merged; PRs #2, #3, and #5 were closed or obsolete. Open issues #1, #6, and #9 did not supersede this concrete push-safety hardening.
- Validation completed: Static source/test/docs review completed through the GitHub repository API. Focused scratch pytest for `tests/test_push_handoff.py` passed with 9 tests, including the new non-fast-forward refusal case. Direct local checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add maintainer allowed-signer policy support for commit trust evidence.

## Historical note

Older autonomous run entries remain available in repository history.
