# Autonomous Forge Roadmap

## Product vision

Autonomous Forge helps a repository keep a clear improvement plan, choose one safe task, produce reviewable planning artifacts, inspect proposed diffs, review supplied or live workflow validation status, run tightly scoped local validation, preview guarded patch text, explicitly apply one confirmed replacement, record post-apply validation evidence, and record what happened.

## Product scope and non-goals

The first product remains a local Python command-line tool. It reads repository files, reports safe next actions, runs only explicitly confirmed allowlisted local validation commands, audits explicit content metadata without printing content, compares supplied audit evidence, reviews supplied unified git diff metadata, reviews supplied commit/workflow status JSON evidence or explicitly collected GitHub workflow-run metadata, summarizes combined change readiness, generates bounded patch previews from explicit replacement content, can explicitly apply one reviewed replacement file after generated preview and change-readiness evidence match the current target, summarizes supplied post-apply validation metadata, and keeps durable project memory.

It is not a hosted platform, dashboard, deployment system, permission-management tool, automatic patch applier, commit bot, or uncontrolled autonomous executor.

## Current architecture

The repository contains a Python package under `src/autonomous_forge`, package metadata in `pyproject.toml`, tests under `tests/`, policy documentation under `docs/`, a visual orientation document at `docs/OVERVIEW.md`, command output contracts and focused command docs under `docs/`, an example policy under `.forge/`, and contributor guidance in `CONTRIBUTING.md`.

The installed `forge` console script routes through `src/autonomous_forge/cli_entry_patch.py`, which exposes primary extension commands and delegates established commands to the base CLI. Compatibility scripts remain available for the newer extension commands.

## Current implementation status

Roadmap v1 established the local CLI, task parsing, deterministic task selection, and dry-run reports. Roadmap v2 added conservative policy parsing, policy-readiness reporting, roadmap linting, command output contracts, run-summary preview output, repository health inventory signals, and a visual project overview. Roadmap v3 has advanced the safe maintenance workflow through planning/proposal artifacts, validation previews, executor gates/contracts/runs, explicit result persistence, content/diff/status/change-readiness review, live workflow-status collection through `gh`, guarded patch previews, one explicitly confirmed patch-apply command, and a post-apply validation handoff.

Product commands still do not execute arbitrary implementation plans, cryptographically verify commits, automatically run validation after patch application, decide commit readiness, or commit changes.

## Technical debt

The CLI can select work, describe policy boundaries, build reviewable plans and proposals, describe validation intent, preview validation command candidates, review explicit paths, audit content metadata, inspect supplied unified git diff metadata, review supplied status evidence or collect GitHub workflow-run metadata through `gh`, combine diff/status evidence into readiness, generate bounded patch previews, apply one explicitly confirmed replacement file after preview/readiness evidence matches current inputs, and summarize explicit post-apply validation metadata.

It does not yet append to a hash-linked long-lived history index, automatically run validation after patch apply, verify commits beyond status evidence, summarize final commit readiness, or execute approved implementation plans. Runtime test execution and main-branch CI observation were unavailable from the automation environment for the latest direct commits.

## Prioritized roadmap

## Roadmap v1 — Completed foundation

### AUTO-001 — Local CLI, roadmap parsing, task selection, and dry-run reports through AUTO-004
Priority: P1-P2
Status: DONE

Goal: Establish an installable local CLI that can parse roadmap tasks, select the next eligible item deterministically, and report repository state without changing files.
Why it matters: A stable command surface and deterministic selection are required before planner behavior can be trusted.
Scope: Add package metadata, source layout, task parser, selection logic, README usage, and deterministic tests.
Expected files or areas: `pyproject.toml`, `src/`, `tests/`, README, `.ai` records.
Acceptance criteria: CLI help works, valid task blocks parse, invalid roadmap blocks fail clearly, priority ordering is deterministic, and reports remain read-only.
Validation: Deterministic unit and CLI tests were added across the foundation commands.
Risks or assumptions: Python remains the low-overhead local-first implementation language.
Notes: Historical detailed task records remain available in repository history.

## Roadmap v2 — Completed safety and reporting surface

### AUTO-005 — Policy, linting, inventory, and run-summary previews through AUTO-017
Priority: P1-P3
Status: DONE

