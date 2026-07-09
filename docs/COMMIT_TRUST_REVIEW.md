# Commit trust review

`forge commit-trust-review` is a local-first checkpoint between `forge commit-verify` and push-readiness.

It consumes a verified `forge commit-verify --format json` report, inspects the same local commit with `git show --format=%H%x00%G?%x00%GS%x00%GF`, and reports whether the commit has trusted signature metadata before any push workflow relies on it.

The command can also consume an optional repository-local JSON allowed-signer policy. This upgrades the trust decision from "the commit is signed with trusted local git metadata" to "the commit is signed and the signer or key fingerprint is on the maintainer allowlist."

## Example

```bash
forge commit-trust-review \
  --root . \
  --commit-verify commit-verify.json \
  --allowed-signers .forge/allowed-signers.json \
  --require-trusted \
  --format json > commit-trust-review.json
```

Compatibility entry point:

```bash
forge-commit-trust-review --root . --commit-verify commit-verify.json --allowed-signers .forge/allowed-signers.json --format json
```

## Allowed-signer policy

The policy file must be repository-local JSON, must stay inside `--root`, and must contain a non-empty `allowed_signers` list. Each entry can match by exact signer, exact key fingerprint, or both.

```json
{
  "allowed_signers": [
    {
      "signer": "Ada Lovelace",
      "key_fingerprint": "ABCDEF123456"
    },
    {
      "key_fingerprint": "FEDCBA654321"
    }
  ]
}
```

Wildcard identity values are refused. When a policy is supplied, a good signature is still blocked if the inspected signer and key fingerprint do not match at least one allowlist entry.

## Trust status

The command reports `trusted` only when all of these are true:

- the input is a verified Forge commit-verification report;
- the inspected commit SHA matches the verified commit SHA;
- local git signature metadata reports a trusted signature code (`G` or `U`);
- any supplied allowed-signer policy is valid and matches the inspected signer or key fingerprint;
- the input keeps `push_allowed` and `remote_changes_allowed` false.

Unsigned, bad, expired, revoked, uncheckable, signer-mismatched, or policy-mismatched signatures are reported as blockers. Use `--require-trusted` when automation should fail closed.

## Safety boundary

The command never stages files, creates commits, pushes, changes remotes, calls networks, reads environment variables, reruns workflows, or modifies the working tree. It only reads repository-local JSON reports/policies and runs one local `git show` metadata inspection for the reviewed commit.
