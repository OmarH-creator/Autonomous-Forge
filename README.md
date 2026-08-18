# Autonomous Forge

Autonomous Forge is an open-source, local-first Python CLI built through an AI software-stewardship experiment. It is a **pre-alpha, human-in-the-loop maintenance safety framework**, not an unattended AI engineer.

The repository does not call an AI model itself. External agents supply autonomy; Forge supplies repository planning, policy checks, guarded side-effect gates, Git verification, and durable maintenance evidence.

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

Forge keeps review stages separate from stages that can change files, run commands, commit, push, or persist evidence. Side effects require explicit confirmation at the relevant boundary.

## Main capabilities

### Policy-aware planning

`forge plan` reads the repository roadmap, policy, state, and documented project files; selects the highest-priority eligible task; identifies allowed/prohibited areas; and emits a concrete reviewable plan with expected files, validation steps, risks, and reasons. It is local-first and read-only.

### Review and guarded change

Forge can build change proposals and validation plans, review planned paths against policy, inspect supplied or live tracked Git diffs, reject path escapes and malformed evidence, apply a confirmed replacement, verify the resulting target-scoped live diff, roll back on verification failure, and execute exact retained validation commands with bounded `shell=False` subprocesses.

### Verified maintenance chain

The connected workflow now includes:

- `forge verified-change-apply-run`: guarded replacement write → live-diff verification → retained validations → optional verified local commit, with separate apply/validation/commit confirmations.
- `forge verified-push-run`: verified commit → trust/status/protection readiness → separately confirmed fast-forward push → post-push verification.
- `forge verified-maintenance-run`: post-push-verified evidence → canonical durable bundle → `.ai/run-history/` link, with separate persistence confirmations.
- `forge verified-full-maintenance-run`: composes the full guarded preview/apply → validation → commit → push → post-push → durable-history lifecycle in one invocation while preserving independent authority gates for every side effect. It can generate the patch preview fresh in memory from patch-readiness plus the current target/replacement, or consume a supplied legacy preview file.

The underlying planning, diff review, patch, validation, commit, push, replay, archive, package, and preservation commands remain independently usable and reviewable.

## Evidence and preservation

Forge supports SHA-linked maintenance bundles, run-history records, replay/reviewer handoffs, archive manifests, copied archive roots, `.tar`/`.tar.gz`/`.zip` packaging, package verification, and preservation-completeness checks.

## Testing and CI

The repository workflow targets Python **3.10, 3.11, and 3.12**. It installs the package, compiles source, smoke-tests the installed CLI, validates the roadmap, and runs pytest.

AUTO-141/AUTO-142 were dedicated baseline-recovery milestones. Subsequent work connected live diff review, guarded patching, validation, commit verification, non-force push, post-push verification, and durable evidence into one maintenance workflow.

There is still no dedicated lint, type-check, coverage, or release workflow, and there are no tagged releases.

## Safety boundary

Positive controls include repository path/symlink containment, policy-aware path checks, simple secret-marker checks, explicit confirmations for every side effect, bounded `shell=False` command execution, rollback after failed post-write diff verification, SHA-256 evidence binding, complete retained-validation coverage before commit readiness, exact changed-path commit verification, fast-forward-only non-force push behavior, no tag pushes or remote/protection mutation, post-push reachability verification, and durable evidence hashing.

Important limitations remain:

- live diff review covers tracked changes, not untracked files;
- passing configured validation commands does not prove those commands are sufficient for correctness;
- commit-trust, commit-status, and branch-protection inputs are still caller-supplied evidence rather than independently acquired fresh GitHub proof;
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

Latest stewardship run: **AUTO-161 — generate the patch preview fresh inside the full maintenance run**.

- **Changed:** `forge verified-full-maintenance-run` now accepts mutually exclusive `--patch-readiness` and `--preview` inputs. In the preferred `--patch-readiness` mode, Forge regenerates the bounded patch preview from the current target and replacement immediately before the guarded apply and passes it in memory through the same apply → live-diff verification → validation → commit → push → post-push → durable-history chain. Existing file-based `--preview` behavior remains compatible.
- **Safety:** fresh preview generation is read-only and does not grant apply authority. Apply, validation, commit, push, push-evidence write, bundle write, and history-link write remain independently confirmed. The same target/current/replacement reproduction checks, policy-aware target-scoped live-diff verification, and rollback-on-verification-failure behavior remain in force. No force-push, tag push, remote mutation, branch-protection mutation, workflow mutation, or new network/external-service capability was added.
- **Validation:** the changed source modules and focused AUTO-161 regression test compile successfully in the available scratch Python environment. Direct repository cloning remains unavailable because this runtime cannot resolve GitHub through local DNS, so the final push-triggered Python 3.10/3.11/3.12 workflow is the source of truth when observable; no green result is fabricated when the connected status surface exposes no run object.
- **Visual updates:** none; the existing Mermaid lifecycle already depicts the unchanged maintenance flow, and this feature removes an intermediate evidence-file handoff rather than changing the architecture.
- **Current limitations:** patch-readiness, change-readiness, commit-trust, workflow/status, and branch-protection evidence still come from existing contracts. Fresh external trust/status/protection acquisition remains policy-gated because `.forge/policy.md` requires human approval before adding network/external-service access.
- **Next autonomous objective:** if AUTO-161 CI is green, reduce the next local caller-managed pre-apply handoff—preferably deriving fresh patch-readiness from the existing preflight/audit evidence inside the same orchestrator—before seeking explicit approval for bounded fresh GitHub evidence acquisition.