Goal: Establish policy parsing, roadmap linting, contributor guidance, command contracts, repository inventory, and run-summary preview behavior.
Why it matters: The product needs a safe local reporting surface before proposing implementation work.
Scope: Keep behavior local-first and read-only while improving repository understanding and durable memory design.
Expected files or areas: `src/autonomous_forge/`, `tests/`, README, `docs/`, `.forge/`.
Acceptance criteria: Implemented commands remain deterministic, documented, and covered by focused tests.
Validation: Added deterministic unit and CLI coverage across the implemented read-only surfaces; PR #4 GitHub Actions passed before JSON run-summary integration.
Risks or assumptions: Do not imply command execution, patch generation, policy enforcement, or automatic history persistence.
Notes: Historical detailed task records remain available in repository history.

## Roadmap v3 — Policy-aware planning toward safe maintenance workflow

### AUTO-018 — Planning, review, history, validation executor, and observation gates through AUTO-056
Priority: P1
Status: DONE

Goal: Advance the safe end-to-end workflow from selected task to review artifacts, local validation execution, guarded result persistence, and saved-observation audits.
Why it matters: Maintainers need machine-readable planning, proposal, validation, command-candidate, path-review, executor, and history evidence before any patch behavior can be considered.
Scope: Add structured plan output, change proposals, validation plans/previews, explicit changed-file reviews, CI smoke checks, combined review artifacts, run-history read/write/list/latest/compare, validation-result preview/write/audit, command-execution handoff, executor gate/contract/dry-run/run, executor-result persistence handoff, guarded handoff persistence, and executor-observation audit with `--require-clear`.
Expected files or areas: `src/autonomous_forge/`, `tests/`, README, `docs/`, `.github/workflows/test.yml`, `.ai` records.
Acceptance criteria: Outputs are deterministic, writes require explicit confirmation, and execution is limited to one exact confirmed no-shell local validation command.
Validation: Deterministic tests and static review were completed through the GitHub repository API. Installed-package CI smoke coverage exercises the current command chain.
Risks or assumptions: These surfaces are advisory except for explicit local validation execution and explicit local persistence.
Notes: Historical detailed task records remain available in repository history.

### AUTO-057 — Content audit and patch-proposal evidence readiness through AUTO-082
Priority: P1
Status: DONE

Goal: Add read-only content-audit checkpoints, compare supplied content-audit outputs, provide fail-closed evidence gates, and carry patch-adjacent evidence through manifest, review, draft, text, provenance, audit, and readiness checkpoints.
Why it matters: Patch-adjacent workflows need a safe bridge between policy-reviewed paths, content metadata, explicit objectives, requested paths, validation steps, reviewed patch summaries, provenance, and installed-route confidence without printing content, generating patches, applying patches, or treating changed evidence as safe by default.
Scope: Add content-audit, diff-source handoff, patch-intent review/description, patch proposal manifest/review/draft, patch text preflight/review, patch application preflight/audit/readiness, compatibility scripts, and CI smoke coverage.
Expected files or areas: `src/autonomous_forge/`, `tests/`, `.github/workflows/test.yml`, README, `docs/`, `.ai` records.
Acceptance criteria: Patch application readiness consumes supplied patch-application preflight and audit JSON, requires ready/clear upstream evidence, verifies matching objective, reviewed paths, validation steps, and blocker-free upstream evidence, keeps `patch_application_allowed` false, and never reads repository file contents, generates patch text, applies patches, runs commands, approves implementation, commits, pushes, or changes files.
Validation: Static source/test/documentation review completed through the GitHub repository API. Deterministic unit/CLI/router tests cover the implemented content-audit and patch-adjacent evidence gates.
Risks or assumptions: Secret-marker checks are guard signals, not complete secret scanning. Ready review evidence does not approve patches, prove correctness, or replace human review.
Notes: Completed before moving into supplied git-diff inspection.

### AUTO-083 — Diff/status review and guarded patch preview through AUTO-087
Priority: P1
Status: DONE

