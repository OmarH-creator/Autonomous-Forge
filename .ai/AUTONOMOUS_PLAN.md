# Autonomous Forge Roadmap

## Product vision

Autonomous Forge helps a repository keep a clear improvement plan, choose one safe task, produce reviewable planning artifacts, inspect proposed diffs, review validation status, run tightly scoped validation, apply explicitly confirmed patches, record validation evidence, summarize commit and push readiness, preserve durable evidence bundles, link completed bundles into run history, replay those bundles, hand off preservation guidance, compare completed handoffs, rank ready preservation candidates, prepare integrity-checked archive manifests, write and verify confirmed archive-manifest JSON records, preview archive-copy destinations, copy verified evidence locally with explicit confirmation, verify copied archive roots, preview archive-package metadata, create one confirmed repository-local archive package, verify written archive-package contents, summarize replay policy gates through the installed primary command surface, summarize final preservation completeness, and optionally require matching workflow-status freshness for preserved evidence without requiring uncontrolled autonomous behavior.

## Product scope and non-goals

The first product remains a local Python CLI. It is not a hosted service, deployment system, permission manager, uncontrolled executor, automatic commit bot, force-push bot, branch-protection manager, remote-configuration manager, workflow-rerun bot, polling service, cryptographic identity authority, package-provenance authority, or long-term storage service unless future commands add explicit local contracts for those responsibilities.

## Current architecture

The repository contains a Python package under `src/autonomous_forge`, tests under `tests/`, command docs under `docs/`, workflow checks under `.github/workflows/`, policy under `.forge/`, and durable memory under `.ai`. The installed `forge` entry point routes the historical CLI plus extension commands through `src/autonomous_forge/cli_entry_patch.py`; compatibility console scripts remain available through `pyproject.toml`. CI smoke checks cover both the primary `forge <extension>` routes and the compatibility scripts so release builds do not silently expose commands on only one surface.

## Current implementation status

Roadmap v3 reaches guarded local commit creation, post-commit verification, commit trust review, branch-protection-aware trusted pre-push readiness review, branch-policy-enforcing explicitly confirmed fast-forward-only non-force push handoff, post-push verification, durable maintenance evidence bundles, persisted bundle verification, replay summaries, replay policy summaries on the installed primary route, opt-in run-history links, history-link quality review, strict linked-bundle replay, reviewer-facing maintenance handoffs, comparison-oriented maintenance handoff summaries, deterministic preservation-candidate ranking, integrity-checked archive manifests, confirmed archive-manifest writes, written-manifest verification, guarded archive-copy previews, confirmed local archive-copy execution, post-copy archive-root verification, archive-package metadata previews, confirmed archive-package writing, read-only archive-package verification, read-only preservation-completeness summaries, and optional workflow-status freshness gating inside the final preservation-completeness command. Product commands still do not force-push, push tags, change remotes, change branch protections, enforce a full cryptographic identity policy, rerun workflows, poll remote workflow completion, prove package provenance/signature identity, or prove validation coverage beyond supplied/local evidence.

The immediate roadmap is baseline recovery under issue #13: `main` remains red, so new feature work is paused. AUTO-141 repaired the importable primary router's successful help-return contract without swallowing parser failures. AUTO-142 continues the same P0 milestone by correcting replay-context compatibility, making exact pytest failure identities visible without suppressing CI failures, aligning stale archive fixtures with generated evidence, and repairing maintenance-review handoff so it compares raw retained history-link context against replayed bundle context instead of comparing summary counts as if they were retained values. The post-fix matrix no longer reports the earlier archive-manifest preview/source-report verification failures; remaining archive failures now reach the later archive-copy destination-mapping gate.

## Prioritized roadmap

## Roadmap v1 — Completed foundation through AUTO-004

### AUTO-001 — Local CLI, roadmap parsing, task selection, and dry-run reports through AUTO-004
Priority: P1
Status: DONE
Goal: Establish an installable local CLI that can parse roadmap tasks, select the next eligible item deterministically, and report repository state without changing files.
Why it matters: A stable command surface and deterministic selection are required before planner behavior can be trusted.
Scope: Add package metadata, source layout, task parser, selection logic, README usage, and deterministic tests.
Expected files or areas: `pyproject.toml`, `src/`, `tests/`, README, `.ai` records.
Acceptance criteria: CLI help works, valid task blocks parse, invalid roadmap blocks fail clearly, priority ordering is deterministic, and reports remain read-only.
Validation: Deterministic unit and CLI tests were added across the foundation commands.
Risks or assumptions: Python remains the low-overhead local-first implementation language.
Notes: Detailed historical task records remain available in repository history.

## Roadmap v2 — Completed safety and reporting surface through AUTO-017

