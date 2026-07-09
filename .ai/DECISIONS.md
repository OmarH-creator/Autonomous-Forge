# Autonomous Decisions

## DEC-121 — 2026-07-09 — Run-history links should have a pointer-level quality review

Context: AUTO-120 added compact replay policy gates for persisted maintenance bundles, but maintainers still had to open a full bundle before knowing whether a small `.ai/run-history/` pointer contained enough information to continue replay review.
Decision: Add `forge maintenance-history-link-review` and `forge-maintenance-history-link-review` as read-only commands that validate one persisted history-link schema and report compact quality gates for confirmed link write status, bundle path/hash pointer, reviewed paths, validation steps, required source-report stage pointers, and retained validation context.
Alternatives considered: Fold pointer review into `forge maintenance-replay-summary`, require every history link to include validation context, or skip pointer review and rely only on bundle verification. Folding it into replay summary would require opening full bundles before pointer quality is known, hard-failing missing context would make older links unusable, and skipping pointer review leaves run-history navigation less trustworthy.
Consequences: Maintainers can triage a run-history pointer before deeper hash-linked bundle replay. The new command reviews pointer quality only; it does not read the linked bundle, recompute hashes, rerun validation, poll workflows, inspect diffs, verify signatures, or prove validation coverage.
Human decision still required: No.

## DEC-120 — 2026-07-09 — Replay summaries should expose compact policy gates

Context: AUTO-119 made `forge maintenance-replay-summary` block replayability when retained validation context no longer matched reviewed paths or preserved validation steps. The output still required maintainers to interpret raw blockers, source-report summaries, and consistency fields to understand which replay checks passed, failed, or were advisory.
Decision: Add a compact `replay_policy` summary to `forge maintenance-replay-summary` with deterministic gates for source-report integrity, bundle completion, evidence-chain status, path review, validation-step presence, and validation-context consistency. Gates report `passed`, `failed`, or `advisory` plus required/advisory severity and a short reason.
Alternatives considered: Add a separate replay-policy command, expand only text output, or make missing validation context a hard failure. A separate command would add surface area, text-only output would leave JSON consumers without structured gates, and hard-failing missing context would break older valid bundles that predate context preservation.
Consequences: Maintainers can quickly see why a persisted bundle is replayable or blocked without opening raw JSON. The gates summarize existing persisted evidence only; they do not rerun validation, poll workflows, verify signatures, inspect diffs, or prove actual validation coverage.
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
