# Push handoff

`forge push-handoff` is the guarded push-capable handoff in Autonomous Forge. It consumes ready branch-protection-aware `forge push-readiness --format json` evidence, inspects local git branch/ref state, explicitly confirms that the requested update is fast-forward from the current remote branch, and only runs one non-force `git push <remote> <commit>:refs/heads/<branch>` after `--confirm-push`.

It is intentionally narrow:

- it pushes one verified commit SHA to one branch ref;
- it requires the current local branch, local `HEAD`, and configured upstream to match the requested remote branch;
- it requires push-readiness evidence to prove the protected branch, strict required status checks, required status contexts, observed status contexts, and no missing required contexts;
- it refuses legacy ready push-readiness reports that do not include branch-protection policy fields;
- it refuses unsafe remote and branch names;
- it refuses already-pushed commits;
- it runs `git merge-base --is-ancestor <remote-sha> <verified-commit>` before any confirmed push and blocks non-fast-forward updates;
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

The command above is a review-only handoff. It inspects evidence and local git refs, including the branch-protection fields carried by push-readiness and the fast-forward ancestry check, but it does not push.

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

The push-readiness JSON must be produced by the branch-protection-aware `forge push-readiness` command and must be ready. The handoff also checks:

- protected branch name from the supplied push-readiness report;
- strict branch status-check policy from the supplied push-readiness report;
- required, observed, and missing required status contexts from the supplied push-readiness report;
- current branch from `git branch --show-current`;
- local commit from `git rev-parse HEAD`;
- upstream from `git rev-parse --abbrev-ref --symbolic-full-name @{u}`;
- remote branch commit from `git rev-parse --verify <remote>/<branch>`;
- fast-forward ancestry from `git merge-base --is-ancestor <remote-sha> <verified-commit>`.

## Safety boundary

The command can mutate the remote only when explicitly confirmed and all gates pass. It does not change local files, local commits, remotes, tags, or repository protections, and it refuses to attempt a push when branch policy evidence is missing/stale, when required status contexts are absent, or when the verified commit is not a descendant of the current remote-tracking branch tip.
