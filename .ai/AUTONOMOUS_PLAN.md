# Autonomous Forge Roadmap

## Product vision

Autonomous Forge helps a repository keep a clear improvement plan, choose one safe task, produce reviewable planning artifacts, inspect proposed diffs, review validation status, run tightly scoped validation, apply explicitly confirmed patches, record validation evidence, summarize commit and push readiness, preserve durable evidence bundles, link completed bundles into run history, replay those bundles, hand off preservation guidance, compare completed handoffs, rank ready preservation candidates, prepare integrity-checked archive manifests, and write confirmed local archive-manifest JSON records without requiring uncontrolled autonomous behavior.

## Product scope and non-goals

The first product remains a local Python CLI. It is not a hosted service, deployment system, permission manager, uncontrolled executor, automatic commit bot, force-push bot, branch-protection manager, remote-configuration manager, workflow-rerun bot, polling service, cryptographic identity authority, or archive-copy system unless a future command adds explicit confirmation-gated archive-copy behavior.

## Current architecture

The repository contains a Python package under `src/autonomous_forge`, tests under `tests/`, command docs under `docs/`, workflow checks under `.github/workflows/`, policy under `.forge/`, and durable memory under `.ai`. The installed `forge` entry point routes the historical CLI plus extension commands through `src/autonomous_forge/cli_entry_patch.py`; compatibility console scripts remain available through `pyproject.toml`.

## Current implementation status

Roadmap v3 now reaches guarded local commit creation, post-commit verification, commit trust review, branch-protection-aware trusted pre-push readiness review, branch-policy-enforcing explicitly confirmed fast-forward-only non-force push handoff, post-push verification, durable maintenance evidence bundles, persisted bundle verification, replay summaries, opt-in run-history links for completed pushed bundles, pointer-level history-link quality review, strict linked-bundle replay verification from a ready history pointer, reviewer-facing maintenance preservation handoffs with history/bundle context consistency, comparison-oriented maintenance handoff summaries, deterministic preservation-candidate ranking for ready handoffs, integrity-checked archive-manifest previews, and confirmation-gated local archive-manifest JSON writes for selected preservation candidates. Product commands still do not force-push, push tags, change remotes, change branch protections, enforce a full cryptographic identity policy, rerun workflows, poll remote workflow completion, copy evidence files, or create archive files.

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
Expected files or areas: `src/autonomous_forge/`, tests, README, docs, `.ai` records.
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

### AUTO-117 — Validation-context-aware maintenance replay summaries through AUTO-121
Priority: P1
Status: DONE
Goal: Preserve and review implementation-plan context through maintenance bundles, replay summaries, compact replay policy gates, and history-link pointer quality review.
Why it matters: Completed maintenance bundles should show whether replay evidence preserved expected file changes, implementation steps, validation steps, and risks without requiring maintainers to open raw JSON first.
Scope: Update maintenance replay, bundle creation, replay-policy, and history-link review surfaces with retained context, consistency checks, policy gates, docs, README, and `.ai` records.
Expected files or areas: `src/autonomous_forge/maintenance_replay_summary.py`, `src/autonomous_forge/maintenance_evidence_bundle.py`, `src/autonomous_forge/maintenance_replay_policy_summary.py`, `src/autonomous_forge/maintenance_history_link_review.py`, tests, docs, README, and `.ai` records.
Acceptance criteria: Replay and history-link reviews expose stable context counts/gates, block malformed or inconsistent required evidence, preserve backward-compatible advisory behavior for missing optional context, and remain local-first/read-only.
Validation: Static source/test/docs review completed through the GitHub repository API with focused tests across affected modules. Direct full checkout/full pytest execution remained unavailable from this environment.
Risks or assumptions: Retained context is advisory JSON evidence; replay summaries do not prove validation covered every planned file, step, or risk.
Notes: Completed before linked-bundle replay from history links.

