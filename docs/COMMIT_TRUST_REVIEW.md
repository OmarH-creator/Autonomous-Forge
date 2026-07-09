# Commit trust review

`forge commit-trust-review` is a local-first checkpoint between `forge commit-verify` and push-readiness.

It consumes a verified `forge commit-verify --format json` report, inspects the same local commit with `git show --format=%H%x00%G?%x00%GS%x00%GF`, and reports whether the commit has trusted signature metadata before any push workflow relies on it.

## Example

```bash
forge commit-trust-review \
  --root . \
  --commit-verify commit-verify.json \
  --require-trusted \
  --format json > commit-trust-review.json
```

Compatibility entry point:

```bash
forge-commit-trust-review --root . --commit-verify commit-verify.json --format json
```

## Trust status

The command reports `trusted` only when all of these are true:

- the input is a verified Forge commit-verification report;
- the inspected commit SHA matches the verified commit SHA;
- local git signature metadata reports a trusted signature code (`G` or `U`);
- the input keeps `push_allowed` and `remote_changes_allowed` false.

Unsigned, bad, expired, revoked, or uncheckable signatures are reported as blockers. Use `--require-trusted` when automation should fail closed.

## Safety boundary

The command never stages files, creates commits, pushes, changes remotes, calls networks, reads environment variables, reruns workflows, or modifies the working tree. It only reads one repository-local JSON report and runs one local `git show` metadata inspection for the reviewed commit.
