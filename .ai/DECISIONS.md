# Autonomous Decisions

## DEC-079 — 2026-07-08 — Patch application needs a provenance audit before any write-capable design

Context: Patch-application preflight can confirm ready patch-text review evidence and explicit per-path provenance metadata, but future patch-application design still needs a separate audit checkpoint that verifies the supplied preflight evidence remains internally consistent and keeps actual patch application disallowed.
Decision: Add `forge patch-application-audit` plus compatibility `forge-patch-application-audit` as a read-only provenance audit. It consumes one patch-application preflight JSON payload, validates safe path/source metadata, checks count consistency, requires non-empty validation steps, carries forward preflight blockers, supports `--require-clear`, and always keeps `patch_application_allowed` false.
Alternatives considered: Move directly to a patch applier, fold this audit into patch-application preflight, inspect git diffs, or rely on documentation-only provenance expectations.
Consequences: Maintainers gain a clearer final advisory checkpoint before any future patch-application design. The command still does not read target file contents, inspect git diffs, generate patch text, apply patches, run commands, check workflow status, approve implementation, mutate history, commit, push, or change files.
Human decision still required: No.

## DEC-077 — 2026-07-08 — Patch application preflight must prove provenance without allowing application

Context: Patch text review now confirms ready preflight evidence and explicit per-path patch summaries, but moving directly from reviewed patch text toward any future patch-application design would require provenance checks that every reviewed path has an explicit source and matching expected summary.
Decision: Add `forge patch-application-preflight` plus compatibility `forge-patch-application-preflight` as a read-only advisory preflight. It consumes ready patch-text review JSON plus explicit `--path`, `--patch-source`, and `--expected-summary` metadata, requires exact reviewed-path coverage, rejects extra provenance paths, and confirms expected summaries match reviewed summaries. `patch_application_allowed` remains hard-coded to `false` because no patch applier exists.
Alternatives considered: Generate or apply patch text immediately, extend patch text review with application semantics, require a git diff first, or document the provenance expectation without a command gate.
Consequences: Maintainers gain a safer pre-application evidence handoff without introducing write-capable patch behavior. The command still does not read target contents, inspect git diffs, generate patch text, apply patches, run commands, approve implementation, mutate history, commit, push, or change files.
Human decision still required: No.

## DEC-076 — 2026-07-08 — Patch text review must stay advisory before patch generation

Context: Patch text preflight now confirms draft-ready evidence and explicit per-path metadata, but moving directly from preflight to generated or applied patch text would blur the line between reviewed scope and implementation authority.
Decision: Add `forge patch-text-review` plus compatibility `forge-patch-text-review` as a read-only review gate. It consumes ready preflight JSON plus explicit `--path` / `--patch-summary` metadata, verifies exact alignment with preflight targets, and offers `--require-ready` as a fail-closed process gate.
Alternatives considered: Generate patch text immediately, extend patch text preflight output, inspect git diffs first, or rely on documentation-only guidance.
Consequences: Maintainers gain a safe advisory handoff before any future patch-text generation or apply workflow. The command still does not read target file contents, inspect git diffs, generate patch text, apply patches, run commands, approve implementation, mutate history, commit, push, or change files.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
