# Verified change run

`forge verified-change-run` is the first orchestration surface for the already-proven guarded maintenance chain. It composes a live-diff-verified patch with all validation steps retained by that patch, verified commit readiness, and optional verified local commit creation.

```bash
forge verified-change-run \
  --patch-apply .ai/evidence/patch-apply.json \
  --status-review .ai/evidence/status-review.json \
  --summary "fix: apply reviewed maintenance change" \
  --confirm-validation \
  --confirm-commit-create \
  --require-committed \
  --format json
```

The command does not introduce a single all-powerful confirmation. Validation execution is gated by `--confirm-validation`; commit creation is separately gated by `--confirm-commit-create`. If validation fails, later validation commands are not run and commit creation is not attempted. If validations pass but commit confirmation is omitted, the result stops at `ready_for_commit`.

After every retained validation command passes, Forge hashes the exact current bytes of the reviewed target and stores that SHA-256 in verified commit-readiness evidence. Immediately before any `git status`/`git add` step, verified commit creation re-hashes the target and requires an exact match. A file edited after validation therefore fails closed before staging instead of allowing stale or unvalidated bytes into the commit. The target hash is bounded to the same 1 MB review envelope and must resolve to a regular non-symlink file inside the repository root.

This is a staleness guard rather than a shared filesystem lock: another writer could still race in the narrow interval between the pre-stage hash check and `git add`. Commit verification continues to check the resulting SHA, summary, and exact changed-path set after creation.

The command reuses the existing `verified-validation-run`, `verified-commit-readiness`, and `verified-commit-create` contracts. It does not push, change remotes, poll workflows, force-push, or modify branch protections. Push and post-push stages remain separate reviewable commands.
