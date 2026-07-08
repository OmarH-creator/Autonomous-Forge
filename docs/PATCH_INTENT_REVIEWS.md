# Patch Intent Reviews

`forge patch-intent-review` is a read-only gate between reviewed content-audit comparison evidence and any future patch-intent or git-diff workflow.

It consumes one `forge diff-source-handoff --format json` output and reports whether it is safe to proceed to a future patch-intent description step. It does not generate a patch, inspect `git diff`, read repository file contents, or change files.

## Example

```bash
forge content-audit \
  --policy .forge/policy.md \
  --root . \
  --file README.md \
  --format json > before-content-audit.json

forge content-audit \
  --policy .forge/policy.md \
  --root . \
  --file README.md \
  --format json > after-content-audit.json

forge diff-source-handoff \
  --root . \
  --before before-content-audit.json \
  --after after-content-audit.json \
  --require-clear \
  --format json > diff-source-handoff.json

forge patch-intent-review \
  --root . \
  --diff-source diff-source-handoff.json \
  --require-ready \
  --format json
```

## Readiness rules

The review is `ready` only when all of the following are true:

- the input is a read-only diff-source handoff payload;
- `requires_attention` is `false`;
- every compared path is `unchanged`;
- every after-review status is `clear`;
- no compared path reports changed fields.

Any added, removed, changed, non-clear, malformed, missing, outside-root, or symlinked evidence is refused or reported as blocked. With `--require-ready`, blocked evidence returns exit code `2` after printing the review output.

## Safety boundary

Patch-intent review reads supplied diff-source handoff JSON only. It does not read repository file contents, inspect git diffs, generate patches, run commands, check workflow status, enforce policy, mutate saved history, commit, push, or change files. A `ready` result is only a process gate for describing future patch intent; it is not approval to apply changes.
