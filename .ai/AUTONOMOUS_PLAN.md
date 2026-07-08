# Autonomous Forge Roadmap

## Product vision

Autonomous Forge helps a repository keep a clear improvement plan, choose one safe task, produce reviewable planning artifacts, inspect proposed diffs, review supplied validation status, run tightly scoped local validation, and record what happened.

## Product scope and non-goals

The first product remains a local Python command-line tool. It reads repository files, reports safe next actions, runs only explicitly confirmed allowlisted local validation commands, audits explicit content metadata without printing content, compares supplied audit evidence, can fail closed on requested clear-evidence gates, reviews supplied unified git diff metadata against policy, flags binary and metadata-only diff evidence for separate review, reviews supplied commit/workflow status JSON evidence, reviews patch-intent readiness, describes patch-intent handoff readiness from supplied evidence, creates explicit patch proposal manifests from reviewed evidence and maintainer-supplied objective/path/validation fields, reviews manifests against fresh content-audit evidence, previews patch proposal draft outlines from ready review evidence, preflights explicit patch-text metadata against draft-ready evidence from one shared validated evidence snapshot, reviews explicit patch-text summary metadata against ready preflight evidence, preflights explicit patch provenance metadata against ready patch-text review evidence, audits patch-application preflight provenance evidence, summarizes patch-application readiness from ready preflight and clear audit evidence before any future patch-applier design, and keeps durable project memory. It is not a hosted platform, dashboard, deployment system, permission-management tool, patch generator, patch applier, live workflow poller, or uncontrolled autonomous executor.

## Current architecture

The repository contains a Python package under `src/autonomous_forge`, package metadata in `pyproject.toml`, tests under `tests/`, policy documentation under `docs/`, a visual orientation document at `docs/OVERVIEW.md`, command output contracts under `docs/`, focused command documentation under `docs/`, an example policy under `.forge/`, and contributor guidance in `CONTRIBUTING.md`. The installed `forge` console script routes through a small compatibility entry point that exposes primary extension commands and delegates established commands to the base CLI. `forge-commit-status-review`, `forge-git-diff-review`, `forge-patch-application-audit`, `forge-patch-application-preflight`, `forge-patch-application-readiness`, `forge-patch-proposal-review`, `forge-patch-proposal-draft`, and `forge-patch-text-review` remain as compatibility scripts. The GitHub Actions workflow smoke-tests documented primary routes and compatibility routes, including supplied commit-status review and supplied git-diff review.

## Current implementation status

Roadmap v1 established the local CLI, task parsing, deterministic task selection, and dry-run reports. Roadmap v2 added conservative policy parsing, policy-readiness reporting, roadmap linting, command output contracts, run-summary preview output, repository health inventory file-presence signals, and a visual project overview. Roadmap v3 has advanced the policy-aware maintenance workflow through implementation plans, proposals, validation previews, review artifacts, run-history records, validation-result handoff, orchestration readiness, command-execution handoff, executor gates, executor contracts, a read-only executor dry-run, a narrow opt-in local executor that can run one exact validation command without a shell, explicit executor-result persistence handoff, guarded executor-handoff persistence, validation-result audits, executor-observation audits with fail-closed gating, latest-limited history audit windows, content-audit, supplied git-diff review with binary/metadata-only hardening, supplied commit-status review, diff-source handoff, patch-intent review, patch-intent description, patch proposal manifests, patch proposal review, patch proposal draft previews from ready review evidence, patch text preflight checks from explicit per-path metadata, single-read evidence reuse for patch-text preflight CLI formatting and readiness gating, patch text review from ready preflight evidence plus explicit per-path patch summaries, patch application preflight from ready patch-text review evidence plus explicit provenance metadata, patch application provenance audit from ready preflight evidence, patch application readiness summary from ready preflight plus clear audit evidence, and CI smoke coverage for the primary/compatibility review routes. Product commands still do not enforce policy, generate patches, apply patches, execute arbitrary implementation plans, poll live workflow status, cryptographically verify commits, or commit changes.

## Technical debt

