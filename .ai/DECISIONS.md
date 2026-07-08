# Autonomous Decisions

## DEC-076 — 2026-07-08 — Patch text review must stay advisory before patch generation

Context: Patch text preflight now confirms draft-ready evidence and explicit per-path metadata, but moving directly from preflight to generated or applied patch text would blur the line between reviewed scope and implementation authority.
Decision: Add `forge patch-text-review` plus compatibility `forge-patch-text-review` as a read-only review gate. It consumes ready preflight JSON plus explicit `--path` / `--patch-summary` metadata, verifies exact alignment with preflight targets, and offers `--require-ready` as a fail-closed process gate.
Alternatives considered: Generate patch text immediately, extend patch text preflight output, inspect git diffs first, or rely on documentation-only guidance.
Consequences: Maintainers gain a safe advisory handoff before any future patch-text generation or apply workflow. The command still does not read target file contents, inspect git diffs, generate patch text, apply patches, run commands, approve implementation, mutate history, commit, push, or change files.
Human decision still required: No.

## DEC-075 — 2026-07-08 — Patch text preflight must gate the same evidence it prints

Context: `forge patch-text-preflight --require-ready` previously produced formatted output from one read of the draft evidence, then performed the readiness gate by re-reading and re-parsing the same draft path. That was deterministic for stable files, but it left an avoidable race where a changed draft could make one invocation print one state and gate another.
Decision: Introduce a reusable `read_patch_text_preflight_data` helper and update the CLI to resolve, read, validate, format, and gate one shared in-memory preflight result per invocation.
Alternatives considered: Keep the duplicate read because normal local files are stable, only optimize JSON-format invocations, or document the limitation without changing code.
Consequences: The CLI behavior is simpler and safer. Text and JSON output, plus `--require-ready`, now use the same trusted evidence snapshot without expanding authority beyond the existing read-only draft/metadata preflight surface.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
