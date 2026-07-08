# Autonomous Forge Roadmap

## Product vision

Autonomous Forge helps a repository keep a clear improvement plan, choose one safe task, produce reviewable planning artifacts, inspect proposed diffs, review supplied validation status, run tightly scoped local validation, preview guarded patch text, and record what happened.

## Product scope and non-goals

The first product remains a local Python command-line tool. It reads repository files, reports safe next actions, runs only explicitly confirmed allowlisted local validation commands, audits explicit content metadata without printing content, compares supplied audit evidence, can fail closed on requested clear-evidence gates, reviews supplied unified git diff metadata against policy, flags binary and metadata-only diff evidence for separate review, reviews supplied commit/workflow status JSON evidence, summarizes combined change readiness, reviews patch-intent readiness, describes patch-intent handoff readiness from supplied evidence, creates explicit patch proposal manifests from reviewed evidence and maintainer-supplied objective/path/validation fields, reviews manifests against fresh content-audit evidence, previews patch proposal draft outlines from ready review evidence, preflights explicit patch-text metadata against draft-ready evidence from one shared validated evidence snapshot, reviews explicit patch-text summary metadata against ready preflight evidence, preflights explicit patch provenance metadata against ready patch-text review evidence, audits patch-application preflight provenance evidence, summarizes patch-application readiness from ready preflight and clear audit evidence before patch generation, generates bounded patch preview text from explicit replacement content, and keeps durable project memory. It is not a hosted platform, dashboard, deployment system, permission-management tool, automatic patch applier, live workflow poller, or uncontrolled autonomous executor.

## Current architecture

The repository contains a Python package under `src/autonomous_forge`, package metadata in `pyproject.toml`, tests under `tests/`, policy documentation under `docs/`, a visual orientation document at `docs/OVERVIEW.md`, command output contracts under `docs/`, focused command documentation under `docs/`, an example policy under `.forge/`, and contributor guidance in `CONTRIBUTING.md`. The installed `forge` console script routes through a small compatibility entry point that exposes primary extension commands and delegates established commands to the base CLI. `forge-change-readiness`, `forge-commit-status-review`, `forge-git-diff-review`, `forge-patch-application-audit`, `forge-patch-application-preflight`, `forge-patch-application-readiness`, `forge-patch-generation-preview`, `forge-patch-proposal-review`, `forge-patch-proposal-draft`, and `forge-patch-text-review` remain as compatibility scripts.

## Current implementation status

Roadmap v1 established the local CLI, task parsing, deterministic task selection, and dry-run reports. Roadmap v2 added conservative policy parsing, policy-readiness reporting, roadmap linting, command output contracts, run-summary preview output, repository health inventory file-presence signals, and a visual project overview. Roadmap v3 has advanced the policy-aware maintenance workflow through implementation plans, proposals, validation previews, review artifacts, run-history records, validation-result handoff, orchestration readiness, command-execution handoff, executor gates, executor contracts, a read-only executor dry-run, a narrow opt-in local executor that can run one exact validation command without a shell, explicit executor-result persistence handoff, guarded executor-handoff persistence, validation-result audits, executor-observation audits with fail-closed gating, latest-limited history audit windows, content-audit, supplied git-diff review with binary/metadata-only hardening, supplied commit-status review, combined change-readiness summaries, diff-source handoff, patch-intent review, patch-intent description, patch proposal manifests, patch proposal review, patch proposal draft previews from ready review evidence, patch text preflight checks from explicit per-path metadata, single-read evidence reuse for patch-text preflight CLI formatting and readiness gating, patch text review from ready preflight evidence plus explicit per-path patch summaries, patch application preflight from ready patch-text review evidence plus explicit provenance metadata, patch application provenance audit from ready preflight evidence, patch application readiness summary from ready preflight plus clear audit evidence, guarded patch-generation preview from explicit replacement content, and CI smoke coverage for key primary/compatibility review routes. Product commands still do not apply patches, execute arbitrary implementation plans, poll live workflow status, cryptographically verify commits, or commit changes.

## Technical debt