The CLI can select work, describe policy boundaries, build reviewable plans and proposals, describe validation intent, preview validation command candidates, review explicit paths, audit explicit file-content metadata without printing content, inspect supplied unified git diff metadata and changed paths, flag binary and metadata-only diff evidence for separate review, review supplied commit/workflow status JSON evidence, compare supplied content-audit JSON outputs, fail closed on non-clear diff-source evidence when requested, review patch-intent readiness from supplied diff-source evidence, describe future patch-intent handoff readiness from supplied patch-review evidence while refusing unsafe candidate path labels, build explicit patch proposal manifests from described evidence and maintainer-supplied objective/path/validation fields, review proposal manifests against fresh content-audit evidence through the primary command surface while refusing missing validation-step evidence, preview patch proposal draft outlines from ready review evidence, preflight explicit patch-text metadata against draft-ready evidence from one validated data object per CLI invocation, review explicit patch text summaries against ready preflight evidence, preflight explicit patch provenance metadata against ready patch-text review evidence while keeping patch application disallowed, audit patch-application preflight provenance evidence while still keeping application disallowed, summarize readiness from matching preflight and audit evidence while still keeping application disallowed, combine review signals, preview and inspect durable run-history records, attach externally supplied validation results, expose orchestration readiness, expose command-execution handoff data, expose executor precondition gates, define an executor contract, dry-run one exact executor candidate command, run one exact confirmed local validation command without a shell, show the exact explicit command for persisting the observed executor result, persist reviewed executor-run JSON through guarded validation-result semantics, audit saved validation observations, audit aggregate saved executor observations across latest-limited direct history records, and preserve hidden path tokens in planned file-area parsing when punctuation follows. It does not yet append to a hash-linked long-lived history index, generate patches, apply patches, verify commits beyond supplied status evidence, poll live workflow status, or execute approved implementation plans. Runtime test execution and main-branch CI observation were unavailable from the automation environment for the latest direct commits.

## Prioritized roadmap

## Roadmap v1 — Completed foundation

### AUTO-001 through AUTO-004 — Local CLI, roadmap parsing, task selection, and dry-run reports
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

### AUTO-005 through AUTO-017 — Policy, linting, inventory, and run-summary previews
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

### AUTO-018 through AUTO-056 — Planning, review, history, validation executor, and observation gates
Priority: P1
Status: DONE

Goal: Advance the safe end-to-end workflow from selected task to review artifacts, local validation execution, guarded result persistence, and saved-observation audits.
Why it matters: Maintainers need machine-readable planning, proposal, validation, command-candidate, path-review, executor, and history evidence before any patch behavior can be considered.
Scope: Add structured plan output, change proposals, validation plans/previews, explicit changed-file reviews, CI smoke checks, combined review artifacts, run-history read/write/list/latest/compare, validation-result preview/write/audit, command-execution handoff, executor gate/contract/dry-run/run, executor-result persistence handoff, guarded handoff persistence, and executor-observation audit with `--require-clear`.
Expected files or areas: `src/autonomous_forge/`, `tests/`, README, `docs/`, `.github/workflows/test.yml`, `.ai` records.
Acceptance criteria: Outputs are deterministic, text and JSON behavior are covered where applicable, CI smoke checks exercise live repository inputs, execution is limited to one exact confirmed no-shell local validation command, writes require explicit confirmation, and patch/diff generation remains absent.
Validation: Deterministic tests and static review were completed through the GitHub repository API. Installed-package CI smoke coverage exercises the current command chain. Direct local checkout execution remained unavailable in this environment.
Risks or assumptions: These surfaces are advisory except for explicit local validation execution and explicit local persistence. They must not imply arbitrary command execution, patch generation, git-diff inspection, approval, automatic write persistence, or policy enforcement.
Notes: Historical detailed task records remain available in repository history.

### AUTO-057 through AUTO-082 — Content audit and patch-proposal evidence readiness
Priority: P1
Status: DONE

