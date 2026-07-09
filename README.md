# Autonomous Forge

Autonomous Forge is an open-source, AI-built and AI-maintained developer tool for safely running repository-native autonomous software-improvement loops.

The project starts as a local-first Python CLI. Its first goal is deliberately small: provide a `forge` command that can grow into dry-run planning, task selection, validation reporting, diff review, supplied commit-status review, combined change readiness, guarded patch preview, explicitly confirmed patch application, post-apply validation handoff, commit-readiness review, commit metadata preview, explicitly confirmed local commit creation, post-commit verification, commit trust review, branch-protection-aware push-readiness review, an explicitly confirmed fast-forward-only non-force push handoff, post-push verification, hash-linked durable maintenance evidence bundles, persisted bundle verification, replay summaries, and durable repository memory without requiring uncontrolled autonomous behavior.

For a visual orientation to the current workflow and its safety boundary, see [the project overview](docs/OVERVIEW.md).

## Current Autonomous Status

Autonomous Forge is pre-alpha. Latest autonomous run: AUTO-106 made `forge push-readiness` branch-protection aware. The gate now requires supplied repository-local branch-protection JSON in addition to commit verification, commit trust, and commit-status evidence; it blocks unprotected branches, missing strict/up-to-date status checks, branch mismatches, and required status contexts that are absent from the status review. Validation included static GitHub API review, scratch syntax compilation for the updated module/CLI/tests, and focused scratch pytest for `tests/test_push_readiness.py`, which passed 12 tests. No visual updates were needed because the overview still accurately describes the local-first safety boundary. Current limitations: direct full checkout/full pytest execution and final workflow visibility remain unavailable from this environment; branch-protection evidence is supplied JSON rather than live API polling, and the product still lacks workflow rerun/polling and signed evidence attestation. Next autonomous objective: require branch-protection-aware push-readiness in the push-handoff boundary and add durable run-history linkage for completed pushed bundles.

The repository now contains:

- Apache-2.0 licensing and durable planning files in `.ai/`.
- A minimal Python package with a primary `forge` console script and compatibility `forge-change-readiness` / `forge-commit-create` / `forge-commit-proposal-preview` / `forge-commit-readiness` / `forge-commit-status-review` / `forge-commit-trust-review` / `forge-commit-verify` / `forge-git-diff-review` / `forge-maintenance-bundle-verify` / `forge-maintenance-evidence-bundle` / `forge-maintenance-replay-summary` / `forge-patch-application-audit` / `forge-patch-application-preflight` / `forge-patch-application-readiness` / `forge-patch-apply` / `forge-patch-generation-preview` / `forge-patch-proposal-review` / `forge-patch-proposal-draft` / `forge-patch-text-preflight` / `forge-patch-text-review` / `forge-post-apply-validation` / `forge-post-push-verify` / `forge-push-handoff` / `forge-push-readiness` console scripts.
- Task parsing, deterministic task selection, roadmap linting, repository reports, policy summaries, run summaries, repository inventory, implementation plans, change proposals, validation plans, validation-run previews, validation orchestration previews, command-execution handoff previews, executor precondition gates, executor contract previews, executor dry-run previews, one narrow opt-in executor run command with explicit result-persistence handoff, guarded executor-handoff persistence, changed-file reviews, changed-content audit, supplied git-diff review, supplied or live commit/workflow status review, change readiness, guarded patch preview and patch apply, post-apply validation, commit readiness, guarded commit metadata preview, explicitly confirmed local commit creation, post-commit verification, commit trust review with optional allowed-signer policy, branch-protection-aware trusted push-readiness review, explicitly confirmed fast-forward-only non-force push handoff, post-push verification, hash-linked durable maintenance evidence bundling, persisted bundle source-report verification, and persisted bundle replay summaries.
- `forge review-artifact` for a single read-only handoff that combines selected task, plan context, proposal intent, structured change intent, patch intent, validation intent, validation command-candidate preview, and explicit planned-path review.
- `forge validation-orchestration` for a single read-only readiness artifact that combines validation plans, command-candidate counts, saved-history validation guards, latest-record status, blockers, and risk notes before any executor exists.
- `forge command-execution-handoff`, `forge executor-gate`, and `forge executor-contract` for the conservative pre-execution chain.
- `forge executor-run` for one explicitly confirmed local validation command after the dry-run gate passes, plus `forge executor-handoff-persist` for separately confirmed durable result persistence.
- Smoke and deterministic coverage for the CLI’s current local workflows, including primary and compatibility replay summary behavior, fast-forward push-handoff behavior, allowed-signer commit-trust behavior, and branch-protection-aware push-readiness behavior.
- CI smoke coverage that validates live repository roadmap, installed console entry points, primary and compatibility extension help routes, and the test suite across Python 3.10, 3.11, and 3.12.

## Install for local development

