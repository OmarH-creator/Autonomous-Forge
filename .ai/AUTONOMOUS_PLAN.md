# Autonomous Forge Roadmap

## Product vision

Autonomous Forge helps a repository keep a clear improvement plan, choose one safe task, produce reviewable planning artifacts, inspect proposed diffs, review validation status, run tightly scoped validation, apply explicitly confirmed patches, record validation evidence, summarize commit readiness, preview commit metadata, create one explicitly confirmed local commit, verify that created commit, review local commit trust metadata, summarize branch-protection-aware trusted push readiness, run a branch-policy-enforcing explicitly confirmed fast-forward-only non-force push handoff, verify that the pushed commit is reachable from the intended remote branch with clear status evidence, preserve hash-linked durable maintenance evidence bundles, verify persisted bundle source-report integrity, summarize persisted bundle replay readiness, link completed bundles into run history, review run-history link quality, preserve implementation-grade plan fields through downstream proposal, validation-plan, validation-preview, validation-orchestration, executor handoff, executor-run, validation-result-write, run-history review, maintenance replay artifacts, newly generated maintenance bundles/history links, replay consistency checks, and compact replay policy gates that compare retained implementation context with reviewed paths and preserved validation steps.

## Product scope and non-goals

The first product remains a local Python CLI. It is not a hosted service, deployment system, permission manager, uncontrolled executor, automatic commit bot, force-push bot, branch-protection manager, remote-configuration manager, workflow-rerun bot, polling service, or cryptographic identity authority.

## Current architecture

The repository contains a Python package under `src/autonomous_forge`, tests under `tests/`, command docs under `docs/`, workflow checks under `.github/workflows/`, policy under `.forge/`, and durable memory under `.ai`. The installed `forge` entry point routes the historical CLI plus extension commands through `src/autonomous_forge/cli_entry_patch.py`; compatibility console scripts remain available through `pyproject.toml`.

## Current implementation status

Roadmap v3 now reaches guarded local commit creation, post-commit verification, commit trust review with optional allowed-signer policy, branch-protection-aware trusted pre-push readiness review, branch-policy-enforcing explicitly confirmed fast-forward-only non-force push handoff, post-push verification, durable maintenance evidence bundles, SHA-256 source-report fingerprints for those bundles, persisted bundle source-report verification, replay summaries for verified persisted bundles, opt-in run-history links for completed pushed bundles, implementation-grade `forge plan` fields, plan-enriched `forge propose` artifacts, plan/proposal-enriched `forge validate-plan` artifacts, enriched validation-preview/orchestration artifacts, enriched executor handoff/gate/contract/dry-run artifacts, enriched executor-run/result-persistence handoff artifacts, validation-result writes that retain implementation context in persisted records, run-history read/compare surfaces that expose retained validation context, maintenance replay summaries that expose retained validation context when persisted bundles include it, maintenance bundle creation/history-link outputs that preserve supported validation context automatically, maintenance replay consistency checks that compare retained expected file changes and validation steps against reviewed bundle evidence, compact replay policy-gate summaries for reviewer triage, and history-link quality review before deeper replay verification. Product commands still do not force-push, push tags, change remotes, change branch protections, enforce a full cryptographic identity policy, rerun workflows, or poll remote workflow completion.

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
Expected files or areas: `src/autonomous_forge/`, tests, README, docs, `.ai` records.
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

