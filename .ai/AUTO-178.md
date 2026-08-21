# AUTO-178 — Final preservation advisory provenance

## Objective

Carry the external-validation provenance already preserved through archive manifest, copied-root verification, and package verification into `forge maintenance-preservation-completeness`, so a final preservation reviewer can inspect provenance continuity without reopening lower-level JSON.

## Repository assessment

- `main` started at `a7615982e2e4032e996c6c030ae6e93d144c82b8` (AUTO-177).
- README, roadmap/state/changelog/decisions, policy, preservation/archive source and tests, CI configuration, recent commits, issues, TODO/FIXME/XXX results, all visible branches, and recent PRs were inspected.
- The seven non-main branches are all diverged and substantially behind current `main`; none contains safer or newer work for this milestone.
- Recent PRs are merged, closed, obsolete, or unrelated. No branch/PR integration was warranted.
- AUTO-177 status and workflow-run lookups returned no observable check objects, so this run does not fabricate a green matrix claim.

## Work

- Added a stable final `external_validation_provenance` review to preservation completeness.
- Re-normalized semantics to `externally_supplied_observation`, `executor_validation_equivalent=false`, and `bundle_gate_effect=advisory_only`.
- Added `continuity_verified`, `manifest_matches_copy`, and `manifest_matches_package` so reviewers can see whether the same normalized summary survived each archive boundary.
- Added `preservation_gate_effect=none`; advisory provenance does not change structural preservation completeness.
- Added stable text exposure of provenance presence/status/verification, attachment count, continuity, evidence SHA-256, and fixed semantics.
- Added deterministic tests for verified propagation, attempted promotion normalization, legacy no-provenance compatibility, and cross-layer drift visibility without accidental gating.
- Updated preservation documentation, README status, and autonomous state.

## Validation

- `python -m py_compile` passed for the changed preservation-completeness module and focused AUTO-178 regression test in the available execution environment.
- Full checkout/full pytest remains unavailable because this runtime cannot resolve `github.com`.
- Final pushed-head status should be inspected when observable; no unsupported green-matrix claim is made.

## Safety

The change is read-only and local-first. It adds no new external access, command execution, repository mutation authority, or persistence authority. External validation observations remain advisory and cannot satisfy executor-validation or preservation-completeness gates.

## Next

If final CI is green, evaluate a durable preservation receipt only if it can consume the existing verified completeness artifact and retain its own explicit write confirmation without duplicating lower-level evidence contracts.
