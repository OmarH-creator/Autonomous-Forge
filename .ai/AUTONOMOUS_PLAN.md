# Autonomous Forge Roadmap

## Product vision

Autonomous Forge helps a repository keep a clear improvement plan, choose one safe task, produce reviewable planning artifacts, inspect proposed diffs, review validation status, run tightly scoped validation, apply explicitly confirmed patches, record validation evidence, summarize commit and push readiness, preserve durable evidence bundles, link completed bundles into run history, replay those bundles, hand off preservation guidance, compare completed handoffs, rank ready preservation candidates, prepare integrity-checked archive manifests, write and verify confirmed archive-manifest JSON records, preview archive-copy destinations, copy verified evidence locally with explicit confirmation, verify copied archive roots, preview archive-package metadata, create one confirmed repository-local archive package, verify written archive-package contents, summarize replay policy gates through the installed primary command surface, summarize final preservation completeness, and optionally require matching workflow-status freshness for preserved evidence without requiring uncontrolled autonomous behavior.

## Product scope and non-goals

The first product remains a local Python CLI. It is not a hosted service, deployment system, permission manager, uncontrolled executor, automatic commit bot, force-push bot, branch-protection manager, remote-configuration manager, workflow-rerun bot, polling service, cryptographic identity authority, package-provenance authority, or long-term storage service unless future commands add explicit local contracts for those responsibilities.

## Current architecture

The repository contains a Python package under `src/autonomous_forge`, tests under `tests/`, command docs under `docs/`, workflow checks under `.github/workflows/`, policy under `.forge/`, and durable memory under `.ai`. The installed `forge` entry point routes the historical CLI plus extension commands through `src/autonomous_forge/cli_entry_patch.py`; compatibility console scripts remain available through `pyproject.toml`. CI smoke checks cover both the primary `forge <extension>` routes and the compatibility scripts so release builds do not silently expose commands on only one surface.

## Current implementation status

Roadmap v3 reaches guarded local commit creation, post-commit verification, commit trust review, branch-protection-aware trusted pre-push readiness review, branch-policy-enforcing explicitly confirmed fast-forward-only non-force push handoff, post-push verification, durable maintenance evidence bundles, persisted bundle verification, replay summaries, replay policy summaries on the installed primary route, opt-in run-history links, history-link quality review, strict linked-bundle replay, reviewer-facing maintenance handoffs, comparison-oriented maintenance handoff summaries, deterministic preservation-candidate ranking, integrity-checked archive manifests, confirmed archive-manifest writes, written-manifest verification, guarded archive-copy previews, confirmed local archive-copy execution, post-copy archive-root verification, archive-package metadata previews, confirmed archive-package writing, read-only archive-package verification, read-only preservation-completeness summaries, optional workflow-status freshness gating inside the final preservation-completeness command, direct policy-aware inspection of the repository's current tracked diff relative to `HEAD`, optional post-write target-scoped live-diff verification with rollback for guarded patch application, validation execution gated by that verified post-write diff evidence, commit-readiness aggregation that requires successful verified validation for every retained patch validation step, and explicitly confirmed commit creation that immediately verifies the resulting SHA, summary, and exact changed-path set against that verified readiness evidence. Product commands still do not force-push, push tags, change remotes, change branch protections, enforce a full cryptographic identity policy, rerun workflows, poll remote workflow completion, prove package provenance/signature identity, or prove validation correctness beyond observed local results and supplied/local evidence.

