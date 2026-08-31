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

Forge can build change proposals and validation plans, review planned paths against policy, inspect supplied or live tracked Git diffs, reject path escapes and malformed evidence, apply confirmed replacements with stale-target protection, verify resulting diffs, and execute retained validation commands with bounded `shell=False` subprocesses.

### Verified maintenance chain

The connected workflow includes guarded replacement → live-diff verification → retained validation → optional verified local commit → trust/status/protection readiness → separately confirmed fast-forward push → post-push verification → durable maintenance evidence and history. The higher-level `forge verified-full-maintenance-run` composes that lifecycle while keeping independent authority gates for side effects.

Verified commit creation isolates staging through a private temporary Git index, binds reviewed target bytes and changed paths to the expected parent, refuses unrelated shared staging, and rechecks reviewed state before and after commit synchronization. Push execution is non-force and explicitly confirmed, and post-push verification remains separate.

## Evidence and preservation

Forge supports SHA-linked maintenance bundles, run-history records, replay/reviewer handoffs, archive manifests, copied archive roots, `.tar`/`.tar.gz`/`.zip` packages, package verification, preservation-completeness checks, and immutable preservation receipts.

Durable writers use repository confinement, explicit confirmation, no-clobber publication, file/directory `fsync`, SHA-256 binding, and fail-closed verification. Archive hashing and package member verification stream in bounded chunks instead of materializing complete evidence files in memory.

Recent preservation hardening includes:

- archive manifests bind selected evidence, including run-history-link bytes where authoritative digests exist;
- archive copy/package verification hashes content incrementally and rejects byte-count or digest drift;
- archive manifests and archive packages are immediately reverified after publication;
- failed or Python-interrupted verification rolls back only bytes still owned by the current invocation;
- preservation-receipt verification and discovery use bounded input/candidate limits and remain informational rather than readiness gates;
- externally supplied validation sidecars remain advisory provenance and are never promoted into executor-produced validation authority.

AUTO-238 closes the archive-package durability-sync failure gap: if the destination hard link has been published but the parent-directory `fsync` fails, Forge now SHA-256 checks the current destination and removes it only when it still matches the exact package created by this invocation. The directory is fsynced again to persist rollback. If another writer changed the package, Forge preserves those bytes and fails closed rather than deleting potentially foreign data.

See `docs/ARCHIVE_PACKAGE_DURABILITY_ROLLBACK.md` for that contract and its limits.

## Testing and CI

The repository workflow targets Python **3.10, 3.11, and 3.12**. It installs the package, compiles source, smoke-tests the installed CLI, validates the roadmap, and runs pytest.

There is still no dedicated lint, type-check, coverage, or release workflow, and there are no tagged releases.

## Safety boundary

Important controls include repository path/symlink containment, policy-aware path checks, explicit confirmations for side effects, bounded local subprocesses, stale-target refusal, SHA-256 evidence binding, private-index commit isolation, fast-forward-only non-force push behavior, post-push verification, no-clobber durable publication, bounded-memory archive hashing, and ownership-checked rollback of newly published archive evidence.

Important limitations remain:

- live diff review covers tracked changes, not untracked files;
- passing configured validation commands does not prove those commands are sufficient for correctness;
- hashes prove byte continuity, not signer identity;
- secret detection is not a full secret scanner;
- no filesystem-level lock can permanently prevent later evidence mutation;
- Python cleanup cannot run after abrupt termination such as `SIGKILL`, host failure, interpreter crash, or power loss;
- a filesystem that fails both publication and rollback directory sync leaves durability uncertain and requires inspection;
- archive-copy publication is per-file rather than a cross-file transaction;
- no-clobber durable publication relies on ordinary same-filesystem hard-link support;
- Forge is not ready for unattended use on important repositories.

## Project memory

The `.ai` directory is the repository's engineering memory:

- `.ai/AUTONOMOUS_PLAN.md`
- `.ai/AUTONOMOUS_STATE.md`
- `.ai/AUTONOMOUS_CHANGELOG.md`
- `.ai/DECISIONS.md`

Historical branches and pull requests are inspect-before-integrate evidence only. Current stewardship works directly on `main` and does not create replacement PRs.

## Current Autonomous Status

Latest stewardship run: **AUTO-238 — roll back archive packages when publication durability sync fails**.

- **Changed:** archive-package no-clobber publication now treats parent-directory `fsync` failure after publication as a failed write and performs SHA-256 ownership-checked rollback. If the destination still equals the exact package created by this invocation it is removed and the directory is fsynced again; if the bytes changed, Forge preserves them and refuses unsafe deletion.
- **Why:** AUTO-237 immediately reverified packages after publication, but a pre-existing failure path could still publish the destination and then fail the first directory durability sync, leaving an artifact behind despite the command reporting failure. AUTO-238 closes that concrete ambiguity without adding a new command or authority surface.
- **Validation:** deterministic tests cover both clean rollback after synthetic directory-sync failure and the racing-mutation case that must preserve changed destination bytes. Final GitHub Actions validation on the completed `main` head is required before this cycle is reported complete.
- **Safety:** explicit confirmation, repository containment, bounded-memory hashing, no-clobber publication, source-entry byte/SHA checks, immediate package verification, and Python-level interruption rollback remain intact. No network, workflow-control, Git commit/push, force-push, overwrite, remote, or branch-protection authority was added.
- **Branch/PR disposition:** work stayed directly on `main`; seven non-main branches remain historical/diverged and inspected PRs are merged, closed, obsolete, superseded, or unrelated. No branch or PR was created or merged.
- **Visual updates:** none; archive/preservation topology did not change, only the existing package publication failure contract became safer.
- **Current limitations:** rollback depends on Python cleanup executing. Abrupt termination can prevent cleanup, and failure of the rollback directory `fsync` leaves durability uncertain. A destination changed by another writer is intentionally preserved for inspection.
- **Next autonomous objective:** inspect the remaining preservation writers for another confirmed durability/publication boundary that can leave ambiguous evidence after failure; any fresh CI failure takes priority.
