# Autonomous Forge Roadmap

## Product vision

Autonomous Forge helps a repository keep a clear improvement plan, choose one safe task, produce reviewable planning artifacts, run tightly scoped local validation, and record what happened.

## Product scope and non-goals

The first product remains a local Python command-line tool. It reads repository files, reports safe next actions, runs only explicitly confirmed allowlisted local validation commands, audits explicit content metadata without printing content, compares supplied audit evidence, can fail closed on requested clear-evidence gates, reviews patch-intent readiness, describes patch-intent handoff readiness from supplied evidence, creates explicit patch proposal manifests from reviewed evidence and maintainer-supplied objective/path/validation fields, reviews manifests against fresh content-audit evidence, previews patch proposal draft outlines from ready review evidence, preflights explicit patch-text metadata against draft-ready evidence from one shared validated evidence snapshot, reviews explicit patch-text summary metadata against ready preflight evidence, preflights explicit patch provenance metadata against ready patch-text review evidence, and keeps durable project memory. It is not a hosted platform, dashboard, deployment system, permission-management tool, patch generator, patch applier, or uncontrolled autonomous executor.

## Current architecture

The repository contains a Python package under `src/autonomous_forge`, package metadata in `pyproject.toml`, tests under `tests/`, policy documentation under `docs/`, a visual orientation document at `docs/OVERVIEW.md`, command output contracts under `docs/COMMANDS.md`, focused command documentation under `docs/`, an example policy under `.forge/`, and contributor guidance in `CONTRIBUTING.md`. The installed `forge` console script routes through a small compatibility entry point that exposes primary extension commands and delegates established commands to the base CLI. `forge-patch-application-preflight`, `forge-patch-proposal-review`, `forge-patch-proposal-draft`, and `forge-patch-text-review` remain as compatibility scripts. The GitHub Actions workflow smoke-tests documented primary routes and compatibility routes, and asserts identical ready-evidence JSON output for review, draft, and patch text review previews.

## Current implementation status

Roadmap v1 established the local CLI, task parsing, deterministic task selection, and dry-run reports. Roadmap v2 added conservative policy parsing, policy-readiness reporting, roadmap linting, command output contracts, run-summary preview output, repository health inventory file-presence signals, and a visual project overview. Roadmap v3 has advanced the policy-aware maintenance workflow through implementation plans, proposals, validation previews, review artifacts, run-history records, validation-result handoff, orchestration readiness, command-execution handoff, executor gates, executor contracts, a read-only executor dry-run, a narrow opt-in local executor that can run one exact validation command without a shell, explicit executor-result persistence handoff, guarded executor-handoff persistence, validation-result audits, executor-observation audits with fail-closed gating, latest-limited history audit windows, content-audit, diff-source handoff, patch-intent review, patch-intent description, patch proposal manifests, patch proposal review, patch proposal draft previews from ready review evidence, patch text preflight checks from explicit per-path metadata, single-read evidence reuse for patch-text preflight CLI formatting and readiness gating, patch text review from ready preflight evidence plus explicit per-path patch summaries, and patch application preflight from ready patch-text review evidence plus explicit provenance metadata. Product commands still do not enforce policy, generate patches, apply patches, execute arbitrary implementation plans, inspect git diffs, verify commits, check workflow status, or commit changes.

## Technical debt

The CLI can select work, describe policy boundaries, build reviewable plans and proposals, describe validation intent, preview validation command candidates, review explicit paths, audit explicit file-content metadata without printing content, compare supplied content-audit JSON outputs, fail closed on non-clear diff-source evidence when requested, review patch-intent readiness from supplied diff-source evidence, describe future patch-intent handoff readiness from supplied patch-review evidence while refusing unsafe candidate path labels, build explicit patch proposal manifests from described evidence and maintainer-supplied objective/path/validation fields, review proposal manifests against fresh content-audit evidence through the primary command surface while refusing missing validation-step evidence, preview patch proposal draft outlines from ready review evidence, preflight explicit patch-text metadata against draft-ready evidence from one validated data object per CLI invocation, review explicit patch text summaries against ready preflight evidence, preflight explicit patch provenance metadata against ready patch-text review evidence while keeping patch application disallowed, combine review signals, preview and inspect durable run-history records, attach externally supplied validation results, expose orchestration readiness, expose command-execution handoff data, expose executor precondition gates, define an executor contract, dry-run one exact executor candidate command, run one exact confirmed local validation command without a shell, show the exact explicit command for persisting the observed executor result, persist reviewed executor-run JSON through guarded validation-result semantics, audit saved validation observations, audit aggregate saved executor observations across latest-limited direct history records, and preserve hidden path tokens in planned file-area parsing when punctuation follows. It does not yet append to a hash-linked long-lived history index, inspect git diffs, generate patches, apply patches, verify commits, check workflow status, or execute approved implementation plans. Runtime test execution and main-branch CI observation were unavailable from the automation environment for the latest direct commits.

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

