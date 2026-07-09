# Push handoff

`forge push-handoff` is the first guarded push-capable handoff in Autonomous Forge. It consumes ready `forge push-readiness --format json` evidence, inspects local git branch/ref state, and only runs one non-force `git push <remote> <commit>:refs/heads/<branch>` after `--confirm-push`.

It is intentionally narrow:

- it pushes one verified commit SHA to one branch ref;
- it requires the current local branch, local `HEAD`, and configured upstream to match the requested remote branch;
- it refuses unsafe remote and branch names;
- it refuses already-pushed commits;
- it never force-pushes, pushes tags, changes remotes, changes branch protections, stages files, creates commits, reads environment variables, or uses shell execution.

## Example

```bash
forge push-handoff \
  --root . \
  --push-readiness push-readiness.json \
  --branch main \
  --remote origin \
  --format json > push-handoff.json
```

The command above is a review-only handoff. It inspects evidence and local git refs, but it does not push.

To execute the guarded push after the report is ready:

```bash
forge push-handoff \
  --root . \
  --push-readiness push-readiness.json \
  --branch main \
  --remote origin \
  --confirm-push \
  --require-pushed \
  --format json > push-handoff.json
```

## Fail-closed behavior

Use `--require-pushed` when automation should fail unless a push was executed. Without `--require-pushed`, blocked or ready review reports can still return successfully so a maintainer can inspect the report.

## Inputs

The push-readiness JSON must be produced by `forge push-readiness` and must be ready. The handoff also checks:

- current branch from `git branch --show-current`;
- local commit from `git rev-parse HEAD`;
- upstream from `git rev-parse --abbrev-ref --symbolic-full-name @{u}`;
- remote branch commit from `git rev-parse --verify <remote>/<branch>`.

## Safety boundary

The command can mutate the remote only when explicitly confirmed and all gates pass. It does not change local files, local commits, remotes, tags, or repository protections.
