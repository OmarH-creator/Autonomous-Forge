# Autonomous Forge Roadmap

## Product vision

Autonomous Forge helps a repository keep a clear improvement plan, choose one safe task, produce reviewable planning artifacts, inspect proposed diffs, review validation status, run tightly scoped validation, apply explicitly confirmed patches, record validation evidence, summarize commit readiness, preview commit metadata, create one explicitly confirmed local commit, verify that created commit, review local commit trust metadata, summarize branch-protection-aware trusted push readiness, run a branch-policy-enforcing explicitly confirmed fast-forward-only non-force push handoff, verify that the pushed commit is reachable from the intended remote branch with clear status evidence, preserve hash-linked durable maintenance evidence bundles, verify persisted bundle source-report integrity, summarize persisted bundle replay readiness, link completed bundles into run history, preserve implementation-grade plan fields through downstream proposal, validation-plan, validation-preview, validation-orchestration, executor handoff, executor-run, and validation-result-write artifacts, and expose retained validation context in run-history read/compare review surfaces.

## Product scope and non-goals

The first product remains a local Python CLI. It is not a hosted service, deployment system, permission manager, uncontrolled executor, automatic commit bot, force-push bot, branch-protection manager, remote-configuration manager, workflow-rerun bot, polling service, or cryptographic identity authority.

## Current architecture

The repository contains a Python package under `src/autonomous_forge`, tests under `tests/`, command docs under `docs/`, workflow checks under `.github/workflows/`, policy under `.forge/`, and durable memory under `.ai`. The installed `forge` entry point routes the historical CLI plus extension commands through `src/autonomous_forge/cli_entry_patch.py`; compatibility console scripts remain available through `pyproject.toml`.

## Current implementation status

Roadmap v3 now reaches guarded local commit creation, post-commit verification, commit trust review with optional allowed-signer policy, branch-protection-aware trusted pre-push readiness review, branch-policy-enforcing explicitly confirmed fast-forward-only non-force push handoff, post-push verification, durable maintenance evidence bundles, SHA-256 source-report fingerprints for those bundles, persisted bundle source-report verification, replay summaries for verified persisted bundles, opt-in run-history links for completed pushed bundles, implementation-grade `forge plan` fields, plan-enriched `forge propose` artifacts, plan/proposal-enriched `forge validate-plan` artifacts, enriched validation-preview/orchestration artifacts, enriched executor handoff/gate/contract/dry-run artifacts, enriched executor-run/result-persistence handoff artifacts, validation-result writes that retain implementation context in persisted records, and run-history read/compare surfaces that expose retained validation context. Product commands still do not force-push, push tags, change remotes, change branch protections, enforce a full cryptographic identity policy, rerun workflows, or poll remote workflow completion.

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
Scope: Add supplied git-diff review, binary/metadata hardening, supplied/live commit-status review, combined change-readiness, and patch-generation preview.
Expected files or areas: `src/autonomous_forge/`, `tests/`, README, `docs/`, `.ai` records.
Acceptance criteria: Patch-generation preview blocks unsafe/unready inputs, produces bounded diff text, and does not apply patches or change files.
Validation: Static source/test/documentation review completed through the GitHub repository API with deterministic tests.
Risks or assumptions: Generated patch previews can expose non-secret repository text by design and rely on simple secret-marker refusal.
Notes: Completed before confirmed patch application.

### AUTO-088 — Explicitly confirmed guarded patch apply through AUTO-098
Priority: P1
Status: DONE
Goal: Complete a guarded local maintenance loop from patch application through validation, local commit creation, push handoff, and post-push verification.
Why it matters: The workflow needs concrete, auditable transitions from proposed file change to validated local change, reviewed commit, guarded push, and post-push evidence without becoming an uncontrolled bot.
Scope: Add `forge patch-apply`, `forge post-apply-validation`, live/supplied `forge commit-status-review`, `forge commit-readiness`, `forge commit-proposal-preview`, `forge commit-create`, `forge commit-verify`, `forge push-readiness`, `forge push-handoff`, `forge post-push-verify`, compatibility routes, tests, focused docs, README usage, CI help-smoke coverage, and project-memory updates.
Expected files or areas: `src/autonomous_forge/`, `tests/`, `docs/`, `pyproject.toml`, `.github/workflows/test.yml`, README, and `.ai` records.
Acceptance criteria: Write-capable commands require explicit confirmation, stage/push only reviewed paths or commits, never force-push or mutate remote configuration, and verification gates fail closed when required evidence is missing, stale, unsafe, or unclear.
Validation: Static source/test/docs/workflow review completed through the GitHub repository API. Direct full repository checkout/test execution remained unavailable in this environment.
Risks or assumptions: Commands intentionally mutate local files, local commits, or remote branches only when explicitly confirmed. They trust supplied evidence and local git/GitHub CLI output.
Notes: Completed before durable maintenance evidence bundling.

