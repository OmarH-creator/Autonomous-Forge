# Autonomous Changelog

## 2026-08-15 — AUTO-142

- Task ID: AUTO-142 — Restore green main baseline, phase 2: partial replay-context compatibility
- Summary: Fixed a concrete replay consistency defect so retained validation context that omits optional `expected_file_changes` is not treated as contradictory path evidence. Explicit expected-change mismatches and retained validation-step mismatches still fail closed. Added deterministic regression coverage for the compatible partial-context case.
- Branch and PR assessment: Inspected README, roadmap/state/changelog/decisions, current source/tests, GitHub Actions, issue #13, all visible branches, and PR history. Work stayed directly on `main`; historical branches are stale or superseded and no PR required integration.
- Validation completed: Local three-case logic probe passed for partial compatible context, explicit reviewed-path mismatch, and validation-step mismatch. GitHub Actions for commit `9fd663f71ea3058654dc476141980b66ae82a063` completed with the repository-wide pytest step still failing across the matrix, so the baseline is not claimed green. Full diff review from pre-run head showed only the replay-summary logic, focused regression test, and run-state changes before README/changelog bookkeeping.
- Commits: `0f9af30bfa58d8967c5bf9de24a2cfd57da052a4`, `9fd663f71ea3058654dc476141980b66ae82a063`, `6f2e4ce0c41cbf52b7a13b65570460e9e29ce48f`, `6359e1a8086145bfe6ba1a7ae481f23608bc426b`.
- Follow-up notes: Continue issue #13 against the next observed deterministic compatibility/fixture cluster. Do not resume feature work until Python 3.10, 3.11, and 3.12 are green.

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

## 2026-07-10 — AUTO-139

- Task ID: AUTO-139 — Preservation workflow-status freshness gate
- Summary: Extended `forge maintenance-preservation-completeness` and `forge-maintenance-preservation-completeness` with optional `--status-evidence` and `--require-workflow-fresh` support. The final preservation gate can now require successful supplied workflow/status JSON whose commit SHA matches the archive manifest commit.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent commits, recent PRs, open issues, branch search, preservation-completeness implementation, focused tests, docs, and workflow smoke coverage. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; branch search returned no open branch work requiring integration.
- Validation completed: Static source/test/docs/workflow review completed through the GitHub repository API. Local scratch syntax compilation passed for the changed preservation-completeness core, CLI module, and focused test file. Added deterministic coverage for matching workflow status, stale workflow status, required-missing workflow evidence, and CLI strict workflow freshness. Direct full checkout/full pytest execution remained unavailable from this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a reviewer checklist or provenance/signature review for storing or transferring verified preservation packages.

## 2026-07-10 — AUTO-138

- Task ID: AUTO-138 — Maintenance preservation completeness summary
- Summary: Added `forge maintenance-preservation-completeness` and `forge-maintenance-preservation-completeness`, a read-only final review command that combines written archive-manifest verification, copied archive-root verification, and archive-package verification into one `complete` or `blocked` preservation status.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent commits, recent PRs, branch search, archive manifest/copy/package verification implementation, focused tests, docs, package scripts, and workflow smoke coverage. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; branch search returned no open branch work requiring integration.
- Validation completed: Static source/test/docs/workflow review completed through the GitHub repository API. Added deterministic coverage for clean completeness, missing package blocking, JSON CLI success, and fail-closed `--require-complete` behavior on package drift. Static review also corrected the package verifier's expected-existing-package blocker so a written package can be verified after package creation. Direct full checkout/full pytest execution remained unavailable in this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a read-only evidence provenance/signature review or workflow-freshness gate if a concrete safe local contract is identified.

## 2026-07-10 — AUTO-137

- Task ID: AUTO-137 — Archive-package verification
- Summary: Added `forge maintenance-archive-package-verify` and `forge-maintenance-archive-package-verify`, a read-only verifier that reopens a written repository-local `.tar.gz`, `.tgz`, `.tar`, or `.zip` archive package and compares entry paths, byte counts, and SHA-256 values against the manifest-backed copied archive root.
- Branch and PR assessment: Inspected repository metadata, README/status, roadmap/state/changelog/decisions, recent PRs, archive package writer/preview implementation, archive copy verification helper tests, package scripts, docs, and workflow smoke coverage. Work stayed directly on `main`. Prior PRs are merged, closed, or obsolete; no open PR or branch required integration.
- Validation completed: Static source/test/docs/workflow review completed through the GitHub repository API. Local scratch syntax compilation passed for the new verifier module, CLI module, and focused test file. Added deterministic coverage for verified `.tar.gz`, verified `.zip`, missing package blocking, drifted package-entry blocking, JSON CLI success, and fail-closed `--require-verified` behavior. Direct full checkout/full pytest execution remained unavailable from this environment.
- Commit hash: pending final commit
- Follow-up notes: Add a preservation-completeness summary that combines manifest verification, copied archive-root verification, and archive-package verification into one final review artifact.

## Historical note

Older autonomous run entries remain available in repository history.