### AUTO-005 — Policy, linting, inventory, and run-summary previews through AUTO-017
Priority: P1
Status: DONE
Goal: Establish policy parsing, roadmap linting, contributor guidance, command contracts, repository inventory, and run-summary preview behavior.
Why it matters: The product needs a safe local reporting surface before proposing implementation work.
Scope: Keep behavior local-first and read-only while improving repository understanding and durable memory design.
Expected files or areas: `src/autonomous_forge/`, tests, README, docs, `.forge/`.
Acceptance criteria: Implemented commands remain deterministic, documented, and covered by focused tests.
Validation: Deterministic unit and CLI coverage exists across the implemented read-only surfaces.
Risks or assumptions: Do not imply command execution, patch generation, policy enforcement, or automatic history persistence.
Notes: Detailed historical task records remain available in repository history.

## Roadmap v3 — Policy-aware planning toward safe maintenance workflow

### AUTO-018 — Planning, review, history, validation executor, and observation gates through AUTO-138
Priority: P1
Status: DONE
Goal: Advance the workflow from selected task to planning artifacts, validation, patch application, commit/push handoffs, evidence bundles, replay, review handoffs, archive manifests, archive copies, archive packages, package verification, and final preservation completeness.
Why it matters: Maintainers need auditable transitions from planned work to preserved evidence without giving the tool uncontrolled authority.
Scope: Add structured plan output, proposal/validation/executor handoffs, patch apply, commit/push review, durable evidence bundles, run-history links, replay summaries, archive manifests, archive copies, archive packages, package verification, preservation-completeness summaries, compatibility routes, tests, docs, README, CI help smoke, and `.ai` records.
Expected files or areas: `src/autonomous_forge/`, `tests/`, README, docs, `.github/workflows/test.yml`, `pyproject.toml`, `.forge/`, and `.ai` records.
Acceptance criteria: Outputs are deterministic; write-capable commands require explicit confirmation; evidence gates fail closed under strict flags; commands do not force-push, change branch protections, rerun workflows, poll remotes, or prove cryptographic identity.
Validation: Static source/test/docs/workflow review completed through the GitHub repository API with focused tests across affected modules. Direct full checkout/full pytest execution remained unavailable from this environment.
Risks or assumptions: The workflow trusts supplied/local JSON evidence and recomputed hashes unless a command explicitly performs local verification.
Notes: Detailed historical task records remain available in repository history.

### AUTO-139 — Preservation workflow-status freshness gate
Priority: P1
Status: DONE
Goal: Let the final preservation-completeness gate require successful workflow/status evidence for the same commit as the written archive manifest.
Why it matters: A package can be structurally preserved while still lacking a final check that its archived run belongs to fresh successful workflow evidence.
Scope: Extend `forge maintenance-preservation-completeness` and `forge-maintenance-preservation-completeness` with `--status-evidence`, `--require-workflow-fresh`, workflow-status stage gates, focused tests, docs, README usage, and `.ai` records.
Expected files or areas: `src/autonomous_forge/maintenance_preservation_completeness.py`, `src/autonomous_forge/maintenance_preservation_completeness_cli.py`, `tests/test_maintenance_preservation_completeness.py`, `docs/MAINTENANCE_PRESERVATION_COMPLETENESS.md`, README, and `.ai` records.
Acceptance criteria: Optional status evidence remains backward compatible; strict workflow freshness fails closed when evidence is missing, failed, pending, unknown, malformed, outside the repository, or for a different commit; matching successful evidence adds a ready `workflow_status` gate; the command remains read-only.
Validation: Static source/test/docs/workflow review completed through the GitHub repository API. Local scratch syntax compilation passed for the changed core, CLI, and focused tests. Direct full checkout/full pytest execution remained unavailable from this environment.
Risks or assumptions: The gate trusts supplied JSON and does not poll GitHub, rerun workflows, prove signer identity, prove package provenance, or prove validation coverage.
Notes: Completed before any preservation-transfer checklist or provenance/signature review.

### AUTO-140 — Primary replay-policy route and smoke coverage
Priority: P1
Status: DONE
Goal: Ensure `maintenance-replay-policy-summary` is available through the installed primary `forge` command surface, not only through its compatibility script.
Why it matters: A command shipped through `pyproject.toml` but missing from `cli_entry_patch.py` creates a release-surface defect: users following primary `forge <command>` docs cannot reach the command and CI did not catch the route gap.
Scope: Add the router import/mapping, focused route tests, installed CLI smoke coverage for primary and compatibility routes, replay-policy docs, README, and `.ai` records.
Expected files or areas: `src/autonomous_forge/cli_entry_patch.py`, `tests/test_cli_entry_patch.py`, `.github/workflows/test.yml`, `docs/MAINTENANCE_REPLAY_POLICY_SUMMARY.md`, README, and `.ai` records.
Acceptance criteria: `forge maintenance-replay-policy-summary --help` exits successfully; `forge-maintenance-replay-policy-summary --help` remains covered; route tests exercise the primary router; the fix introduces no new write behavior.
Validation: Static source/test/docs/workflow review completed through the GitHub repository API. Local scratch syntax compilation passed for the changed router and focused router test file. Direct full checkout/full pytest execution remained unavailable from this environment.
Risks or assumptions: This is a concrete release-surface blocker fix, not a new standalone command; CI status may lag the pushed commits.
Notes: Completed before adding any preservation-transfer checklist or provenance/signature review.

