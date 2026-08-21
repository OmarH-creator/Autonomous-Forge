# AUTO-181 — Surface preservation receipts in reviewer comparison

## Objective

Carry AUTO-180's bounded immutable preservation-receipt discovery into the existing `maintenance-review-compare` surface without creating a new command or making receipt state a preservation/ranking gate.

## Inspection

Inspected README/docs/examples, preservation/reviewer source and tests, `.forge/policy.md`, Python 3.10/3.11/3.12 CI, `.ai` state/plan/changelog/decisions, recent commits, open issues/TODO surface, all eight visible branches, and recent PR history. The seven non-main branches are historical/diverged and no reviewed PR contains newer relevant work.

## Change

- Added repeatable `--completeness` to `forge maintenance-review-compare`.
- Reused `build_maintenance_preservation_receipt_data` plus `discover_maintenance_preservation_receipts`; no duplicate receipt contract was created.
- Matched receipt reviews to handoffs/candidates by commit SHA, remote, and branch.
- Exposed compact receipt status/counts in handoffs, preservation candidates, aggregate comparison output, and stable text output.
- Kept receipt state out of `_handoff_score` and `_candidate_sort_key`; verified, absent, or damaged receipts cannot change comparison readiness or preservation ranking.
- Added deterministic tests for ranking independence, invalid-receipt advisory behavior, and repeatable CLI inputs.

## Validation

- Proposed core, CLI, and focused test syntax-compiled successfully in the available scratch environment.
- A focused executable smoke with stubbed repository evidence proved that a lower-ranked candidate can have a verified receipt while the stronger candidate remains selected, demonstrating receipt status does not affect ranking.
- Full repository checkout/pytest is unavailable because this runtime cannot resolve `github.com` directly. The connected workflow/status surface exposed no AUTO-180 run objects at inspection time, so no unsupported green-matrix claim is made.

## Safety and limitations

Receipt review remains `informational_only`, `receipt_required_for_preservation=false`, and `affects_preservation_ranking=false`. Supplied completeness artifacts must pass the existing completeness/receipt contract. The command remains read-only and adds no network, command execution, Git write, workflow, overwrite, force-push, or protection authority.

## Next

Inspect AUTO-181 CI when observable. If green, continue the same preservation-review milestone only where a concrete reviewer gap remains; do not create a parallel receipt evidence contract.