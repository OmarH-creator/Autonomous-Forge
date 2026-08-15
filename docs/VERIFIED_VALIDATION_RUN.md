# Verified validation run

`forge verified-validation-run` connects a live-diff-verified guarded patch apply to the existing narrow validation executor.

It is intentionally stricter than calling `forge executor-run` directly. Before any subprocess can start, the command requires repository-local patch-apply JSON showing all of the following:

- the patch was actually applied and changed one target;
- `patch_application_allowed` was closed after the write;
- post-write live diff verification succeeded;
- the embedded live diff review is clear and covers exactly one file;
- that reviewed file is exactly the applied target;
- the requested validation command is one of the validation steps retained by the patch-apply evidence.

The existing executor contract still applies after those checks. In particular, `--confirm-executor-dry-run` remains mandatory, only an exact executor-contract candidate can run, shell control syntax remains blocked, and execution uses `subprocess.run(..., shell=False)` with a bounded timeout.

## Example

```bash
forge verified-validation-run \
  --patch-apply .ai/evidence/patch-apply.json \
  --command "python -m pytest" \
  --confirm-executor-dry-run \
  --format json
```

Representative successful output fields:

```json
{
  "title": "Autonomous Forge verified validation run",
  "execution_status": "completed",
  "validation_result": "passed",
  "live_diff_verified": true,
  "verified_target_path": "src/example.py",
  "persistence_handoff": {
    "available": true,
    "auto_persistence": false,
    "confirmation_required": "--confirm-write"
  }
}
```

The command does **not** apply a patch, automatically write validation history, create a commit, push, poll workflows, modify remotes, or bypass any existing executor confirmation. A successful observed result still produces only the existing explicit persistence handoff; saving it remains a separate confirmed action.
