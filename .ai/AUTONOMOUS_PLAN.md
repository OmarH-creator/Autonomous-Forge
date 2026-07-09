# Autonomous Forge Roadmap

## Product vision

Autonomous Forge helps a repository keep a clear improvement plan, choose one safe task, produce reviewable planning artifacts, inspect proposed diffs, review validation status, run tightly scoped validation, apply explicitly confirmed patches, record validation evidence, summarize commit readiness, preview commit metadata, create one explicitly confirmed local commit, verify that created commit, summarize push readiness, run an explicitly confirmed non-force push handoff, verify that the pushed commit is reachable from the intended remote branch with clear status evidence, and preserve durable maintenance evidence bundles.

## Product scope and non-goals

The first product remains a local Python CLI. It is not a hosted service, deployment system, permission manager, uncontrolled executor, automatic commit bot, force-push bot, branch-protection manager, remote-configuration manager, workflow-rerun bot, or cryptographic trust system.

## Current architecture

The repository contains a Python package under `src/autonomous_forge`, tests under `tests/`, command docs under `docs/`, workflow checks under `.github/workflows/`, policy under `.forge/`, and durable memory under `.ai/`. The installed `forge` entry point routes the historical CLI plus extension commands through `src/autonomous_forge/cli_entry_patch.py`; compatibility console scripts remain available through `pyproject.toml`.

## Current implementation status

Roadmap v3 now reaches guarded local commit creation, post-commit verification, pre-push readiness review, explicitly confirmed non-force push handoff, post-push verification, and durable maintenance evidence bundles after patch apply, post-apply validation, live/supplied status review, commit readiness, and commit proposal preview. Product commands still do not force-push, push tags, change remotes, change branch protections, verify commit signatures, cryptographically verify identity, rerun workflows, or poll remote workflow completion.

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
Validation: Static source/test/docs/workflow review completed through the GitHub repository API. Scratch syntax compilation and focused pytest covered the latest post-push verification module, CLI, and tests; `tests/test_post_push_verify.py` passed with 8 tests in scratch. Direct full repository checkout/test execution remained unavailable in this environment.
Risks or assumptions: Commands intentionally mutate local files, local commits, or remote branches only when explicitly confirmed. They trust supplied evidence and local git/GitHub CLI output; they do not verify signatures, authorship, cryptographic trust, or workflow correctness beyond supplied status fields.
Notes: Completed before durable maintenance evidence bundling.

### AUTO-099 — Durable maintenance evidence bundle
Priority: P1
Status: DONE
Goal: Add a durable evidence bundle that links completed patch apply, post-apply validation, commit verification, push handoff, and post-push verification reports.
Why it matters: Maintainers need one portable run artifact that ties the safe end-to-end maintenance loop together after the patch, validation, commit, push, and post-push gates have completed.
Scope: Add `forge maintenance-evidence-bundle`, compatibility route, deterministic tests, docs, README workflow examples, CI help smoke, and project-memory updates.
Expected files or areas: `src/autonomous_forge/`, `tests/`, `docs/`, `pyproject.toml`, `.github/workflows/test.yml`, README, and `.ai` records.
Acceptance criteria: The bundle requires completed evidence, validates matching commit and reviewed paths across the chain, reports blockers for inconsistent evidence, and writes one bounded JSON bundle only with explicit confirmation.
Validation: Scratch syntax compilation covered the new module, CLI, and tests. Focused scratch pytest for `tests/test_maintenance_evidence_bundle.py` passed with 7 tests. Static source/test/docs/workflow review completed through the GitHub repository API; CI smoke now covers primary and compatibility help routes.
Risks or assumptions: Bundles trust supplied JSON evidence and do not hash source reports yet, verify signatures, rerun workflows, or prove cryptographic identity.
Notes: Next safe step is hash-linked bundle integrity checks for durable report provenance.

## Future Ideas

- Hash-linked local run reports.
- Optional issue import.
- Policy-aware changed-file summaries.
- Signed commit verification before any push workflow.
- Hash-linked maintenance evidence bundle integrity checks.
