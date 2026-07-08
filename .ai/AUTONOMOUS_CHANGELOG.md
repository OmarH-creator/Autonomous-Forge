# Autonomous Changelog

## 2026-07-08 — AUTO-065

- Task ID: AUTO-065 — Add patch-intent description artifact
- Summary: Added `forge patch-intent-describe`, a read-only artifact that consumes reviewed `patch-intent-review` JSON and reports `described` only when the supplied evidence is ready, allows patch intent, contains compared paths, and has no blockers. The command supports `--require-described`, returning exit code `2` for blocked evidence while leaving files unchanged.
- Branch and PR assessment: Inspected repository metadata, recent PRs, open issues, README, roadmap/state/changelog/decisions, CI workflow, patch-intent review implementation, CLI entrypoint, and related tests. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Deterministic tests cover described evidence, blocked evidence, text/JSON output, content non-disclosure, bad payloads, unsafe paths, symlinks, and installed-entrypoint `--require-described` pass/fail behavior. CI smoke coverage now exercises installed `forge patch-intent-describe --require-described` with clear live patch-intent review evidence. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit/status check
- Follow-up notes: Add an explicit read-only patch-proposal description surface that accepts a concrete change objective and reviewed patch-intent description evidence without generating or applying patches automatically.

## 2026-07-08 — AUTO-064

- Task ID: AUTO-064 — Add patch-intent review gate
- Summary: Added `forge patch-intent-review`, a read-only gate that consumes reviewed `diff-source-handoff` JSON and reports `ready` only when the supplied evidence is unchanged, clear, and attention-free. The command supports `--require-ready`, returning exit code `2` for blocked evidence while leaving files unchanged.
- Branch and PR assessment: Inspected repository metadata, recent commits, closed/merged PRs, README, roadmap/state/changelog/decisions, CI workflow, diff-source handoff implementation, CLI entrypoint, and related tests. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Deterministic tests cover ready evidence, changed evidence, non-clear after-review evidence, text/JSON output, bad payloads, unsafe paths, symlinks, and installed-entrypoint `--require-ready` pass/fail behavior. CI smoke coverage now exercises installed `forge patch-intent-review --require-ready` with clear live diff-source evidence. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit/status check
- Follow-up notes: Add a read-only patch-intent description artifact that consumes ready patch-intent review evidence without generating or applying patches automatically.

## 2026-07-08 — AUTO-063

- Task ID: AUTO-063 — Restore changed-content CLI entrypoints
- Summary: Restored the installed `forge content-audit` and `forge diff-source-handoff` command routing in `src/autonomous_forge/cli.py`. This fixes a CI-risk mismatch where `.github/workflows/test.yml` invoked changed-content audit commands that were implemented in modules but not exposed through the current CLI parser.
- Branch and PR assessment: Inspected repository metadata, recent commits, README, state, changelog, CI workflow, CLI command routing, content-audit implementation, diff-source handoff implementation, and CLI tests. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Added deterministic CLI regression tests for `content-audit` JSON output without leaking audited file content, `diff-source-handoff --require-clear` passing on unchanged clear evidence, and `diff-source-handoff --require-clear` returning exit code `2` on changed evidence. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: pending final commit/status check
- Follow-up notes: Add a lightweight parser/CI command registry test that asserts every command named by the smoke workflow is present in the installed parser before CI reaches command execution.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.