Goal: Add read-only content-audit checkpoints, compare supplied content-audit outputs, provide fail-closed evidence gates, review patch-intent readiness, describe patch-intent handoff readiness, refuse unsafe candidate path labels, build explicit patch proposal manifests, review those manifests against fresh content-audit evidence, expose that final review through the primary `forge` command surface, require validation-step evidence, protect primary and compatibility proposal-review routes in CI, preview patch proposal draft outlines from ready review evidence, preflight patch-text metadata against draft-ready evidence, ensure preflight output/gating derive from one validated evidence snapshot, review explicit patch-text summaries against ready preflight evidence, preflight explicit patch provenance metadata against ready patch-text review evidence, audit patch-application preflight provenance evidence before any write-capable patch behavior, summarize patch-application readiness from ready preflight and clear audit evidence before applier design, and smoke-test the current audit chain in CI.
Why it matters: Patch-adjacent workflows need a safe bridge between policy-reviewed paths, content metadata, patch-intent readiness, safe candidate path labels, explicit objectives, requested paths, validation steps, fresh content-audit evidence, ready proposal reviews, draft-ready proposal context, explicit patch-text metadata, reviewed patch-text summaries, explicit patch provenance, provenance audits, readiness summaries, and installed-route confidence without printing content, generating patches, applying patches, or treating changed evidence as safe by default.
Scope: Add content-audit, diff-source handoff, patch-intent review, patch-intent description, patch proposal manifest, patch proposal review, validation-step enforcement, primary/compatibility CI coverage, `forge patch-proposal-draft --format text|json` with `--require-draft-ready`, `forge-patch-proposal-draft` compatibility, `forge patch-text-preflight --format text|json` with `--require-ready`, single-read preflight data reuse, `forge patch-text-review --format text|json` with `--require-ready`, `forge-patch-text-review` compatibility, `forge patch-application-preflight --format text|json` with `--require-ready`, `forge-patch-application-preflight` compatibility, `forge patch-application-audit --format text|json` with `--require-clear`, `forge-patch-application-audit` compatibility, `forge patch-application-readiness --format text|json` with `--require-ready`, `forge-patch-application-readiness` compatibility, and CI smoke coverage for the primary and compatibility audit outputs.
Expected files or areas: `pyproject.toml`, `src/autonomous_forge/cli_entry_patch.py`, `src/autonomous_forge/content_audit.py`, `src/autonomous_forge/diff_source_handoff.py`, `src/autonomous_forge/patch_intent_review.py`, `src/autonomous_forge/patch_intent_description.py`, `src/autonomous_forge/patch_proposal_manifest.py`, `src/autonomous_forge/patch_proposal_review.py`, `src/autonomous_forge/patch_proposal_draft.py`, `src/autonomous_forge/patch_text_preflight.py`, `src/autonomous_forge/patch_text_review.py`, `src/autonomous_forge/patch_application_preflight.py`, `src/autonomous_forge/patch_application_audit.py`, `src/autonomous_forge/patch_application_readiness.py`, `src/autonomous_forge/*_cli.py`, `tests/`, `.github/workflows/test.yml`, README, `docs/`, `.ai` records.
Acceptance criteria: Patch application readiness consumes supplied patch-application preflight and audit JSON, requires ready/clear upstream evidence, verifies matching objective, reviewed paths, validation steps, and blocker-free upstream evidence, keeps `patch_application_allowed` false, supports `--require-ready`, is covered by deterministic core/CLI/router tests, and never reads repository file contents, generates patch text, applies patches, runs commands, approves implementation, commits, pushes, or changes files.
Validation: Static review completed through the GitHub repository API. Deterministic unit/CLI/router tests cover the implemented content-audit, diff-source, patch-intent, patch-description, manifest, review, draft, preflight, patch text review, patch application preflight, patch application audit, patch application readiness, primary-routing, and compatibility behaviors. CI smoke assertions cover unchanged live content-audit/diff-source/patch-intent/description/manifest/review/draft/preflight/review/audit evidence gates through primary and compatibility routes where applicable.
Risks or assumptions: Secret-marker checks are intentionally simple guard signals, not complete secret scanning. A clear content-audit, unchanged diff-source handoff, ready patch-intent review, described patch-intent description, ready patch proposal manifest, ready patch proposal review, draft-ready patch proposal draft result, ready patch text preflight result, ready patch text review result, ready patch application preflight result, clear patch application audit result, or ready patch application readiness result does not approve patches, prove correctness, or replace human review. `--require-clear`, `--require-ready`, `--require-described`, and `--require-draft-ready` change only the process exit code.
Notes: Completed before moving into supplied git-diff inspection.

### AUTO-083 — Add supplied git diff review
Priority: P1
Status: DONE

Goal: Inspect supplied unified git diff metadata and changed paths against repository policy before any future patch-applier workflow can rely on a patch file.
Why it matters: The previous evidence chain stopped before actual git-diff inspection. Maintainers need a bounded way to review changed paths, file status, hunk counts, additions, deletions, and policy matches without applying a patch.
Scope: Add `forge git-diff-review` and compatibility `forge-git-diff-review`, deterministic parser/review logic, fail-closed `--require-clear`, JSON/text output, tests, README usage, focused command documentation, and project memory updates.
Expected files or areas: `src/autonomous_forge/git_diff_review.py`, `src/autonomous_forge/git_diff_review_cli.py`, `src/autonomous_forge/cli_entry_patch.py`, `pyproject.toml`, `tests/test_git_diff_review.py`, `docs/GIT_DIFF_REVIEW.md`, README, and `.ai` records.
Acceptance criteria: The command accepts a repository-local `.diff` or `.patch`, refuses unsafe or out-of-root diff inputs, parses file changes without printing file contents, reports additions/deletions/hunks/status, reviews old/new paths against policy, supports `--require-clear`, and never applies patches, runs commands, checks workflows, approves implementation, commits, pushes, or changes files.
Validation: Static source/package/router/test review completed through the GitHub repository API. Deterministic tests were added for clean diffs, blocked paths, JSON/text output, fail-closed behavior, out-of-root refusal, and primary `forge` routing. Direct local checkout/test execution remained unavailable in this environment.
Risks or assumptions: This is advisory supplied-diff inspection only. It does not prove correctness, test success, or patch safety beyond path/policy and parsing signals.
Notes: Completed before binary/metadata hardening and status review.

