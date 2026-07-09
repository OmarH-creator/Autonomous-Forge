# Autonomous Decisions

## DEC-097 — 2026-07-09 — Remote push must be explicit, non-force, and ref-checked

Context: The workflow can now verify a created local commit and combine it with clear workflow status in a push-readiness report, but it still had no concrete handoff beyond evidence review.
Decision: Add `forge push-handoff` plus compatibility `forge-push-handoff`. The command consumes ready push-readiness JSON, validates safe branch and remote names, checks the current local branch, local `HEAD`, configured upstream, and remote branch SHA, reports readiness without pushing by default, and only runs one non-force `git push <remote> <commit>:refs/heads/<branch>` after `--confirm-push`.
Alternatives considered: Keep push fully manual, add a push directly to push-readiness, allow generic git push arguments, force-push when remote diverges, push tags automatically, or change remotes/protections from the tool.
Consequences: Maintainers now have a concrete guarded remote handoff. The command intentionally mutates the configured remote when explicitly confirmed and all checks pass, but it still does not force-push, push tags, change remotes, change branch protections, create commits, or verify post-push workflow status.
Human decision still required: No.

## DEC-096 — 2026-07-09 — Push readiness requires verified commit and clear status evidence

Context: The workflow can now create one explicitly confirmed local commit and verify that the created commit matches reviewed commit-create evidence, but it still had no single gate that combines that verified commit evidence with fresh workflow status before any future push workflow.
Decision: Add `forge push-readiness` plus compatibility `forge-push-readiness`. The command consumes commit-verify JSON and commit-status-review JSON, requires verified commit evidence, requires the status-review commit SHA to match the verified commit SHA, requires successful status evidence with no failed/pending/unknown contexts, validates safe reviewed paths, supports fail-closed `--require-ready`, and keeps `push_allowed` and `remote_changes_allowed` false.
Alternatives considered: Move directly to a push command, add push-readiness inside commit-verify, rely on README guidance, require signed commits first, or trust commit-status evidence without matching the verified commit SHA.
Consequences: Maintainers now have a deterministic pre-push checkpoint while the product still cannot push. The command trusts supplied upstream evidence, does not verify signatures or author identity, and does not prove remote branch safety.
Human decision still required: No.

## DEC-095 — 2026-07-09 — Created commits need local verification before push readiness

Context: The workflow can now create one explicitly confirmed local commit from reviewed commit proposal evidence, but the product had no command that verifies the created commit still matches the reviewed SHA, message, and changed paths before any future push workflow.
Decision: Add `forge commit-verify` plus compatibility `forge-commit-verify`. The command consumes created commit-create JSON evidence, validates that push and remote authority remain disabled, inspects the local commit with `git show` and `git diff-tree`, compares the commit SHA, subject, reviewed body lines, and exact changed paths, and supports fail-closed `--require-verified` behavior.
Alternatives considered: Move directly to push-readiness, add verification inside commit-create, rely on manual `git show`, or require signed commits before any verification command.
Consequences: Maintainers now have a concrete post-commit verification checkpoint before any push workflow is considered. The command trusts supplied commit-create evidence and local git output, does not verify signatures or authorship, and never pushes or mutates the working tree.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history.
