# Autonomous Decisions

## DEC-058 — 2026-07-08 — Assert content-audit semantics in installed CI smoke

Context: `forge content-audit` is now installed and JSON-smoke-tested in CI, but a JSON-only check does not prove that the live repository audit is classifying expected paths as clear, allowed, readable, or attention-free.
Decision: Extend the installed-package workflow smoke step with semantic assertions over `/tmp/autonomous-forge-content-audit.json`, including expected total count, clear counts, `requires_attention=false`, and allowed/readable status for the content-audit module.
Alternatives considered: Leave JSON shape validation only, move the assertions to unit tests only, add a new workflow job, make content-audit a fail-closed gate immediately, inspect git diffs, or generate patches.
Consequences: The content-audit command has stronger CI evidence before future patch-adjacent work depends on it, while the command remains read-only and advisory.
Human decision still required: No.

## DEC-057 — 2026-07-08 — Prefer latest saved evidence in limited run-history audits and smoke-test new content audit

Context: `forge run-history-list` and `forge executor-observation-audit` accept `--max-records`, but the previous implementation applied that limit to the first filename-sorted records. In a growing run-history directory, a small limit could therefore audit old records while omitting the newest saved validation evidence. During the same run, a concurrent content-audit command landed without installed-package workflow smoke coverage.
Decision: Keep deterministic filename ordering, but apply the limit to the newest filename-sorted direct JSON records and display that limited window in ascending filename order. Expose the ordering in run-history-list output and document the audit behavior. Also add CI smoke coverage that runs installed `forge content-audit --format json` against explicit repository paths and validates JSON shape.
Alternatives considered: Keep oldest-first limits, reverse all displayed output, remove `--max-records`, scan recursively, use filesystem modification time, rely only on `run-history-latest`, or defer content-audit smoke coverage until a later semantic assertion pass.
Consequences: Limited run-history and executor-observation audit windows now better match maintainer expectations for recent evidence while preserving stable output and the existing direct-file safety boundary. The new content-audit CLI route is now exercised in GitHub Actions after installation, but semantic output assertions still need a follow-up.
Human decision still required: No.

## DEC-056 — 2026-07-08 — Make executor-observation audit usable as a fail-closed gate

Context: `forge executor-observation-audit` can review aggregate saved executor observations, but before future patch-adjacent work it should also be usable as an explicit process gate rather than only an informational report.
Decision: Add `--require-clear` to `forge executor-observation-audit`. The command still prints the same read-only text or JSON audit, but returns a failing exit code unless the aggregate status is `clear`.
Alternatives considered: Keep the audit informational only, make all non-clear audits fail by default, persist gate decisions to history, poll workflow status, inspect diffs, verify commits, or infer validation success from saved fields.
Consequences: Maintainers and CI can now fail closed on blocked, missing, refused, or needs-review saved executor evidence before future patch or diff workflows rely on it, while the command remains read-only and non-authoritative.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
