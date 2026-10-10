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
- the full inspected message subject agrees with `git show` and the reviewed summary;
- the ordered non-empty commit body lines match the reviewed lines exactly (missing, reordered, substring-only, or additional lines block verification);
- local `git diff-tree --root --name-only -r -z` reports exactly the reviewed paths using NUL-delimited filenames, including for an initial/root commit; and
- no blockers are present.

## Exit codes

Without `--require-verified`, blocked reports are printed with exit code 0 so humans can inspect the report. With `--require-verified`, the command returns exit code 2 unless the commit is verified.

## Integrity notes

The verifier compares full non-empty message lines rather than searching for reviewed snippets anywhere in the commit message. Blank paragraph separators are ignored; extra non-empty text is not. Git path inspection uses NUL separators so filenames containing newlines cannot masquerade as multiple reviewed paths. The verifier also supports a repository's initial/root commit. This is a read-only local Git inspection, not an assertion of author identity, code correctness, or push approval.