### AUTO-122 — Linked-bundle replay, handoff, comparison, and archive-manifest preview through AUTO-128
Priority: P1
Status: DONE
Goal: Connect ready run-history pointers to hash-verified bundle replay, reviewer handoffs, comparison ranking, and archive-manifest previews.
Why it matters: Maintainers need one workflow that starts from a small `.ai/run-history` pointer, checks pointer quality, verifies the referenced bundle hash, summarizes replay policy gates, ranks completed records, and previews the files that should be preserved together.
Scope: Add linked-bundle replay from history links, reviewer-facing maintenance handoffs, strict context-consistency gates, maintenance review comparison, preservation-candidate ranking, archive-manifest preview, compatibility routes, tests, docs, README, `.github/workflows/test.yml`, `pyproject.toml`, and `.ai` records.
Expected files or areas: `src/autonomous_forge/maintenance_history_link_review_cli.py`, `src/autonomous_forge/maintenance_review_handoff.py`, `src/autonomous_forge/maintenance_review_compare.py`, `src/autonomous_forge/maintenance_archive_manifest.py`, tests, docs, README, `.github/workflows/test.yml`, `pyproject.toml`, and `.ai` records.
Acceptance criteria: Ready history links can verify linked bundles, handoffs fail closed on hash/context drift, comparison ranks ready preservation candidates deterministically, archive manifests list selected evidence entries without writing files, and strict flags return non-zero on blocked evidence.
Validation: Static source/test/docs/workflow review completed through the GitHub repository API with scratch syntax compilation for focused changes. Direct full checkout/full pytest execution remained unavailable from this environment.
Risks or assumptions: The workflow reviews persisted JSON evidence and recomputed hashes; it does not rerun validation, poll workflows, inspect live remotes, prove signer identity, prove coverage, or write archive files.
Notes: Completed before archive manifest integrity gates.

### AUTO-129 — Archive manifest integrity gates
Priority: P1
Status: DONE
Goal: Make archive manifest previews verify current preservation evidence fingerprints before any write-capable archive step exists.
Why it matters: A manifest that only lists files can still point at drifted source reports; reviewers need pass/fail/advisory gates proving listed evidence currently matches bundle metadata.
Scope: Extend `forge maintenance-archive-manifest` / `forge-maintenance-archive-manifest` with recomputed source-report SHA-256 and byte-count verification, compact archive-integrity summary gates, focused tests, docs, README, and `.ai` records.
Expected files or areas: `src/autonomous_forge/maintenance_archive_manifest.py`, `tests/test_maintenance_archive_manifest.py`, `docs/MAINTENANCE_ARCHIVE_MANIFEST.md`, README, and `.ai` records.
Acceptance criteria: Ready manifests expose `archive_integrity`, verify all source-report hashes and byte counts, block readiness on missing or drifted entries, keep run-history link handling advisory, and remain read-only with no archive writes.
Validation: Static source/test/docs review completed through the GitHub repository API. Scratch syntax compilation passed for the updated implementation and focused test content. Direct full checkout/full pytest execution remained unavailable from this environment.
Risks or assumptions: Integrity checks detect local evidence drift but do not rerun validation, poll workflows, prove signer identity, or prove validation coverage.
Notes: Completed before a confirmation-gated local archive-manifest writer.

### AUTO-130 — Confirmation-gated archive manifest writer
Priority: P1
Status: DONE
Goal: Persist a ready integrity-checked archive manifest as one repository-local JSON file only when explicitly confirmed.
Why it matters: Reviewers need a durable manifest file that records the selected preservation candidate and every evidence file to keep together before any archive-copy behavior exists.
Scope: Extend `forge maintenance-archive-manifest` / `forge-maintenance-archive-manifest` with `--output` and `--confirm-write`, output path safety checks, overwrite refusal, focused tests, docs, README, and `.ai` records.
Expected files or areas: `src/autonomous_forge/maintenance_archive_manifest.py`, `src/autonomous_forge/maintenance_archive_manifest_cli.py`, `tests/test_maintenance_archive_manifest.py`, `docs/MAINTENANCE_ARCHIVE_MANIFEST.md`, README, and `.ai` records.
Acceptance criteria: Preview remains default; writing requires `--output --confirm-write`; blocked manifests are not written; output paths must stay under root; parent directories must already exist; existing files are not overwritten; written manifests retain selected candidate, archive entries, integrity gates, blockers, and manifest path.
Validation: Static source/test/docs review completed through the GitHub repository API. Scratch syntax compilation passed for the updated implementation, CLI, and focused test content. Direct full checkout/full pytest execution remained unavailable from this environment.
Risks or assumptions: Written manifests preserve current evidence metadata but do not copy evidence files, create archives, rerun validation, poll workflows, prove signer identity, or prove validation coverage.
Notes: Next safe step is a manifest verification/read command before any archive-copy behavior.

## Future Ideas

- Hash-linked local run reports.
- Optional issue import.
- Policy-aware changed-file summaries.
- Branch protection and workflow-status replay summaries.
- Combined history-link replay handoff.
- Maintenance handoff comparison summaries.
- Written archive-manifest verification.
- Confirmation-gated archive-copy previews.
