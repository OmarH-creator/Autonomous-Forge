# Push-readiness gate

`forge push-readiness` combines verified local commit evidence, trusted commit-signature evidence, fresh commit-status review evidence, and supplied branch-protection/status-policy evidence before an explicitly confirmed push handoff is considered.

The command is intentionally non-pushing. It reads four repository-local JSON files, reports whether the evidence is ready for human push consideration, and keeps `push_allowed` and `remote_changes_allowed` false.

## Inputs

- `--commit-verify`: JSON from `forge commit-verify --format json`.
- `--commit-trust`: JSON from `forge commit-trust-review --format json`.
- `--status-review`: JSON from `forge commit-status-review --format json`, typically collected with `--from-github` for the verified commit.
- `--branch-protection`: repository-local JSON evidence describing the target branch protection settings. The expected fields are `branch` or `name`, `protected: true`, and `required_status_checks` with `strict: true` plus required `contexts` and/or `checks`.
- `--branch`: branch name expected in the supplied branch-protection evidence, defaulting to `main`.
- `--root`: repository root used to constrain all JSON inputs.

All inputs must stay inside the configured root, use `.json`, be bounded in size, and not be symlinks.

## Example

```bash
forge commit-trust-review \
  --root . \
  --commit-verify commit-verify.json \
  --allowed-signers .forge/allowed-signers.json \
  --require-trusted \
  --format json > commit-trust-review.json

forge commit-status-review --root . --from-github --commit-sha abc1234 --require-clear --format json > commit-status-review.json
gh api repos/OWNER/REPO/branches/main --jq '{branch: .name, protected: .protected, required_status_checks: .protection.required_status_checks}' > branch-protection.json
forge push-readiness \
  --root . \
  --commit-verify commit-verify.json \
  --commit-trust commit-trust-review.json \
  --status-review commit-status-review.json \
  --branch-protection branch-protection.json \
  --branch main \
  --require-ready \
  --format json > push-readiness.json
```

A ready report requires:

- `commit-verify` status is `verified`.
- `commit-trust-review` status is `trusted` with trusted signature code `G` or `U`.
- Verified commit SHA matches both the trust-review commit SHA and the status-review commit SHA.
- Trust-reviewed paths exactly match the verified commit paths.
- Status review is `clear` with at least one successful context.
- Branch protection evidence shows the target branch is protected.
- Required status checks are strict/up-to-date.
- Every required branch status context is present in the status review evidence.
- No failed, pending, unknown, trust, verification, branch-protection, or blocker status evidence is present.
- Reviewed paths are safe repository-relative labels.

## Safety boundary

`forge push-readiness` never runs `git`, calls networks, stages files, creates commits, pushes, changes remotes, reads environment variables, changes branch protections, or modifies the working tree. It is a pre-push evidence gate only.
