# Autonomous Forge Roadmap

## Product vision

Autonomous Forge helps a repository keep a clear improvement plan, choose one safe task, produce reviewable planning artifacts, inspect proposed diffs, review validation status, run tightly scoped validation, apply explicitly confirmed patches, record validation evidence, summarize commit readiness, preview commit metadata, create one explicitly confirmed local commit, verify that created commit, summarize push readiness, and run an explicitly confirmed non-force push handoff with local ref checks.

## Product scope and non-goals

The first product remains a local Python CLI. It is not a hosted service, deployment system, permission manager, uncontrolled executor, automatic commit bot, force-push bot, branch-protection manager, or remote-configuration manager.

## Current architecture

The repository contains a Python package under `src/autonomous_forge`, tests under `tests/`, command docs under `docs/`, workflow checks under `.github/workflows/`, policy under `.forge/`, and durable memory under `.ai/`.

## Current implementation status

Roadmap v3 now reaches guarded local commit creation, post-commit verification, pre-push readiness review, and explicitly confirmed non-force push handoff after patch apply, post-apply validation, live/supplied status review, commit readiness, and commit proposal preview. Product commands still do not force-push, push tags, change remotes, change branch protections, verify commit signatures, or cryptographically verify commit identity.

## Prioritized roadmap

## Roadmap v1 — Completed foundation

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
Notes: Historical detailed task records remain available in repository history.

## Roadmap v2 — Completed safety and reporting surface

### AUTO-005 — Policy, linting, inventory, and run-summary previews through AUTO-017
Priority: P1
Status: DONE
Goal: Establish policy parsing, roadmap linting, contributor guidance, command contracts, repository inventory, and run-summary preview behavior.
Why it matters: The product needs a safe local reporting surface before proposing implementation work.
Scope: Keep behavior local-first and read-only while improving repository understanding and durable memory design.
Expected files or areas: `src/autonomous_forge/`, `tests/`, README, `docs/`, `.forge/`.
Acceptance criteria: Implemented commands remain deterministic, documented, and covered by focused tests.
Validation: Deterministic unit and CLI coverage exists across the implemented read-only surfaces.
Risks or assumptions: Do not imply command execution, patch generation, policy enforcement, or automatic history persistence.
Notes: Historical detailed task records remain available in repository history.

## Roadmap v3 — Policy-aware planning toward safe maintenance workflow

### AUTO-018 — Planning, review, history, validation executor, and observation gates through AUTO-056
Priority: P1
Status: DONE
Goal: Advance the workflow from selected task to review artifacts, local validation execution, guarded result persistence, and saved-observation audits.
Why it matters: Maintainers need machine-readable planning, validation, path-review, executor, and history evidence before patch behavior can be considered.
Scope: Add structured plan output, change proposals, validation plans/previews, review artifacts, run history, executor gates/contracts/dry-runs/runs, result persistence handoff, and observation audit.
Expected files or areas: `src/autonomous_forge/`, `tests/`, README, `docs/`, `.github/workflows/test.yml`, `.ai` records.
Acceptance criteria: Outputs are deterministic, writes require explicit confirmation, and execution is limited to one exact confirmed no-shell local validation command.
Validation: Deterministic tests and static review were completed through the GitHub repository API; CI smoke exercises the current command chain.
Risks or assumptions: These surfaces are advisory except for explicit local validation execution and explicit local persistence.
Notes: Historical detailed task records remain available in repository history.

### AUTO-057 — Content audit and patch-proposal evidence readiness through AUTO-082
Priority: P1
Status: DONE
Goal: Add content-audit checkpoints and patch-adjacent evidence gates through manifest, review, draft, text, provenance, audit, and readiness checkpoints.
Why it matters: Patch-adjacent workflows need a safe bridge between policy-reviewed paths, content metadata, objectives, paths, validation steps, summaries, and provenance.
Scope: Add content-audit, diff-source handoff, patch-intent review/description, patch proposal manifest/review/draft, patch text preflight/review, patch application preflight/audit/readiness, compatibility scripts, and CI smoke coverage.
Expected files or areas: `src/autonomous_forge/`, `tests/`, `.github/workflows/test.yml`, README, `docs/`, `.ai` records.
Acceptance criteria: Evidence gates remain deterministic, blocker-aware, local-first, and non-mutating before patch application exists.
Validation: Static source/test/documentation review completed through the GitHub repository API with deterministic unit/CLI/router tests.
Risks or assumptions: Secret-marker checks are guard signals, not complete secret scanning.
Notes: Completed before supplied git-diff inspection.

