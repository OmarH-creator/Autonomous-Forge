# Autonomous Forge Roadmap

## Product vision

Autonomous Forge helps a repository keep a clear improvement plan, choose one safe task, produce reviewable planning artifacts, run tightly scoped local validation, and record what happened.

## Product scope and non-goals

The first product remains a local Python command-line tool. It reads repository files, reports safe next actions, runs only explicitly confirmed allowlisted local validation commands, audits explicit content metadata without printing content, compares supplied audit evidence, can fail closed on requested clear-evidence gates, reviews patch-intent readiness from supplied evidence, and keeps durable project memory. It is not a hosted platform, dashboard, deployment system, permission-management tool, patch generator, or uncontrolled autonomous executor.

## Current architecture

The repository contains a Python package under `src/autonomous_forge`, package metadata in `pyproject.toml`, tests under `tests/`, policy documentation under `docs/`, a visual orientation document at `docs/OVERVIEW.md`, command output contracts under `docs/COMMANDS.md`, focused command documentation under `docs/`, an example policy under `.forge/`, and contributor guidance in `CONTRIBUTING.md`. The installed `forge` console script routes through a small CLI entry point that exposes extension commands and delegates established commands to the base CLI. The CLI exposes planning, proposal, validation, validation-preview, validation-orchestration, command-execution-handoff, executor-gate, executor-contract, executor-dry-run, executor-run, executor-handoff-persist, validation-result-preview, validation-result-write, validation-result-audit, executor-observation-audit, changed-file review, content-audit, diff-source-handoff with optional fail-closed clear gating, patch-intent-review with optional fail-closed readiness gating, review-artifact, run-history-preview, opt-in run-history-write, run-history-read, run-history-list, run-history-latest, run-history-compare, preflight-readiness, inventory, policy, report, run-summary, and roadmap task commands. All commands remain local-first and use zero runtime dependencies; only `forge executor-run` runs one exact confirmed local validation command, `forge content-audit` reads explicit repository file contents to compute bounded metadata and secret-marker signals without printing content, `forge run-history-write` writes a local history file, and `forge validation-result-write` / `forge executor-handoff-persist` rewrite one saved history file, with explicit confirmation required for each mutating or executing path.

## Current implementation status

Roadmap v1 established the local CLI, task parsing, deterministic task selection, and dry-run reports. Roadmap v2 added conservative policy parsing, policy-readiness reporting, roadmap linting, command output contracts, run-summary preview output, repository health inventory file-presence signals, and a visual project overview. Roadmap v3 has advanced the policy-aware maintenance workflow through implementation plans, proposals, validation previews, review artifacts, run-history records, validation-result handoff, orchestration readiness, command-execution handoff, executor gates, executor contracts, a read-only executor dry-run, a narrow opt-in local executor that can run one exact validation command without a shell, explicit executor-result persistence handoff, guarded executor-handoff persistence, validation-result audits, executor-observation audits with fail-closed gating, latest-limited history audit windows, `forge content-audit` with installed-package semantic CI assertions, hardened expected-file area parsing for hidden policy paths, `forge diff-source-handoff` for comparing explicit content-audit outputs before patch-adjacent workflows, `forge diff-source-handoff --require-clear` for fail-closed gating over that comparison evidence, and `forge patch-intent-review --require-ready` for fail-closed patch-intent readiness from supplied diff-source evidence. Product commands still do not enforce policy, generate patches, execute arbitrary implementation plans, inspect git diffs, verify commits, check workflow status, or commit changes.

## Technical debt

The CLI can select work, describe policy boundaries, build reviewable plans and proposals, describe validation intent, preview validation command candidates, review explicit paths, audit explicit file-content metadata without printing content, compare supplied content-audit JSON outputs, fail closed on non-clear diff-source evidence when requested, review patch-intent readiness from supplied diff-source evidence, combine review signals, preview and inspect durable run-history records, attach externally supplied validation results, expose orchestration readiness, expose command-execution handoff data, expose executor precondition gates, define an executor contract, dry-run one exact executor candidate command, run one exact confirmed local validation command without a shell, show the exact explicit command for persisting the observed executor result, persist reviewed executor-run JSON through guarded validation-result semantics, audit saved validation observations, audit aggregate saved executor observations across latest-limited direct history records, and preserve hidden path tokens in planned file-area parsing when punctuation follows. It does not yet append to a hash-linked long-lived history index, inspect git diffs, generate patches, verify commits, check workflow status, or execute approved implementation plans. Runtime test execution and main-branch CI observation were unavailable from the automation environment for the latest direct commits.

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
Expected files or areas: `src/autonomous_forge/`, `tests/`, README, `docs/`, `.ai/`, `.forge/`.
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
Acceptance criteria: Outputs are deterministic, text and JSON behavior are covered where applicable, CI smoke checks exercise live repository inputs, execution is limited to one exact confirmed no-shell validation command, writes require explicit confirmation, and patch/diff generation remains absent.
Validation: Deterministic tests and static review were completed through the GitHub repository API. Installed-package CI smoke coverage exercises the current command chain. Direct local checkout execution remained unavailable in this environment.
Risks or assumptions: These surfaces are advisory except for explicit local validation execution and explicit local persistence. They must not imply arbitrary command execution, patch generation, git-diff inspection, approval, automatic write persistence, or policy enforcement.
Notes: Historical detailed task records remain available in repository history.

