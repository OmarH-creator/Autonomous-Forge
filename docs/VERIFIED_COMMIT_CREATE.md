# Verified commit creation

`forge verified-commit-create` carries ready `forge verified-commit-readiness` evidence into one explicitly confirmed local commit and immediately verifies the resulting commit SHA, summary, and changed paths.

Example:

```bash
forge verified-commit-create \
  --root . \
  --verified-readiness .ai/run-history/verified-readiness.json \
  --summary "feat: apply reviewed maintenance change" \
  --body-line "Validation evidence retained by verified readiness." \
  --confirm-commit-create \
  --require-verified \
  --format json
```

The command refuses non-ready or contradictory readiness evidence before invoking git. It stages only the reviewed paths carried by that readiness artifact, creates one local commit, then checks the resulting commit SHA, summary, and exact changed-path set. A commit that exists but cannot be verified is reported as `created_unverified` and `--require-verified` exits non-zero.

Safety boundary:

- repository-local bounded JSON input only;
- explicit `--confirm-commit-create` required before any staging or commit;
- `git add` is scoped to reviewed paths;
- no push, force-push, tag push, remote changes, branch-protection changes, network calls, or workflow polling;
- post-commit verification is immediate and read-only;
- the command does not roll back a commit that was created but failed post-commit verification; that state is surfaced as a blocker for human handling.