The issue #13 green-baseline recovery milestone is complete. AUTO-141 repaired the importable primary router help-return contract without swallowing parser failures. AUTO-142 then corrected replay-context compatibility, made exact pytest failure identities visible without suppressing CI failures, aligned archive fixtures with generated evidence, repaired maintenance-review handoff context comparison, canonicalized repository-contained archive paths, collapsed semantically duplicate validation steps at the shared validation-plan boundary, restored the primary replay-policy help identity, repaired deterministic multi-bundle comparison fixtures, and fixed preservation ranking so it scores raw retained validation context instead of a lossy summary object. Stale planning/validation/executor assertions were updated to the current enriched safety contract rather than weakening product behavior. GitHub Actions run `31871553378` passed installation, compilation, installed CLI smoke, roadmap lint, and the full 655-test pytest suite on Python 3.10, 3.11, and 3.12.

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
Risks or assumptions: This phase resolved only the router-help contract. The larger context-consistency and stale output-contract clusters remained under issue #13.
Notes: Completed as the first slice of the same green-baseline recovery milestone.

### AUTO-142 — Restore green main baseline, phase 2: replay-context compatibility and fixture recovery
Priority: P0
Status: DONE
Goal: Resolve the remaining deterministic baseline failures without weakening explicit evidence-integrity or mismatch checks.
Why it matters: Feature delivery was paused while `main` was red; restoring a trustworthy supported-version matrix was the release blocker for further product work.
Scope: Correct proven compatibility defects in replay/context handling; compare retained raw history context correctly; canonicalize repository-contained archive paths; deduplicate semantically equivalent validation steps at the shared planning boundary; restore primary replay-policy help identity; make multi-bundle comparison fixtures deterministic and replay-policy-valid; fix preservation ranking to use raw retained validation context; update deterministic assertions to the current safe enriched contract where appropriate; preserve fail-closed behavior for explicit mismatches and malformed evidence.
Expected files or areas: `src/autonomous_forge/validation.py`, maintenance/replay/archive modules touched by AUTO-142, affected tests under `tests/`, README, `.ai` records, issue #13.
Acceptance criteria: Missing optional context is not treated as contradictory evidence; supplied mismatches still block; retained validation-step drift still blocks; malformed or integrity-drifted evidence still blocks; repository/archive containment and overwrite guards remain fail-closed; semantically duplicate validation steps do not create duplicate downstream command candidates; comparison ranking reflects actual retained review context; Python 3.10/3.11/3.12 pytest passes before feature work resumes.
Validation: Completed across replay-context, CI-diagnostic, fixture, handoff-context, archive-path, validation-step, router-help, comparison-ranking, and enriched-contract slices. GitHub Actions run `31871553378` passed installation, source compilation, installed CLI smoke checks, roadmap lint, and the complete 655-test pytest suite on Python 3.10, 3.11, and 3.12.
Risks or assumptions: Direct repository cloning is unavailable from this runtime because outbound DNS to github.com is blocked, so GitHub repository and Actions APIs were used as the source of truth. Compatibility changes did not suppress explicit mismatch, malformed-evidence, hash-integrity, parser-error, containment, overwrite, or side-effect safeguards.
Notes: Issue #13 exit criteria are satisfied. Feature delivery may resume while the supported-version matrix remains green. The next autonomous objective should integrate the already shipped planning, diff-inspection, guarded patch-generation/application, validation, commit-verification, push-handoff, and durable-evidence capabilities into a stronger end-to-end maintenance path rather than add another standalone read-only review command.

