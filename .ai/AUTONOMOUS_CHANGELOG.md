# Autonomous Changelog

## 2026-07-08 — AUTO-062

- Task ID: AUTO-062 — Add fail-closed diff-source handoff gate
- Summary: Added `--require-clear` to `forge diff-source-handoff`. The command remains read-only and still emits the same text or JSON comparison evidence, but it now returns exit code `2` when supplied content-audit comparison evidence has added, removed, changed, non-clear, or otherwise attention-required observations.
- Branch and PR assessment: Inspected repository metadata, recent closed/merged PRs, open issues, README, roadmap/state/changelog/decisions, CI workflow, CLI entrypoint, diff-source handoff docs, content-audit behavior, and installed-entrypoint tests. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Deterministic installed-entrypoint tests now cover clear evidence passing with `--require-clear` and changed evidence returning exit code `2`. CI smoke coverage now runs the installed `forge diff-source-handoff --require-clear` command against unchanged live content-audit outputs and validates the JSON evidence.
- Commit hash: pending final commit/status check
- Follow-up notes: Add a guarded read-only patch-intent or git-diff review surface that consumes clear content-audit and diff-source evidence without generating or applying patches automatically.

## 2026-07-08 — AUTO-061

- Task ID: AUTO-061 — Add diff-source handoff comparison
- Summary: Added `forge diff-source-handoff`, a read-only comparison command for two explicit `content-audit` JSON outputs. The handoff verifies content-audit payloads, constrains JSON inputs under the configured root, reports added/removed/changed/unchanged audited paths, highlights changed observation fields, and provides a conservative `requires_attention` gate before future patch-generation or diff-review work relies on content-audit evidence.
- Branch and PR assessment: Inspected repository metadata, recent commits, branch search, recent closed/merged PRs, README, roadmap/state/changelog/decisions, CI workflow, content-audit implementation, CLI entrypoint wiring, and related tests. Recent PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Deterministic tests were added for unchanged, changed, added, removed, blocked-after, JSON/text, malformed payload, duplicate path, symlink refusal, and outside-root refusal cases. Installed-entrypoint tests and CI smoke assertions were added for `forge diff-source-handoff`. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: 4124f7aa5a7c990154f24ad3902044f318d14231
- Follow-up notes: Add a guarded patch-intent or git-diff review surface that consumes content-audit and diff-source handoff evidence without generating or applying patches automatically.

## 2026-07-08 — AUTO-060

- Task ID: AUTO-060 — Cover installed content-audit entrypoint behavior
- Summary: Added deterministic regression coverage for the installed CLI entrypoint path that exposes `forge content-audit`. The new tests exercise JSON success through `autonomous_forge.cli_entry.main` and missing-policy refusal so the package script route used by GitHub Actions remains protected.
- Branch and PR assessment: Inspected repository metadata, recent commits, branch search, closed/merged PRs, README, roadmap/state/changelog/decisions, workflow smoke coverage, content-audit implementation, base CLI wiring, installed entrypoint wiring, and existing CLI/content-audit tests. Older PRs are closed, merged, or obsolete; no open PR required integration in this run.
- Validation completed: Static review completed through the GitHub repository API. Regression tests were committed for installed-entrypoint content-audit JSON output and missing-policy refusal. Direct local checkout/test execution remained unavailable in this environment.
- Commit hash: 55e62c6be4d7bd357ecbb598ebd56145fa7aace7
- Follow-up notes: Add a diff-source handoff that can compare explicit content-audit outputs before patch generation.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.
