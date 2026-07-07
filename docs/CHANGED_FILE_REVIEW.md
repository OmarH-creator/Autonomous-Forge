# Changed-File Review

`forge review-files` is a read-only review surface for explicit changed-file paths.

It exists to bridge the gap between proposal planning and future change-set review without adding command execution, patch generation, policy enforcement, or repository writes.

## Example

```bash
forge review-files \
  --policy .forge/policy.md \
  --root . \
  --file src/autonomous_forge/cli.py \
  --file tests/test_path_review.py
```

For structured output:

```bash
forge review-files \
  --policy .forge/policy.md \
  --root . \
  --file src/autonomous_forge/cli.py \
  --format json
```

## Output signals

For every provided path, the command reports:

- `path_status`: `present`, `missing`, or `unknown` based on local path presence only.
- `policy_status`: `allowed`, `prohibited`, or `unknown` based on documented policy path patterns only.

The summary reports total reviewed paths and counts by policy status.

## Safety limits

The command does not read file contents, inspect git diffs, scan secrets, read environment variables, call networks, run validation commands, approve policy exceptions, enforce policy decisions, generate patches, or change files.

The output is advisory. Prohibited or unknown paths require human review before implementation should continue.
