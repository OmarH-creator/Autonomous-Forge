# Autonomous Forge

Autonomous Forge is an open-source, local-first Python CLI built through an AI software-stewardship experiment. It is best understood as a **pre-alpha, human-in-the-loop maintenance safety framework**, not an unattended AI engineer.

The repository does not call an AI model itself. External agents supplied the autonomy; Forge supplies repository planning, policy checks, guarded side-effect gates, Git verification, and durable maintenance evidence.

## What it does

```mermaid
flowchart LR
    A[Repository files] --> B[Policy-aware plan]
    B --> C[Reviewable proposal]
    C --> D[Path and live diff review]
    D --> E[Guarded patch apply]
    E --> F[Verified validation]
    F --> G[Verified local commit]
    G --> H[Guarded non-force push]
    H --> I[Post-push verification]
    I --> J[Durable evidence and history]
    J --> K[Archive and preservation]
```

Forge keeps the review stages separate from the stages that can change files, run commands, commit, push, or persist evidence. Side effects require explicit confirmation at the relevant boundary.

## Main capabilities

### Policy-aware planning

`forge plan` is the policy-aware planning milestone that started the product direction. It:

- reads the repository roadmap, policy, state, and documented project files;
- chooses the highest-priority eligible task;
- identifies allowed and prohibited file areas;
- produces a concrete reviewable implementation plan;
- lists expected files, validation steps, risks, and reasons;
- remains local-first and read-only.

### Review and guarded change

Forge can:

- build change proposals and validation plans;
- review planned paths against policy;
- inspect a supplied patch or the repository's current tracked diff relative to `HEAD`;
- reject path escapes, unsafe symlinks, malformed evidence, and context drift;
- apply a confirmed reviewed replacement and verify its actual target-scoped Git diff;
- restore the original target if post-write diff verification fails;
- execute exact retained validation commands with `shell=False` and bounded timeouts.

### Verified commit and push chain

The maintenance chain now includes:

- `forge verified-change-run`: executes every retained validation step, builds verified commit readiness, and can create and immediately verify the reviewed local commit. Validation and commit creation keep separate confirmations.
- `forge verified-change-apply-run`: composes the guarded replacement write, mandatory live-diff verification, all retained validation steps, and optional verified local commit without requiring a caller-managed intermediate patch-apply JSON file. Patch apply, validation, and commit creation remain three independent confirmations.
- `forge verified-push-run`: consumes either a completed committed `verified-change-run` artifact or the newer committed `verified-change-apply-run` wrapper, carries the verified commit through commit-trust, status, and branch-protection readiness, and can execute the existing guarded non-force push only with a **separate `--confirm-push` authority gate**. Wrapper mode verifies the retained patch/application/validation/commit evidence before using the nested commit and preserves that wrapper in the push result. After a completed push it performs post-push remote verification; optional fetching is separately requested with `--fetch-after-push`.
- `forge verified-maintenance-run`: consumes that completed `post_push_verified` orchestration artifact plus the earlier patch, validation, and commit-verification evidence, builds the canonical provenance-complete maintenance bundle, and can persist the bundle plus its `.ai/run-history/` link under two **separate** write confirmations. It does not require users to extract duplicate standalone push-handoff and post-push JSON files first.
- the underlying `verified-push-handoff`, `post-push-verify`, maintenance evidence, replay, archive, package, and preservation commands remain independently usable and reviewable.

A typical push-stage invocation using the embedded apply-to-commit artifact is:

```bash
forge verified-push-run \
  --change-apply-run .ai/evidence/verified-change-apply-run.json \
  --commit-trust .ai/evidence/commit-trust.json \
  --status-review .ai/evidence/commit-status.json \
  --branch-protection .ai/evidence/branch-protection.json \
  --branch main \
  --remote origin \
  --confirm-push \
  --fetch-after-push \
  --require-post-push-verified \
  --format json
```

For backward compatibility, `--change-run` remains available and is mutually exclusive with `--change-apply-run`. Without `--confirm-push`, the command can report `ready_for_push` but cannot treat validation or commit confirmation as push authority.

A completed push run can then be preserved without splitting its embedded push/post-push evidence back into extra files:

```bash
forge verified-maintenance-run \
  --patch-apply .ai/evidence/patch-apply.json \
  --post-apply-validation .ai/evidence/post-apply-validation.json \
  --commit-verify .ai/evidence/commit-verify.json \
  --verified-push-run .ai/evidence/verified-push-run.json \
  --bundle-id AUTO-155 \
  --output .ai/evidence/AUTO-155-bundle.json \
  --confirm-bundle-write \
  --history-link .ai/run-history/AUTO-155.json \
  --confirm-history-link \
  --require-complete \
  --require-history-linked \
  --format json
```

### Evidence and preservation

Forge also supports:

- evidence bundles with verified push/post-push provenance binding;
- hash-linked run-history records;
- replay summaries and reviewer handoffs;
- archive manifests and copied archive roots;
- `.tar`, `.tar.gz`, and `.zip` packaging;
- package verification and preservation-completeness checks;
- optional workflow-status freshness evidence.

## Development history

The project began as a tiny roadmap-driven CLI and grew into a connected maintenance framework. Major stages include:

