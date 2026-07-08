# Autonomous Changelog

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

## 2026-07-08 — AUTO-062

- Task ID: AUTO-062 — Add fail-closed diff-source handoff gate
- Summary: Added `--require-clear` to `forge diff-source-handoff`. The command remains read-only and still emits the same text or JSON comparison evidence, but it now returns exit code `2` when supplied content-audit comparison evidence has added, removed, changed, non-clear, or otherwise attention-required observations.
- Branch and PR assessment: Inspected repository metadata, recent closed/merged PRs, open issues, README, roadmap/state/changelog/decisions, CI workflow, CLI entrypoint, diff-source handoff docs, content-audit behavior, and installed-entrypoint tests. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Deterministic installed-entrypoint tests now cover clear evidence passing with `--require-clear` and changed evidence returning exit code `2`. CI smoke coverage now runs the installed `forge diff-source-handoff --require-clear` command against unchanged live content-audit outputs and validates the JSON evidence.
- Commit hash: pending final commit/status check
- Follow-up notes: Add a guarded read-only patch-intent or git-diff review surface that consumes clear content-audit and diff-source evidence without generating or applying patches automatically.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.
