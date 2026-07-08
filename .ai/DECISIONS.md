# Autonomous Decisions

## DEC-080 — 2026-07-08 — Patch-application audit must be smoke-tested in the installed workflow

Context: `forge patch-application-audit` and compatibility `forge-patch-application-audit` now provide the final read-only provenance audit before any future patch-application design, but the installed GitHub Actions smoke chain still stopped at patch-application preflight.
Decision: Extend the installed CLI smoke workflow to run both primary and compatibility patch-application audit commands after preflight, parse both JSON outputs, assert clear audit status, verify patch application remains disallowed, check provenance and reviewed-path alignment, require validation-step evidence, and assert primary/compatibility output parity.
Alternatives considered: Rely on deterministic unit tests only, add documentation instead of CI coverage, move directly to a patch-applier design, or test only the primary route.
Consequences: The release workflow now exercises the full current read-only patch-adjacent evidence chain through the installed command surface. This remains advisory and does not generate patches, apply patches, inspect git diffs, run implementation commands, approve changes, mutate repository contents, commit, or push from product code.
Human decision still required: No.

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

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.
