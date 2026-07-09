# Autonomous Decisions

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

## DEC-094 — 2026-07-09 — Commit creation must be explicit, local, and non-pushing

Context: The workflow can now apply one explicitly confirmed replacement, record supplied post-apply validation evidence, review supplied or live-collected status evidence, summarize commit readiness, and preview commit metadata. The next valuable step is moving beyond metadata preview into actual local commit creation without creating a push bot.
Decision: Add `forge commit-create` plus compatibility `forge-commit-create`. The command consumes ready commit-proposal-preview JSON, validates safe reviewed paths and disabled push/remote fields, requires `--confirm-commit-create`, checks local git status for reviewed paths, stages only reviewed paths, runs one local `git commit` with the reviewed message, reports the created commit SHA, and keeps `push_allowed` and `remote_changes_allowed` false.
Alternatives considered: Keep commit creation manual only, create a push workflow immediately, add commit creation inside commit-proposal-preview, infer commit metadata from diffs, or allow broad `git add .` behavior.
Consequences: Maintainers now have a concrete local commit step in the safe end-to-end workflow. The command intentionally mutates local git state only after explicit confirmation, still trusts supplied upstream evidence, and does not sign, verify, or push commits.
Human decision still required: No.

## DEC-093 — 2026-07-09 — Commit metadata preview comes before commit creation

Context: The workflow can now apply one explicitly confirmed replacement, record supplied post-apply validation evidence, review supplied or live-collected status evidence, and summarize commit readiness. Before any command creates commits, maintainers need a deterministic preview of the intended commit metadata that still cannot mutate Git state.
Decision: Add `forge commit-proposal-preview` plus compatibility `forge-commit-proposal-preview`. The command consumes ready commit-readiness JSON and explicit summary/body metadata. It reports `ready` only when commit-readiness evidence is ready, read-only, blocker-free, contains reviewed paths and validation steps, and keeps commit authority disabled. It keeps `commit_allowed`, `commit_creation_allowed`, and `push_allowed` false.
Alternatives considered: Move directly to a commit command, embed commit message text inside commit-readiness, rely on README guidance, infer metadata from diffs, or make the preview inspect repository contents.
Consequences: Maintainers get a reviewable commit message artifact before any future commit workflow. The command does not prove the metadata is ideal, does not create commits, and still trusts supplied commit-readiness evidence.
Human decision still required: No.

## Historical note

Older autonomous decision entries remain available in repository history.