### AUTO-109 — Enriched policy-aware forge plan output through AUTO-116
Priority: P1
Status: DONE
Goal: Carry implementation-grade `forge plan` context through proposal, validation, orchestration, executor, persistence, and run-history review artifacts.
Why it matters: The immediate product objective is a policy-aware `forge plan` command; downstream stages need structured implementation details rather than only prose fields.
Scope: Add structured `expected_file_changes`, `implementation_steps`, `validation_steps`, and `risk_register` propagation through planner, proposal, validation-plan, validation-preview/orchestration, executor handoff/gate/contract/dry-run/run, validation-result-write, run-history-read, and run-history-compare surfaces.
Expected files or areas: `src/autonomous_forge/`, `tests/`, `docs/`, README, and `.ai` records.
Acceptance criteria: Text/JSON outputs preserve implementation context through the safe workflow; explicit writes remain confirmation-gated; read surfaces expose retained context deterministically; focused tests cover each step.
Validation: Static source/test/docs review completed through the GitHub repository API with focused tests across the affected modules. Direct full checkout/full pytest execution remained unavailable in this environment.
Risks or assumptions: Context fields are advisory unless a later stage explicitly validates them; readers and writers do not prove validation coverage.
Notes: Completed before validation-context-aware maintenance replay summaries.

### AUTO-117 — Validation-context-aware maintenance replay summaries
Priority: P1
Status: DONE
Goal: Expose retained validation context in `forge maintenance-replay-summary` for persisted bundles that include implementation-plan context.
Why it matters: Completed maintenance bundles should show whether replay evidence preserved expected file changes, implementation steps, validation steps, and risks without requiring maintainers to open raw JSON.
Scope: Update `src/autonomous_forge/maintenance_replay_summary.py`, focused replay tests, maintenance bundle docs, README, and `.ai` records.
Expected files or areas: `src/autonomous_forge/maintenance_replay_summary.py`, `tests/test_maintenance_replay_summary.py`, `docs/MAINTENANCE_EVIDENCE_BUNDLE.md`, README, and `.ai` records.
Acceptance criteria: Replay summaries report validation-context presence, supported field names, per-field counts, and total retained context items; malformed validation context blocks replayability; older bundles without context remain readable; behavior remains read-only and deterministic.
Validation: Static source/test/docs review completed through the GitHub repository API. Direct full checkout/full pytest execution remained unavailable from this environment.
Risks or assumptions: Validation context remains advisory persisted JSON evidence; replay summaries do not prove validation covered every planned file, implementation step, validation step, or risk.
Notes: Completed before validation-context preservation in maintenance bundle creation/history links.

### AUTO-118 — Validation-context-preserving maintenance bundle creation and history links
Priority: P1
Status: DONE
Goal: Preserve supported upstream validation context in newly generated maintenance bundles and optional run-history link pointers.
Why it matters: Replay summaries can only audit implementation-plan context if bundle creation keeps that context when building durable run evidence.
Scope: Update `src/autonomous_forge/maintenance_evidence_bundle.py`, add focused validation-context bundle tests, update maintenance bundle docs, README, and `.ai` records.
Expected files or areas: `src/autonomous_forge/maintenance_evidence_bundle.py`, `tests/test_maintenance_bundle_validation_context.py`, `docs/MAINTENANCE_EVIDENCE_BUNDLE.md`, README, and `.ai` records.
Acceptance criteria: Bundle output retains `expected_file_changes`, `implementation_steps`, `validation_steps`, and `risk_register` from upstream evidence; history links retain the same context; malformed context blocks completion; text output reports context counts; older evidence without context remains compatible.
Validation: Local scratch syntax compilation passed. Focused scratch pytest for the new bundle-context tests passed 4 tests. Static source/test/docs review completed through the GitHub repository API. Direct full checkout/full pytest execution remained unavailable from this environment.
Risks or assumptions: Retained context is advisory JSON evidence; bundle creation still does not prove validation covered every planned file, step, or risk.
Notes: Completed before replay consistency checks.

