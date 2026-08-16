# Autonomous Forge

## The three-day Autonomus AI experiment

Autonomous Forge is an open-source Python tool built and maintained by scheduled AI agents. The agents were given a GitHub repository and permission to decide what to build, how to structure it, and how to improve it.

This README documents what happened during the experiment and the subsequent baseline-recovery work.

## Short result

The experiment was successful as a research test, but the project is not production-ready.

The AI grew a small repository into a large safety and maintenance framework. The code installs, compiles, and the supported Python 3.10/3.11/3.12 matrix is green again after a dedicated baseline-recovery milestone. That recovery does not by itself make the project production-ready; the framework remains pre-alpha and deliberately human-in-the-loop.

The best description is:

> A useful pre-alpha, human-in-the-loop safety framework — not a self-running AI engineer.

## What the project does

Autonomous Forge is a local-first command-line tool. It helps a maintainer or AI-assisted workflow move through a controlled maintenance process:

```mermaid
flowchart LR
    A[Repository files] --> B[Plan and select a task]
    B --> C[Create a reviewable proposal]
    C --> D[Review paths, diffs, status, and risks]
    D --> E[Preview validation]
    E --> F[Optional confirmed change]
    F --> G[Commit and push checks]
    G --> H[Evidence bundle and replay]
    H --> I[Archive and preservation checks]
    D --> J[Human review]
    J --> F
```

The repository does not call an AI model. The external scheduler and AI agents supplied the autonomy. Forge supplies local planning, safety checks, side-effect gates, and evidence records.

## What happened

The repository started with only a README and a license. By the end of the original three-day experiment, it contained:

- Total lines added across all Git history: 49,200
- Total lines deleted across history: 11,616
- Actual lines then present: 37,584 lines
- 283 tracked files.
- 112 Python source files.
- 90 Python test files.
- 68 documentation files.
- 6 `.ai` planning and memory files.
- 1,486 commits by the same Git author.
- 123 numbered `AUTO-###` task groups, reaching `AUTO-140`.
- No runtime dependencies.

### Commit activity

| Local date | Commits |
|---|---:|
| 7 July 2026 | 194 |
| 8 July 2026 | 658 |
| 9 July 2026 | 572 |
| 10 July 2026 | 61 |

```mermaid
xychart-beta
    title "Commits by local date"
    x-axis ["Jul 7", "Jul 8", "Jul 9", "Jul 10"]
    y-axis "Commits" 0 --> 700
    bar [194, 658, 572, 61]
```

One task was usually split into several commits: core code, CLI wiring, tests, smoke checks, documentation, roadmap, state, changelog, and decision records. This made the work easy to inspect, but it also created many CI runs.

## Main development stages

| Stage | Main work | Result |
|---|---|---|
| `AUTO-001`–`AUTO-014` | CLI, roadmap parsing, task selection, reports, policy, inventory | Small working local tool |
| `AUTO-015`–`AUTO-023` | Package CI, JSON output, planning, proposals, validation | Better review surface; first contract failures appeared |
| `AUTO-024`–`AUTO-062` | Review artifacts, run history, executor gates, content and diff audits | Large safety and evidence layer |
| `AUTO-063`–`AUTO-108` | Patch reviews, patch apply, git review, commit and push gates | Near end-to-end maintenance chain |
| `AUTO-109`–`AUTO-125` | Enriched context, replay, history links, reviewer handoffs | Stronger evidence, but more connected contracts |
| `AUTO-126`–`AUTO-140` | Archive manifests, copies, packages, verification, completeness | Detailed preservation workflow |
| `AUTO-141`–`AUTO-142` | Red-baseline recovery, compatibility defects, fixture/contract repair | Supported Python matrix restored to green |
| `AUTO-143` | Live tracked git-diff inspection | Actual pending tracked changes can be policy-reviewed without exporting a patch |
| `AUTO-144` | Verified guarded patch apply | Confirmed replacement writes can verify their actual tracked target diff and roll back if that verification fails |
| `AUTO-145` | Verified validation execution | One exact validation command can be tied to a live-diff-verified patch |
| `AUTO-146` | Verified commit readiness | All retained patch validation steps must have successful verified runs before commit readiness can be ready |
| `AUTO-147` | Verified commit creation | Ready verified evidence can create one confirmed local commit and immediately verify its SHA, summary, and exact changed paths |
| `AUTO-148` | Verified guarded push handoff | Verified commit-creation provenance now flows through trust/status/branch-policy readiness into the existing explicit non-force push gate |
| `AUTO-149` | Verified post-push provenance | The existing post-push verifier now accepts verified push handoff evidence, checks wrapper/nested evidence consistency, and retains validation provenance after remote reachability verification |
| `AUTO-150` | Durable verified maintenance provenance | The existing maintenance evidence bundle can bind verified push/post-push provenance and fail closed if commit, path, remote, branch, or validation evidence drifts |
| `AUTO-151` | Canonical verified push evidence | Durable bundles can use the verified push wrapper as the sole push-stage file while preserving legacy bundle-verification compatibility |

