# Git Diff Review

`forge git-diff-review` reviews a repository-local `.diff` or `.patch` file before any future patch-applier workflow relies on it.

The command is local-first and read-only. It inspects unified diff metadata, changed paths, hunk counts, additions, deletions, and policy matches. It does not apply the diff, read changed file contents, run commands, check workflow status, approve implementation, commit, push, or change files.

## Example

```bash
git diff -- src tests > changes.diff
forge git-diff-review --policy .forge/policy.md --root . --diff changes.diff --require-clear --format json
```

## Inputs

- `--policy`: repository policy file, defaulting to `.forge/policy.md`.
- `--root`: repository root used to constrain the supplied diff path and path-presence checks.
- `--diff`: repository-local `.diff` or `.patch` file to inspect.
- `--require-clear`: returns exit code `2` unless every reviewed path is allowed and the supplied diff parses cleanly.
- `--format`: `text` or `json`, defaulting to `text`.

## Output contract

Successful text output includes stable sections for:

- file changes with old path, new path, status, additions, deletions, and hunk count;
- path reviews with presence and policy status;
- summary counts;
- parse warnings, when present;
- `Requires attention: true|false`;
- reason, next step, and safety boundary.

JSON output includes `title`, `mode`, `source`, `policy`, `file_changes`, `path_reviews`, `summary`, `parse_warnings`, `requires_attention`, `reason`, `next_step`, and `safety_boundary`.

## Exit codes

- `0` when the review is produced and `--require-clear` is not requested.
- `0` when `--require-clear` is requested and `requires_attention` is `false`.
- `2` when input files are missing or unsafe, the diff file is outside the root, the diff is not `.diff` or `.patch`, the diff is not UTF-8, or `--require-clear` is requested and review evidence is not clear.

## Safety limits

This command is advisory. A clear result does not prove correctness, test success, or implementation quality. It only says the supplied unified diff parsed cleanly and all reviewed diff paths matched documented allowed policy paths.
