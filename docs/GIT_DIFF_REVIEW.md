# Git Diff Review

`forge git-diff-review` reviews either a repository-local `.diff`/`.patch` file or the repository's current tracked changes relative to `HEAD` before guarded patch and validation workflows rely on them.

The command is local-first and read-only. In supplied-file mode it parses the provided unified diff. In current-repository mode it runs exactly `git diff --no-ext-diff --no-textconv HEAD --` with `shell=False` inside the configured root, then applies the same policy/path review. It does not apply patches, run validation commands, call networks, mutate git state, commit, push, or change files.

## Examples

Review a saved diff:

```bash
git diff -- src tests > changes.diff
forge git-diff-review --policy .forge/policy.md --root . --diff changes.diff --require-clear --format json
```

Review the repository's actual tracked staged and unstaged changes relative to `HEAD`:

```bash
forge git-diff-review --policy .forge/policy.md --root . --current --require-clear --format json
```

## Inputs

- `--policy`: repository policy file, defaulting to `.forge/policy.md`.
- `--root`: repository root used to constrain path checks and, in `--current` mode, the working directory for local git inspection.
- exactly one of:
  - `--diff`: repository-local `.diff` or `.patch` file to inspect;
  - `--current`: capture tracked staged and unstaged changes relative to `HEAD` using local git.
- `--require-clear`: returns exit code `2` unless the selected review requires no attention.
- `--format`: `text` or `json`, defaulting to `text`.

## Current-repository scope

`--current` deliberately reviews tracked changes only. Untracked files are not part of `git diff HEAD`, so a clean result does not prove the repository has no untracked files. The command disables external diff drivers and text conversion, uses no shell, applies a 15-second timeout, and refuses diff output larger than 1 MB. A git failure, missing git executable, timeout, non-UTF-8 output, or oversized diff is reported as a refused review.

An empty tracked diff is considered clear because there is nothing tracked to review; the output explicitly tells the caller to inspect untracked files separately before continuing.

## Output contract

Successful text output includes stable sections for:

- source identity (`supplied unified git diff` or `current tracked repository diff against HEAD`);
- file changes with old path, new path, status, additions, deletions, hunk count, binary flag, and metadata-only flag;
- mode changes, when present;
- path reviews with presence and policy status;
- summary counts, including binary-file and metadata-only counts;
- parse warnings, when present;
- `Requires attention: true|false`;
- reason, next step, and safety boundary.

JSON output includes `title`, `mode`, `source`, `policy`, `file_changes`, `path_reviews`, `summary`, `parse_warnings`, `requires_attention`, `reason`, `next_step`, and `safety_boundary`.

## Exit codes

- `0` when the review is produced and `--require-clear` is not requested.
- `0` when `--require-clear` is requested and `requires_attention` is `false`.
- `2` when inputs are missing or unsafe, git inspection fails, the diff exceeds its bound, or `--require-clear` is requested and review evidence is not clear.

## Safety limits

This command is advisory. A clear result does not prove correctness, test success, implementation quality, or absence of untracked files. It only says the selected unified tracked diff evidence parsed cleanly, avoided binary/metadata-only evidence that needs separate review, and all reviewed diff paths matched documented allowed policy paths.
