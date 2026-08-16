# Post-push verification

`forge post-push-verify` verifies the last guarded push handoff after it has executed.

The command consumes either:

- a pushed `forge push-handoff --format json` report; or
- the provenance-rich pushed `forge verified-push-handoff --format json` report from the verified patch → validation → commit → push chain;

plus:

- a clear `forge commit-status-review --format json` report for the same commit;
- local remote-tracking ref evidence from `git rev-parse --verify <remote>/<branch>` and `git merge-base --is-ancestor <commit> <remote>/<branch>`.

When a verified push-handoff wrapper is supplied, Forge also requires its commit, branch, remote, and reviewed paths to agree with the nested guarded push-handoff evidence. The output preserves the verified validation commands so later durable evidence can retain the same provenance chain.

It reports `verified` only when the pushed commit is reachable from the intended remote branch, the status review is clear for the same commit, and any verified-handoff provenance is internally consistent.

## Example

```bash
forge post-push-verify \
  --root . \
  --push-handoff verified-push-handoff.json \
  --status-review verified-commit-status-review.json \
  --require-verified \
  --format json > post-push-verify.json
```

Use `--fetch` when the local remote-tracking ref should be refreshed first:

```bash
forge post-push-verify \
  --root . \
  --push-handoff verified-push-handoff.json \
  --status-review verified-commit-status-review.json \
  --fetch \
  --require-verified \
  --format json
```

## Safety boundary

The command never pushes, force-pushes, creates commits, stages files, changes remotes, changes branch protections, reruns workflows, or uses shell execution. `--fetch` runs only `git fetch --prune <remote> <branch>` for the remote and branch recorded in the handoff evidence. Verified wrappers fail closed if their retained provenance disagrees with the nested guarded push evidence.
