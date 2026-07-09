# Autonomous Changelog

## 2026-07-09 — AUTO-108

- Task ID: AUTO-108 — Maintenance bundle run-history links
- Summary: Extended `forge maintenance-evidence-bundle` with opt-in durable run-history links. After a completed bundle is persisted with `--output ... --confirm-write`, the command can now write a small `maintenance-bundle-history-link/v1` JSON pointer under `.ai/run-history/` with `--history-link ... --confirm-history-link`, recording bundle path/hash/byte count, commit, remote branch, reviewed paths, validation steps, and source-report fingerprints.
- Branch and PR assessment: Inspected repository metadata, recent PRs, open issues, branch search results, README/status, roadmap, state, changelog, decisions, maintenance bundle implementation, CLI, tests, and docs. Work stayed directly on `main`. AUTO-107 was already marked DONE and recommended durable run-history linkage as the next safe step. PR #11 is merged; PR #10 is closed and superseded by direct `main` updates; PR #4 was already merged; PRs #2, #3, and #5 are closed or obsolete. Open issues #1, #6, and #9 did not supersede this capability.
- Validation completed: Static source/test/docs review completed through the GitHub repository API. Focused deterministic tests were added for confirmed history-link writing, missing confirmation/unwritten bundle blockers, and outside-run-history refusal. Direct full repository checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a read-only maintenance history index for persisted bundle-link records.

## 2026-07-09 — AUTO-107

- Task ID: AUTO-107 — Branch-policy-enforcing push handoff
- Summary: Hardened `forge push-handoff` so the push-capable boundary now explicitly requires branch-protection-aware push-readiness evidence. The handoff blocks legacy ready reports without protected-branch, strict status-check, required-context, observed-context, or missing-context fields; it also blocks protected-branch mismatches and required contexts that were not observed before any confirmed push can execute.
- Branch and PR assessment: Inspected repository metadata, recent commits, branch search results, recent PRs, README/status, roadmap, state, changelog, decisions, push-readiness/push-handoff implementation, tests, and docs. Work stayed directly on `main`. Recent history showed AUTO-106 branch-protection-aware push readiness already on main. PR #11 is merged; PR #10 is closed and superseded by direct `main` updates; PR #4 was already merged; PRs #2, #3, and #5 were closed or obsolete. No open PR or branch required integration for this run.
- Validation completed: Static source/test/docs review completed through the GitHub repository API. Focused scratch pytest for `tests/test_push_handoff.py` passed with 12 tests covering ready branch-policy evidence, confirmed push, non-fast-forward refusal, legacy readiness without branch policy, protected branch mismatch, missing required status context, unready evidence, wrong branch, already-pushed commit, git inspection failure, unsafe branch, and repository-local JSON loading. Direct full repository checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add durable run-history linkage for completed pushed bundles.

## 2026-07-09 — AUTO-106

- Task ID: AUTO-106 — Branch-protection-aware push readiness
- Summary: Upgraded `forge push-readiness` so push readiness now requires supplied branch-protection/status-policy JSON along with commit verification, commit trust, and commit-status evidence. The gate reports branch protection status, required/observed/missing status contexts, strict status-check policy, and blocks unprotected branches, branch mismatches, non-strict checks, and missing required contexts while keeping `push_allowed=false`.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent PRs, open issues, README/status, roadmap, state, changelog, decisions, push-readiness implementation, CLI, tests, and docs. Work stayed directly on `main`. Recent history showed AUTO-105 allowed-signer policy work already on main. PR #11 is merged; PR #10 is closed and superseded by direct `main` updates; PR #4 was already merged; PRs #2, #3, and #5 were closed or obsolete. Open issues #1, #6, and #9 did not supersede this pre-push policy guard.
- Validation completed: Static source/test/docs review completed through the GitHub repository API. Scratch syntax compilation covered the updated module and CLI. Focused scratch pytest for `tests/test_push_readiness.py` passed with 12 tests covering ready branch-protected evidence, unverified/untrusted evidence, SHA/path mismatches, unclear status, unprotected branch evidence, missing required contexts, non-strict checks, unsafe paths, and repository-local JSON loading. Direct local checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Require branch-protection-aware push-readiness explicitly in `forge push-handoff` and add durable run-history linkage for completed pushed bundles.

## Historical note

Older autonomous run entries remain available in repository history.