### AUTO-083 — Diff/status review and guarded patch preview through AUTO-087
Priority: P1
Status: DONE
Goal: Inspect supplied diffs, connect them to validation status, and generate bounded patch preview text only from explicit replacement content and ready evidence.
Why it matters: A safe maintenance workflow needs reviewable diff evidence, validation evidence, and generated patch text before patch apply.
Scope: Add supplied git-diff review, binary/metadata hardening, supplied commit-status review, combined change-readiness, and patch-generation preview.
Expected files or areas: `src/autonomous_forge/`, `tests/`, README, `docs/`, `.ai` records.
Acceptance criteria: Patch-generation preview blocks unsafe/unready inputs, produces bounded diff text, and does not apply patches or change files.
Validation: Static source/test/documentation review completed through the GitHub repository API with deterministic tests.
Risks or assumptions: Generated patch previews can expose non-secret repository text by design and rely on simple secret-marker refusal.
Notes: Completed before confirmed patch application.

### AUTO-088 — Explicitly confirmed guarded patch apply
Priority: P1
Status: DONE
Goal: Add one narrow write-capable command that applies an explicit replacement file only after generated patch preview and change-readiness evidence match the current target.
Why it matters: The workflow needs an auditable bridge from generated patch text to one local file change before post-apply validation and commit workflows.
Scope: Add `forge patch-apply` and compatibility route, deterministic tests, focused docs, README usage, and project-memory updates.
Expected files or areas: `src/autonomous_forge/patch_apply.py`, `src/autonomous_forge/patch_apply_cli.py`, `src/autonomous_forge/cli_entry_patch.py`, `pyproject.toml`, `tests/test_patch_apply.py`, `docs/PATCH_APPLY.md`, README, and `.ai` records.
Acceptance criteria: Patch apply requires generated preview JSON, ready change-readiness JSON, a reviewed target path, one explicit replacement file, and `--confirm-apply`; it writes only the target file and never commits or pushes.
Validation: Static source/test/documentation review completed through the GitHub repository API with deterministic tests.
Risks or assumptions: This command intentionally changes one local file when explicitly confirmed and does not prove correctness.
Notes: Completed before hardening patch-apply exit gating.

### AUTO-089 — Honor patch-apply require-applied exit gating
Priority: P1
Status: DONE
Goal: Fix `forge patch-apply` so producing a blocked report is distinct from fail-closed automation.
Why it matters: The first write-capable command must be predictable for both interactive review and automation.
Scope: Update `patch_apply_cli.py`, focused tests, patch-apply docs, README status, and project-memory records.
Expected files or areas: `src/autonomous_forge/patch_apply_cli.py`, `tests/test_patch_apply.py`, `docs/PATCH_APPLY.md`, README, and `.ai` records.
Acceptance criteria: Without `--require-applied`, blocked reports return exit code 0; with it, unchanged reports return exit code 2; valid apply still succeeds.
Validation: Static source/test/docs review completed through the GitHub repository API with deterministic tests.
Risks or assumptions: A zero exit code without `--require-applied` means the report was generated successfully, not that a file changed.
Notes: Completed before post-apply validation handoff.