The CLI can select work, describe policy boundaries, build reviewable plans and proposals, describe validation intent, preview validation command candidates, review explicit paths, audit explicit file-content metadata without printing content, inspect supplied unified git diff metadata and changed paths, flag binary and metadata-only diff evidence for separate review, review supplied commit/workflow status JSON evidence, combine diff/status evidence into a single readiness artifact, compare supplied content-audit JSON outputs, fail closed on non-clear or non-ready evidence when requested, review patch-intent readiness from supplied diff-source evidence, describe future patch-intent handoff readiness from supplied patch-review evidence while refusing unsafe candidate path labels, build explicit patch proposal manifests from described evidence and maintainer-supplied objective/path/validation fields, review proposal manifests against fresh content-audit evidence through the primary command surface while refusing missing validation-step evidence, preview patch proposal draft outlines from ready review evidence, preflight explicit patch-text metadata against draft-ready evidence from one validated data object per CLI invocation, review explicit patch text summaries against ready preflight evidence, preflight explicit patch provenance metadata against ready patch-text review evidence while keeping patch application disallowed, audit patch-application preflight provenance evidence while still keeping application disallowed, summarize readiness from matching preflight and audit evidence while still keeping application disallowed, generate bounded unified diff previews from explicit replacement text while still keeping application disallowed, preview and inspect durable run-history records, attach externally supplied validation results, expose orchestration readiness, expose command-execution handoff data, expose executor precondition gates, define an executor contract, dry-run one exact executor candidate command, run one exact confirmed local validation command without a shell, show the exact explicit command for persisting the observed executor result, persist reviewed executor-run JSON through guarded validation-result semantics, audit saved validation observations, audit aggregate saved executor observations across latest-limited direct history records, and preserve hidden path tokens in planned file-area parsing when punctuation follows. It does not yet append to a hash-linked long-lived history index, apply patches, verify commits beyond supplied status evidence, poll live workflow status, or execute approved implementation plans. Runtime test execution and main-branch CI observation were unavailable from the automation environment for the latest direct commits.

## Prioritized roadmap

## Roadmap v1 — Completed foundation

### AUTO-001 through AUTO-004 — Local CLI, roadmap parsing, task selection, and dry-run reports
Priority: P1-P2
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

### AUTO-005 through AUTO-017 — Policy, linting, inventory, and run-summary previews
Priority: P1-P3
Status: DONE

Goal: Establish policy parsing, roadmap linting, contributor guidance, command contracts, repository inventory, and run-summary preview behavior.
Why it matters: The product needs a safe local reporting surface before proposing implementation work.
Scope: Keep behavior local-first and read-only while improving repository understanding and durable memory design.
Expected files or areas: `src/autonomous_forge/`, `tests/`, README, `docs/`, `.forge/`.
Acceptance criteria: Implemented commands remain deterministic, documented, and covered by focused tests.
Validation: Added deterministic unit and CLI coverage across the implemented read-only surfaces; PR #4 GitHub Actions passed before JSON run-summary integration.
Risks or assumptions: Do not imply command execution, patch generation, policy enforcement, or automatic history persistence.
Notes: Historical detailed task records remain available in repository history.

## Roadmap v3 — Policy-aware planning toward safe maintenance workflow

### AUTO-018 through AUTO-056 — Planning, review, history, validation executor, and observation gates
Priority: P1
Status: DONE