### AUTO-084 — Harden supplied git diff review for binary and metadata-only changes
Priority: P1
Status: DONE

Goal: Prevent allowed-path binary diffs and metadata-only file-mode changes from passing as ordinary clear text diffs.
Why it matters: A future patch-applier workflow must not treat non-text or file-mode-only evidence as equivalent to reviewed textual hunks simply because the changed path matches an allowed policy path.
Scope: Extend `forge git-diff-review` data with per-file `binary`, `mode_changes`, and `metadata_only` fields; add summary counts; make `--require-clear` fail closed on binary or metadata-only evidence; update tests, docs, README, and project memory.
Expected files or areas: `src/autonomous_forge/git_diff_review.py`, `tests/test_git_diff_review.py`, `docs/GIT_DIFF_REVIEW.md`, README, and `.ai` records.
Acceptance criteria: Binary diff markers and mode-only diffs are parsed, surfaced in text/JSON output, counted in summaries, and require attention even when their paths are otherwise allowed.
Validation: Static source/test/documentation review completed through the GitHub repository API. Deterministic tests were added for binary diffs, metadata-only mode changes, text/JSON output fields, and fail-closed clear gating. Direct local checkout/test execution remained unavailable in this environment.
Risks or assumptions: Binary and metadata-only changes are not always unsafe, but they require explicit review outside the normal text-hunk path. This remains advisory and still does not apply patches or prove correctness.
Notes: Completed before supplied status review.

### AUTO-085 — Add supplied commit and workflow status review
Priority: P1
Status: DONE

Goal: Review supplied commit-status, check-run, or workflow-run JSON evidence before a future patch-application workflow relies on validation status.
Why it matters: Reviewed diffs are not enough; maintainers also need a bounded validation-status checkpoint so failed, pending, unknown, or missing status evidence cannot be treated as clear.
Scope: Add `forge commit-status-review` and compatibility `forge-commit-status-review`, deterministic JSON/text review logic, fail-closed `--require-clear`, tests, README usage, command documentation, CI smoke coverage, and project memory updates.
Expected files or areas: `src/autonomous_forge/commit_status_review.py`, `src/autonomous_forge/commit_status_review_cli.py`, `src/autonomous_forge/cli_entry_patch.py`, `pyproject.toml`, `tests/test_commit_status_review.py`, `docs/COMMIT_STATUS_REVIEW.md`, `docs/COMMANDS.md`, `.github/workflows/test.yml`, README, and `.ai` records.
Acceptance criteria: The command accepts repository-local `.json` status evidence, refuses unsafe or out-of-root inputs, classifies status/check/workflow contexts as successful, failed, pending, or unknown, supports `--require-clear`, and never calls networks, polls GitHub, runs workflows, runs commands, approves implementation, commits, pushes, or changes files.
Validation: Static source/test/documentation/workflow review completed through the GitHub repository API. Deterministic tests were added for successful, failed, pending, unknown, missing, workflow-run, JSON/text, fail-closed, and out-of-root evidence. CI smoke coverage was added for primary and compatibility installed routes. Direct local checkout/test execution remained unavailable in this environment.
Risks or assumptions: Supplied status evidence can be stale or incomplete. This command does not independently verify commits, poll live workflow status, prove correctness, or replace human review.
Notes: The next safe step is a combined change-readiness summary over clear supplied git-diff review and clear supplied commit-status review before any write-capable patch applier is considered.

## Future Ideas

- Hash-linked local run reports.
- Optional issue import.
- Policy-aware changed-file summaries.
- Explicit validation orchestration after validation plans are reviewable.
- Read-only patch application provenance audits before any patch applier exists.
- Guarded commit and workflow status inspection before patch application.
- Combined change-readiness summary over reviewed diffs and supplied status evidence.

## Do Not Change Without Explicit Human Approval

- Remote and branch settings.
- Repository visibility and access controls.
- Production infrastructure.
- Features that change repository files outside documented safe paths.
- Sensitive configuration handling, telemetry, analytics, billing, or deployment behavior.
