# AUTO-208 — Preserve live-status provenance through push readiness

## Objective

Carry AUTO-207's structured live workflow-status provenance across the next integrated boundary so push-readiness and verified push-handoff evidence retain the collector's bounded-completeness and exact-commit guarantees.

## Repository assessment

Inspected README/docs, relevant push-readiness/status-review/verified-push implementation and tests, repository policy and CI expectations, autonomous roadmap/state/changelog/decisions, recent commits, open issues, all eight visible branches, and recent PR history. The seven non-main branches remain historical/diverged. Recent PRs are merged, closed, obsolete, or unrelated. Open issues #1, #6, and #9 remain broader product/discussion requests rather than blockers.

## Change

`build_push_readiness_data()` now recognizes structured `live_collection_evidence` from commit-status review, normalizes it into `live_status_evidence`, verifies that the requested commit matches the verified commit, enforces the established 1-20 run bound, and requires both bounded-completeness and per-run commit-binding proof. Missing live evidence remains valid for backward-compatible supplied non-live status reviews.

The existing verified push-handoff embeds the push-readiness object, so the same normalized proof remains reviewable through that boundary without adding a duplicate evidence format.

## Validation

Added deterministic AUTO-208 coverage for successful proof retention/text exposure, commit-drift blocking, lost completeness/commit-binding blocking, and supplied non-live compatibility. The changed Python implementation was syntax-compiled before publication. Final GitHub Actions is inspected before completion is claimed.

## Safety

No new external command, network surface, workflow rerun, push authority, force-push/tag-push behavior, remote/protection mutation, or workflow permission was added. This only strengthens evidence continuity and keeps the independent push confirmation boundary intact.

## Branch/PR disposition

Work stayed directly on `main`. No branch or PR was created or merged; no stale branch contained newer applicable implementation work.

## Visuals

None. The lifecycle topology is unchanged; this is an evidence-continuity hardening inside the existing push-readiness/handoff stage.

## Next

If final CI is green, continue the same integrated milestone by carrying this proof into a concise top-level verified-push evidence summary or durable maintenance provenance only where it improves reviewability without duplicating contracts.
