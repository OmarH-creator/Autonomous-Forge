# Autonomous Forge Roadmap

## Product vision

Autonomous Forge helps a repository keep a clear improvement plan, choose one safe task, produce reviewable planning artifacts, inspect proposed diffs, review validation status, run tightly scoped validation, apply explicitly confirmed patches, record validation evidence, summarize commit readiness, preview commit metadata, create one explicitly confirmed local commit, verify that created commit, review local commit trust metadata, summarize branch-protection-aware trusted push readiness, run a branch-policy-enforcing explicitly confirmed fast-forward-only non-force push handoff, verify that the pushed commit is reachable from the intended remote branch with clear status evidence, preserve hash-linked durable maintenance evidence bundles, verify persisted bundle source-report integrity, and summarize persisted bundle replay readiness.

## Product scope and non-goals

The first product remains a local Python CLI. It is not a hosted service, deployment system, permission manager, uncontrolled executor, automatic commit bot, force-push bot, branch-protection manager, remote-configuration manager, workflow-rerun bot, polling service, or cryptographic identity authority.

## Current architecture

The repository contains a Python package under `src/autonomous_forge`, tests under `tests/`, command docs under `docs/`, workflow checks under `.github/workflows/`, policy under `.forge/`, and durable memory under `.ai/`. The installed `forge` entry point routes the historical CLI plus extension commands through `src/autonomous_forge/cli_entry_patch.py`; compatibility console scripts remain available through `pyproject.toml`.

## Current implementation status

Roadmap v3 now reaches guarded local commit creation, post-commit verification, commit trust review with optional allowed-signer policy, branch-protection-aware trusted pre-push readiness review, branch-policy-enforcing explicitly confirmed fast-forward-only non-force push handoff, post-push verification, durable maintenance evidence bundles, SHA-256 source-report fingerprints for those bundles, persisted bundle source-report verification, and replay summaries for verified persisted bundles. Product commands still do not force-push, push tags, change remotes, change branch protections, enforce a full cryptographic identity policy, rerun workflows, or poll remote workflow completion.

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

### AUTO-099 — Durable maintenance evidence bundle through AUTO-103
Priority: P1
Status: DONE
Goal: Add durable evidence bundling, bundle source-report fingerprinting, persisted bundle verification, and replay summaries.
Why it matters: Maintainers need one portable run artifact and later verification/replay checks that tie the safe end-to-end maintenance loop together after patch, validation, commit, push, and post-push gates have completed.
Scope: Add `forge maintenance-evidence-bundle`, `forge maintenance-bundle-verify`, `forge maintenance-replay-summary`, compatibility routes, deterministic tests, docs, README workflow examples, CI help smoke, and project-memory updates.
Expected files or areas: `src/autonomous_forge/`, `tests/`, `docs/`, `pyproject.toml`, `.github/workflows/test.yml`, README, and `.ai` records.
Acceptance criteria: Bundles require completed evidence, validate matching commit and reviewed paths across the chain, record SHA-256 source-report fingerprints, detect later drift, summarize replayability, and write bounded JSON only with explicit confirmation.
Validation: Scratch syntax compilation and focused pytest covered the bundle, verification, and replay-summary tests across AUTO-099 through AUTO-103. Static source/test/docs/workflow review completed through the GitHub repository API.
Risks or assumptions: Bundles trust supplied JSON evidence and source-report hashes; they do not sign evidence, prove author identity, rerun workflows, or establish a cryptographic trust model.
Notes: Completed before push trust hardening.

### AUTO-104 — Fast-forward-only push handoff guard
Priority: P1
Status: DONE
Goal: Harden the confirmed push handoff so it refuses non-fast-forward remote updates before attempting any push.
Why it matters: The product now has a push-capable command; safe automation should detect stale or divergent remote history deterministically rather than relying only on the remote `git push` rejection path.
Scope: Extend `forge push-handoff` with an explicit `git merge-base --is-ancestor <remote-sha> <verified-commit>` check after readiness, branch, HEAD, upstream, and remote-ref checks pass; expose `fast_forward_checked`; add focused deterministic tests; update docs, README, and project memory.
Expected files or areas: `src/autonomous_forge/push_handoff.py`, `tests/test_push_handoff.py`, `docs/PUSH_HANDOFF.md`, README, and `.ai` records.
Acceptance criteria: Ready and confirmed handoffs check fast-forward ancestry, already-pushed commits remain blocked, divergent remote history blocks before push execution, wrong branch/unready evidence skips the ancestry check, and no force-push, tag push, remote mutation, branch-protection mutation, staging, commit creation, shell execution, or environment reads are introduced.
Validation: Static source/test/docs review completed through the GitHub repository API. Focused scratch pytest for `tests/test_push_handoff.py` passed with 9 tests, including ready, confirmed push, non-fast-forward refusal, wrong branch, already-pushed commit, git failure, unsafe branch, and local JSON loading cases. Direct full repository checkout/full pytest execution remained unavailable in this environment.
Risks or assumptions: The fast-forward check uses local remote-tracking refs; maintainers should refresh refs before the handoff when remote state may have changed. The command still does not verify branch protection or enforce a full signer allowlist.
Notes: Completed before maintainer allowed-signer policy support.

