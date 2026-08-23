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

After `git add`, Forge now reads the exact staged target from the index with `git show :<target>`, applies the same 1 MB bound, computes its SHA-256, and requires it to equal the validated target digest before `git commit` is allowed. This closes the ordinary race where a concurrent edit could land between the pre-stage working-tree hash check and staging. The staged digest is retained in the verified commit-creation report for review.

These are fail-closed staleness and index-continuity checks rather than a shared Git index lock. Another process that mutates the index after the staged digest check and before `git commit` can still race; post-commit verification continues to enforce the resulting SHA, summary, and exact changed-path set.

The command reuses the existing `verified-validation-run`, `verified-commit-readiness`, and `verified-commit-create` contracts. It does not push, change remotes, poll workflows, force-push, or modify branch protections. Push and post-push stages remain separate reviewable commands.