### AUTO-099 — Durable maintenance evidence bundle through AUTO-108
Priority: P1
Status: DONE
Goal: Add durable evidence bundling, source-report fingerprinting, persisted bundle verification, replay summaries, and run-history links for completed pushed bundles.
Why it matters: Maintainers need portable run artifacts and discoverable history pointers that tie the safe end-to-end maintenance loop together after patch, validation, commit, push, and post-push gates have completed.
Scope: Add `forge maintenance-evidence-bundle`, `forge maintenance-bundle-verify`, `forge maintenance-replay-summary`, history-link support, compatibility routes, deterministic tests, docs, README workflow examples, CI help smoke, and project-memory updates.
Expected files or areas: `src/autonomous_forge/`, `tests/`, `docs/`, `pyproject.toml`, `.github/workflows/test.yml`, README, and `.ai` records.
Acceptance criteria: Bundles require completed evidence, validate matching commit and reviewed paths across the chain, record SHA-256 source-report fingerprints, detect later drift, summarize replayability, and write bounded JSON/history links only with explicit confirmation.
Validation: Static source/test/docs review completed through the GitHub repository API. Direct full checkout/full pytest execution remained unavailable in this environment.
Risks or assumptions: Bundles and links trust supplied JSON evidence and source-report hashes; they do not sign evidence, prove author identity, rerun workflows, or establish a cryptographic trust model.
Notes: Completed before plan-output enrichment.

### AUTO-109 — Enriched policy-aware forge plan output
Priority: P1
Status: DONE
Goal: Make `forge plan` produce an implementation-grade plan artifact with concrete steps, expected file changes, validation steps, and risks.
Why it matters: The immediate product objective is a policy-aware `forge plan` command; downstream proposal, validation, and execution stages need structured implementation details rather than only prose fields.
Scope: Extend `src/autonomous_forge/planner.py` to derive deterministic `implementation_steps`, `expected_file_changes`, `validation_steps`, and `risk_register` values from roadmap and policy inputs; update planner tests, command docs, README, and `.ai` records.
Expected files or areas: `src/autonomous_forge/planner.py`, `tests/test_planner.py`, `docs/COMMANDS.md`, README, and `.ai` records.
Acceptance criteria: Text output includes expected file changes, implementation steps, validation steps, and risk register sections; JSON output includes matching structured fields; behavior remains local-first, read-only, deterministic, and covered by tests.
Validation: Scratch syntax compilation passed for the updated planner and planner tests before repository writes. Static source/test/docs review completed through the GitHub repository API. Direct full checkout/full pytest execution remained unavailable in this environment.
Risks or assumptions: Roadmap prose splitting is intentionally simple and deterministic; maintainers should keep plan fields concise and reviewable.
Notes: Completed before plan-enriched proposals.

### AUTO-110 — Plan-enriched change proposal artifacts
Priority: P1
Status: DONE
Goal: Carry implementation-grade `forge plan` fields into `forge propose` artifacts.
Why it matters: Downstream review should preserve the same expected file changes, implementation steps, validation steps, and risk register that the planner selected instead of reducing them back to generic planned operations.
Scope: Update `src/autonomous_forge/proposal.py` to consume `expected_file_changes`, `implementation_steps`, `validation_steps`, and `risk_register` from structured plan data; keep backward-compatible proposal fields; update proposal tests, command docs, README, and `.ai` records.
Expected files or areas: `src/autonomous_forge/proposal.py`, `tests/test_proposal.py`, `docs/COMMANDS.md`, README, and `.ai` records.
Acceptance criteria: Proposal text includes expected file changes, implementation steps, validation steps, and risk register sections; JSON output includes matching structured fields while preserving planned file/operation fields; behavior remains local-first, read-only, deterministic, and covered by tests.
Validation: Scratch syntax compilation passed for the updated proposal module and proposal tests before repository writes. Static source/test/docs review completed through the GitHub repository API. Direct full checkout/full pytest execution remained unavailable in this environment.
Risks or assumptions: Proposal artifacts trust the planner's deterministic field normalization and remain advisory only.
Notes: Completed before plan-enriched validation plans.