### AUTO-143 — Inspect the actual current tracked repository diff
Priority: P1
Status: DONE
Goal: Extend the existing git-diff review surface so maintainers can inspect the repository's real tracked staged and unstaged changes relative to `HEAD` without first exporting a patch file.
Why it matters: The end-to-end maintenance path previously depended on caller-supplied diff evidence. Reading the live tracked diff closes a practical handoff gap between planning/implementation and policy-aware review while remaining local-first and read-only.
Scope: Add a bounded local git-diff capture helper, extend `forge git-diff-review` with mutually exclusive `--current` and `--diff` inputs, preserve the existing policy/path review gates, add deterministic tests, update CLI docs, README status, and project memory.
Expected files or areas: `src/autonomous_forge/repository_git_diff.py`, `src/autonomous_forge/git_diff_review_cli.py`, `tests/test_git_diff_review.py`, `docs/GIT_DIFF_REVIEW.md`, README, and `.ai` records.
Acceptance criteria: `--current` runs exactly `git diff --no-ext-diff --no-textconv HEAD --` with `shell=False` in the configured root; git failures/timeouts/non-UTF-8/oversized output fail closed; tracked diffs pass through the existing policy review; clean tracked state is clear but explicitly warns that untracked files are excluded; supplied `.diff`/`.patch` behavior remains supported; Python 3.10/3.11/3.12 CI remains green.
Validation: GitHub Actions run `31881238816` on the focused regression-test head passed installation, compilation, installed CLI smoke, roadmap lint, and the full pytest suite across Python 3.10, 3.11, and 3.12.
Risks or assumptions: `--current` deliberately excludes untracked files and does not prove correctness or test success. External diff drivers and text conversion are disabled; the command does not apply patches, run validation, call networks, mutate git state, commit, or push.
Notes: Continue this same integration milestone next by feeding live reviewed diff evidence into a guarded patch/validation workflow rather than adding another isolated review command.

### AUTO-144 — Verify the actual tracked diff after guarded patch apply
Priority: P1
Status: DONE
Goal: Connect the existing confirmed patch-apply write to actual post-write tracked-diff evidence and restore the original target content when that evidence cannot be verified.
Why it matters: AUTO-143 made live diff inspection available, but `forge patch-apply` still left post-write review as caller work. A write could therefore remain in the checkout when its actual tracked delta could not be verified against policy.
Scope: Add safe target-scoped live-diff capture, opt-in `--verify-live-diff` and `--policy` support on `forge patch-apply`, policy-aware exact-one-target post-write verification, rollback on verification failure, deterministic tests, command documentation, README status, and project-memory updates.
Expected files or areas: `src/autonomous_forge/repository_git_diff.py`, `src/autonomous_forge/patch_apply.py`, `src/autonomous_forge/patch_apply_cli.py`, `tests/test_patch_apply.py`, `docs/PATCH_APPLY.md`, README, and `.ai` records.
Acceptance criteria: Missing confirmation still prevents writes; verified mode runs bounded `git diff --no-ext-diff --no-textconv HEAD -- <validated-target>` with `shell=False`; a clear policy-allowed diff containing exactly one changed file and exactly the requested target succeeds; git, decoding, bounds, parsing, policy, file-count, or target-identity failures restore the original target and fail closed; no validation, commit, push, remote, workflow-rerun, or branch-protection authority is added; Python 3.10/3.11/3.12 CI remains green.
Validation: GitHub Actions run `31891899123` on implementation/test head `5c726ae297ddd3f524eb547512f60cb4a8985153` passed package installation, source compilation, installed CLI smoke, roadmap lint, and pytest across Python 3.10, 3.11, and 3.12.
Risks or assumptions: Verification covers only the requested tracked target and deliberately excludes untracked files. It does not run tests or prove correctness. Rollback restores the exact original UTF-8 target text captured before the write.
Notes: Continue the same integration milestone next by carrying verified apply evidence into the existing validation execution/result handoff and then commit verification, instead of adding another isolated audit command.

