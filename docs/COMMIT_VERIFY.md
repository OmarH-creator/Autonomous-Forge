# Commit verification

`forge commit-verify` checks one created local commit against the reviewed `forge commit-create --format json` report that produced it.

The command is intentionally narrow. It reads one repository-local JSON report, inspects the reported commit through local `git`, compares the commit SHA, subject, reviewed body lines, and changed file paths, then reports whether the commit is verified.

It never stages files, creates commits, pushes, changes remotes, calls networks, reads environment variables, or modifies the working tree.

## Example

```bash
forge commit-verify \
  --root . \
  --commit-create commit-create.json \
  --require-verified \
  --format json > commit-verify.json
```

Compatibility entry point:

```bash
forge-commit-verify --root . --commit-create commit-create.json --require-verified
```

## Verification rules

A commit is verified only when all of the following are true:

- the input is a Forge `commit-create` JSON report;
- the report says a commit was created;
- `push_allowed` and `remote_changes_allowed` remain false;
- the reported commit SHA has a safe hexadecimal shape;
- local `git show` returns the same commit SHA and subject;
- every reviewed commit body line appears in the inspected commit body;
- local `git diff-tree --name-only -r` reports exactly the reviewed paths; and
- no blockers are present.

## Exit codes

Without `--require-verified`, blocked reports are printed with exit code 0 so humans can inspect the report. With `--require-verified`, the command returns exit code 2 unless the commit is verified.