### AUTO-090 — Post-apply validation handoff
Priority: P1
Status: DONE
Goal: Add a handoff that records whether a confirmed patch application has supplied passing validation evidence for every validation step required by the patch-apply report.
Why it matters: After local file writes, the workflow needs an explicit validation checkpoint before commit readiness.
Scope: Add `forge post-apply-validation`, compatibility route, tests, docs, README usage, project memory, and lint-compatible historical roadmap headings.
Expected files or areas: `src/autonomous_forge/post_apply_validation.py`, `src/autonomous_forge/post_apply_validation_cli.py`, `src/autonomous_forge/cli_entry_patch.py`, `pyproject.toml`, `tests/test_post_apply_validation.py`, `docs/POST_APPLY_VALIDATION.md`, README, and `.ai` records.
Acceptance criteria: Post-apply validation consumes patch-apply JSON, requires applied/file-changed evidence, compares required and executed steps, supports `--require-validated`, and never runs commands or commits.
Validation: Static source/test/docs review completed through the GitHub repository API with deterministic tests.
Risks or assumptions: The command trusts supplied validation metadata.
Notes: Completed before live workflow-status collection.

### AUTO-091 — Live workflow-status collection for commit-status review
Priority: P1
Status: DONE
Goal: Extend `forge commit-status-review` so maintainers can explicitly collect GitHub workflow-run status for a commit instead of only supplying stale JSON evidence.
Why it matters: The workflow needs a concrete way to inspect current external workflow state before commit readiness.
Scope: Add `--from-github`, optional `--commit-sha`, bounded `--limit`, deterministic tests, docs, README, and project memory.
Expected files or areas: `src/autonomous_forge/commit_status_review.py`, `src/autonomous_forge/commit_status_review_cli.py`, `tests/test_commit_status_review.py`, `docs/COMMIT_STATUS_REVIEW.md`, README, and `.ai` records.
Acceptance criteria: The command supports supplied JSON or explicit live collection through local `git`/`gh`, gates with `--require-clear`, and never reruns workflows or writes files.
Validation: Static source/test/docs review completed through the GitHub repository API with deterministic tests.
Risks or assumptions: Live mode depends on local `git`, GitHub CLI, repository authentication, and GitHub workflow data availability.
Notes: Completed before commit-readiness summary.

### AUTO-092 — Commit-readiness summary
Priority: P1
Status: DONE
Goal: Add a summary that combines post-apply validation, final git-diff review, and commit-status review evidence before any commit workflow is considered.
Why it matters: Maintainers need one gate showing whether a changed file is ready for human commit consideration without granting commit authority.
Scope: Add `forge commit-readiness`, compatibility route, deterministic tests, docs, README usage, CI help-smoke coverage, and project memory.
Expected files or areas: `src/autonomous_forge/commit_readiness.py`, `src/autonomous_forge/commit_readiness_cli.py`, `src/autonomous_forge/cli_entry_patch.py`, `pyproject.toml`, `tests/test_commit_readiness.py`, `docs/COMMIT_READINESS.md`, `.github/workflows/test.yml`, README, and `.ai` records.
Acceptance criteria: Commit-readiness consumes post-apply-validation JSON, final git-diff-review JSON, and commit-status-review JSON; requires validated post-apply evidence, clear final diff, clear status, and safe paths; keeps commit authority false.
Validation: Static source/test/docs/workflow review completed through the GitHub repository API with deterministic tests.
Risks or assumptions: The command trusts supplied upstream evidence.
Notes: Completed before commit proposal preview.

