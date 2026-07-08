# Autonomous Changelog

## 2026-07-08 — AUTO-066

- Task ID: AUTO-066 — Harden patch-intent description candidate paths
- Summary: Hardened `forge patch-intent-describe` so supplied patch-intent review JSON is refused when `compared_paths` contains unsafe candidate path labels such as absolute paths, parent traversal, blank/current-directory labels, whitespace-padded labels, or backslash-based labels.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent PRs, README, roadmap/state/changelog/decisions, CI workflow, patch-intent description implementation, docs, and tests. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic regression coverage for unsafe compared-path labels while preserving existing described/blocked/text/JSON/symlink behavior. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit/status check
- Follow-up notes: Add an explicit read-only patch-proposal description surface that accepts a concrete change objective and reviewed patch-intent description evidence without generating or applying patches automatically.

## 2026-07-08 — AUTO-065

- Task ID: AUTO-065 — Add patch-intent description artifact
- Summary: Added `forge patch-intent-describe`, a read-only artifact that consumes reviewed `patch-intent-review` JSON and reports `described` only when the supplied evidence is ready, allows patch intent, contains compared paths, and has no blockers. The command supports `--require-described`, returning exit code `2` for blocked evidence while leaving files unchanged.
- Branch and PR assessment: Inspected repository metadata, recent PRs, open issues, README, roadmap/state/changelog/decisions, CI workflow, patch-intent review implementation, CLI entrypoint, and related tests. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Deterministic tests cover described evidence, blocked evidence, text/JSON output, content non-disclosure, bad payloads, unsafe paths, symlinks, and installed-entrypoint `--require-described` pass/fail behavior. CI smoke coverage now exercises installed `forge patch-intent-describe --require-described` with clear live patch-intent review evidence. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit/status check
- Follow-up notes: Add an explicit read-only patch-proposal description surface that accepts a concrete change objective and reviewed patch-intent description evidence without generating or applying patches automatically.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.
