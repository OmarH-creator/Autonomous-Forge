# Run-History Previews

`forge run-history-preview` prints the record shape that a future local run-history feature could use, without writing a history file.

The command is a review surface only. It consumes the same plan, policy, state, root, and structured review-artifact inputs as the current pre-execution handoff, then reports the selected task, review status, intent summaries, validation status, command-candidate metadata, changed-files placeholder, commit placeholder, blockers, and safety notes.

## Example

```bash
forge run-history-preview \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root .
```

For deterministic machine-readable output:

```bash
forge run-history-preview \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root . \
  --format json
```

## Stable fields

The JSON output includes:

- `title`: `Autonomous Forge run-history preview`.
- `mode`: always `read-only`.
- `source`: `review artifact structured data`.
- `persistence`: always `not written`.
- `record.schema_version`: currently `run-history-preview/v1`.
- `record.task`: selected task ID, title, priority, and status before any run.
- `record.review_status`: review-artifact status.
- `record.requires_attention`: whether attention signals are present.
- `record.planned_file_areas`: planned areas from the change proposal.
- `record.change_intent_summary`: structured change-intent counts.
- `record.patch_intent_summary`: structured patch-intent counts.
- `record.validation_execution`: currently `not run`.
- `record.validation_result`: currently `not run`.
- `record.validation_command_candidates`: preview-only command-candidate metadata.
- `record.changed_files_summary`: currently `none`.
- `record.commit`: currently `none`.
- `record.blockers`: durable blockers that future history should preserve.
- `record.safety_notes`: explicit non-execution and non-persistence notes.

## Safety boundary

`forge run-history-preview` does not write history files, change repository files, inspect diffs, read changed-file contents, generate patches, run validation commands, make review decisions, enforce policy decisions, read environment variables, or call networks.

Future persistence work should preserve this schema first, then add a separate opt-in record writer only after review-artifact, patch-intent, validation, and policy boundaries are stable.
