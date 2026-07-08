# Executor Result Handoffs

`forge executor-run` now includes a `persistence_handoff` section in both text and JSON output.

The handoff converts the observed executor result into the exact explicit command a maintainer may run to persist that result through `forge validation-result-write`.

## Safety boundary

The handoff is advisory only. It does not:

- write or rewrite run-history records;
- infer validation success beyond the executor return code;
- hide failed, timed-out, or launch-failed validation runs;
- poll workflows, verify commits, inspect diffs, generate patches, enforce policy, commit, or push.

Persistence still requires the existing explicit `--confirm-write` flag on `forge validation-result-write`.

## Example JSON fields

```json
{
  "persistence_handoff": {
    "available": true,
    "auto_persistence": false,
    "confirmation_required": "--confirm-write",
    "record": ".ai/run-history/latest.json",
    "validation_result": "passed",
    "validation_note": "executor-run completed for 'python -m pytest'; return_code=0",
    "write_command": "forge validation-result-write --root . --record .ai/run-history/latest.json --result passed --note 'executor-run completed for '\''python -m pytest'\''; return_code=0' --confirm-write"
  }
}
```

## Typical flow

```bash
forge executor-run \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root . \
  --command "python -m pytest" \
  --confirm-executor-dry-run \
  --format json
```

Review `persistence_handoff.write_command`. Run it only when the observed executor result should be saved to the selected run-history record.