Goal: Advance the safe end-to-end workflow from selected task to review artifacts, local validation execution, guarded result persistence, and saved-observation audits.
Why it matters: Maintainers need machine-readable planning, proposal, validation, command-candidate, path-review, executor, and history evidence before any patch behavior can be considered.
Scope: Add structured plan output, change proposals, validation plans/previews, explicit changed-file reviews, CI smoke checks, combined review artifacts, run-history read/write/list/latest/compare, validation-result preview/write/audit, command-execution handoff, executor gate/contract/dry-run/run, executor-result persistence handoff, guarded handoff persistence, and executor-observation audit with `--require-clear`.
Expected files or areas: `src/autonomous_forge/`, `tests/`, README, `docs/`, `.github/workflows/test.yml`, `.ai` records.
Acceptance criteria: Outputs are deterministic, text and JSON behavior are covered where applicable, CI smoke checks exercise live repository inputs, execution is limited to one exact confirmed no-shell local validation command, writes require explicit confirmation, and patch/diff generation remains absent.
Validation: Deterministic tests and static review were completed through the GitHub repository API. Installed-package CI smoke coverage exercises the current command chain. Direct local checkout execution remained unavailable in this environment.
Risks or assumptions: These surfaces are advisory except for explicit local validation execution and explicit local persistence. They must not imply arbitrary command execution, patch generation, git-diff inspection, approval, automatic write persistence, or policy enforcement.
Notes: Historical detailed task records remain available in repository history.

### AUTO-057 through AUTO-082 — Content audit and patch-proposal evidence readiness
Priority: P1
Status: DONE

Goal: Add read-only content-audit checkpoints, compare supplied content-audit outputs, provide fail-closed evidence gates, review patch-intent readiness, describe patch-intent handoff readiness, refuse unsafe candidate path labels, build explicit patch proposal manifests, review those manifests against fresh content-audit evidence, expose that final review through the primary `forge` command surface, require validation-step evidence, protect primary and compatibility proposal-review routes in CI, preview patch proposal draft outlines from ready review evidence, preflight patch-text metadata against draft-ready evidence, ensure preflight output/gating derive from one validated evidence snapshot, review explicit patch-text summaries against ready preflight evidence, preflight explicit patch provenance metadata against ready patch-text review evidence, audit patch-application preflight provenance evidence before any write-capable patch behavior, summarize patch-application readiness from ready preflight and clear audit evidence before applier design, and smoke-test the current audit chain in CI.
Why it matters: Patch-adjacent workflows need a safe bridge between policy-reviewed paths, content metadata, patch-intent readiness, safe candidate path labels, explicit objectives, requested paths, validation steps, fresh content-audit evidence, ready proposal reviews, draft-ready proposal context, explicit patch-text metadata, reviewed patch-text summaries, explicit patch provenance, provenance audits, readiness summaries, and installed-route confidence without printing content, generating patches, applying patches, or treating changed evidence as safe by default.
Scope: Add content-audit, diff-source handoff, patch-intent review, patch-intent description, patch proposal manifest, patch proposal review, validation-step enforcement, primary/compatibility CI coverage, `forge patch-proposal-draft --format text|json` with `--require-draft-ready`, `forge-patch-proposal-draft` compatibility, `forge patch-text-preflight --format text|json` with `--require-ready`, single-read preflight data reuse, `forge patch-text-review --format text|json` with `--require-ready`, `forge-patch-text-review` compatibility, `forge patch-application-preflight --format text|json` with `--require-ready`, `forge-patch-application-preflight` compatibility, `forge patch-application-audit --format text|json` with `--require-clear`, `forge-patch-application-audit` compatibility, `forge patch-application-readiness --format text|json` with `--require-ready`, `forge-patch-application-readiness` compatibility, and CI smoke coverage for the primary and compatibility audit outputs.
Expected files or areas: `pyproject.toml`, `src/autonomous_forge/cli_entry_patch.py`, `src/autonomous_forge/content_audit.py`, `src/autonomous_forge/diff_source_handoff.py`, `src/autonomous_forge/patch_intent_review.py`, `src/autonomous_forge/patch_intent_description.py`, `src/autonomous_forge/patch_proposal_manifest.py`, `src/autonomous_forge/patch_proposal_review.py`, `src/autonomous_forge/patch_proposal_draft.py`, `src/autonomous_forge/patch_text_preflight.py`, `src/autonomous_forge/patch_text_review.py`, `src/autonomous_forge/patch_application_preflight.py`, `src/autonomous_forge/patch_application_audit.py`, `src/autonomous_forge/patch_application_readiness.py`, `src/autonomous_forge/*_cli.py`, `tests/`, `.github/workflows/test.yml`, README, `docs/`, `.ai` records.
Acceptance criteria: Patch application readiness consumes supplied patch-application preflight and audit JSON, requires ready/clear upstream evidence, verifies matching objective, reviewed paths, validation steps, and blocker-free upstream evidence, keeps `patch_application_allowed` false, supports `--require-ready`, is covered by deterministic core/CLI/router tests, and never reads repository file contents, generates patch text, applies patches, runs commands, approves implementation, commits, pushes, or changes files.
Validation: Static source/test/documentation review completed through the GitHub repository API. Deterministic unit/CLI/router tests cover the implemented content-audit, diff-source, patch-intent, patch-description, manifest, review, draft, preflight, patch text review, patch application preflight, patch application audit, patch application readiness, primary-routing, and compatibility behaviors. CI smoke assertions cover unchanged live content-audit/diff-source/patch-intent/description/manifest/review/draft/preflight/review/audit evidence gates through primary and compatibility routes where applicable.
Risks or assumptions: Secret-marker checks are intentionally simple guard signals, not complete secret scanning. A clear content-audit, unchanged diff-source handoff, ready patch-intent review, described patch-intent description, ready patch proposal manifest, ready patch proposal review, draft-ready patch proposal draft result, ready patch text preflight result, ready patch text review result, ready patch application preflight result, clear patch application audit result, or ready patch application readiness result does not approve patches, prove correctness, or replace human review. `--require-clear`, `--require-ready`, `--require-described`, and `--require-draft-ready` change only the process exit code.
Notes: Completed before moving into supplied git-diff inspection.

