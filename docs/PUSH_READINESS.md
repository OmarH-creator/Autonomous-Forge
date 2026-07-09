# Push-readiness gate

`forge push-readiness` combines verified local commit evidence with fresh commit-status review evidence before any future push command is considered.

The command is intentionally non-pushing. It reads two repository-local JSON files, reports whether the evidence is ready for human push consideration, and keeps `push_allowed` and `remote_changes_allowed` false.

## Inputs

- `--commit-verify`: JSON from `forge commit-verify --format json`.
- `--status-review`: JSON from `forge commit-status-review --format json`, typically collected with `--from-github` for the verified commit.
- `--root`: repository root used to constrain both JSON inputs.

Both inputs must stay inside the configured root, use `.json`, be bounded in size, and not be symlinks.

## Example

```bash
forge commit-status-review --root . --from-github --commit-sha abc1234 --require-clear --format json > commit-status-review.json
forge push-readiness \
  --root . \
  --commit-verify commit-verify.json \
  --status-review commit-status-review.json \
  --require-ready \
  --format json > push-readiness.json
```

A ready report requires:

- `commit-verify` status is `verified`.
- Verified commit SHA matches the status-review commit SHA.
- Status review is `clear` with at least one successful context.
- No failed, pending, unknown, or blocker status evidence is present.
- Reviewed paths are safe repository-relative labels.

## Safety boundary

`forge push-readiness` never runs `git`, calls networks, stages files, creates commits, pushes, changes remotes, reads environment variables, or modifies the working tree. It is a pre-push evidence gate only.