## Main features created

### Planning

- Reads a Markdown roadmap.
- Selects the highest-priority eligible task.
- Checks roadmap structure and task fields.
- Reads allowed paths, prohibited paths, and approval rules.
- Produces human-readable and JSON plans.

### Review and validation

- Builds change proposals and validation plans.
- Reviews planned files against policy.
- Reviews supplied diffs or the repository's current tracked staged/unstaged diff relative to `HEAD`.
- Detects path escapes and symlinks.
- Creates validation previews without running commands.
- Stores and compares local run-history records.
- Can bind successful observed validation results back to the exact verified patch evidence that authorized them.

### Controlled changes

Separate commands can, after explicit confirmation:

- apply a reviewed replacement patch, optionally verify the actual target-scoped tracked diff immediately after the write, and restore the original target if that verification fails;
- run one exact validation command with `shell=False`;
- create a local commit, including a verified path that requires ready patch/validation evidence and immediately checks the resulting commit SHA, summary, and exact changed paths;
- perform a guarded, non-force push, including a verified handoff that preserves commit provenance through trust/status/branch-policy gates;
- write a local evidence copy or archive package.

The default review commands are read-only. The commands that can change files, run commands, create commits, or push changes are separate and confirmation-gated.

### Evidence and preservation

The final part of the experiment focused on proving that maintenance evidence had not changed:

- evidence bundles, including canonical verified push/post-push provenance binding;
- hash-linked run-history records;
- replay summaries;
- reviewer handoffs;
- archive manifests;
- copied archive roots;
- `.tar`, `.tar.gz`, and `.zip` packages;
- package verification;
- final preservation-completeness checks;
- optional workflow-status freshness evidence.

## How the agents worked

The experiment used two roles:

1. a product-and-engineering role that selected and shipped improvements;
2. a maintenance role focused on failing tests, CI, and maintenance PRs.

Most product work was committed directly to `main`. Historical maintenance work created or updated branches and pull requests; later stewardship cycles use `main` directly and treat old branch/PR work as inspect-before-integrate evidence rather than as the default delivery path.

The `.ai` directory acts as project memory:

- `.ai/AUTONOMOUS_PLAN.md`
- `.ai/AUTONOMOUS_STATE.md`
- `.ai/AUTONOMOUS_CHANGELOG.md`
- `.ai/DECISIONS.md`

This is useful, but it is not a complete event log. The repository does not record a model ID, scheduler ID, token use, or a reliable agent ID for every commit. Therefore, the exact work split between AI agents cannot be proved from Git history alone.

## Testing and CI

### What works

- Tests use temporary directories and deterministic fixtures.
- CI tests Python 3.10, 3.11, and 3.12.
- CI installs the package, compiles the source, checks installed CLI commands, lints the roadmap, and runs pytest.
- Many safety cases are covered: path escapes, symlinks, malformed evidence, hash drift, missing files, overwrites, missing confirmations, and rollback when post-write tracked-diff verification cannot be established.
- The supported-version matrix was restored to green after AUTO-142; AUTO-143 through AUTO-150 also passed their supported-version implementation/test heads. AUTO-151 implementation head `bcb047baad593c231e100f66943df55954b86eed` passed Actions run `31966668746` after removing the duplicate raw push-handoff requirement from canonical verified maintenance evidence.

### Historical failure and recovery

A prior audit produced:

```text
569 passed, 82 failed, 1 skipped
```

Those failures had three main causes:

- maintenance, archive, and replay fixtures that predated newer context-consistency rules;
- planning, validation, executor, and review assertions that predated enriched output contracts;
- router-help behavior where direct Python callers saw successful argparse `SystemExit(0)` rather than the router's numeric return-code contract.

AUTO-141 and AUTO-142 stopped feature delivery and repaired the baseline rather than suppressing failures. The recovery included successful-help normalization without swallowing parser errors, replay-context compatibility fixes, raw history/bundle context consistency, canonical archive destination mapping, semantic validation-step deduplication, deterministic multi-bundle comparison fixtures, replay-policy route identity repair, preservation ranking using actual retained validation context, and assertion updates to the newer structured safety contracts.

