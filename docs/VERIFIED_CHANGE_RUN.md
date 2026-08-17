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

The command reuses the existing `verified-validation-run`, `verified-commit-readiness`, and `verified-commit-create` contracts. It does not push, change remotes, poll workflows, force-push, or modify branch protections. Push and post-push stages remain separate reviewable commands.
