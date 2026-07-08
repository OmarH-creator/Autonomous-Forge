# Autonomous Changelog

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

## 2026-07-08 — AUTO-059

- Task ID: AUTO-059 — Harden planned file-area parsing for hidden policy paths
- Summary: Integrated the useful blocker fix from open PR #7 directly onto `main`. `_split_expected_areas` now iteratively peels surrounding backticks and trailing sentence/list punctuation so hidden dotfile paths such as `.env` remain exact in planned-file area output when roadmap text uses patterns like ``.env`.`` or ``.env`,``.
- Branch and PR assessment: Inspected repository metadata, recent commits, branches, open/closed PRs, open issues, README, roadmap/state/changelog/decisions, proposal parsing code, and dotfile tests. PR #7 contained relevant validated work for a concrete failing test; its patch was integrated directly on `main` per the main-only workflow. PR #8 remains open and unintegrated because this run focused on the active failing parser blocker. Older PRs are closed, merged, or obsolete.
- Validation completed: Static review completed through the GitHub repository API. Regression tests now cover the existing hidden-dotfile sentence-punctuation case and a trailing-comma roadmap token. Direct local pytest execution remained unavailable in this environment.
- Commit hash: pending final commit/status check
- Follow-up notes: Close PR #7 as obsolete after confirming the mainline fix is recorded; add a diff-source handoff that can compare explicit content-audit outputs before patch generation.

## Historical note

Older autonomous run entries remain available in repository history. This compact changelog prioritizes the latest direct mainline stewardship run so the current state remains easy to review.