GitHub Actions run [31871553378](https://github.com/OmarH-creator/Autonomous-Forge/actions/runs/31871553378) passed package installation, source compilation, installed CLI smoke checks, roadmap lint, and the full pytest suite on Python 3.10, 3.11, and 3.12. AUTO-143 implementation/test run [31881238816](https://github.com/OmarH-creator/Autonomous-Forge/actions/runs/31881238816) also passed the supported matrix after adding live tracked-diff inspection. AUTO-144 implementation/test run [31891899123](https://github.com/OmarH-creator/Autonomous-Forge/actions/runs/31891899123) passed the same supported matrix after adding verified guarded patch apply and rollback coverage. AUTO-145 final run [31903262061](https://github.com/OmarH-creator/Autonomous-Forge/actions/runs/31903262061) passed the supported matrix after adding validation execution tied to verified patch evidence. AUTO-146 implementation/test run [31914016579](https://github.com/OmarH-creator/Autonomous-Forge/actions/runs/31914016579) passed after the new complete-validation coverage gate and its focused tests were added. AUTO-147 implementation/test/documentation run [31923545476](https://github.com/OmarH-creator/Autonomous-Forge/actions/runs/31923545476) passed after adding verified commit creation and immediate post-commit verification. AUTO-148 implementation run [31933115623](https://github.com/OmarH-creator/Autonomous-Forge/actions/runs/31933115623) passed after adding the verified commit-to-push handoff. AUTO-149 final run [31943499555](https://github.com/OmarH-creator/Autonomous-Forge/actions/runs/31943499555) passed after carrying verified provenance through post-push verification. AUTO-150 implementation/test run [31954596328](https://github.com/OmarH-creator/Autonomous-Forge/actions/runs/31954596328) passed after binding that provenance into the durable maintenance-bundle path. AUTO-151 implementation run [31966668746](https://github.com/OmarH-creator/Autonomous-Forge/actions/runs/31966668746) passed after making the verified push wrapper the canonical durable push-stage file.

There is still no dedicated lint, type-check, coverage, or release workflow. There are no tags or GitHub releases. The main workflow in the repository is `.github/workflows/test.yml`; it is a test workflow, not an AI scheduler.

## Is it safe?

The design is safety-aware, but the safety is not proven end to end.

Positive controls include:

- local path and symlink containment;
- simple secret-marker checks without printing file contents;
- explicit confirmation flags for writes, commits, packages, and pushes;
- `shell=False` for the narrow executor command and live git-diff inspection;
- optional post-write target-scoped live-diff verification with rollback to the original target contents on verification failure;
- verified validation results can be tied back to the exact guarded patch evidence before commit readiness;
- verified commit creation stages only reviewed paths and immediately checks the created commit's SHA, summary, and exact changed-path set;
- verified push handoff refuses git activity until commit creation, trust, workflow status, and protected-branch evidence agree on the same reviewed commit;
- post-push verification accepts that verified handoff directly, refuses wrapper/nested provenance drift, and retains reviewed paths plus verified validation commands after remote reachability checks;
- maintenance evidence bundles can use that verified push wrapper as the canonical push-stage file, validate its nested guarded handoff, fingerprint the wrapper, and block durable completion if commit, branch, remote, reviewed paths, or validation commands disagree;
- no force push and no tag push;
- no telemetry or AI API code;
- read-only review commands separated from side-effect commands.

Important limits include:

- live `git-diff-review --current` covers tracked changes relative to `HEAD`, not untracked files;
- verified patch apply covers only the requested tracked target and does not itself run tests or prove correctness;
- verified commit readiness proves coverage of the validation commands retained by the patch, not that those commands are sufficient to establish correctness;
- verified commit creation does not roll back or rewrite history if a created commit later fails immediate verification; it reports `created_unverified` and blocks strict continuation instead;
- verified push handoff trusts repository-local trust/status/branch-protection JSON and does not itself fetch fresh remote workflow or protection evidence;
- post-push verification trusts supplied status-review evidence and local remote-tracking refs unless `--fetch` is explicitly requested;
- durable verified provenance still depends on repository-local JSON artifacts; hashes detect later byte drift but do not prove signer identity;
- canonical push evidence still depends on the verified wrapper's embedded guarded push-handoff being genuine; consistency checks do not provide cryptographic signer identity;
- workflow freshness trusts supplied JSON evidence;
- evidence can be supplied by a caller, so provenance is not fully trusted;
- package signature and signer identity are not fully proved;
- secret detection is not a complete secret scanner;
- some commands can cause real local or remote side effects after confirmation;
- there is no shared lock for external scheduled agents;
- some high-level overview documentation may lag newer guarded capabilities.

## Why did the AI choose this project?

This is an inference from the files and commits, not a claim about hidden model reasoning.

The starting roadmap described a small local tool that could choose one task, check policy, and produce a dry-run report. The experiment also rewarded safe, reviewable changes and discouraged uncontrolled network access, secrets, unsafe commands, and unsafe merges.

A repository-maintenance tool was therefore a natural choice because:

- it matched the safety limits;
- it gave the AI a clear list of small tasks;
- it could be built with standard-library Python;
- each feature could have tests, JSON output, and documentation;
- the repository could act as its own memory.

The project is self-referential: an AI-maintained repository created a tool for safer AI-assisted repository maintenance. This made the experiment easy to continue, but it also encouraged the AI to build more tools for building tools instead of solving one concrete user problem.

## Final judgement

### What succeeded

The AI showed that it can grow a repository from a two-file start into a structured project with a clear architecture, many tests, safety boundaries, durable engineering memory, and—after a dedicated recovery milestone—a green supported-version test baseline.

### What remains incomplete

It has not created an in-repository AI runtime, scheduler, polished end-to-end product demo, production release, or fully trusted evidence-provenance/signature system. A green matrix removes the immediate release blocker; it does not prove the entire maintenance workflow safe for unattended use.

### What it is useful for today

Use it as:

- a case study of AI software stewardship;
- a reference for human-in-the-loop maintenance gates;
- a starting point for safer repository automation;
- a testbed for evidence and replay design.

Do not yet use it as an unattended tool for important repositories.

## Lessons for future experiments

1. Stop feature work whenever `main` is red.
2. Add one shared lock or lease for all scheduled agents.
3. Add a circuit breaker after repeated CI failures.
4. Record agent role, run ID, start/end time, commit list, and CI result. Do not record private prompts.
5. Use one coherent commit per stewardship cycle where practical, or cancel obsolete CI runs.
6. Treat JSON output schemas as contracts and update fixtures before changing them.
7. Add one end-to-end test in a temporary repository: plan → review → patch → validate → commit → evidence.
8. Keep the supported Python matrix green before adding more product surface.
9. Choose a concrete user problem and measure whether the project solves it.

The central lesson is simple:

> Autonomous coding can create impressive structure very quickly. Validation discipline must decide what is allowed to remain.

## Current Autonomous Status

Latest stewardship run: **AUTO-151 — canonical verified push evidence**.

- **Changed:** `forge maintenance-evidence-bundle` no longer requires a duplicate raw `--push-handoff` file when `--verified-push-handoff` is supplied. Canonical mode validates the wrapper's embedded guarded push handoff, reuses the established maintenance-bundle checks, fingerprints the verified wrapper as the push-stage source, and marks the bundle with `push_evidence_source: verified_push_handoff`. Legacy raw input and the prior raw+verified compatibility mode remain supported.
- **Safety:** canonical mode fails closed if the verified wrapper is incomplete, unconfirmed, blocked, missing its nested guarded handoff, or disagrees with that nested handoff on commit, branch, remote, reviewed paths, push completion, force-push policy, or remote-mutation policy. Existing bundle, post-push, durable-write, and history-link gates remain unchanged; no new subprocess, Git, network, push, or workflow mutation was added.
- **Validation:** Actions run `31966668746` on implementation head `bcb047baad593c231e100f66943df55954b86eed` passed package installation, source compilation, installed CLI smoke checks, roadmap validation, and pytest on Python 3.10, 3.11, and 3.12. New deterministic tests prove canonical construction without a standalone raw push file, downstream persisted-bundle hash verification, wrapper/nested commit-drift refusal, parser support, and refusal when neither push evidence input is supplied.
- **Visual updates:** none; AUTO-151 removes a duplicate evidence input inside the existing push → durable evidence boundary, so the architecture itself did not gain a new stage.
- **Current limitations:** the canonical wrapper and other evidence are still repository-local JSON rather than signer-authenticated records. The wrapper embeds the guarded raw handoff, so the duplication is removed at the file/interface level but not replaced by cryptographic identity or proof that retained validation was sufficient.
- **Next autonomous objective:** prove the existing plan → guarded patch → verified validation → commit → push → post-push → durable history chain in one temporary-repository end-to-end integration test, then consider an orchestrating command only if it can preserve every explicit side-effect gate.
