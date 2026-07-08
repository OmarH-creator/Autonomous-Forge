# Autonomous Decisions

## DEC-083 — 2026-07-08 — Supplied git diffs need bounded policy review before patch application

Context: The repository had a long patch-adjacent evidence chain through content audit, diff-source handoff, patch-intent review, patch text review, patch-application preflight, patch-application audit, and patch-application readiness. It still explicitly lacked git-diff inspection, so future patch-applier design would not have a native way to inspect changed paths and diff metadata before considering application.
Decision: Add `forge git-diff-review` plus compatibility `forge-git-diff-review` as a local read-only command over a repository-local `.diff` or `.patch` file. It parses unified diff headers, file status, hunk counts, additions, deletions, old/new path labels, policy status, and path-presence signals, with `--require-clear` for fail-closed advisory gating.
Alternatives considered: Move directly to a patch applier, keep relying on JSON evidence summaries only, add documentation-only guidance, run `git diff` internally, or check workflow status first.
Consequences: Maintainers now get bounded supplied-diff inspection without applying patches or running commands. The command still does not read target file contents, generate patch text, apply patches, run validation, check workflow status, approve implementation, mutate history, commit, push, or change files.
Human decision still required: No.

## DEC-082 — 2026-07-08 — Patch application needs a final readiness summary before applier design

Context: Patch-application preflight can confirm reviewed patch-text evidence and explicit provenance metadata, and patch-application audit can verify that provenance remains internally consistent while actual application stays disallowed. Maintainers still need one compact checkpoint that confirms both evidence files agree before any future write-capable patch-applier design is considered.
Decision: Add `forge patch-application-readiness` plus compatibility `forge-patch-application-readiness` as a read-only summary over supplied preflight and audit JSON. It requires read-only payloads, compares objectives, reviewed paths, validation steps, upstream blockers, and confirms both inputs keep `patch_application_allowed` false. The readiness command itself also keeps `patch_application_allowed` false.
Alternatives considered: Move directly to a patch applier, make patch-application audit imply readiness, inspect git diffs, generate patch text, or document the handoff without a command surface.
Consequences: Maintainers gain a final advisory evidence checkpoint before any future guarded patch-applier design. The command still does not read target contents, inspect git diffs, generate patch text, apply patches, run commands, check workflow status, mutate history, commit, push, or change files.
Human decision still required: No.

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

## Historical note

Older autonomous decision entries remain available in repository history. This compact decision log prioritizes the latest direct mainline stewardship decisions so the current state remains easy to review.