### AUTO-057 through AUTO-077 — Content audit and patch-proposal evidence readiness
Priority: P1
Status: DONE

Goal: Add read-only content-audit checkpoints, compare supplied content-audit outputs, provide fail-closed evidence gates, review patch-intent readiness, describe patch-intent handoff readiness, refuse unsafe candidate path labels, build explicit patch proposal manifests, review those manifests against fresh content-audit evidence, expose that final review through the primary `forge` command surface, require validation-step evidence, protect primary and compatibility proposal-review routes in CI, preview patch proposal draft outlines from ready review evidence, preflight patch-text metadata against draft-ready evidence, ensure preflight output/gating derive from one validated evidence snapshot, review explicit patch-text summaries against ready preflight evidence, and preflight explicit patch provenance metadata against ready patch-text review evidence.
Why it matters: Patch-adjacent workflows need a safe bridge between policy-reviewed paths, content metadata, patch-intent readiness, safe candidate path labels, explicit objectives, requested paths, validation steps, fresh content-audit evidence, ready proposal reviews, draft-ready proposal context, explicit patch-text metadata, reviewed patch-text summaries, and explicit patch provenance without printing content, generating patches, inspecting git diffs, applying patches, or treating changed evidence as safe by default.
Scope: Add content-audit, diff-source handoff, patch-intent review, patch-intent description, patch proposal manifest, patch proposal review, validation-step enforcement, primary/compatibility CI coverage, `forge patch-proposal-draft --format text|json` with `--require-draft-ready`, `forge-patch-proposal-draft` compatibility, `forge patch-text-preflight --format text|json` with `--require-ready`, single-read preflight data reuse, `forge patch-text-review --format text|json` with `--require-ready`, `forge-patch-text-review` compatibility, `forge patch-application-preflight --format text|json` with `--require-ready`, and `forge-patch-application-preflight` compatibility.
Expected files or areas: `pyproject.toml`, `src/autonomous_forge/cli_entry_patch.py`, `src/autonomous_forge/content_audit.py`, `src/autonomous_forge/diff_source_handoff.py`, `src/autonomous_forge/patch_intent_review.py`, `src/autonomous_forge/patch_intent_description.py`, `src/autonomous_forge/patch_proposal_manifest.py`, `src/autonomous_forge/patch_proposal_review.py`, `src/autonomous_forge/patch_proposal_draft.py`, `src/autonomous_forge/patch_text_preflight.py`, `src/autonomous_forge/patch_text_review.py`, `src/autonomous_forge/patch_application_preflight.py`, `src/autonomous_forge/*_cli.py`, `tests/`, `.github/workflows/test.yml`, README, `docs/`, `.ai` records.
Acceptance criteria: Patch application preflight reads supplied patch-text-review JSON plus explicit path/source/expected-summary metadata only once per CLI invocation, requires ready patch-text review evidence, requires patch-text review allowance, requires safe reviewed and provenance path labels, requires one explicit source and one expected summary per reviewed path, requires exact provenance coverage of reviewed paths, supports `--require-ready`, keeps `patch_application_allowed` false, and never reads repository file contents, inspects git diffs, generates patch text, applies patches, runs commands, approves implementation, commits, pushes, or changes files.
Validation: Static review completed through the GitHub repository API. Deterministic unit/CLI/router tests cover the implemented content-audit, diff-source, patch-intent, patch-description, manifest, review, draft, preflight, patch text review, patch application preflight, primary-routing, and compatibility behaviors. CI smoke assertions cover unchanged live content-audit/diff-source/patch-intent/description/manifest/review/draft/preflight/review evidence gates through primary and compatibility routes where applicable.
Risks or assumptions: Secret-marker checks are intentionally simple guard signals, not complete secret scanning. A clear content-audit, unchanged diff-source handoff, ready patch-intent review, described patch-intent description, ready patch proposal manifest, ready patch proposal review, draft-ready patch proposal draft result, ready patch text preflight result, ready patch text review result, or ready patch application preflight result does not approve patches, prove correctness, or replace human review. `--require-clear`, `--require-ready`, `--require-described`, and `--require-draft-ready` change only the process exit code.
Notes: The next safe step is adding a read-only patch provenance/audit chain that can compare future patch-application preflight evidence against saved review artifacts before any write-capable patch behavior exists.

## Future Ideas

- Hash-linked local run reports.
- Optional issue import.
- Policy-aware changed-file summaries.
- Explicit validation orchestration after validation plans are reviewable.
- Read-only patch text provenance and patch-application preflight gates.

## Do Not Change Without Explicit Human Approval

- Remote and branch settings.
- Repository visibility and access controls.
- Production infrastructure.
- Features that change repository files outside documented safe paths.
- Sensitive configuration handling, telemetry, analytics, billing, or deployment behavior.
