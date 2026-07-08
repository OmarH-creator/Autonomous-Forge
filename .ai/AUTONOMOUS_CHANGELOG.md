# Autonomous Changelog

## 2026-07-08 — AUTO-069

- Task ID: AUTO-069 — Harden patch proposal review path labels
- Summary: Hardened `forge-patch-proposal-review` so supplied manifest and content-audit JSON must contain safe repository-relative path labels before the review reports or trusts requested/audited paths as patch-adjacent evidence. The guard now refuses blank labels, leading/trailing whitespace, absolute paths, parent traversal, `.`/`..`, empty path segments, and backslash paths.
- Branch and PR assessment: Inspected repository metadata, recent README/state/changelog/decisions/roadmap records, CI workflow, patch proposal review implementation, docs, and tests. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic regression tests for unsafe manifest requested-path labels and unsafe content-audit audited-path labels. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit/status check
- Follow-up notes: Integrate the review gate into the primary `forge` subcommand surface or add a read-only patch proposal draft preview that still does not generate or apply patches.

## 2026-07-08 — AUTO-068

- Task ID: AUTO-068 — Add patch proposal review gate
- Summary: Added a read-only patch proposal review gate. The new `forge-patch-proposal-review` installed command consumes a ready patch proposal manifest plus fresh changed-content audit JSON, then fails closed unless requested paths exactly match fresh audited paths and all requested paths are clear.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent PRs, open issues, README, roadmap/state/changelog/decisions, CI workflow, patch proposal manifest implementation, content-audit behavior, docs, and tests. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic core and standalone CLI tests for ready reviews, blocked manifest evidence, missing fresh audit evidence, extra audited paths, non-clear requested paths, bad payload refusal, duplicate audit-path refusal, symlink input refusal, text/JSON output, and `--require-ready` exit behavior. CI smoke coverage now exercises the installed standalone command after the live content-audit/manifest chain. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit/status check
- Follow-up notes: Integrate the review gate into the primary `forge` subcommand surface or add a read-only patch proposal draft preview that still does not generate or apply patches.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.
