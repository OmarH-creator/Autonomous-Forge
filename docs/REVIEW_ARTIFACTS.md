# Review Artifacts

`forge review-artifact` creates one read-only handoff for the currently selected roadmap task.

It combines these existing review surfaces:

- structured implementation-plan context from `forge plan`;
- structured proposal intent from `forge propose`;
- validation intent from `forge validate-plan`;
- validation command-candidate metadata from `forge validation-preview`;
- explicit planned-path review using the same advisory checks as `forge review-files`.

## Example

```bash
forge review-artifact \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root .
```

For machine-readable review:

```bash
forge review-artifact \
  --plan .ai/AUTONOMOUS_PLAN.md \
  --state .ai/AUTONOMOUS_STATE.md \
  --policy .forge/policy.md \
  --root . \
  --format json
```

## Output contract

The artifact reports:

- selected task identity and reason;
- state-file and documented-file presence signals;
- planned file areas and high-level operations;
- validation steps and `validation_execution: not run`;
- validation command candidates, conservative eligibility, and classification reasons;
- advisory path review summary for planned file areas;
- approval-required items, blockers, risk notes, and attention status.

## Safety limits

The command is output-only. It does not change files, inspect git diffs, read reviewed file contents, scan secrets, read environment variables, run validation commands, generate patches, approve exceptions, enforce policy decisions, call networks, commit, or push.
