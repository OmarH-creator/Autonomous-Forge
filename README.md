# Autonomous Forge

Autonomous Forge is an open-source, AI-built and AI-maintained developer tool for safely running repository-native autonomous software-improvement loops.

The project starts as a local-first Python CLI. Its first goal is deliberately small: provide a `forge` command that can grow into dry-run planning, task selection, validation reporting, diff review, supplied commit-status review, combined change readiness, guarded patch preview, explicitly confirmed patch application, post-apply validation handoff, commit-readiness review, and durable repository memory without requiring uncontrolled autonomous behavior.

For a visual orientation to the current workflow and its safety boundary, see [the project overview](docs/OVERVIEW.md).

## Current Autonomous Status

Autonomous Forge is pre-alpha. Latest autonomous run: AUTO-092 added `forge commit-readiness` and compatibility `forge-commit-readiness`, a read-only summary that combines post-apply validation, final git-diff review, and supplied or live-collected commit-status review evidence before any future commit workflow is considered. It reports ready only when the applied change is validated, the final diff is clear, the validated target path is present in that diff review, and status evidence is clear; it keeps `commit_allowed` and `commit_workflow_allowed` false. Direct local checkout/test execution remains unavailable in this environment, so validation was limited to static GitHub API source/test/docs review plus committed deterministic tests and CI help-smoke coverage. No visual updates were needed because the existing overview still accurately describes the local-first safety boundary. Current limitations: no cryptographic commit verification, automatic validation execution after patch application, or command that creates commits. Next autonomous objective: add a guarded commit-proposal preview that prepares commit metadata from ready evidence without committing.

The repository now contains:

- Apache-2.0 licensing and durable planning files in `.ai/`.
- A minimal Python package with a primary `forge` console script and compatibility `forge-change-readiness` / `forge-commit-readiness` / `forge-commit-status-review` / `forge-git-diff-review` / `forge-patch-application-audit` / `forge-patch-application-preflight` / `forge-patch-application-readiness` / `forge-patch-apply` / `forge-patch-generation-preview` / `forge-patch-proposal-review` / `forge-patch-proposal-draft` / `forge-patch-text-preflight` / `forge-patch-text-review` / `forge-post-apply-validation` console scripts.
- Task parsing, deterministic task selection, roadmap linting, repository reports, policy summaries, run summaries, repository inventory, implementation plans, change proposals, validation plans, validation-run previews, validation orchestration previews, command-execution handoff previews, executor precondition gates, executor contract previews, executor dry-run previews, one narrow opt-in executor run command with explicit result-persistence handoff, a guarded executor-handoff persistence CLI, changed-file reviews, changed-content audit, supplied git-diff review with binary/metadata-only hardening and an optional `--require-clear` gate, commit/workflow status review over supplied JSON or explicit live `gh` workflow-run collection with an optional `--require-clear` gate, combined supplied change-readiness summaries with an optional `--require-ready` gate, diff-source handoff comparison with an optional `--require-clear` gate, patch-intent review with an optional `--require-ready` gate, patch-intent description with an optional `--require-described` gate and unsafe candidate-path-label refusal, patch proposal manifests with an optional `--require-ready` gate, patch proposal review with `--require-ready`, unsafe requested/audited path-label refusal, non-empty validation-step enforcement, patch proposal draft preview with `--require-draft-ready`, patch text preflight with `--require-ready`, patch text review with `--require-ready`, patch application preflight with `--require-ready`, patch application provenance audit with `--require-clear`, patch application readiness summary with `--require-ready`, guarded patch-generation preview with `--require-generated`, explicitly confirmed guarded patch apply with `--confirm-apply` plus optional `--require-applied`, post-apply validation handoff with `--require-validated`, and commit-readiness review with `--require-ready`.
- `forge review-artifact` for a single read-only handoff that combines selected task, plan context, proposal intent, structured change intent, patch intent, validation intent, validation command-candidate preview, and explicit planned-path review.
- `forge validation-orchestration` for a single read-only readiness artifact that combines validation plans, command-candidate counts, saved-history validation guards, latest-record status, blockers, and risk notes before any executor exists.
- `forge command-execution-handoff`, `forge executor-gate`, and `forge executor-contract` for the conservative pre-execution chain.
- `forge executor-run` for one explicitly confirmed local validation command after the dry-run gate passes, plus `forge executor-handoff-persist` for separately confirmed durable result persistence.
- Smoke and deterministic coverage for the CLI’s current local workflows, including primary and compatibility change readiness behavior, primary and compatibility commit readiness behavior, primary and compatibility commit status review behavior, live `gh` workflow-run status collection, primary and compatibility git diff review behavior, primary and compatibility patch proposal review/draft behavior, primary/compatibility patch text preflight behavior, primary/compatibility patch text review behavior, primary/compatibility patch application preflight behavior, patch application audit behavior, patch application readiness behavior, patch generation preview behavior, patch apply behavior, and post-apply validation handoff behavior.
- CI smoke coverage that validates live repository roadmap, installed console entry points, primary and compatibility extension help routes, and the test suite across Python 3.10, 3.11, and 3.12.

## Install for local development

