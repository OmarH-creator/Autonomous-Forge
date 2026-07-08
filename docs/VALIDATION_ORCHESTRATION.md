# Validation orchestration previews

`forge validation-orchestration` is a read-only readiness layer for deciding whether a saved validation context is safe to review before any validation executor exists.

It combines:

- the selected roadmap task and validation plan;
- validation command-candidate preview counts;
- saved run-history validation-result guards from the direct history list;
- the latest readable run-history record guard;
- explicit blockers and risk notes.

The preview is intentionally conservative. It does not run validation commands, poll GitHub Actions, verify commits, inspect diffs, generate patches, grant approval, enforce policy, or mutate history records.

## CLI usage

```bash
forge validation-orchestration \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root .
```

For deterministic JSON output:

```bash
forge validation-orchestration \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root . \
  --format json
```

## Python usage

```python
from pathlib import Path
from autonomous_forge.validation_orchestration import build_validation_orchestration_preview

output = build_validation_orchestration_preview(
    Path(".ai/AUTONOMOUS_PLAN.md").read_text(encoding="utf-8"),
    Path(".forge/policy.md").read_text(encoding="utf-8"),
    state_path=Path(".ai/AUTONOMOUS_STATE.md"),
    root=Path("."),
    output_format="json",
)
print(output)
```

## Status meanings

- `blocked`: a validation command candidate is blocked, or saved history contains a failed supplied validation result.
- `needs-validation-context`: saved history is missing, incomplete, refused, skipped, not run, or unknown.
- `needs-command-review`: saved history is clear, but no eligible validation command candidate is available for manual review.
- `ready-for-manual-validation-review`: saved history is clear and at least one eligible validation command candidate is present.

## Output contract

The JSON output contains:

- `selected_task`
- `validation_execution`
- `commands_allowed`
- `orchestration_status`
- `command_candidate_summary`
- `history_validation_guard`
- `latest_record_validation_guard`
- `latest_record_path`
- `blockers`
- `risk_notes`
- `safety_boundary`

The command remains a preview surface only. It deliberately avoids execution and workflow polling.
