# Autonomous Forge Roadmap

## Product vision

Autonomous Forge helps a repository keep a clear improvement plan, choose one safe task, produce reviewable planning artifacts, inspect proposed diffs, review validation status, run tightly scoped validation, apply explicitly confirmed patches, record validation evidence, summarize commit readiness, preview commit metadata, create one explicitly confirmed local commit, verify that created commit, review local commit trust metadata, summarize trusted push readiness, run an explicitly confirmed non-force push handoff, verify that the pushed commit is reachable from the intended remote branch with clear status evidence, preserve hash-linked durable maintenance evidence bundles, and verify persisted bundle source-report integrity.

## Product scope and non-goals

The first product remains a local Python CLI. It is not a hosted service, deployment system, permission manager, uncontrolled executor, automatic commit bot, force-push bot, branch-protection manager, remote-configuration manager, workflow-rerun bot, or cryptographic identity authority.

## Current architecture

The repository contains a Python package under `src/autonomous_forge`, tests under `tests/`, command docs under `docs/`, workflow checks under `.github/workflows/`, policy under `.forge/`, and durable memory under `.ai/`. The installed `forge` entry point routes the historical CLI plus extension commands through `src/autonomous_forge/cli_entry_patch.py`; compatibility console scripts remain available through `pyproject.toml`.

## Current implementation status

Roadmap v3 now reaches guarded local commit creation, post-commit verification, commit trust review, trusted pre-push readiness review, explicitly confirmed non-force push handoff, post-push verification, durable maintenance evidence bundles, SHA-256 source-report fingerprints for those bundles, and persisted bundle source-report verification. Product commands still do not force-push, push tags, change remotes, change branch protections, enforce a full cryptographic identity policy, rerun workflows, or poll remote workflow completion.

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
Validation: Scratch syntax compilation covered the new module, CLI, and tests. Focused scratch pytest for `tests/test_maintenance_evidence_bundle.py` passed with 7 tests. Static source/test/docs/workflow review completed through the GitHub repository API; CI smoke covers primary and compatibility help routes.
Risks or assumptions: Bundles trust supplied JSON evidence and do not verify signatures, rerun workflows, or prove cryptographic identity.
Notes: Completed before hash-linked source-report fingerprints.

### AUTO-100 — Hash-linked maintenance evidence bundle integrity
Priority: P1
Status: DONE
Goal: Add source-report fingerprints to durable maintenance evidence bundles.
Why it matters: A durable bundle should preserve enough provenance to detect when the source JSON reports used to build it have later been edited, swapped, or regenerated.
Scope: Extend `forge maintenance-evidence-bundle` data with deterministic `source_reports` entries containing stage, repository-local path, byte count, and SHA-256 digest for each source evidence report; add validation for malformed or incomplete source-report hash metadata; update focused tests, docs, README, and project memory.
Expected files or areas: `src/autonomous_forge/maintenance_evidence_bundle.py`, `tests/test_maintenance_evidence_bundle.py`, `docs/MAINTENANCE_EVIDENCE_BUNDLE.md`, README, and `.ai` records.
Acceptance criteria: Bundles built from local JSON inputs include five source-report fingerprints, malformed hashes are refused, missing hash stages block complete status when hashes are supplied, and persisted bundles still require explicit confirmation.
Validation: Static source/test/docs review completed through the GitHub repository API. Scratch syntax compilation covered the updated module. Focused scratch pytest for `tests/test_maintenance_evidence_bundle.py` passed with 9 tests.
Risks or assumptions: SHA-256 fingerprints detect byte drift only; they do not sign evidence, prove author identity, rerun workflows, verify commit signatures, or replace human review.
Notes: Completed before persisted-bundle verification.

### AUTO-101 — Persisted maintenance bundle verification
Priority: P1
Status: DONE
Goal: Verify persisted maintenance evidence bundles against their recorded source-report fingerprints.
Why it matters: After a bundle is saved, maintainers need a deterministic way to detect if any source evidence report has changed, been swapped, or no longer matches the byte stream used to create the bundle.
Scope: Add `forge maintenance-bundle-verify` and compatibility `forge-maintenance-bundle-verify`; read one persisted bundle and the repository-local source reports named inside it; recompute byte counts and SHA-256 hashes; report verified or drifted status with blockers; update tests, docs, README, CI smoke, and project memory.
Expected files or areas: `src/autonomous_forge/maintenance_bundle_verify.py`, `src/autonomous_forge/maintenance_bundle_verify_cli.py`, `tests/test_maintenance_bundle_verify.py`, `docs/MAINTENANCE_EVIDENCE_BUNDLE.md`, `pyproject.toml`, `.github/workflows/test.yml`, README, and `.ai` records.
Acceptance criteria: Matching source reports verify, drifted reports are reported without mutation, unsafe out-of-root paths are refused, missing stages are refused, `--require-verified` fails closed, and the command performs no writes, patching, validation execution, commit, push, or remote operations.
Validation: Scratch syntax compilation covered the new module and CLI. Focused scratch pytest for `tests/test_maintenance_bundle_verify.py` passed with 6 tests. Static source/test/docs/workflow review completed through the GitHub repository API.
Risks or assumptions: Verification detects local byte drift only. It does not sign bundles, prove author identity, verify commit signatures, rerun workflows, or establish a cryptographic trust model.
Notes: Completed before commit trust review.

### AUTO-102 — Commit trust review and trusted push-readiness
Priority: P1
Status: DONE
Goal: Add a local commit trust checkpoint and require that trust evidence in push-readiness.
Why it matters: A safe push workflow should not rely only on commit content and workflow status; it should also have an explicit checkpoint for local git signature/trust metadata before a push handoff is considered ready.
Scope: Add `forge commit-trust-review` and compatibility `forge-commit-trust-review`; inspect one verified commit with bounded `git show` signature metadata; block unsigned, bad, expired, revoked, uncheckable, mismatched, or path-mismatched trust evidence; integrate commit-trust-review JSON into `forge push-readiness`; update tests, docs, README, workflow smoke coverage, and project memory.
Expected files or areas: `src/autonomous_forge/commit_trust_review.py`, `src/autonomous_forge/commit_trust_review_cli.py`, `src/autonomous_forge/push_readiness.py`, `src/autonomous_forge/push_readiness_cli.py`, `tests/test_commit_trust_review.py`, `tests/test_push_readiness.py`, `docs/PUSH_READINESS.md`, `pyproject.toml`, `.github/workflows/test.yml`, README, and `.ai` records.
Acceptance criteria: Trusted signature codes `G` and `U` can pass, unsigned/untrusted/mismatched commits block, push-readiness requires trusted commit evidence matching the verified commit and reviewed paths, `--require-trusted` and `--require-ready` fail closed, and no command stages files, creates commits, pushes, changes remotes, reruns workflows, or changes branch protection.
Validation: Static source/test/docs/workflow review completed through the GitHub repository API. Deterministic tests cover commit trust review and push-readiness blockers for untrusted, mismatched, and unclear evidence. Direct full repository checkout/full pytest execution remained unavailable in this environment.
Risks or assumptions: Local git signature metadata is a trust checkpoint, not a complete cryptographic identity policy. `G` and `U` are treated as trusted enough for this local gate, but human policy may still require stricter signer/key rules.
Notes: Next safe step is an end-to-end local evidence replay summary using verified persisted bundles.

## Future Ideas

- Hash-linked local run reports.
- Optional issue import.
- Policy-aware changed-file summaries.
- Branch protection and workflow-status replay summaries.
- End-to-end local evidence replay summary using verified persisted bundles.
