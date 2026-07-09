# Autonomous Forge

Autonomous Forge is an open-source, AI-built and AI-maintained developer tool for safely running repository-native autonomous software-improvement loops.

The project is a local-first Python CLI. Its current workflow can plan repository work, propose and validate changes, review supplied diffs/statuses, apply explicitly confirmed patches, verify commits and push handoffs, preserve maintenance evidence into manifests/copies/packages, and now require matching workflow-status freshness as part of the final preservation-completeness gate.

For a visual orientation to the current workflow and its safety boundary, see [the project overview](docs/OVERVIEW.md).

## Current Autonomous Status

Autonomous Forge is pre-alpha. Latest autonomous run: AUTO-139 extended `forge maintenance-preservation-completeness` / `forge-maintenance-preservation-completeness` so the final preservation gate can optionally require supplied workflow-status evidence that is successful and matches the archive manifest commit. Validation included repository metadata, README/docs/source/tests/CI and `.ai` state inspection through the GitHub API, branch/PR review, static source/test review, and local scratch syntax compilation for the changed core, CLI, and focused tests. Full checkout/full pytest remains unavailable in this runtime, so final confirmation depends on GitHub Actions once visible. No visual updates were needed because the existing overview diagram still represents the workflow boundary. Current limitations: the workflow-status freshness gate trusts supplied JSON evidence and does not poll GitHub, rerun workflows, prove signer identity, prove package provenance, or prove validation coverage. Next autonomous objective: add a reviewer checklist or provenance/signature review that preserves the verified package without expanding into uncontrolled remote behavior.

The repository now contains:

- Apache-2.0 licensing and durable planning files in `.ai/`.
- A minimal Python package with a primary `forge` console script plus compatibility scripts for the safer maintenance workflow commands.
- Task parsing, deterministic task selection, roadmap linting, repository reports, policy summaries, repository inventory, enriched implementation plans, proposal/validation/orchestration/executor handoffs, patch apply, commit/push review, durable evidence bundles, run-history links, replay summaries, archive manifests, archive copies, archive packages, package verification, preservation-completeness summaries, and optional workflow-status freshness review for preserved evidence.
- Deterministic tests for the CLI’s current local workflows, including enriched `forge plan`, downstream implementation context propagation, patch/commit/push safety gates, bundle/history replay checks, archive manifest/copy/package verification, preservation completeness, and workflow-status freshness gating.
- CI smoke coverage that validates the live roadmap, installed console entry points, extension help routes, and the test suite across Python 3.10, 3.11, and 3.12.

## Install for local development

```bash
python -m pip install -e .
forge --help
forge plan --help
forge maintenance-preservation-completeness --help
```

For full setup, contribution workflow, and safety expectations, see `CONTRIBUTING.md`.

## Core planning and review workflow

```bash
forge tasks --plan .ai/AUTONOMOUS_PLAN.md --next
forge plan --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge propose --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge validate-plan --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge validation-orchestration --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge executor-dry-run --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root . --command "python -m pytest" --confirm-executor-dry-run
forge maintenance-preservation-completeness --manifest .ai/archives/AUTO-120-manifest.json --archive-root .ai/archive-copies/AUTO-120 --package .ai/archive-packages/AUTO-120.tar.gz --status-evidence .ai/status/AUTO-120-workflows.json --require-workflow-fresh --require-complete
```

Most commands are local-first and read-only unless their contract explicitly requires a confirmation flag for a narrow local write, local validation execution, local commit creation, non-force push handoff, local evidence copy, or local archive package creation. `forge plan` is read-only: it selects the highest-priority eligible roadmap task, lists policy boundaries, turns roadmap prose into reviewable implementation steps/file targets/validation steps/risks, and never changes repository state. `forge maintenance-preservation-completeness` is read-only; it combines written-manifest, copied-root, package verification, and optional supplied workflow-status freshness into one final preservation status and fail-closed strict gates.

## Run tests

```bash
python -m pip install -e . pytest==8.3.5
python -m pytest -q
```

## Safe contribution expectations

Contributions should stay small, local-first, and reviewable. Do not add network actions, external command execution, secret handling, deployment behavior, telemetry, or repository-permission changes unless the roadmap and repository policy explicitly allow it.