Goal: Move beyond evidence-only review by inspecting supplied diffs, connecting them to supplied validation status, and generating bounded patch preview text only from explicit replacement content and ready upstream evidence.
Why it matters: A safe end-to-end maintenance workflow needs reviewable diff evidence, validation evidence, and generated patch text before any patch applier is designed.
Scope: Add supplied git-diff review, binary/metadata hardening, supplied commit-status review, combined change-readiness, and `forge patch-generation-preview` / `forge-patch-generation-preview`.
Expected files or areas: `src/autonomous_forge/git_diff_review.py`, `src/autonomous_forge/commit_status_review.py`, `src/autonomous_forge/change_readiness.py`, `src/autonomous_forge/patch_generation_preview.py`, `src/autonomous_forge/*_cli.py`, `src/autonomous_forge/cli_entry_patch.py`, `pyproject.toml`, `tests/`, README, `docs/`, and `.ai` records.
Acceptance criteria: Patch-generation preview accepts ready patch-application readiness JSON, requires the target path to be reviewed, reads one explicit replacement text file, produces bounded unified diff preview text, blocks identical replacements and simple secret-marker strings, supports `--require-generated`, keeps `patch_application_allowed` false, and never applies patches, runs commands, calls networks, mutates history, commits, pushes, or changes files.
Validation: Static source/test/documentation review completed through the GitHub repository API. Deterministic tests were added for generated previews, blocked upstream evidence, identical text, unreviewed paths, unsafe paths, CLI JSON output, fail-closed generated gating, and secret-marker refusal.
Risks or assumptions: Generated patch previews can expose non-secret repository text by design and rely on simple secret-marker refusal rather than complete secret scanning.
Notes: Completed before moving into confirmed patch application.

### AUTO-088 — Explicitly confirmed guarded patch apply
Priority: P1
Status: DONE

Goal: Add one narrow write-capable command that applies an explicit replacement file only after generated patch preview and change-readiness evidence match the current target.
Why it matters: The workflow needs a real, auditable bridge from generated patch text to a local file change before post-apply validation and commit workflows can be designed.
Scope: Add `forge patch-apply` and `forge-patch-apply`, deterministic core/CLI tests, focused documentation, README usage, and project-memory updates.
Expected files or areas: `src/autonomous_forge/patch_apply.py`, `src/autonomous_forge/patch_apply_cli.py`, `src/autonomous_forge/cli_entry_patch.py`, `pyproject.toml`, `tests/test_patch_apply.py`, `docs/PATCH_APPLY.md`, README, and `.ai` records.
Acceptance criteria: Patch apply requires generated patch-preview JSON, ready change-readiness JSON, a reviewed target path, one explicit replacement file, and `--confirm-apply`; verifies current target content plus replacement exactly reproduce the supplied preview; writes only the target file; reports deterministic text/JSON; blocks stale previews, unsafe paths, unready evidence, missing confirmation, identical replacements, and simple secret-marker strings; and never runs commands, calls networks, mutates saved history, reads environment variables, commits, pushes, or edits unrelated files.
Validation: Static source/test/documentation review completed through the GitHub repository API. Deterministic tests cover confirmed matching apply readiness, missing confirmation, stale preview refusal, blocked change-readiness evidence, unsafe paths, CLI JSON write behavior, and no-confirmation refusal.
Risks or assumptions: This command intentionally changes one local file when explicitly confirmed. It does not prove the change is correct or validated, and it relies on simple secret-marker refusal rather than complete secret scanning.
Notes: Completed before hardening patch-apply exit gating.

### AUTO-089 — Honor patch-apply require-applied exit gating
Priority: P1
Status: DONE

Goal: Fix `forge patch-apply` so producing a blocked report is distinct from fail-closed automation.
Why it matters: The first write-capable command must be predictable for both interactive review and automation. Without this fix, the documented `--require-applied` flag was misleading because all unchanged reports failed.
Scope: Update `patch_apply_cli.py`, focused tests, patch-apply docs, README status, and project-memory records.
Expected files or areas: `src/autonomous_forge/patch_apply_cli.py`, `tests/test_patch_apply.py`, `docs/PATCH_APPLY.md`, README, and `.ai` records.
Acceptance criteria: Without `--require-applied`, blocked reports return exit code 0 and leave the target unchanged. With `--require-applied`, unchanged reports return exit code 2. Confirmed valid apply still writes the reviewed target and exits successfully.
Validation: Static source/test/docs review completed through the GitHub repository API. Deterministic tests cover blocked report success, fail-closed required application, and confirmed write behavior.
Risks or assumptions: A zero exit code without `--require-applied` means the report was generated successfully, not that a file changed.
Notes: Completed before post-apply validation handoff.

