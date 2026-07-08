# Autonomous Decisions

## DEC-064 — 2026-07-08 — Gate patch-intent work on clear diff-source evidence

Context: `forge diff-source-handoff --require-clear` can fail closed on changed or non-clear content-audit comparison evidence, but future patch-intent work needs a separate review surface that consumes that evidence and clearly says whether patch-intent description may proceed.
Decision: Add `forge patch-intent-review` as a read-only gate over one supplied diff-source handoff JSON payload. It reports `ready` only when the payload is read-only, attention-free, unchanged across all compared paths, clear after review, and has no changed fields. `--require-ready` returns exit code `2` for blocked evidence.
Alternatives considered: Generate patch intent directly from diff-source evidence, inspect git diffs, make `diff-source-handoff` also own patch readiness, infer patch approval from clear evidence, or postpone the gate until patch generation exists.
Consequences: Future patch-adjacent workflows get a conservative process gate before any patch-intent description. A ready result still does not approve patches, inspect diffs, run commands, or prove correctness.
Human decision still required: No.

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

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
