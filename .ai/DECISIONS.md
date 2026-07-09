# Autonomous Decisions

## DEC-113 — 2026-07-09 — Executor handoff should preserve implementation context

Context: AUTO-109 through AUTO-112 made `forge plan`, `forge propose`, `forge validate-plan`, `forge validation-preview`, and `forge validation-orchestration` carry implementation-grade fields, but `forge command-execution-handoff`, `forge executor-gate`, `forge executor-contract`, and `forge executor-dry-run` still centered on command candidates, gate status, confirmation flags, and result-record targets. That created a structure-loss gap immediately before validation execution.
Decision: Update executor handoff/gate/contract/dry-run artifacts to consume and emit `expected_file_changes`, `implementation_steps`, `validation_steps`, and `risk_register` while preserving existing command candidate, gate, contract, dry-run, and result-capture keys. Keep the fields advisory and do not expand execution authority.
Alternatives considered: Add another audit/preflight command, create separate v2 executor artifacts, replace existing command/gate fields, or defer context propagation until executor-run/result persistence. Those options either duplicated the workflow surface, risked downstream compatibility, or left confirmed executor review without full implementation context.
Consequences: Executor review now retains the implementation objective, planned file targets, validation steps, and risk register before any explicitly confirmed validation execution. These commands still do not enforce policy decisions, inspect diffs, generate patches, stage, commit, push, call networks, or mutate repository state.
Human decision still required: No.

## DEC-112 — 2026-07-09 — Validation preview and orchestration should preserve implementation context

Context: AUTO-109 through AUTO-111 made `forge plan`, `forge propose`, and `forge validate-plan` carry implementation-grade fields, but `forge validation-preview` and `forge validation-orchestration` still centered on command candidates, blockers, risk notes, and run-history guards. That created another structure-loss gap before executor contract and dry-run handoff.
Decision: Update `forge validation-preview` and `forge validation-orchestration` to consume and emit `expected_file_changes`, `implementation_steps`, `validation_steps`, and `risk_register` while preserving backward-compatible command-candidate summaries, blockers, risk notes, and run-history guard keys. Keep both commands read-only and advisory.
Alternatives considered: Add another audit/preflight command, create separate v2 preview/orchestration commands, replace existing command-candidate/history fields, or wait until executor work. Those options either duplicated the surface, risked breaking downstream consumers, or left executor handoff without full implementation context.
Consequences: Validation-preview and orchestration artifacts now retain the same structured implementation context selected by `forge plan` and refined by proposal/validation-plan stages. The commands still do not enforce policy decisions, run commands, inspect diffs, generate patches, stage, commit, push, call networks, or mutate repository state.
Human decision still required: No.

## DEC-111 — 2026-07-09 — Validation plans should preserve enriched proposal fields

Context: AUTO-109 made `forge plan` emit implementation-grade fields and AUTO-110 carried them into `forge propose`, but `forge validate-plan` still reduced the handoff mostly to validation steps, expected file areas, path checks, and flattened risk notes. That created a structure-loss gap before validation preview and executor orchestration.
Decision: Update `forge validate-plan` to consume and emit the proposal's `expected_file_changes`, `implementation_steps`, `validation_steps`, and `risk_register` fields while preserving backward-compatible `expected_file_areas`, `path_checks`, and `risk_notes` keys for existing consumers. Keep the command read-only and advisory.
Alternatives considered: Add another audit/preflight command, create a separate validation-plan-v2 command, replace existing path-check fields outright, or defer propagation until validation-preview work. Those options either duplicated workflow surface, broke downstream compatibility, or left the proposal/validation handoff incomplete.
Consequences: Validation-plan artifacts now carry the same implementation-grade structure selected by `forge plan` and reviewed by `forge propose`, improving downstream handoff consistency. The command still does not enforce policy decisions, run commands, inspect diffs, generate patches, stage, commit, push, call networks, or mutate repository state.
Human decision still required: No.

## DEC-110 — 2026-07-09 — Proposals should preserve enriched plan fields

Context: AUTO-109 made `forge plan` emit implementation-grade fields, but `forge propose` still reduced selected tasks to generic planned operations and policy lists. That created a handoff gap between planning and proposal review.
Decision: Update `forge propose` to consume and emit the planner's `expected_file_changes`, `implementation_steps`, `validation_steps`, and `risk_register` fields while preserving backward-compatible `planned_file_areas` and `planned_operations` keys for existing consumers. Keep the command read-only and advisory.
Alternatives considered: Add another audit/preflight command, create a separate proposal-v2 command, replace existing proposal fields outright, or defer propagation until validation-plan work. Those options either duplicated workflow surface, broke downstream compatibility, or left the planning/proposal handoff incomplete.
Consequences: Proposal artifacts now carry the same implementation-grade structure selected by `forge plan`, improving downstream review consistency. The command still does not enforce policy decisions, run commands, inspect diffs, generate patches, stage, commit, push, call networks, or mutate repository state.
Human decision still required: No.

## DEC-109 — 2026-07-09 — Forge plan output should be implementation-grade

Context: The immediate product objective remains a policy-aware `forge plan` command. The command already selected the highest-priority eligible task and exposed policy/path information, but its output still left implementation steps, normalized file targets, validation steps, and risk review mostly embedded in prose.
Decision: Enrich `forge plan` text and JSON output with deterministic `implementation_steps`, `expected_file_changes`, `validation_steps`, and `risk_register` fields derived from the selected roadmap task and repository policy. Keep the command read-only and advisory.
Alternatives considered: Add another patch/audit/preflight command, create a separate planner-v2 command, defer planning improvements until proposal generation, or make `forge plan` execute validation. Those options either violated the current product objective or increased risk beyond planning.
Consequences: The plan artifact is now more concrete and directly reviewable before proposal, validation, and change execution. The command still does not enforce policy decisions, run commands, inspect diffs, generate patches, stage, commit, push, call networks, or mutate repository state.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history.