### AUTO-083 through AUTO-087 — Diff/status review and guarded patch preview
Priority: P1
Status: DONE

Goal: Move beyond evidence-only review by inspecting supplied diffs, connecting them to supplied validation status, and generating bounded patch preview text only from explicit replacement content and ready upstream evidence.
Why it matters: A safe end-to-end maintenance workflow needs reviewable diff evidence, validation evidence, and generated patch text before any patch applier is designed.
Scope: Add supplied git-diff review, binary/metadata hardening, supplied commit-status review, combined change-readiness, and `forge patch-generation-preview` / `forge-patch-generation-preview`.
Expected files or areas: `src/autonomous_forge/git_diff_review.py`, `src/autonomous_forge/commit_status_review.py`, `src/autonomous_forge/change_readiness.py`, `src/autonomous_forge/patch_generation_preview.py`, `src/autonomous_forge/*_cli.py`, `src/autonomous_forge/cli_entry_patch.py`, `pyproject.toml`, `tests/`, README, `docs/`, and `.ai` records.
Acceptance criteria: Patch-generation preview accepts ready patch-application readiness JSON, requires the target path to be reviewed, reads one explicit replacement text file, produces bounded unified diff preview text, blocks identical replacements and simple secret-marker strings, supports `--require-generated`, keeps `patch_application_allowed` false, and never applies patches, runs commands, calls networks, mutates history, commits, pushes, or changes files.
Validation: Static source/test/documentation review completed through the GitHub repository API. Deterministic tests were added for generated previews, blocked upstream evidence, identical text, unreviewed paths, unsafe paths, CLI JSON output, fail-closed generated gating, and secret-marker refusal. Direct local checkout/test execution remained unavailable in this environment.
Risks or assumptions: Generated patch previews can expose non-secret repository text by design and rely on simple secret-marker refusal rather than complete secret scanning. A generated preview is not approval and does not prove validation success or patch safety.
Notes: Next safe step is an explicitly confirmed patch-applier design that consumes generated previews plus clear diff/status evidence.

## Future Ideas

- Hash-linked local run reports.
- Optional issue import.
- Policy-aware changed-file summaries.
- Explicit validation orchestration after validation plans are reviewable.
- Read-only patch application provenance audits before any patch applier exists.
- Guarded commit and workflow status inspection before patch application.
- Explicitly confirmed patch applier after generated preview, clear diff evidence, and clear status evidence.

## Do Not Change Without Explicit Human Approval

- Remote and branch settings.
- Repository visibility and access controls.
- Production infrastructure.