### AUTO-093 — Commit proposal preview
Priority: P1
Status: DONE
Goal: Add a guarded metadata preview that prepares a reviewable commit message from ready commit-readiness evidence without creating a commit.
Why it matters: After commit-readiness exists, maintainers need a concrete bridge from ready evidence to reviewable commit metadata before any actual commit command is considered.
Scope: Add `forge commit-proposal-preview` and `forge-commit-proposal-preview`, deterministic core/CLI tests, focused documentation, README usage, CI help-smoke coverage, and project-memory updates.
Expected files or areas: `src/autonomous_forge/commit_proposal_preview.py`, `src/autonomous_forge/commit_proposal_preview_cli.py`, `src/autonomous_forge/cli_entry_patch.py`, `pyproject.toml`, `tests/test_commit_proposal_preview.py`, `docs/COMMIT_PROPOSAL_PREVIEW.md`, `.github/workflows/test.yml`, README, and `.ai` records.
Acceptance criteria: Commit proposal preview consumes ready commit-readiness JSON plus explicit summary/body metadata; requires read-only ready evidence, reviewed paths, validation steps, blocker-free upstream evidence, and disabled commit authority; bounds metadata text, refuses simple secret-marker strings, supports `--require-ready`, and never stages files, creates commits, pushes, reads repository contents, runs commands, or changes files.
Validation: Static source/test/docs/workflow review completed through the GitHub repository API. Deterministic tests cover ready metadata, blocked upstream evidence, unsafe summary format, secret-marker refusal, primary CLI JSON output, and fail-closed `--require-ready` behavior. Direct local checkout/test execution remained unavailable in this environment.
Risks or assumptions: The command does not prove the metadata is the best commit message and still trusts supplied commit-readiness evidence.
Notes: Completed before guarded commit creation.

### AUTO-094 — Guarded local commit creation
Priority: P1
Status: DONE
Goal: Add the first explicitly confirmed local commit command that turns ready commit proposal evidence into one local git commit.
Why it matters: The safe maintenance workflow needs a concrete step beyond metadata preview while still blocking pushes, remotes, and uncontrolled git operations.
Scope: Add `forge commit-create` and `forge-commit-create`, deterministic core tests with a fake git runner, focused documentation, README usage, CI help-smoke coverage, and project-memory updates.
Expected files or areas: `src/autonomous_forge/commit_create.py`, `src/autonomous_forge/commit_create_cli.py`, `src/autonomous_forge/cli_entry_patch.py`, `pyproject.toml`, `tests/test_commit_create.py`, `docs/COMMIT_CREATE.md`, `.github/workflows/test.yml`, README, and `.ai` records.
Acceptance criteria: Commit-create consumes ready commit-proposal-preview JSON, validates reviewed paths and disabled push/remote fields, requires `--confirm-commit-create`, checks local git status for reviewed paths, stages only reviewed paths, creates one local commit, reports the created commit SHA, supports `--require-created`, and never pushes or changes remotes.
Validation: Static source/test/docs/workflow review completed through the GitHub repository API. Local scratch syntax compilation covered the new module and CLI; deterministic tests cover missing confirmation, guarded git command sequence, unready proposal blocking, no-change blocking, and unsafe path refusal. Direct repository checkout/test execution remained unavailable in this environment.
Risks or assumptions: The command intentionally mutates local git state when explicitly confirmed, trusts supplied upstream proposal evidence, and does not sign, verify, or push commits.
Notes: Completed before post-commit verification.

### AUTO-095 — Post-commit verification
Priority: P1
Status: DONE
Goal: Verify that a created local commit matches the reviewed commit-create report before any push-readiness workflow is considered.
Why it matters: Once the product can create local commits, it needs a deterministic checkpoint that confirms the created commit SHA, message, and changed paths still match reviewed evidence.
Scope: Add `forge commit-verify` and `forge-commit-verify`, deterministic core tests with a fake git runner, focused documentation, README usage, CI help-smoke coverage, and project-memory updates.
Expected files or areas: `src/autonomous_forge/commit_verify.py`, `src/autonomous_forge/commit_verify_cli.py`, `src/autonomous_forge/cli_entry_patch.py`, `pyproject.toml`, `tests/test_commit_verify.py`, `docs/COMMIT_VERIFY.md`, `.github/workflows/test.yml`, README, and `.ai` records.
Acceptance criteria: Commit-verify consumes created commit-create JSON, validates safe reviewed paths and disabled push/remote fields, inspects one local commit with `git show` and `git diff-tree`, compares SHA, subject, reviewed body lines, and exact changed paths, supports `--require-verified`, and never stages, commits, pushes, changes remotes, or modifies the working tree.
Validation: Static source/test/docs/workflow review completed through the GitHub repository API. Scratch syntax compilation covered the new module, CLI, and tests; deterministic tests cover uncreated reports, verified metadata/path inspection, unexpected paths, summary mismatch, and unsafe path refusal. Direct repository checkout/test execution remained unavailable in this environment.
Risks or assumptions: The command trusts supplied commit-create evidence and local git output, and does not verify signatures, authorship, or workflow freshness.
Notes: Completed before push-readiness review.

