# Commit Status Review

`forge commit-status-review` reviews supplied commit-status, check-run, or workflow-run JSON evidence before a future patch-application workflow relies on validation status.

The command is intentionally local-first and read-only. It does not call GitHub, poll workflows, run commands, or infer correctness beyond the supplied JSON fields. A maintainer or automation can export status evidence from GitHub or another system, save it as a repository-local `.json` file, and ask Autonomous Forge to summarize whether all supplied contexts are successful.

## Usage

```bash
forge commit-status-review \
  --root . \
  --status commit-status.json \
  --require-clear \
  --format json

forge-commit-status-review \
  --root . \
  --status commit-status.json \
  --format text
```

## Accepted evidence shapes

The command accepts a JSON object with one or more of these fields:

- `statuses`: GitHub combined-status style entries using `context`, `state`, `description`, and optionally `target_url`.
- `check_runs`: check-run style entries using `name`, `status` or `conclusion`, and optionally `html_url` or `details_url`.
- `workflow_runs`: workflow-run style entries using `name`, `status`, `conclusion`, and optionally `html_url`.
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

Commit-status review reads supplied JSON status evidence only. It does not call networks, poll GitHub, run workflows, run commands, inspect diffs, read repository file contents, infer correctness beyond supplied status fields, approve implementation, enforce policy decisions, mutate saved history, read environment variables, commit, push, or change repository files.