### AUTO-145 — Gate validation execution on verified live-diff patch evidence
Priority: P1
Status: DONE
Goal: Connect AUTO-144 verified guarded patch evidence to the existing narrow validation executor so an observed validation result can be tied to the actual policy-reviewed target diff that was written.
Why it matters: Before this slice, `executor-run` could execute an approved validation command but had no evidence that the command belonged to a patch whose actual post-write diff had been verified. That left a caller-reconstructed handoff in the end-to-end workflow.
Scope: Add `forge verified-validation-run`, require repository-local live-diff-verified patch-apply evidence, preserve the existing executor contract and confirmation gate, add deterministic tests, command docs, installed CLI smoke coverage, README status, and `.ai` records.
Expected files or areas: `src/autonomous_forge/verified_validation_run.py`, `src/autonomous_forge/verified_validation_run_cli.py`, `src/autonomous_forge/cli_entry_patch.py`, `tests/test_verified_validation_run.py`, `docs/VERIFIED_VALIDATION_RUN.md`, `.github/workflows/test.yml`, README, and `.ai` records.
Acceptance criteria: Invalid, external, symlinked, oversized, unverified, attention-requiring, multi-file, or target-mismatched patch evidence blocks before subprocess creation; the requested command must be retained by the patch evidence and remain an exact executor-contract candidate; `--confirm-executor-dry-run`, timeout bounds, and `shell=False` execution remain in force; successful execution keeps persistence explicit rather than automatic; primary installed help routing and the supported Python matrix remain green.
Validation: Deterministic tests cover successful exact shell-free execution, refusal before runner creation when live-diff proof is absent, rejection of a command not retained by patch validation steps, preservation of the executor confirmation gate, and the primary installed `forge verified-validation-run --help` route. Final GitHub Actions matrix is inspected after the run records are committed.
Risks or assumptions: The integration trusts repository-local Forge JSON evidence and validates one exact command at a time. It does not prove that every relevant validation step has run, automatically persist validation history, create commits, push, poll workflows, change remotes, or alter branch protections.
Notes: Continue this same milestone by carrying successful verified-validation evidence into commit-readiness/commit verification, then push handoff and durable evidence, without adding another isolated audit command.

### AUTO-146 — Require complete verified validation coverage before commit readiness
Priority: P1
Status: DONE
Goal: Carry the AUTO-144/145 patch and observed-validation evidence chain directly into commit readiness without caller-reconstructed post-apply or diff JSON.
Why it matters: AUTO-145 tied one observed validation command to a verified target diff, but commit readiness still required separately reconstructed post-apply and diff evidence and did not aggregate multiple verified validation runs into complete coverage of the patch's retained validation plan.
Scope: Add `forge verified-commit-readiness`, consume one verified guarded patch record plus one or more successful verified-validation records and one commit-status review, require every retained patch validation step to have passed, reuse the embedded live-diff review and existing commit-readiness status gates, add deterministic tests, CLI documentation, README status, and `.ai` records.
Expected files or areas: `src/autonomous_forge/verified_commit_readiness.py`, `src/autonomous_forge/verified_commit_readiness_cli.py`, `src/autonomous_forge/cli_entry_patch.py`, `tests/test_verified_commit_readiness.py`, `docs/VERIFIED_COMMIT_READINESS.md`, README, and `.ai` records.
Acceptance criteria: Evidence must be repository-local bounded UTF-8 JSON; patch apply must show an applied file change, closed patch authority, and verified live diff; every successful validation run must bind to the same target and patch evidence and request a retained validation step; missing required validation steps keep readiness blocked; target/source contradictions fail closed; the existing final diff and status checks remain in force; the command never stages, commits, pushes, polls workflows, changes remotes, force-pushes, or alters protections; supported Python CI remains green.
Validation: Deterministic tests cover complete multi-step readiness, missing-step blocking, strict CLI failure when coverage is incomplete, target mismatch refusal, and primary installed help routing. Final GitHub Actions matrix is inspected after the documentation/state commits land.
Risks or assumptions: The command trusts repository-local Forge JSON evidence and observed return codes; it proves that every retained validation step has one successful verified run but not that those commands are sufficient for correctness. Commit creation and post-commit verification remain separate confirmation-gated stages.
Notes: Continue this same milestone by carrying a ready verified-commit-readiness artifact into commit creation and post-commit verification, then into push handoff and durable evidence.