### AUTO-096 — Push-readiness gate
Priority: P1
Status: DONE
Goal: Combine verified commit evidence with clear workflow status before any future push command is considered.
Why it matters: After local commit creation and verification, maintainers need one deterministic pre-push gate that proves the verified commit still has clear status evidence while push authority remains disabled.
Scope: Add `forge push-readiness` and `forge-push-readiness`, deterministic tests, focused documentation, README usage, CI help-smoke coverage, and project-memory updates.
Expected files or areas: `src/autonomous_forge/push_readiness.py`, `src/autonomous_forge/push_readiness_cli.py`, `src/autonomous_forge/cli_entry_patch.py`, `pyproject.toml`, `tests/test_push_readiness.py`, `docs/PUSH_READINESS.md`, `.github/workflows/test.yml`, README, and `.ai` records.
Acceptance criteria: Push-readiness consumes commit-verify JSON and commit-status-review JSON, requires verified commit evidence, requires a matching status-review commit SHA, requires at least one successful status context and no failed/pending/unknown contexts, validates safe reviewed paths, supports `--require-ready`, and never runs git, calls networks, stages files, creates commits, pushes, changes remotes, or modifies files.
Validation: Static source/test/docs/workflow review completed through the GitHub repository API. Scratch syntax compilation covered the new module, CLI, and tests before writing. Deterministic tests cover ready evidence, unverified commits, status SHA mismatch, unclear status evidence, unsafe paths, and repository-local JSON loading. Direct repository checkout/test execution remained unavailable in this environment.
Risks or assumptions: The command trusts supplied commit-verify and status-review evidence, and it still does not prove signed commit identity or provide a push command.
Notes: Completed before push-handoff.

### AUTO-097 — Explicitly confirmed non-force push handoff
Priority: P1
Status: DONE
Goal: Add a guarded local push handoff that consumes ready push-readiness evidence and can push exactly one verified commit to one branch after explicit confirmation.
Why it matters: The end-to-end maintenance workflow needs a concrete remote handoff beyond evidence review while still refusing force-pushes, tags, remote configuration changes, and branch-protection changes.
Scope: Add `forge push-handoff` and `forge-push-handoff`, deterministic fake-git tests, focused documentation, README usage, CI help-smoke coverage, and project-memory updates.
Expected files or areas: `src/autonomous_forge/push_handoff.py`, `src/autonomous_forge/push_handoff_cli.py`, `src/autonomous_forge/cli_entry_patch.py`, `pyproject.toml`, `tests/test_push_handoff.py`, `docs/PUSH_HANDOFF.md`, `.github/workflows/test.yml`, README, and `.ai` records.
Acceptance criteria: Push-handoff consumes ready push-readiness JSON, validates safe branch and remote names, checks local branch, `HEAD`, upstream, and remote branch refs, reports a ready handoff without pushing by default, runs one non-force `git push <remote> <commit>:refs/heads/<branch>` only with `--confirm-push`, supports `--require-pushed`, and never stages files, creates commits, force-pushes, pushes tags, changes remotes, or changes branch protections.
Validation: Static source/test/docs/workflow review completed through the GitHub repository API. Scratch syntax compilation covered the new module, CLI, and tests; focused pytest for `tests/test_push_handoff.py` passed locally in scratch with 8 tests. Direct full repository checkout/test execution remained unavailable in this environment.
Risks or assumptions: The command intentionally mutates the configured remote only after explicit confirmation, trusts supplied push-readiness evidence and local git output, and does not perform post-push status verification.
Notes: Next safe step is post-push verification that confirms the pushed commit appears on the requested remote branch and has fresh workflow/status evidence.

## Future Ideas

- Hash-linked local run reports.
- Optional issue import.
- Policy-aware changed-file summaries.
- Signed commit verification before any push workflow.
