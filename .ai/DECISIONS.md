# Autonomous Decisions

## DEC-075 — 2026-07-08 — Patch text preflight must gate the same evidence it prints

Context: `forge patch-text-preflight --require-ready` previously produced formatted output from one read of the draft evidence, then performed the readiness gate by re-reading and re-parsing the same draft path. That was deterministic for stable files, but it left an avoidable race where a changed draft could make one invocation print one state and gate another.
Decision: Introduce a reusable `read_patch_text_preflight_data` helper and update the CLI to resolve, read, validate, format, and gate one shared in-memory preflight result per invocation.
Alternatives considered: Keep the duplicate read because normal local files are stable, only optimize JSON-format invocations, or document the limitation without changing code.
Consequences: The CLI behavior is simpler and safer. Text and JSON output, plus `--require-ready`, now use the same trusted evidence snapshot without expanding authority beyond the existing read-only draft/metadata preflight surface.
Human decision still required: No.

## DEC-074 — 2026-07-08 — Patch text work needs a metadata preflight before patch text exists

Context: Patch proposal draft previews can confirm ready review evidence, target paths, and validation plans, but moving directly from draft evidence to patch text would skip an explicit check that the future patch text scope has per-path metadata aligned with the draft targets.
Decision: Add `forge patch-text-preflight` as a primary `forge` subcommand. It consumes draft-ready patch proposal JSON plus explicit `--path` / `--change-summary` metadata, verifies exact alignment with draft targets, and offers `--require-ready` as a fail-closed process gate.
Alternatives considered: Generate patch text immediately, extend patch proposal draft output, require git-diff inspection first, or rely on documentation-only guidance.
Consequences: Maintainers gain a safe handoff between draft-ready evidence and future patch text review without granting implementation authority. The command still does not read target file contents, inspect git diffs, generate patch text, apply patches, run commands, approve implementation, mutate history, commit, push, or change files.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