```bash
python -m pip install -e .
forge --help
forge change-readiness --help
forge commit-create --help
forge commit-proposal-preview --help
forge commit-readiness --help
forge commit-status-review --help
forge commit-trust-review --help
forge commit-verify --help
forge git-diff-review --help
forge maintenance-bundle-verify --help
forge maintenance-evidence-bundle --help
forge maintenance-replay-summary --help
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
forge post-push-verify --help
forge push-handoff --help
forge push-readiness --help
forge-change-readiness --help
forge-commit-create --help
forge-commit-proposal-preview --help
forge-commit-readiness --help
forge-commit-status-review --help
forge-commit-trust-review --help
forge-commit-verify --help
forge-git-diff-review --help
forge-maintenance-bundle-verify --help
forge-maintenance-evidence-bundle --help
forge-maintenance-replay-summary --help
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
forge-post-push-verify --help
forge-push-handoff --help
forge-push-readiness --help
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
forge commit-proposal-preview --root . --commit-readiness commit-readiness.json --summary "feat: describe reviewed change" --body-line "Summarize ready evidence before commit creation." --require-ready --format json > commit-proposal-preview.json
forge commit-create --root . --proposal commit-proposal-preview.json --confirm-commit-create --require-created --format json > commit-create.json
forge commit-verify --root . --commit-create commit-create.json --require-verified --format json > commit-verify.json
forge commit-trust-review --root . --commit-verify commit-verify.json --allowed-signers .forge/allowed-signers.json --require-trusted --format json > commit-trust-review.json
forge commit-status-review --root . --from-github --commit-sha "$(jq -r .inspected_commit commit-verify.json)" --require-clear --format json > verified-commit-status-review.json
gh api repos/OWNER/REPO/branches/main --jq '{branch: .name, protected: .protected, required_status_checks: .protection.required_status_checks}' > branch-protection.json
forge push-readiness --root . --commit-verify commit-verify.json --commit-trust commit-trust-review.json --status-review verified-commit-status-review.json --branch-protection branch-protection.json --branch main --require-ready --format json > push-readiness.json
forge push-handoff --root . --push-readiness push-readiness.json --branch main --remote origin --format json > push-handoff.json
forge push-handoff --root . --push-readiness push-readiness.json --branch main --remote origin --confirm-push --require-pushed --format json > push-handoff.json
forge post-push-verify --root . --push-handoff push-handoff.json --status-review verified-commit-status-review.json --fetch --require-verified --format json > post-push-verify.json
forge maintenance-evidence-bundle --root . --patch-apply patch-apply.json --post-apply-validation post-apply-validation.json --commit-verify commit-verify.json --push-handoff push-handoff.json --post-push-verify post-push-verify.json --bundle-id AUTO-106 --require-complete --format json > maintenance-evidence-bundle.json
forge maintenance-evidence-bundle --root . --patch-apply patch-apply.json --post-apply-validation post-apply-validation.json --commit-verify commit-verify.json --push-handoff push-handoff.json --post-push-verify post-push-verify.json --bundle-id AUTO-106 --output .ai/run-history/AUTO-106-bundle.json --confirm-write --require-written --format json
forge maintenance-bundle-verify --root . --bundle .ai/run-history/AUTO-106-bundle.json --require-verified --format json > maintenance-bundle-verify.json
forge maintenance-replay-summary --root . --bundle .ai/run-history/AUTO-106-bundle.json --require-replayable --format json > maintenance-replay-summary.json
forge executor-run --plan .ai/AUTONOMOUS_PLAN.md --state .ai/AUTONOMOUS_STATE.md --policy .forge/policy.md --root . --command "python -m pytest" --confirm-executor-dry-run --format json > executor-run-output.json
forge executor-handoff-persist --root . --executor-output executor-run-output.json --confirm-write --format json
forge validation-result-audit --root . --record .ai/run-history/latest.json --format json
forge executor-observation-audit --root . --max-records 20 --require-clear --format json
```

Most commands above are local-first. `forge commit-status-review --from-github` is the explicit network-adjacent exception: it shells out to local `git` and GitHub CLI (`gh`) to collect workflow-run metadata for one commit, then applies the same deterministic status gate. `forge push-readiness` consumes supplied branch-protection JSON; it does not call GitHub itself or change branch protection. `forge executor-run` can run one exact local validation command after explicit confirmation; it does not mutate files or persist results automatically. `forge executor-handoff-persist`, `forge run-history-write`, `forge validation-result-write`, and `forge maintenance-evidence-bundle --output ... --confirm-write` require explicit confirmation before writing. Patch-adjacent commands consume supplied JSON evidence and explicit metadata; `forge git-diff-review` inspects supplied unified diff metadata, `forge commit-status-review` inspects supplied or live workflow status evidence, `forge patch-generation-preview` generates bounded unified diff text from explicit replacement content, `forge patch-apply` overwrites one reviewed target file only when explicitly confirmed and the current target/replacement still reproduce the supplied preview, `forge post-apply-validation` checks supplied post-apply validation metadata, `forge commit-readiness` combines validation, final diff, and status evidence, `forge commit-proposal-preview` prepares bounded commit message metadata, `forge commit-create` stages reviewed paths and creates one local commit only after explicit confirmation, `forge commit-verify` inspects the created local commit against the reviewed report, `forge commit-trust-review` inspects local git signature/trust metadata for the verified commit and can optionally require a repository-local allowed-signer policy, `forge push-handoff` performs one explicitly confirmed fast-forward-only non-force push, and post-push/bundle commands preserve or verify evidence. These commands do not approve implementation, force-push, push tags, mutate remote configuration, change branch protection, rerun workflows, or replace human review.

## Run tests

```bash
python -m pip install -e . pytest==8.3.5
python -m pytest -q
```

## Safe contribution expectations

Contributions should stay small, local-first, and reviewable. Do not add network actions, external command execution, secret handling, deployment behavior, telemetry, or repository-permission changes unless the roadmap and repository policy explicitly allow it.
