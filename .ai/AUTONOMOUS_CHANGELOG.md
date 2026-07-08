# Autonomous Changelog

## 2026-07-08 — AUTO-067

- Task ID: AUTO-067 — Add patch proposal manifest handoff
- Summary: Added `forge patch-proposal-manifest`, a read-only handoff that consumes described patch-intent evidence plus an explicit objective, requested paths, and validation steps. It fails closed when evidence is blocked, requested paths are unsafe, duplicated, or not already reviewed as candidate paths, validation steps are missing, or the supplied description payload is unsafe.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent PRs, README, roadmap/state/changelog/decisions, CI workflow, patch-intent description implementation, docs, and tests. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic core and installed-entrypoint tests for ready manifests, blocked unreviewed paths, blocked non-described evidence, unsafe requested labels, duplicate candidate labels, missing validation steps, symlink refusal, content non-disclosure, and JSON/text output. CI smoke coverage now exercises installed `forge patch-proposal-manifest --require-ready` with live unchanged patch-intent description evidence. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit/status check
- Follow-up notes: Add a guarded read-only patch proposal review that compares a ready manifest against fresh content-audit evidence before any patch generation or git-diff inspection.

## 2026-07-08 — AUTO-066

- Task ID: AUTO-066 — Harden patch-intent description candidate paths
- Summary: Hardened `forge patch-intent-describe` so supplied patch-intent review JSON is refused when `compared_paths` contains unsafe candidate path labels such as absolute paths, parent traversal, blank/current-directory labels, whitespace-padded labels, or backslash-based labels.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent PRs, README, roadmap/state/changelog/decisions, CI workflow, patch-intent description implementation, docs, and tests. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic regression coverage for unsafe compared-path labels while preserving existing described/blocked/text/JSON/symlink behavior. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit/status check
- Follow-up notes: Add an explicit read-only patch-proposal description surface that accepts a concrete change objective and reviewed patch-intent description evidence without generating or applying patches automatically.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.