| Stage | Result |
|---|---|
| `AUTO-001`–`AUTO-014` | Core CLI, roadmap parsing, task selection, policy and inventory |
| `AUTO-015`–`AUTO-062` | Planning, proposals, validation, audit and run-history contracts |
| `AUTO-063`–`AUTO-108` | Patch application, Git review, commit and push gates |
| `AUTO-109`–`AUTO-140` | Enriched replay, reviewer handoffs, archive and preservation workflow |
| `AUTO-141`–`AUTO-142` | Dedicated red-baseline recovery; supported Python matrix restored to green |
| `AUTO-143`–`AUTO-152` | Live Git diff inspection through verified patch, validation, commit, push, post-push, durable evidence, and an end-to-end disposable-repository proof |
| `AUTO-153` | First orchestration surface: verified validation through local commit creation |
| `AUTO-154` | Second orchestration surface: committed verified change through separately confirmed push and post-push verification |
| `AUTO-155` | Third orchestration surface: post-push-verified run through separately confirmed canonical durable bundle and run-history persistence |
| `AUTO-156` | Guarded patch application through verified validation/commit using embedded SHA-bound patch evidence instead of an intermediate patch JSON handoff |
| `AUTO-157` | Verified push orchestration accepts and preserves the committed change-apply wrapper without splitting nested change evidence back into another JSON handoff |

## Testing and CI

The main workflow tests Python **3.10, 3.11, and 3.12**. It installs the package, compiles source, smoke-tests the installed CLI, validates the roadmap, and runs pytest.

A historical audit reached `569 passed, 82 failed, 1 skipped`. AUTO-141/AUTO-142 paused feature work and repaired the actual compatibility, fixture, routing, context-consistency, and archive-path defects instead of suppressing failures. The supported matrix has remained green through the subsequent verified-maintenance integration work.

AUTO-156 final head `b1eb018cb4b15acc98771f2d304362a62c739ac8` passed Actions run `32041811743`; Python 3.10, 3.11, and 3.12 each passed package installation, compilation, installed CLI smoke, roadmap validation, and pytest. AUTO-157 validation is recorded in the Current Autonomous Status below.

There is still no dedicated lint, type-check, coverage, or release workflow, and there are no tagged releases.

## Safety boundary

Positive controls include:

- repository path and symlink containment;
- policy-aware allowed/prohibited path checks;
- simple secret-marker checks without printing file contents;
- explicit confirmations for writes, validation execution, commits, pushes, package writes, and durable evidence writes;
- `shell=False` for the narrow command executor and live Git-diff inspection;
- target-scoped post-write diff verification with rollback on verification failure;
- canonical SHA-256 binding between embedded guarded-patch evidence and its validation observations;
- complete retained-validation coverage before verified commit readiness;
- exact changed-path verification after commit creation;
- fast-forward-only, non-force guarded push behavior;
- no tag pushes, remote mutations, or branch-protection changes from the verified push path;
- post-push remote reachability verification;
- durable evidence hashing and replay/preservation checks.

Important limitations remain:

- live current-diff review covers tracked changes, not untracked files;
- validation coverage proves the configured commands passed, not that those commands are sufficient for correctness;
- commit-trust, commit-status, and branch-protection JSON are still supplied evidence rather than independently acquired fresh GitHub proof;
- post-push verification relies on local remote-tracking refs unless fetch is explicitly requested;
- hashes detect byte drift but do not prove signer identity;
- secret detection is not a full secret scanner;
- there is no shared lock for external scheduled agents;
- Forge is not ready for unattended use on important repositories.

## Project memory

The `.ai` directory is the repository's engineering memory:

- `.ai/AUTONOMOUS_PLAN.md`
- `.ai/AUTONOMOUS_STATE.md`
- `.ai/AUTONOMOUS_CHANGELOG.md`
- `.ai/DECISIONS.md`

Historical branches and pull requests are inspect-before-integrate evidence only. Current stewardship works directly on `main` and does not create replacement PRs.

## Current Autonomous Status

Latest stewardship run: **AUTO-157 — embedded change-apply provenance into verified push orchestration**.

- **Changed:** `forge verified-push-run` now accepts either `--change-run` or mutually exclusive `--change-apply-run`. Wrapper mode verifies committed status, explicit apply/validation/commit confirmations, retained patch evidence, successful guarded apply, live-diff verification, closed push authority, and nested change-run consistency before using the verified commit. The accepted wrapper is retained in the push-run result for downstream durable provenance.
- **Safety:** push remains a separate explicit authority gate. Wrapper drift or missing evidence blocks before the push handoff. Existing standalone change-run input remains backward compatible. No force-push, tag push, remote mutation, branch-protection change, or fresh network trust acquisition was added.
- **Validation:** deterministic tests cover direct wrapper acceptance, preserved wrapper provenance, fail-closed wrapper status drift, and the new CLI input. GitHub Actions on the final AUTO-157 head is the source of truth for supported-version validation.
- **Visual updates:** none; the existing maintenance-flow diagram already shows verified commit flowing into guarded push and post-push verification, so another visual would duplicate the architecture.
- **Current limitations:** `verified-maintenance-run` still requires earlier patch/validation/commit evidence as separate inputs even though the successful push artifact can now retain the complete change-apply wrapper.
- **Next autonomous objective:** let `verified-maintenance-run` derive its canonical patch/validation/commit stages directly from the retained `change_apply_run` inside a successful verified-push-run artifact, preserving provenance through durable evidence without caller-managed duplicate JSON files.
