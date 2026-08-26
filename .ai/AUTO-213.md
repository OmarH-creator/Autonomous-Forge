# AUTO-213 — Surface verified live-status provenance in reviewer handoff/comparison

## Objective

Carry AUTO-212's already-verified linked live workflow-status proof into higher-level maintenance review surfaces without adding a new evidence contract, readiness gate, or preservation-ranking signal.

## Repository assessment

- `main` remained the single source of truth.
- AUTO-212 final head `bbccd52a61e5f1ec6fddfede51fc1672b69c5a5d` passed GitHub Actions run `33003816024`.
- README/docs/examples, relevant source/tests/config/CI, roadmap/state/changelog/decisions, recent commits, open issues, all eight visible branches, and recent PR history were inspected.
- The seven non-main branches remain historical/diverged. Recent PRs are merged, closed, obsolete, or unrelated; no integration was warranted.

## Change

- `maintenance-review-handoff` now exposes `live_status_provenance` derived only from the linked-bundle review's `live_status_evidence_summary_verification` result.
- The handoff exposes source, requested commit, workflow-run limit, collection completeness, per-run commit binding, evidence SHA-256, and verification status.
- The handoff field is explicitly `review_effect=informational_only` and `affects_handoff_readiness=false`; underlying linked-bundle verification remains authoritative.
- `maintenance-review-compare` carries the same normalized field into handoff rows and preservation candidates and reports `verified_live_status_count`.
- `_handoff_score()` was intentionally left unchanged, and the comparison field declares `affects_preservation_ranking=false`.

## Validation

Deterministic AUTO-213 tests cover:

- verified live-status propagation into a ready handoff;
- stable text rendering of bounded completeness and exact-commit binding;
- propagation into comparison rows and preservation candidates; and
- preservation-score independence from live-status presence/verification.

Fresh GitHub Actions validation is required before this task can be marked DONE.

## Safety and limitations

This slice adds no network or subprocess capability, workflow rerun, push authority, force-push/tag-push behavior, remote mutation, branch-protection mutation, or persistence authority. It surfaces evidence already verified by the linked-bundle review. Legacy/non-live history remains compatible and receives no synthetic proof.

The linked durable bundle and linked-bundle reviewer remain authoritative. This provenance shows which workflow evidence was collected and bound to the commit; it does not prove those workflows are sufficient for correctness. Commit trust and branch protection remain caller-supplied.

## Next action

Inspect AUTO-213 CI first. Any executable failure takes priority. If green, carry the normalized live-status proof only into the next preservation-facing surface where it materially improves reviewability without changing readiness or ranking semantics.
