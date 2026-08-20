# AUTO-174 — Verify compact external validation provenance during linked history replay

## Objective
Teach the existing maintenance history-link replay surface to validate AUTO-173's compact advisory validation provenance against the actual linked bundle, without adding a new standalone review command or promoting external observations to executor proof.

## Repository assessment
Inspected README/docs/examples, relevant source/tests/config/CI, `.forge/policy.md`, autonomous plan/state/changelog/decisions, recent commits, open issues, TODO/FIXME/XXX search, all visible branches, and PR history. Historical feature/maintenance branches remain stale or superseded. Reviewed PRs are merged, closed, obsolete, or unrelated; none warranted integration. Work remained directly on `main`.

## Change
`forge maintenance-history-link-review --verify-linked-bundle` now recomputes deterministic SHA-256 for the linked bundle's complete `external_validation_evidence` block when the history link contains `external_validation_evidence_summary`. It also checks source-record label, attachment count, provenance semantics, executor-equivalence flag, and advisory gate effect. The verification result is exposed in both JSON and text linked-replay output.

## Safety rationale
A present summary that disagrees with the linked bundle blocks linked replay and therefore fails `--require-linked-replayable`. External evidence must remain `externally_supplied_observation`, `executor_validation_equivalent: false`, and `bundle_gate_effect: advisory_only`. The path remains read-only and grants no apply, validation, commit, push, fetch, workflow, remote, or branch-protection authority.

## Backward compatibility
Links created before compact summaries existed remain usable. Absence of `external_validation_evidence_summary` is reported as `status: not_present` and does not by itself block an otherwise valid linked replay, even if the linked bundle contains external advisory evidence.

## Validation
Added deterministic tests for successful hash-bound verification, tampered summary SHA refusal, attempted executor-proof promotion refusal, and legacy-link compatibility. Direct full-checkout pytest could not run because the execution environment cannot resolve `github.com`; no green matrix result is fabricated when current GitHub check/run evidence is unavailable.

## Documentation and visuals
Added dedicated maintenance-history provenance verification documentation and updated README Current Autonomous Status. No new visual was warranted because this strengthens an existing verification edge rather than changing the lifecycle architecture.

## Limitations
SHA-256 proves consistency with the linked bundle bytes but not signer identity. Legacy links can legitimately lack the newer compact summary; consumers must treat that absence as visible compatibility state, not verified compact provenance.

## Next action
If CI is green, carry the verified advisory-provenance result into maintenance review handoff/comparison output so reviewers can preserve it without reopening low-level linked replay JSON.