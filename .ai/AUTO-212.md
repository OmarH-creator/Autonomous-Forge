# AUTO-212 — Verify live-status provenance during linked history review

## Inspection

- Rechecked the blocked AUTO-211 validation first. Actions run `32985057781` for `638aae2befed777827c0c25bd9bf0d2c92b65827` is still queued after two earlier AUTO-211 runs failed at workflow startup before any Python job executed.
- Inspected README/docs/examples, the maintenance history-link reviewer, bundle verification, verified maintenance provenance, focused tests, policy/config/CI, roadmap/state/changelog/decisions, recent commits, all eight visible branches, open issues, and recent PR history.
- Seven non-main branches remain historical/diverged; no stale branch or PR contains newer applicable work.

## Objective

Close the next provenance boundary by making `forge maintenance-history-link-review --verify-linked-bundle` independently verify AUTO-211's compact `live_status_evidence_summary` against the authoritative linked maintenance bundle.

## Changes

- Added linked-bundle verification for the compact live workflow-status summary.
- Recompute and compare the normalized deterministic SHA-256.
- Revalidate `gh run list` source, exact commit binding, 1–20 workflow-run bound, collection completeness, and per-run commit binding in both the history-link summary and linked bundle evidence.
- Block linked replay verification when any present summary disagrees with the linked bundle.
- Preserve legacy links without a live-status summary as backward compatible.
- Expose verification in JSON and stable text output.
- Added focused deterministic regression tests and updated command documentation.

## Validation

- Modified implementation syntax-compiles successfully in the available scratch Python environment.
- Focused AUTO-212 test module syntax-compiles successfully.
- Full local pytest is unavailable because this runtime cannot resolve `github.com` for a checkout.
- Fresh GitHub Actions validation is required before this task is marked DONE; current state remains IN PROGRESS until the matrix is observable.

## Safety

Evidence review only. No new network or subprocess surface, workflow rerun, push authority, force-push/tag-push behavior, remote mutation, branch-protection mutation, or persistence authority was introduced. The durable bundle remains authoritative.

## Branch/PR disposition

Work stayed directly on `main`. No branch or PR was created or merged. Historical non-main branches remain inspect-only evidence.

## Next

Inspect AUTO-212 CI first. Any executable failure takes priority. If green, carry the verified live-status result into higher-level reviewer handoff/comparison output only if it can reuse the same contract without changing readiness/ranking semantics.
