# Autonomous Decisions

## DEC-062 — 2026-07-08 — Make diff-source evidence fail closed when requested

Context: `forge diff-source-handoff` exposes whether content-audit comparison evidence requires attention, but future patch-adjacent workflows need an explicit process-level gate instead of parsing output manually.
Decision: Add `--require-clear` to `forge diff-source-handoff`. The command remains read-only and continues to print the same text or JSON output, but returns exit code `2` whenever the comparison's `requires_attention` value is true.
Alternatives considered: Add a separate gate command, make all diff-source handoffs fail when attention is required, infer patch approval from clear evidence, or postpone gating until patch generation exists.
Consequences: Future local scripts can fail closed on changed or non-clear content-audit evidence while preserving the existing review output and safety boundary. Clear evidence still does not approve patches or prove correctness.
Human decision still required: No.

## DEC-061 — 2026-07-08 — Add a diff-source handoff before patch work

Context: `forge content-audit` can produce bounded, read-only file-content observations, but future patch-adjacent workflows need a safe way to compare two reviewed content-audit outputs before relying on those observations.
Decision: Add `forge diff-source-handoff` as a read-only comparison of two explicit content-audit JSON outputs. The command constrains inputs under the configured root, refuses malformed or non-content-audit payloads, reports changed observation fields, and leaves all patch generation, git-diff inspection, command execution, workflow polling, and policy enforcement out of scope.
Alternatives considered: Generate patches directly, inspect `git diff`, compare raw file contents, make `content-audit` compare files itself, or postpone patch-adjacent evidence review until a full executor exists.
Consequences: The product now has a reviewable bridge from explicit content metadata to future patch/diff workflows while preserving the no-patch, no-diff, no-command, no-mutation safety boundary.
Human decision still required: No.

## DEC-060 — 2026-07-08 — Cover installed content-audit entrypoint behavior

Context: GitHub Actions exercises `forge content-audit` through the installed package script, which routes through `autonomous_forge.cli_entry`, while existing focused tests mostly covered the content-audit core and base command surfaces.
Decision: Add deterministic regression coverage for the installed entrypoint path, including JSON success for an allowed readable file and a missing-policy refusal case.
Alternatives considered: Rely only on workflow smoke coverage, duplicate the command entirely in the base CLI, add broader extension-command tests in one larger sweep, or defer coverage until diff-source handoff work.
Consequences: The installed package route used by CI is now protected by fast deterministic tests without changing content-audit runtime behavior. Future entrypoint extensions should receive similar targeted coverage.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
