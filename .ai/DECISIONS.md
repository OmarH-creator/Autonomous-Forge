# Autonomous Decisions

## DEC-120 — 2026-07-09 — Replay policy gates should be compact and reviewer-friendly

Context: AUTO-119 made replay summaries fail closed when retained validation context conflicts with reviewed paths or validation steps, but maintainers still had to read raw blockers and detailed replay output to understand which replayability gates passed, failed, or remained advisory.
Decision: Add compact replay policy-gate summaries and expose them through `forge-maintenance-replay-policy-summary` for bundle-first review workflows. The gates are source-report integrity, bundle completion, evidence-chain status, reviewed-path presence, validation-step presence, and validation-context consistency.
Alternatives considered: Leave replay policy only inside raw replay blockers, add a separate audit/preflight command, make missing validation context a hard blocker, or expand bundle verification instead. A compact policy-summary command improves reviewability without adding write authority; hard-blocking missing context would break older valid bundles.
Consequences: Maintainers can triage persisted bundle replay quality from named pass/fail/advisory gates. The summary remains advisory persisted-evidence review and does not rerun validation, inspect diffs, verify branch protections, or prove validation coverage.
Human decision still required: No.

## DEC-119 — 2026-07-09 — Maintenance replay should check retained context consistency

Context: AUTO-118 made newly generated maintenance bundles and history links preserve retained validation context, and AUTO-117 made replay summaries expose that context. Replayability still only checked whether context was present and well formed, so a bundle could remain replayable even if retained expected file changes no longer referenced reviewed paths or retained validation steps no longer matched the bundle's preserved validation evidence.
Decision: Update `forge maintenance-replay-summary` to compute `validation_context_consistency`. When retained expected file changes are present, each reviewed path must be represented by at least one retained expected-change entry. When retained validation steps are present, each retained step must also appear in the bundle's validation steps. Mismatches block replayability.
Alternatives considered: Add a separate context-audit command, make every missing context field a hard failure, only warn in text output, or attempt to prove validation coverage. A separate command would add workflow surface area, hard-failing missing context would break older valid bundles, warnings would let inconsistent evidence pass, and validation-coverage proof is beyond replay summary authority.
Consequences: Persisted bundle replay now fails closed when retained implementation context conflicts with reviewed-path or validation-step evidence. The check remains advisory evidence comparison; it does not rerun validation, inspect diffs, verify signatures, prove policy compliance, or guarantee that validation covered every planned file, step, or risk.
Human decision still required: No.

## DEC-118 — 2026-07-09 — Maintenance bundle creation should preserve validation context

Context: AUTO-117 made `forge maintenance-replay-summary` report retained validation context when a persisted bundle includes it, but `forge maintenance-evidence-bundle` did not yet copy supported upstream validation-context fields into newly generated bundles or the optional run-history link pointer. That meant new bundles could lose implementation-plan context before replay review.
Decision: Update maintenance bundle creation and history-link output to retain supported `validation_context` fields from upstream evidence: `expected_file_changes`, `implementation_steps`, `validation_steps`, and `risk_register`. Malformed validation context now blocks bundle completion rather than being silently ignored.
Alternatives considered: Preserve context only in the persisted bundle, preserve context only in the history link, defer to a new audit command, or ignore context until a larger replay redesign. Preserving it in both bundle and link keeps durable evidence and discoverability aligned; a separate command would add surface area and deferral would keep the replay-summary improvement underfed.
Consequences: Newly generated bundles and history links can carry implementation-plan evidence into replay summaries. The retained context remains advisory JSON evidence only; the bundle still does not prove validation coverage for every planned file, step, or risk.
Human decision still required: No.

## 2026-07-09 — Historical decisions

Older autonomous decision entries remain available in repository history.
