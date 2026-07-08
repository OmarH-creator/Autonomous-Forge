# Post-apply validation handoff

`forge post-apply-validation` summarizes explicit validation evidence after a guarded `forge patch-apply` run.

It is intentionally read-only. It does not run validation commands, inspect git diffs, poll workflow status, verify commits, write files, commit, or push. It only checks that a supplied patch-apply JSON report shows an applied file change and that the caller supplied a passing validation result plus every required validation step listed by the patch-apply report.

## Example

```bash
forge post-apply-validation \
  --root . \
  --patch-apply patch-apply.json \
  --result passed \
  --executed-step "python -m pytest" \
  --executed-step "forge git-diff-review --require-clear" \
  --note "local validation completed after patch apply" \
  --require-validated \
  --format json > post-apply-validation.json
```

## Inputs

- `--patch-apply`: repository-local JSON output from `forge patch-apply`.
- `--result`: explicit supplied validation result. Allowed values are `passed`, `failed`, `error`, `not_run`, and `skipped`.
- `--executed-step`: one validation step that was actually executed. Repeat the flag for multiple steps.
- `--note`: optional human-readable note.
- `--require-validated`: fail closed with exit code 2 unless the handoff is validated.

## Validation rules

The handoff is `validated` only when all of the following are true:

- the patch-apply report has title `Autonomous Forge guarded patch apply`;
- the patch-apply report has mode `explicit local file write`;
- `apply_status` is `applied`;
- `file_changed` is `true`;
- `patch_application_allowed` is already closed back to `false`;
- the supplied result is `passed`;
- every required validation step from the patch-apply report is present in the supplied executed-step list.

Otherwise, the handoff is `blocked` and reports missing steps or validation blockers.

## Safety boundary

The command consumes supplied metadata only. It does not prove that commands were truly run, that the patch is correct, that workflow checks passed, or that a commit is safe. It creates a deterministic handoff artifact for the next separate commit-readiness step.