### AUTO-147 — Create and immediately verify one commit from ready verified evidence
Priority: P1
Status: DONE
Goal: Carry ready verified-commit-readiness evidence through one explicitly confirmed local commit and immediate post-commit verification without reconstructing the reviewed patch/validation context.
Why it matters: AUTO-146 proved that the target diff and every retained validation step were ready for commit, but the legacy commit-create path accepted a separately prepared generic proposal and commit verification was a separate handoff. That could break evidence continuity at the first git-history mutation.
Scope: Add `forge verified-commit-create`, bounded repository-local verified-readiness input, reuse the existing commit-metadata preview contract, require explicit confirmation, stage only reviewed paths, create one local commit, immediately verify the resulting SHA, summary, and exact changed-path set, add deterministic tests, command documentation, README status, and `.ai` records.
Expected files or areas: `src/autonomous_forge/verified_commit_create.py`, `src/autonomous_forge/verified_commit_create_cli.py`, `src/autonomous_forge/cli_entry_patch.py`, `tests/test_verified_commit_create.py`, `docs/VERIFIED_COMMIT_CREATE.md`, README, and `.ai` records.
Acceptance criteria: Non-ready or contradictory readiness evidence and missing confirmation block before git mutation; staging is scoped only to reviewed paths; a successful commit is immediately checked for safe SHA, reviewed summary, and an exact changed-path match; created commits that fail verification are reported as `created_unverified` and strict continuation exits non-zero; no push, force-push, tag push, remote change, workflow polling, network call, or branch-protection change is added; supported Python CI remains green.
Validation: Actions run `31923545476` on implementation/test/documentation head `5680655b2a2a3edabf3a9acabd3dac0ca6904cb8` passed package installation, source compilation, installed CLI smoke, roadmap lint, and pytest across Python 3.10, 3.11, and 3.12.
Risks or assumptions: The command trusts bounded repository-local verified-readiness JSON and does not prove that the selected validation commands are sufficient. If a commit is created but immediate verification fails, Forge reports the mismatch rather than rewriting history or resetting the commit automatically.
Notes: Continue the same end-to-end milestone by carrying the verified commit-creation report into push readiness, guarded non-force push handoff, post-push verification, and durable maintenance evidence rather than adding another standalone review command.

### AUTO-152 — Prove guarded maintenance workflow end to end
Priority: P1
Status: DONE
Goal: Prove the existing plan → guarded patch → verified validation → commit → push → post-push → durable history chain in one disposable repository.
Why it matters: The individual safety gates were green independently, but the product needed evidence that their contracts compose without losing provenance or bypassing confirmation.
Scope: Add one deterministic temporary-repository integration test using a local bare Git remote; exercise real local Git and write operations while keeping external trust/status/protection evidence deterministic.
Expected files or areas: `tests/test_end_to_end_maintenance_workflow.py`, `README.md`, `.ai/AUTONOMOUS_PLAN.md`, `.ai/AUTONOMOUS_STATE.md`, `.ai/AUTONOMOUS_CHANGELOG.md`, `.ai/DECISIONS.md`.
Acceptance criteria: The test selects AUTO-152 with policy-aware planning, applies and live-diff-verifies one reviewed change, runs its exact validation command, creates and verifies a reviewed commit, performs a non-force push to a disposable remote, verifies post-push reachability, writes a complete canonical maintenance bundle, and links durable run history; all explicit safety confirmations stay required.
Validation: Actions run `31978493467` passed install, compile, installed CLI smoke, roadmap validation, and pytest across Python 3.10, 3.11, and 3.12.
Risks or assumptions: External commit trust, workflow status, and branch-protection evidence are deterministic fixtures; the test does not prove remote GitHub freshness or signer identity.
Notes: Initial CI failure was a test-only assertion against a nonexistent planner key; corrected to the established top-level `expected_file_changes` contract without changing production behavior.

## Future Ideas

- Hash-linked local run reports.
- Optional issue import.
- Policy-aware changed-file summaries.
- Branch protection and workflow-status replay summaries.
- Combined history-link replay handoff.
- Maintenance handoff comparison summaries.
- Evidence provenance/signature review for preserved packages.
- Reviewer checklist for storing or transferring verified preservation packages.
