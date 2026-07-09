# Autonomous Decisions

## DEC-117 — 2026-07-09 — Maintenance replay summaries should expose retained validation context

Context: AUTO-115 preserved implementation context under `record.validation_context`, and AUTO-116 exposed that retained context through run-history read/compare surfaces. Persisted maintenance bundles and replay summaries still centered on reviewed paths, validation steps, evidence-chain status, and source-report hashes, so maintainers could not tell from replay output whether a bundle preserved implementation-plan context.
Decision: Update `forge maintenance-replay-summary` to summarize optional bundle `validation_context` fields in text and JSON output. The replay summary reports context presence, supported field names, per-field item counts, and total retained context items, and blocks replayability when context is present but malformed.
Alternatives considered: Add a new bundle-context audit command, ignore context until bundle creation is changed, or treat missing context as a hard replay blocker. A separate command would add surface area, waiting would leave current persisted bundles opaque, and hard-blocking missing context would break older valid bundles that predate context retention.
Consequences: Replay summaries can now show whether completed maintenance evidence preserved implementation-plan context without opening raw bundle JSON. The context remains advisory evidence only; replay summary still does not prove validation coverage or verify every planned file, step, risk, commit, workflow, diff, patch, or policy condition.
Human decision still required: No.

## DEC-116 — 2026-07-09 — Run-history read and compare should expose retained validation context

Context: AUTO-115 made `forge validation-result-write` preserve implementation context under `record.validation_context`, but `forge run-history-read` and `forge run-history-compare` still summarized validation result status without surfacing the retained expected file changes, implementation steps, validation steps, or risk register.
Decision: Update the run-history reader to expose supported validation-context fields in text and JSON summaries, and update run-history comparison to compare validation context as a first-class field while showing before/after context-field presence in the compact overview.
Alternatives considered: Add a new validation-context audit command, expand only JSON output, defer context visibility until bundle verification, or verify validation coverage against the retained fields. Those options either duplicated the command surface, left text users blind, delayed the current evidence-review gap, or implied proof the reader/compare surfaces cannot provide.
Consequences: Maintainers can audit persisted validation context without opening raw JSON and can see when two saved records differ in retained implementation context. The commands remain read-only and advisory; they do not verify validation coverage, commits, workflow status, diffs, patches, or policy compliance.
Human decision still required: No.

## DEC-115 — 2026-07-09 — Validation-result writes should retain implementation context

Context: AUTO-109 through AUTO-114 carried expected file changes, implementation steps, validation steps, and risk register fields from `forge plan` through executor-run output and the validation-result persistence handoff. The final `validation-result-write` persistence step still attached only validation execution/result/note fields, which meant persisted records could lose a normalized context block for the result being attached.
Decision: Update `forge validation-result-write` internals to copy existing implementation context fields from the source run-history record into `record.validation_context` when attaching a supplied validation result. Also report retained context through the Python API while keeping the existing CLI JSON summary compact and backward-compatible.
Alternatives considered: Add a new result-record review command, require executor-output JSON for every validation-result write, expand CLI JSON unconditionally, or automatically verify validation coverage against retained fields. Those options either delayed persistence closure, narrowed a general writer into one executor-only path, risked breaking existing automation, or implied proof the writer cannot provide.
Consequences: Saved validation-result records now preserve implementation intent beside externally supplied validation evidence, making later review and bundling safer. The writer still requires explicit confirmation, does not run commands, does not infer success, and treats retained context as advisory copied from trusted local JSON.
Human decision still required: No.

## DEC-114 — 2026-07-09 — Executor-run results should preserve implementation context

Context: AUTO-109 through AUTO-113 made planning, proposal, validation, orchestration, executor handoff, executor gate, executor contract, and executor dry-run artifacts carry implementation-grade fields, but `forge executor-run` still centered on command text, execution status, return code, captured output, and validation-result persistence command text. That created a structure-loss gap exactly when local validation evidence became observable.
Decision: Update `forge executor-run` and its nested `persistence_handoff` to consume and emit `expected_file_changes`, `implementation_steps`, `validation_steps`, and `risk_register` while preserving existing execution, output-capture, result, and write-command keys. Keep the fields advisory and keep saved-history mutation behind the existing separate explicit `validation-result-write --confirm-write` command.
Alternatives considered: Add another audit/preflight command, create a separate executor-run-v2 command, automatically write enriched validation-result records, or defer context propagation to bundle creation. Those options either duplicated the workflow surface, risked downstream compatibility, expanded write authority, or left observed validation evidence detached from implementation intent.
Consequences: Executor-run output and the persistence handoff now retain implementation objective, planned file targets, validation steps, and risk review beside the observed result. The command still executes only one exact gated command with `shell=false`, does not automatically persist history, and does not inspect diffs, generate patches, stage, commit, push, call networks, or enforce policy decisions.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history.
