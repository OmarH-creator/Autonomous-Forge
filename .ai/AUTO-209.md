# AUTO-209 — Expose live-status provenance on verified push runs

## Inspection

Inspected current `main`, README/docs/examples, verified push orchestration, push readiness, live commit-status review, relevant tests/config/CI, repository policy, `.ai` plan/state/changelog/decisions, recent commits, open issues, all visible branches, and recent PR history. AUTO-208 final head `5b5af577487cb86ba5df764455abb7cc5f57e7be` is green in Actions run 32925219891. The seven non-main branches remain historical/diverged and recent PRs are merged, closed, obsolete, or unrelated; no branch or PR warranted integration.

## Objective

Preserve the already-validated live workflow-status proof as a concise first-class field on the higher-level verified push run, improving end-to-end reviewability without creating another evidence contract or authority path.

## Work

`build_verified_push_run_data()` now promotes normalized `live_status_evidence` from its verified push handoff's push-readiness artifact to the top-level verified-push-run result. The field preserves the source, requested commit, bounded workflow-run limit, collection-completeness proof, and per-run commit-binding proof. Supplied non-live status remains compatible and yields `null`.

Added deterministic coverage for live provenance promotion and non-live compatibility, plus dedicated command documentation. README Current Autonomous Status and autonomous state are updated for this run.

## Safety

No new subprocess type, network surface, workflow rerun, push authority, force-push/tag-push behavior, remote mutation, branch-protection mutation, or secret handling was introduced. Existing push-readiness validation remains the authoritative validator and `--confirm-push` remains an independent authority gate.

## Validation

AUTO-208 baseline is green. AUTO-209 source/test changes are submitted directly to `main`; final Python 3.10/3.11/3.12 CI must be observed before this run is reported complete. No visual update was warranted because lifecycle topology did not change.

## Next

If CI is green, carry the same normalized live-status proof into a compact durable maintenance/history summary, reusing this field rather than introducing parallel evidence semantics.
