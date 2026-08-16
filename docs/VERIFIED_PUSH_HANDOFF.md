# Verified push handoff

`forge verified-push-handoff` connects the verified local commit path to the existing protected-branch push gates.

It accepts four repository-local JSON inputs:

- `--verified-commit`: output from `forge verified-commit-create` with `commit_status=created` and `commit_verified=true`;
- `--commit-trust`: trusted commit-signature review for the same SHA and reviewed paths;
- `--status-review`: successful commit status/workflow review for that SHA;
- `--branch-protection`: protected-branch evidence with strict required status checks.

Example review-only handoff:

```bash
forge verified-push-handoff \
  --verified-commit .ai/run-history/verified-commit.json \
  --commit-trust .ai/run-history/commit-trust.json \
  --status-review .ai/run-history/status-review.json \
  --branch-protection .ai/run-history/branch-protection.json \
  --branch main \
  --remote origin \
  --format json
```

To execute the already-reviewed push, add `--confirm-push`. The command reuses the existing `push-readiness` and `push-handoff` contracts. It therefore verifies the commit/trust/status/branch-policy chain before local git inspection, requires the current branch/HEAD/upstream to match, checks that the requested update is fast-forward-only, and runs only:

```text
git push <remote> <verified-commit>:refs/heads/<branch>
```

It never force-pushes, pushes tags, changes remotes, changes branch protections, or bypasses explicit confirmation. `--require-pushed` makes automation exit non-zero unless the guarded push actually completed.

The command preserves the reviewed path list and verified validation-command list from `verified-commit-create` in its output so later post-push verification and durable evidence can retain the same provenance chain.
