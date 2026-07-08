# Autonomous Changelog

## 2026-07-08 — AUTO-068

- Task ID: AUTO-068 — Add patch proposal review gate
- Summary: Added a read-only patch proposal review gate. The new `forge-patch-proposal-review` installed command consumes a ready patch proposal manifest plus fresh changed-content audit JSON, then fails closed unless requested paths exactly match fresh audited paths and all requested paths are clear.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent PRs, open issues, README, roadmap/state/changelog/decisions, CI workflow, patch proposal manifest implementation, content-audit behavior, docs, and tests. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic core and standalone CLI tests for ready reviews, blocked manifest evidence, missing fresh audit evidence, extra audited paths, non-clear requested paths, bad payload refusal, duplicate audit-path refusal, symlink input refusal, text/JSON output, and `--require-ready` exit behavior. CI smoke coverage now exercises the installed standalone command after the live content-audit/manifest chain. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit/status check
- Follow-up notes: Integrate the review gate into the primary `forge` subcommand surface or add a read-only patch proposal draft preview that still does not generate or apply patches.

## 2026-07-08 — AUTO-067

- Task ID: AUTO-067 — Add patch proposal manifest handoff
- Summary: Added `forge patch-proposal-manifest`, a read-only handoff that consumes described patch-intent evidence plus an explicit objective, requested paths, and validation steps. It fails closed when evidence is blocked, requested paths are unsafe, duplicated, or not already reviewed as candidate paths, validation steps are missing, or the supplied description payload is unsafe.
- Branch and PR assessment: Inspected repository metadata, recent commits, recent PRs, README, roadmap/state/changelog/decisions, CI workflow, patch-intent description implementation, docs, and tests. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic core and installed-entrypoint tests for ready manifests, blocked unreviewed paths, blocked non-described evidence, unsafe requested labels, duplicate candidate labels, missing validation steps, symlink refusal, content non-disclosure, and JSON/text output. CI smoke coverage now exercises installed `forge patch-proposal-manifest --require-ready` with live unchanged patch-intent description evidence. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit/status check
- Follow-up notes: Add a guarded read-only patch proposal review that compares a ready manifest against fresh content-audit evidence before any patch generation or git-diff inspection.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.