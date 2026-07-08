# Autonomous Decisions

## DEC-074 — 2026-07-08 — Patch text work needs a metadata preflight before patch text exists

Context: Patch proposal draft previews can confirm ready review evidence, target paths, and validation plans, but moving directly from draft evidence to patch text would skip an explicit check that the future patch text scope has per-path metadata aligned with the draft targets.
Decision: Add `forge patch-text-preflight` as a primary `forge` subcommand. It consumes draft-ready patch proposal JSON plus explicit `--path` / `--change-summary` metadata, verifies exact alignment with draft targets, and offers `--require-ready` as a fail-closed process gate.
Alternatives considered: Generate patch text immediately, extend patch proposal draft output, require git-diff inspection first, or rely on documentation-only guidance.
Consequences: Maintainers gain a safe handoff between draft-ready evidence and future patch text review without granting implementation authority. The command still does not read target file contents, inspect git diffs, generate patch text, apply patches, run commands, approve implementation, mutate history, commit, push, or change files.
Human decision still required: No.

## DEC-073 — 2026-07-08 — Patch proposal drafts must remain read-only evidence previews

Context: Patch proposal review now produces ready evidence from explicit manifests and fresh content-audit JSON, but the product still lacks a safe intermediate surface before any future patch text or git-diff workflow. Jumping directly from review evidence to patch generation would blur the boundary between reviewed intent and actual implementation.
Decision: Add `forge patch-proposal-draft` plus compatibility `forge-patch-proposal-draft` as a read-only preview that consumes ready proposal-review JSON and emits objective, target paths, validation plan, draft sections, blockers, next step, and safety boundary. Gate it with `--require-draft-ready` for fail-closed process use.
Alternatives considered: Generate patch text immediately, extend patch proposal review output instead of adding a dedicated draft preview, rely only on documentation, or wait until git-diff inspection exists.
Consequences: Maintainers get a stable proposal-draft handoff without granting implementation authority. The command still does not read target file contents, inspect git diffs, generate patches, apply patches, run commands, approve implementation, mutate history, commit, push, or change files.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
