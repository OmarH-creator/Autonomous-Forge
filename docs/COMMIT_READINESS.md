# Commit readiness

`forge commit-readiness` is a read-only summary for the final checkpoint after a guarded patch apply.

It consumes three repository-local JSON artifacts:

1. `forge post-apply-validation --format json`
2. final `forge git-diff-review --format json`
3. `forge commit-status-review --format json`, either supplied or collected with `--from-github`

The command reports `ready` only when the post-apply validation is validated, the final diff review is clear, the validated target path is present in that final diff review, and the commit-status review is clear.

```bash
forge commit-readiness \
  --root . \
  --post-apply-validation post-apply-validation.json \
  --diff-review git-diff-review.json \
  --status-review commit-status-review.json \
  --require-ready \
  --format json > commit-readiness.json
```

Compatibility entry point:

```bash
forge-commit-readiness \
  --root . \
  --post-apply-validation post-apply-validation.json \
  --diff-review git-diff-review.json \
  --status-review commit-status-review.json
```

Safety boundary:

- It does not run validation commands.
- It does not collect live workflow status; use `forge commit-status-review --from-github` before this command when live evidence is needed.
- It does not inspect raw diffs or repository file contents.
- It does not apply patches, create commits, push, or mutate saved history.
- It keeps `commit_allowed` and `commit_workflow_allowed` false. A ready result is advisory evidence for human review or a future separately guarded commit workflow.