```bash
python -m pip install -e .
forge --help
forge change-readiness --help
forge commit-readiness --help
forge commit-status-review --help
forge git-diff-review --help
forge patch-application-audit --help
forge patch-application-preflight --help
forge patch-application-readiness --help
forge patch-apply --help
forge patch-generation-preview --help
forge patch-proposal-review --help
forge patch-proposal-draft --help
forge patch-text-preflight --help
forge patch-text-review --help
forge post-apply-validation --help
forge-change-readiness --help
forge-commit-readiness --help
forge-commit-status-review --help
forge-git-diff-review --help
forge-patch-application-audit --help
forge-patch-application-preflight --help
forge-patch-application-readiness --help
forge-patch-apply --help
forge-patch-generation-preview --help
forge-patch-proposal-review --help
forge-patch-proposal-draft --help
forge-patch-text-preflight --help
forge-patch-text-review --help
forge-post-apply-validation --help
```

For full setup, contribution workflow, and safety expectations, see `CONTRIBUTING.md`.

## Core planning and review workflow

```bash
forge tasks --plan .ai/AUTONOMOUS_PLAN.md --next
forge plan --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge propose --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge validate-plan --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge validation-orchestration --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge command-execution-handoff --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge executor-gate --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge executor-contract --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root .
forge executor-dry-run --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root . --command "python -m pytest" --confirm-executor-dry-run
git diff -- README.md > changes.diff
forge git-diff-review --policy .forge/policy.md --root . --diff changes.diff --require-clear --format json > git-diff-review.json
forge commit-status-review --root . --from-github --require-clear --format json > commit-status-review.json
forge change-readiness --root . --diff-review git-diff-review.json --status-review commit-status-review.json --require-ready --format json > change-readiness.json
forge content-audit --policy .forge/policy.md --root . --file README.md --format json
forge diff-source-handoff --root . --before before-content-audit.json --after after-content-audit.json --require-clear --format json
forge patch-intent-review --root . --diff-source diff-source-handoff.json --require-ready --format json > patch-intent-review.json
forge patch-intent-describe --root . --patch-review patch-intent-review.json --require-described --format json > patch-intent-description.json
forge patch-proposal-manifest --root . --description patch-intent-description.json --objective "Describe the reviewed change." --path README.md --validation "python -m pytest" --require-ready --format json > patch-proposal-manifest.json
forge patch-proposal-review --root . --manifest patch-proposal-manifest.json --content-audit fresh-content-audit.json --require-ready --format json > patch-proposal-review.json
forge patch-proposal-draft --root . --review patch-proposal-review.json --require-draft-ready --format json > patch-proposal-draft.json
forge patch-text-preflight --root . --draft patch-proposal-draft.json --path README.md --change-summary "Describe the intended README patch text." --require-ready --format json > patch-text-preflight.json
forge patch-text-review --root . --preflight patch-text-preflight.json --path README.md --patch-summary "Review the intended README patch text." --require-ready --format json > patch-text-review.json
forge patch-application-preflight --root . --review patch-text-review.json --path README.md --patch-source manual-review-note --expected-summary "Review the intended README patch text." --require-ready --format json > patch-application-preflight.json
forge patch-application-audit --root . --preflight patch-application-preflight.json --require-clear --format json > patch-application-audit.json
forge patch-application-readiness --root . --preflight patch-application-preflight.json --audit patch-application-audit.json --require-ready --format json > patch-application-readiness.json
forge patch-generation-preview --root . --readiness patch-application-readiness.json --path README.md --replacement README.replacement.md --require-generated --format json > patch-generation-preview.json
forge patch-apply --root . --preview patch-generation-preview.json --change-readiness change-readiness.json --path README.md --replacement README.replacement.md --confirm-apply --require-applied --format json > patch-apply.json
forge post-apply-validation --root . --patch-apply patch-apply.json --result passed --executed-step "python -m pytest" --require-validated --format json > post-apply-validation.json
forge commit-readiness --root . --post-apply-validation post-apply-validation.json --diff-review git-diff-review.json --status-review commit-status-review.json --require-ready --format json > commit-readiness.json
forge executor-run --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root . --command "python -m pytest" --confirm-executor-dry-run --format json > executor-run-output.json
forge executor-handoff-persist --root . --executor-output executor-run-output.json --confirm-write --format json
forge validation-result-audit --root . --record .ai/run-history/latest.json --format json
forge executor-observation-audit --root . --max-records 20 --require-clear --format json
```

Most commands above are local-first. `forge commit-status-review --from-github` is the explicit exception: it shells out to local `git` and GitHub CLI (`gh`) to collect workflow-run metadata for one commit, then applies the same deterministic status gate. `forge executor-run` can run one exact local validation command after explicit confirmation; it does not mutate files or persist results automatically. `forge executor-handoff-persist`, `forge run-history-write`, and `forge validation-result-write` require explicit confirmation before writing. Patch-adjacent commands consume supplied JSON evidence and explicit metadata; `forge git-diff-review` inspects supplied unified diff metadata, `forge commit-status-review` inspects supplied or live workflow status evidence, `forge patch-generation-preview` generates bounded unified diff text from explicit replacement content, `forge patch-apply` overwrites one reviewed target file only when explicitly confirmed and the current target/replacement still reproduce the supplied preview, `forge post-apply-validation` checks supplied post-apply validation metadata, and `forge commit-readiness` combines validation, final diff, and status evidence before any future commit workflow. Use `--require-applied`, `--require-validated`, and `--require-ready` when automation should fail closed at those gates. No command approves implementation, commits, or pushes.

## Run tests

```bash
python -m pip install -e . pytest==8.3.5
python -m pytest -q
```

## Safe contribution expectations

Contributions should stay small, local-first, and reviewable. Do not add network actions, external command execution, secret handling, deployment behavior, telemetry, or repository-permission changes unless the roadmap and repository policy explicitly allow it.