### AUTO-111 — Plan-enriched validation plan artifacts
Priority: P1
Status: DONE
Goal: Carry implementation-grade `forge plan` and `forge propose` fields into `forge validate-plan` artifacts.
Why it matters: Validation handoff should preserve expected file changes, implementation steps, validation steps, and risk register entries before moving toward validation preview and executor orchestration.
Scope: Update `src/autonomous_forge/validation.py` to consume `expected_file_changes`, `implementation_steps`, `validation_steps`, and `risk_register` from proposal data; keep backward-compatible `expected_file_areas` and advisory path checks; update validation tests, command docs, README, and `.ai` records.
Expected files or areas: `src/autonomous_forge/validation.py`, `tests/test_validation.py`, `docs/COMMANDS.md`, README, and `.ai` records.
Acceptance criteria: Validation-plan text includes expected file changes, implementation steps, validation steps, risk register, expected file areas, and path checks; JSON output includes matching structured fields while preserving existing path-check keys; behavior remains local-first, read-only, deterministic, and covered by tests.
Validation: Scratch syntax compilation passed for the updated validation module and validation tests before repository writes. Static source/test/docs review completed through the GitHub repository API. Direct full checkout/full pytest execution remained unavailable in this environment.
Risks or assumptions: Validation-plan artifacts trust the proposal's deterministic planner field propagation and remain advisory only.
Notes: Completed before enriched validation-preview and orchestration artifacts.

### AUTO-112 — Plan-enriched validation preview and orchestration artifacts
Priority: P1
Status: DONE
Goal: Carry implementation-grade validation-plan fields into `forge validation-preview` and `forge validation-orchestration` artifacts.
Why it matters: Validation preview and orchestration are the handoff before executor contract/dry-run behavior; they need expected file changes, implementation steps, validation steps, and risk register context alongside command candidates and run-history guards.
Scope: Update `src/autonomous_forge/validation_preview.py` and `src/autonomous_forge/validation_orchestration.py` to preserve enriched validation-plan fields; update focused tests, command docs, README, and `.ai` records.
Expected files or areas: `src/autonomous_forge/validation_preview.py`, `src/autonomous_forge/validation_orchestration.py`, `tests/test_validation_preview.py`, `tests/test_validation_orchestration.py`, `docs/COMMANDS.md`, README, and `.ai` records.
Acceptance criteria: Validation-preview and validation-orchestration text include expected file changes, implementation steps, validation steps, and risk register sections; JSON output includes matching structured fields while preserving existing command-candidate/history guard keys; behavior remains local-first, read-only, deterministic, and covered by focused tests.
Validation: Scratch syntax compilation passed for the updated preview/orchestration modules and tests before repository writes. Static source/test/docs review completed through the GitHub repository API. Direct full checkout/full pytest execution remained unavailable in this environment.
Risks or assumptions: Preview and orchestration artifacts trust validation-plan field propagation and remain advisory only; command candidates are still classification hints, not execution permission.
Notes: Completed before enriched executor handoff context.

### AUTO-113 — Enriched executor handoff context
Priority: P1
Status: DONE
Goal: Carry implementation-grade validation context into executor handoff, gate, contract, and dry-run artifacts.
Why it matters: The executor review path is where validation commands become eligible for explicit confirmation; it must retain expected file changes, implementation steps, validation steps, and risk register context alongside command candidates and result persistence targets.
Scope: Update `src/autonomous_forge/command_execution_handoff.py`, `src/autonomous_forge/executor_gate.py`, `src/autonomous_forge/executor_contract.py`, and `src/autonomous_forge/executor_dry_run.py`; update focused tests, executor context docs, README, and `.ai` records.
Expected files or areas: executor handoff/gate/contract/dry-run modules, matching tests, `docs/EXECUTOR_CONTEXT.md`, README, and `.ai` records.
Acceptance criteria: Command-execution handoff, executor gate, executor contract, and executor dry-run text/JSON include expected file changes, implementation steps, validation steps, and risk register fields while preserving existing command/gate/result keys; behavior remains local-first, deterministic, and covered by focused tests.
Validation: Static source/test/docs review completed through the GitHub repository API. Direct full checkout/full pytest execution remained unavailable in this environment.
Risks or assumptions: Executor context fields remain advisory; confirmed executor behavior still requires exact command matching and explicit confirmation.
Notes: Completed before enriched executor-run context.