### AUTO-119 — Validation-context consistency checks in maintenance replay
Priority: P1
Status: DONE
Goal: Block replayability when retained validation context no longer matches reviewed bundle paths or preserved validation steps.
Why it matters: Durable maintenance bundles should not be trusted as replayable when their retained implementation-plan context has drifted away from the reviewed evidence chain.
Scope: Update `src/autonomous_forge/maintenance_replay_summary.py`, focused replay tests, maintenance bundle docs, README, and `.ai` records.
Expected files or areas: `src/autonomous_forge/maintenance_replay_summary.py`, `tests/test_maintenance_replay_summary.py`, `docs/MAINTENANCE_EVIDENCE_BUNDLE.md`, README, and `.ai` records.
Acceptance criteria: Replay summaries expose `validation_context_consistency`; reviewed paths must be represented in retained expected file changes when those changes exist; retained validation steps must appear in bundle validation steps; mismatches block replayability; older bundles without context remain backward-compatible.
Validation: Static source/test/docs review completed through the GitHub repository API. Direct full checkout/full pytest execution remained unavailable from this environment.
Risks or assumptions: The consistency check compares advisory JSON evidence and does not prove actual validation coverage or policy compliance.
Notes: Completed before compact replay policy gates.

### AUTO-120 — Compact replay policy-gate summaries
Priority: P1
Status: DONE
Goal: Provide compact pass/fail/advisory replay policy gates for persisted maintenance bundles.
Why it matters: Maintainers need a quick reviewer-facing answer for which replay gates passed, failed, or remain advisory without reading raw replay blockers or full bundle JSON.
Scope: Add `forge-maintenance-replay-policy-summary`, focused policy-summary tests, docs, README usage, `pyproject.toml` script wiring, and `.ai` records.
Expected files or areas: `src/autonomous_forge/maintenance_replay_policy_summary.py`, `src/autonomous_forge/maintenance_replay_policy_summary_cli.py`, `tests/test_maintenance_replay_policy_summary.py`, `docs/MAINTENANCE_REPLAY_POLICY_SUMMARY.md`, `pyproject.toml`, README, and `.ai` records.
Acceptance criteria: Policy summaries report stable gates for bundle completeness, source-report verification, evidence-chain completeness, reviewed paths, validation steps, and validation-context consistency; missing optional validation context is advisory; failed gates block the compact policy status; behavior is local-first and read-only.
Validation: Local scratch pytest passed 5 focused policy-summary tests. Static source/test/docs review completed through the GitHub repository API. Direct full checkout/full pytest execution remained unavailable from this environment.
Risks or assumptions: Policy gates summarize persisted JSON evidence and do not rerun validation, inspect diffs, verify branch protections, verify signatures, poll workflow status, or prove coverage.
Notes: Completed before history-link quality review.

### AUTO-121 — Maintenance history-link quality review
Priority: P1
Status: DONE
Goal: Review run-history bundle links before maintainers open full bundles for replay verification.
Why it matters: Maintainers need a compact pointer-level quality check that says whether a `.ai/run-history/` link has enough durable information to continue into hash-verified replay.
Scope: Add `forge maintenance-history-link-review`, `forge-maintenance-history-link-review`, focused tests, docs, README usage, `pyproject.toml` script wiring, CLI routing, and `.ai` records.
Expected files or areas: `src/autonomous_forge/maintenance_history_link_review.py`, `src/autonomous_forge/maintenance_history_link_review_cli.py`, `tests/test_maintenance_history_link_review.py`, `docs/MAINTENANCE_HISTORY_LINK_REVIEW.md`, `src/autonomous_forge/cli_entry_patch.py`, `pyproject.toml`, README, and `.ai` records.
Acceptance criteria: Reviews require a supported history-link schema, report stable quality gates for link write status, bundle pointer/hash, reviewed paths, validation steps, source-report stages, and retained validation context; missing optional validation context is advisory; missing required pointer evidence blocks readiness; behavior is local-first and read-only.
Validation: Static source/test/docs review completed through the GitHub repository API. Direct full checkout/full pytest execution remained unavailable from this environment.
Risks or assumptions: The command reviews only the history pointer; `forge maintenance-replay-summary` is still required to read the linked bundle and recompute source-report hashes.
Notes: Next safe step is connecting ready history links to bundle replay verification.

## Future Ideas

- Hash-linked local run reports.
- Optional issue import.
- Policy-aware changed-file summaries.
- Branch protection and workflow-status replay summaries.
- Run-history link to bundle replay handoff.
