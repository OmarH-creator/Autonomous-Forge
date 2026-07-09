# Post-push verification

`forge post-push-verify` verifies the last guarded push handoff after it has executed.

The command consumes:

- a pushed `forge push-handoff --format json` report;
- a clear `forge commit-status-review --format json` report for the same commit;
- local remote-tracking ref evidence from `git rev-parse --verify <remote>/<branch>` and `git merge-base --is-ancestor <commit> <remote>/<branch>`.

It reports `verified` only when the pushed commit is reachable from the intended remote branch and the status review is clear for the same commit.

## Example

```bash
forge post-push-verify \
  --root . \
  --push-handoff push-handoff.json \
  --status-review verified-commit-status-review.json \
  --require-verified \
  --format json > post-push-verify.json
```

Use `--fetch` when the local remote-tracking ref should be refreshed first:

```bash
forge post-push-verify \
  --root . \
  --push-handoff push-handoff.json \
  --status-review verified-commit-status-review.json \
  --fetch \
  --require-verified \
  --format json
```

## Safety boundary

The command never pushes, force-pushes, creates commits, stages files, changes remotes, changes branch protections, reruns workflows, or uses shell execution. `--fetch` runs only `git fetch --prune <remote> <branch>` for the remote and branch recorded in the handoff evidence.