### AUTO-090 — Post-apply validation handoff
Priority: P1
Status: DONE

Goal: Add a read-only handoff that records whether a confirmed patch application has supplied passing validation evidence for every validation step required by the patch-apply report.
Why it matters: After the first write-capable local command, the workflow needs an explicit validation checkpoint before any future commit-readiness or commit workflow can be considered.
Scope: Add `forge post-apply-validation` and `forge-post-apply-validation`, deterministic core/CLI tests, focused documentation, README usage, and project-memory updates. Also make historical grouped roadmap headings lint-compatible on `main`, directly integrating the useful portion of open PR #10 without merging the PR.
Expected files or areas: `src/autonomous_forge/post_apply_validation.py`, `src/autonomous_forge/post_apply_validation_cli.py`, `src/autonomous_forge/cli_entry_patch.py`, `pyproject.toml`, `tests/test_post_apply_validation.py`, `docs/POST_APPLY_VALIDATION.md`, README, and `.ai` records.
Acceptance criteria: Post-apply validation consumes a patch-apply JSON report, requires applied/file-changed evidence, requires `patch_application_allowed` to be closed back to false, compares required validation steps with supplied executed steps, requires a passing supplied result for `--require-validated`, reports missing steps and blockers deterministically, and never runs commands, polls workflows, inspects diffs, verifies commits, writes files, commits, or pushes.
Validation: Static source/test/docs review completed through the GitHub repository API. Deterministic tests cover validated full step coverage, missing required steps, failed result, unapplied patch reports, unsafe paths, CLI JSON output, and fail-closed `--require-validated` behavior. Direct local checkout/test execution remained unavailable in this environment.
Risks or assumptions: The command trusts supplied validation metadata; it does not prove commands were truly executed or that external workflow checks passed.
Notes: Completed before live workflow-status collection.

### AUTO-091 — Live workflow-status collection for commit-status review
Priority: P1
Status: DONE

Goal: Extend `forge commit-status-review` so maintainers can explicitly collect GitHub workflow-run status for a commit instead of only supplying stale JSON evidence.
Why it matters: After patch application and post-apply validation, the workflow needs a concrete way to inspect current external workflow state before commit-readiness behavior is designed.
Scope: Add `--from-github`, optional `--commit-sha`, and bounded `--limit` handling to the existing commit-status review command; collect commit SHA with local `git` when needed; collect workflow metadata with `gh run list`; normalize it through the existing status-review model; update deterministic tests, command docs, README, and project-memory records.
Expected files or areas: `src/autonomous_forge/commit_status_review.py`, `src/autonomous_forge/commit_status_review_cli.py`, `tests/test_commit_status_review.py`, `docs/COMMIT_STATUS_REVIEW.md`, README, and `.ai` records.
Acceptance criteria: The command still supports repository-local `--status` JSON, rejects unsafe roots and invalid SHAs, collects at most 20 workflow runs through `gh` only when explicitly requested, reports clear/blocked status through the existing `--require-clear` gate, and never reruns workflows, inspects logs, applies patches, writes files, commits, or pushes.
Validation: Static source/test/docs review completed through the GitHub repository API. Deterministic tests cover git/gh command invocation, workflow-run normalization, bad SHA refusal, primary CLI JSON output, and fail-closed clear gating. Direct local checkout/test execution remained unavailable in this environment.
Risks or assumptions: Live mode depends on local `git`, GitHub CLI, repository authentication, and GitHub workflow data availability. It can prove only reported workflow status, not code correctness or commit authenticity.
Notes: Next safe step is commit-readiness summary that combines post-apply validation, final git-diff review, and live or supplied status evidence without committing.

## Future Ideas

- Hash-linked local run reports.
- Optional issue import.
- Policy-aware changed-file summaries.
- Explicit validation orchestration after validation plans are reviewable.
- Read-only patch application provenance audits before any patch applier exists.
- Commit-readiness summary after post-apply validation and live/supplied workflow status.

## Do Not Change Without Explicit Human Approval

- Remote and branch settings.
- Repository visibility and access controls.
- Production infrastructure.
- Features that change repository files outside documented safe paths.
- Sensitive configuration handling, telemetry, analytics, billing, or deployment behavior.