### AUTO-057 through AUTO-064 — Content audit and patch-intent evidence readiness
Priority: P1
Status: DONE

Goal: Add read-only content-audit checkpoints, compare supplied content-audit outputs, provide fail-closed evidence gates, and review patch-intent readiness before future patch or git-diff workflows rely on explicit file-content evidence.
Why it matters: Patch-adjacent workflows need a safe bridge between policy-reviewed paths, actual file-content metadata, and patch-intent readiness without printing content, generating patches, inspecting git diffs, or treating changed evidence as safe by default.
Scope: Add `forge content-audit --format text|json`, audit explicit repository-relative paths for policy status, bounded UTF-8 metadata, configured secret-like markers, and conservative review status; keep limited history audits focused on newest filename-sorted records; add installed-package CI semantic assertions for live content-audit output; harden hidden expected-file path parsing; add `forge diff-source-handoff --format text|json` to compare two supplied content-audit JSON outputs; add `forge diff-source-handoff --require-clear`; add `forge patch-intent-review --format text|json` with `--require-ready` to gate future patch-intent description on unchanged clear diff-source evidence.
Expected files or areas: `src/autonomous_forge/content_audit.py`, `src/autonomous_forge/diff_source_handoff.py`, `src/autonomous_forge/patch_intent_review.py`, `src/autonomous_forge/cli_entry.py`, `tests/test_content_audit*.py`, `tests/test_diff_source_handoff.py`, `tests/test_patch_intent_review.py`, `tests/test_cli_entry.py`, `.github/workflows/test.yml`, README, `docs/`, `.ai` records.
Acceptance criteria: Content-audit output stays read-only, constrains paths to the repository root, never prints file contents, reports blocked/unknown/unreadable/secret-like cases conservatively, supports text and JSON output, and CI asserts clear live-path semantics after installation. Diff-source handoff reads supplied audit JSON only, constrains audit-output paths under the configured root, refuses malformed or duplicate audit entries, reports changed observations deterministically, supports `--require-clear`, and never reads repository file contents, inspects git diffs, generates patches, or runs commands. Patch-intent review reads supplied diff-source JSON only, reports ready only for unchanged clear no-attention evidence, supports `--require-ready`, and never generates or applies patches.
Validation: Static review completed through the GitHub repository API. Deterministic unit/CLI tests cover clear allowed files, prohibited files, unknown policy areas, secret-like marker reporting without value disclosure, JSON output, path traversal refusal, CLI text/JSON output, missing-policy refusal, unchanged/changed/added/removed audit comparisons, non-clear after-audit handling, unsafe audit-output paths, malformed JSON, duplicate audited paths, installed-entrypoint diff-source behavior, clear gate pass/fail behavior, patch-intent ready/blocked behavior, and CI smoke assertions for unchanged live content-audit/diff-source/patch-intent evidence gates.
Risks or assumptions: Secret-marker checks are intentionally simple guard signals, not complete secret scanning. A clear content-audit, unchanged diff-source handoff, or ready patch-intent review result does not approve patches, prove correctness, or replace human review. `--require-clear` and `--require-ready` change only the process exit code.
Notes: The next safe step is a read-only patch-intent description artifact that consumes ready patch-intent review evidence without generating or applying patches automatically.

## Future Ideas

- Hash-linked local run reports.
- Optional issue import.
- Policy-aware changed-file summaries.
- Explicit validation orchestration after validation plans are reviewable.
- Read-only patch-intent description from ready patch-intent review evidence.

## Do Not Change Without Explicit Human Approval

- Remote and branch settings.
- Repository visibility and access controls.
- Production infrastructure.
- Features that change repository files outside documented safe paths.
- Sensitive configuration handling, telemetry, analytics, billing, or deployment behavior.