### AUTO-105 — Maintainer allowed-signer trust policy
Priority: P1
Status: DONE
Goal: Let commit trust review enforce a repository-local allowed-signer policy before push-readiness can pass.
Why it matters: A safe push workflow should not treat every locally trusted signature as equally acceptable for a repository; maintainers need a bounded way to express allowed signer names and key fingerprints.
Scope: Extend `forge commit-trust-review` with `--allowed-signers` JSON input; validate a non-empty `allowed_signers` list; refuse wildcard identity values; block trusted signatures that do not match an allowed signer or key fingerprint; update tests, docs, README, and project memory.
Expected files or areas: `src/autonomous_forge/commit_trust_review.py`, `src/autonomous_forge/commit_trust_review_cli.py`, `tests/test_commit_trust_review.py`, `docs/COMMIT_TRUST_REVIEW.md`, README, and `.ai` records.
Acceptance criteria: Allowed signer matches pass, mismatches block, malformed/empty policies block, unsigned/bad/mismatched commits still block, and no staging, commit, push, network, branch-protection mutation, workflow rerun, or environment-read behavior is introduced.
Validation: Static source/test/docs review completed through the GitHub repository API. Scratch syntax compilation and focused scratch pytest for `tests/test_commit_trust_review.py` passed with 8 tests.
Risks or assumptions: Policy matching uses exact local git signer/key strings and does not manage keys, call GitHub signing APIs, prove organization membership, or replace human maintainer review.
Notes: Completed before branch-protection-aware push readiness.

### AUTO-106 — Branch-protection-aware push readiness
Priority: P1
Status: DONE
Goal: Require supplied branch-protection/status-policy evidence before push-readiness can pass.
Why it matters: A safe push workflow should verify that the target branch is protected and that all required status contexts were observed as clear before any push handoff is considered ready.
Scope: Extend `forge push-readiness` and its CLI with required `--branch-protection` JSON; check protected branch name, strict/up-to-date required status checks, required contexts/checks, and missing required status contexts against supplied status-review evidence; update deterministic tests, docs, README, and project memory.
Expected files or areas: `src/autonomous_forge/push_readiness.py`, `src/autonomous_forge/push_readiness_cli.py`, `tests/test_push_readiness.py`, `docs/PUSH_READINESS.md`, README, and `.ai` records.
Acceptance criteria: Ready evidence requires protected branch evidence, strict required status checks, matching branch, at least one required context, every required context present in status-review evidence, and no verification/trust/status blockers. Unprotected, non-strict, branch-mismatched, missing-context, untrusted, unverified, unclear, or unsafe evidence blocks while `push_allowed` remains false.
Validation: Static source/test/docs review completed through the GitHub repository API. Scratch syntax compilation covered the updated module and CLI. Focused scratch pytest for `tests/test_push_readiness.py` passed with 12 tests.
Risks or assumptions: The branch-protection check trusts supplied JSON and exact status-context names. It does not call GitHub, prove current branch rules, change protection, rerun workflows, poll remote status, or replace human review.
Notes: Completed before branch-policy-enforcing push handoff.

### AUTO-107 — Branch-policy-enforcing push handoff
Priority: P1
Status: DONE
Goal: Require branch-protection-aware push-readiness explicitly at the push-capable handoff boundary.
Why it matters: A safe confirmed push command should not accept stale ready evidence that predates branch-protection/status-policy checks.
Scope: Harden `forge push-handoff` to require protected branch, strict status-check policy, required/observed status contexts, and no missing required contexts from supplied push-readiness evidence; expose those fields in the handoff report; update tests, docs, README, and project memory.
Expected files or areas: `src/autonomous_forge/push_handoff.py`, `tests/test_push_handoff.py`, `docs/PUSH_HANDOFF.md`, README, and `.ai` records.
Acceptance criteria: Ready branch-policy evidence still permits review/confirmed handoff when git refs are safe; legacy readiness without branch-policy fields blocks; protected branch mismatch blocks; missing required status contexts block; fast-forward, already-pushed, wrong-branch, unsafe-branch, and git-failure guards remain intact; no force-push, tag push, remote mutation, branch-protection mutation, staging, commit creation, shell execution, or environment reads are introduced.
Validation: Static source/test/docs review completed through the GitHub repository API. Focused scratch pytest for `tests/test_push_handoff.py` passed with 12 tests.
Risks or assumptions: The handoff trusts branch-policy fields carried by push-readiness JSON and exact status-context names. It does not call GitHub, prove branch rules are current, change protections, rerun workflows, or replace human review.
Notes: Next safe step is durable run-history linkage for completed pushed bundles.

## Future Ideas

- Hash-linked local run reports.
- Optional issue import.
- Policy-aware changed-file summaries.
- Branch protection and workflow-status replay summaries.
- Durable run-history linkage for completed pushed maintenance bundles.
