# Autonomous Changelog

## 2026-08-15 — AUTO-141

- Task ID: AUTO-141 — Restore router help contract on red main
- Summary: Fixed the importable primary `forge` router so successful argparse help exits from extension commands normalize to return code `0`, while non-zero parser exits still propagate. Added regression coverage for the non-zero case.
- Branch and PR assessment: Inspected README, roadmap/state/changelog/decisions, recent commits, open issues, all visible branches, PR history, router source, focused tests, and current commit status. Stayed directly on `main`; no stale branch or PR contained work that should be merged for this defect.
- Validation completed: Reviewed the complete committed diff from pre-run main; only `src/autonomous_forge/cli_entry_patch.py` and `tests/test_cli_entry_patch.py` changed in the product slice. The router change is limited to extension dispatch semantics. Fresh GitHub status checks were not yet visible at inspection time.
- Commits: `e2184b2b87592fbc98a85712e42e3865d49944a8`, `2bbe729b21f3d6555f43d50adcc0b46ad4ab4e68`.
- Follow-up notes: Continue issue #13 and repair the remaining red-baseline clusters before any new feature work.

## 2026-07-10 — AUTO-140

- Task ID: AUTO-140 — Primary replay-policy route and smoke coverage
- Summary: Fixed a release-surface blocker by routing `forge maintenance-replay-policy-summary` through the installed primary `forge` entry point while preserving the existing `forge-maintenance-replay-policy-summary` compatibility script.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent commits, recent PRs, open issues, router implementation, replay-policy CLI, focused tests, docs, and workflow smoke coverage. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; no open PR or branch required integration.
- Validation completed: Static source/test/docs/workflow review completed through the GitHub repository API. Added focused router help coverage and CI smoke coverage for both primary and compatibility replay-policy summary routes. Local scratch syntax compilation passed for the changed router and focused router test file. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a reviewer checklist or provenance/signature review for storing or transferring verified preservation packages.

## Historical note

Older autonomous run entries remain available in repository history.
