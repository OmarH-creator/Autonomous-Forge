# Commit Create

`forge commit-create` is the first intentionally commit-capable local command. It consumes a ready `forge commit-proposal-preview --format json` report and creates one local git commit only when the maintainer supplies explicit confirmation.

It is not a push workflow. It does not change remotes, call networks, rerun validation, poll workflow status, or infer whether the change is correct.

## Usage

```bash
forge commit-create \
  --root . \
  --proposal commit-proposal-preview.json \
  --confirm-commit-create \
  --require-created \
  --format json > commit-create.json
```

Compatibility entry point:

```bash
forge-commit-create --help
```

## Inputs

- `--proposal`: repository-local JSON produced by `forge commit-proposal-preview --format json`.
- `--confirm-commit-create`: required before the command stages reviewed paths and runs a path-limited `git commit --only`.
- `--require-created`: returns exit code `2` unless a local commit is created.
- `--format`: `text` or `json`; default is `text`.

## Creation criteria

The command creates a local commit only when the proposal is ready, produced in commit-proposal-preview mode, contains reviewed paths, keeps `commit_allowed`, `commit_creation_allowed`, and `push_allowed` false, has no proposal blockers, and `git status --porcelain -- <reviewed paths>` reports local changes for the reviewed paths.

## Staged-file isolation

Git normally commits **all staged changes**, including unrelated files staged before Forge runs. This command instead uses root-anchored literal Git pathspecs for the status check, staging, and `git commit --only -- <reviewed paths>`. Only reviewed paths enter the commit; unrelated staged index entries remain staged. Reviewed new files and deletions are supported. The command still stages reviewed paths in the shared index before committing, so a failed commit can leave reviewed paths staged. It does not provide the stronger isolated-index, byte, parent, or concurrent-state guarantees of `forge verified-commit-create`.

Example: if `other.txt` was already staged and the proposal reviews only `README.md`, the resulting commit changes only `README.md`; `other.txt` stays staged for a separate commit.

## Output

JSON output includes `commit_status`, `commit_summary`, `commit_body_lines`, reviewed paths, observed git status lines, the created commit SHA when available, blocker details, and explicit `push_allowed` and `remote_changes_allowed` fields set to `false`.

## Safety boundary

This command reads supplied commit-proposal-preview JSON and runs local git only after explicit confirmation. It stages reviewed paths and commits only those literal paths with the reviewed message, never pushes, never changes remotes, never calls networks, never reads environment variables, and does not run validation or workflows.
