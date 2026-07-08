# Commit Status Review

`forge commit-status-review` reviews commit-status, check-run, or workflow-run evidence before a future patch-application or commit-readiness workflow relies on validation status.

The default mode remains local-first and read-only over a repository-local JSON file. When explicitly requested with `--from-github`, the command moves beyond supplied evidence by shelling out to local `git` and GitHub CLI (`gh`) to collect workflow-run status for a commit. That live collection path reads only the current commit SHA and workflow-run metadata; it does not rerun workflows, inspect logs, apply patches, commit, push, or change files.

## Usage

```bash
forge commit-status-review \
  --root . \
  --status commit-status.json \
  --require-clear \
  --format json

forge commit-status-review \
  --root . \
  --from-github \
  --commit-sha abc1234 \
  --require-clear \
  --format json

forge-commit-status-review \
  --root . \
  --from-github \
  --format text
```

`--from-github` defaults to `git rev-parse HEAD` when `--commit-sha` is omitted. It then runs `gh run list --commit <sha>` and normalizes the returned workflow runs into the same review model used for supplied JSON status evidence.

## Accepted evidence shapes

The command accepts a JSON object with one or more of these fields:

- `statuses`: GitHub combined-status style entries using `context`, `state`, `description`, and optionally `target_url`.
- `check_runs`: check-run style entries using `name`, `status` or `conclusion`, and optionally `html_url` or `details_url`.
- `workflow_runs`: workflow-run style entries using `name`, `status`, `conclusion`, and optionally `html_url` or `url`.
- `state`: a single combined status when no context list is present.

Successful states are treated as clear. Failed or errored states, pending/in-progress states, unknown states, and missing status evidence are blocked. `--require-clear` changes only the process exit code.

## Example

```json
{
  "sha": "abc123",
  "statuses": [
    {"context": "ci/test", "state": "success", "description": "passed"}
  ],
  "workflow_runs": [
    {"name": "Test", "status": "completed", "conclusion": "success"}
  ]
}
```

## Safety boundary

Supplied-status mode reads repository-local JSON status evidence only. It does not call networks, poll GitHub, run workflows, run commands, inspect diffs, read repository file contents, infer correctness beyond supplied status fields, approve implementation, enforce policy decisions, mutate saved history, read environment variables, commit, push, or change repository files.

Live GitHub mode is opt-in. It shells out only to local `git` and `gh` to collect workflow-run metadata for one commit, then applies the same deterministic review logic. It does not rerun workflows, inspect job logs, read repository file contents, apply patches, commit, push, or change files.