### AUTO-114 — Enriched executor-run result context
Priority: P1
Status: DONE
Goal: Carry implementation-grade executor context into `forge executor-run` output and its validation-result persistence handoff.
Why it matters: Once a validation command is observed locally, the result should remain tied to expected file changes, implementation steps, validation steps, and risk register context before anyone persists that result into durable run history.
Scope: Update `src/autonomous_forge/executor_run.py` and `tests/test_executor_run.py`; update executor context docs, README, and `.ai` records.
Expected files or areas: `src/autonomous_forge/executor_run.py`, `tests/test_executor_run.py`, `docs/EXECUTOR_CONTEXT.md`, README, and `.ai` records.
Acceptance criteria: Executor-run text/JSON include expected file changes, implementation steps, validation steps, and risk register fields for both blocked and executed runs; `persistence_handoff` includes the same fields while preserving existing write-command keys; behavior remains explicit-confirmation-only, no-shell, local-first, and covered by focused tests.
Validation: Static source/test/docs review completed through the GitHub repository API. Direct full checkout/full pytest execution remained unavailable in this environment.
Risks or assumptions: Executor-run and persistence-handoff context fields remain advisory; actual saved validation-result records still require a separate explicit `validation-result-write --confirm-write` action.
Notes: Completed before validation-result-write context retention.

### AUTO-115 — Validation-result-write context retention
Priority: P1
Status: DONE
Goal: Carry implementation-grade executor context into persisted validation-result-write records.
Why it matters: After a local validation result is attached, persisted evidence should not lose the expected file changes, implementation steps, validation steps, or risk register that explain what the validation was meant to prove.
Scope: Update `src/autonomous_forge/validation_result_writer.py` to copy existing context fields into `record.validation_context`, add focused tests, document persisted fields, update README, and refresh `.ai` records.
Expected files or areas: `src/autonomous_forge/validation_result_writer.py`, `tests/test_validation_result_writer.py`, `docs/VALIDATION_RESULT_WRITES.md`, README, and `.ai` records.
Acceptance criteria: Validation-result writes preserve existing implementation context in the saved record, report retained context fields through the Python API, keep CLI JSON backward-compatible, require explicit confirmation, and retain existing path/result safety checks.
Validation: Static source/test/docs review completed through the GitHub repository API. Direct full checkout/full pytest execution remained unavailable in this environment.
Risks or assumptions: Context fields are copied from trusted local run-history JSON and remain advisory; the writer does not verify that validation actually covered every retained field.
Notes: Completed before validation-context-aware run-history review surfaces.

### AUTO-116 — Validation-context-aware run-history read and compare
Priority: P1
Status: DONE
Goal: Expose retained validation context in `forge run-history-read` and compare it in `forge run-history-compare`.
Why it matters: AUTO-115 saved implementation context beside validation results, but maintainers still needed an audit surface that exposed that context without opening raw JSON.
Scope: Update `src/autonomous_forge/run_history_reader.py` and `src/autonomous_forge/run_history_compare.py`; add focused tests; update run-history docs, README, and `.ai` records.
Expected files or areas: `src/autonomous_forge/run_history_reader.py`, `src/autonomous_forge/run_history_compare.py`, `tests/test_run_history_reader.py`, `tests/test_run_history_compare.py`, `docs/RUN_HISTORY_READS.md`, `docs/RUN_HISTORY_COMPARISONS.md`, README, and `.ai` records.
Acceptance criteria: Single-record text/JSON summaries expose retained validation context when present, comparisons include validation context as a changed/unchanged field, malformed validation-context values fail closed, behavior remains read-only and deterministic, and focused tests cover the new surfaces.
Validation: Scratch syntax compilation passed for the changed modules and focused tests. Static source/test/docs review completed through the GitHub repository API. Direct full checkout/full pytest execution remained unavailable in this environment.
Risks or assumptions: Validation context remains advisory saved JSON evidence; read/compare surfaces do not prove validation coverage or verify commits, workflows, diffs, patches, or policy compliance.
Notes: Next safe step is using retained validation context in maintenance bundle or replay review surfaces.

## Future Ideas

- Hash-linked local run reports.
- Optional issue import.
- Policy-aware changed-file summaries.
- Branch protection and workflow-status replay summaries.
- Use retained validation context in maintenance bundle or replay review surfaces.
