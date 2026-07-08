# Autonomous Decisions

## DEC-073 — 2026-07-08 — Patch proposal drafts must remain read-only evidence previews

Context: Patch proposal review now produces ready evidence from explicit manifests and fresh content-audit JSON, but the product still lacks a safe intermediate surface before any future patch text or git-diff workflow. Jumping directly from review evidence to patch generation would blur the boundary between reviewed intent and actual implementation.
Decision: Add `forge patch-proposal-draft` plus compatibility `forge-patch-proposal-draft` as a read-only preview that consumes ready proposal-review JSON and emits objective, target paths, validation plan, draft sections, blockers, next step, and safety boundary. Gate it with `--require-draft-ready` for fail-closed process use.
Alternatives considered: Generate patch text immediately, extend patch proposal review output instead of adding a dedicated draft preview, rely only on documentation, or wait until git-diff inspection exists.
Consequences: Maintainers get a stable proposal-draft handoff without granting implementation authority. The command still does not read target file contents, inspect git diffs, generate patches, apply patches, run commands, approve implementation, mutate history, commit, push, or change files.
Human decision still required: No.

## DEC-072 — 2026-07-08 — CI must exercise the primary patch proposal review route

Context: The product now documents and tests `forge patch-proposal-review` as the primary command surface, but the live GitHub Actions smoke chain still used only the compatibility `forge-patch-proposal-review` console script for the end-to-end proposal-review step. A future packaging or router regression could therefore pass CI while breaking the documented workflow.
Decision: Update CI to smoke-test `forge patch-proposal-review --help`, run the primary `forge patch-proposal-review --require-ready` command in the installed end-to-end chain, still run `forge-patch-proposal-review` for compatibility, JSON-validate both outputs, and assert that compatibility output equals the primary output for the same evidence.
Alternatives considered: Rely only on deterministic unit tests, replace the compatibility command entirely, keep CI focused on the standalone script, or wait until patch draft previews exist.
Consequences: CI now protects the documented primary workflow and the compatibility route without changing runtime behavior. The smoke path remains read-only and still does not inspect git diffs, generate or apply patches, run implementation commands, approve changes, commit, or push.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