### AUTO-141 — Restore green main baseline, phase 1: router help contract
Priority: P0
Status: DONE
Goal: Repair the concrete router-help failures on red `main` before any new feature work.
Why it matters: The project must stop feature delivery while the baseline is red. Two known failures came from successful argparse help exits escaping the importable primary router as `SystemExit(0)` instead of its numeric return-code contract.
Scope: Normalize only successful extension `SystemExit` values at `cli_entry_patch.py`, preserve non-zero parser failures, add deterministic regression coverage, record the repair in project memory, and verify CI when available.
Expected files or areas: `src/autonomous_forge/cli_entry_patch.py`, `tests/test_cli_entry_patch.py`, README, `.ai` records, issue #13.
Acceptance criteria: Existing extension help tests return `0`; invalid extension arguments still raise non-zero `SystemExit`; no safety gate or side-effect boundary changes; full CI is inspected after the change.
Validation: Product diff committed on `main`; subsequent CI advanced through install, compile, CLI smoke, and roadmap validation before the repository-wide pytest step remained red, confirming the broader baseline recovery still had work remaining.
Risks or assumptions: This phase resolved only the router-help contract. The larger context-consistency and stale output-contract clusters remain under issue #13.
Notes: Completed as the first slice of the same green-baseline recovery milestone.

### AUTO-142 — Restore green main baseline, phase 2: replay-context compatibility and fixture recovery
Priority: P0
Status: TODO
Goal: Resolve the maintenance/archive/replay context-consistency failure cluster without weakening explicit evidence-integrity or mismatch checks.
Why it matters: `main` remains red, and the largest historical failure group comes from newer context-consistency semantics interacting with older partial evidence fixtures and one proven internal summary/raw-context mismatch. Feature delivery must remain paused until the baseline is green.
Scope: Correct proven compatibility defects in replay/context handling; ensure maintenance-review handoff compares raw retained history evidence with replayed bundle context rather than summary counts; update deterministic fixtures or assertions to the current safe contract where appropriate; preserve fail-closed behavior for explicit mismatches and malformed evidence; continue the same milestone across maintenance/archive/replay tests until the cluster is exhausted; and keep CI diagnostics actionable enough to identify exact failing test node IDs without weakening the suite.
Expected files or areas: `src/autonomous_forge/maintenance_replay_summary.py`, `src/autonomous_forge/maintenance_review_handoff.py`, maintenance/archive/replay tests under `tests/`, `.github/workflows/test.yml`, README, `.ai` records, issue #13.
Acceptance criteria: Missing optional context is not treated as contradictory evidence; supplied expected-change context must still cover reviewed paths; handoff context consistency compares retained values rather than summary counts; retained validation-step drift still blocks; malformed or integrity-drifted evidence still blocks; remaining context-contract failures are repaired without weakening safety; failed pytest runs expose actionable failing-test identities while preserving pytest's exit status; full Python 3.10/3.11/3.12 pytest matrix ultimately passes before feature work resumes.
Validation: The first AUTO-142 slice added a deterministic partial-context regression case and preserved existing explicit path-mismatch and validation-step-mismatch tests. GitHub Actions run `31841541663` passed install, compile, CLI smoke, and roadmap lint but failed at pytest across Python 3.10, 3.11, and 3.12. Commit `80efd9c4423cc7208891533a0c55ddc4ec0fb657` added failure-name annotations without changing pytest's exit status. Those annotations exposed the archive cluster. Fixture commits `f01a9c7f2d83f7d6c6a5673cfdaac926d0842713` and `9f30db304460e6f2f1466ad8efbdec8659e07eba` aligned source-report metadata and expected-change text with generated evidence. Commit `f03aed1c34285c041f02afa236898090ad8d9022` repaired the handoff summary/raw-context defect; its three-version matrix still failed pytest, but the prior archive-manifest preview/source-report failures and several upstream archive-copy failures disappeared, proving the repaired gate now advances to later archive-copy destination checks.
Risks or assumptions: Direct repository cloning is unavailable from this runtime because outbound DNS to github.com is blocked. The CI diagnostic wrapper relies on pytest's standard `FAILED ` summary lines and caps the annotation at 80 entries; if no such summary is produced, the job still fails with a generic diagnostic annotation. Compatibility changes must never suppress explicit mismatch, malformed-evidence, hash-integrity, parser-error, or side-effect safeguards. The next archive-copy repair must distinguish source paths from destination paths without permitting overwrite or repository-root escape.
Notes: Continue this same P0 milestone across subsequent autonomous runs until `main` is green or a concrete external blocker prevents further repair.

## Future Ideas

- Hash-linked local run reports.
- Optional issue import.
- Policy-aware changed-file summaries.
- Branch protection and workflow-status replay summaries.
- Combined history-link replay handoff.
- Maintenance handoff comparison summaries.
- Evidence provenance/signature review for preserved packages.
- Reviewer checklist for storing or transferring verified preservation packages.
