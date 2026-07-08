# Patch Proposal Draft Previews

`forge patch-proposal-draft` is a read-only handoff after `forge patch-proposal-review`.

It consumes one saved patch proposal review JSON document and prepares a stable proposal-draft outline for the next patch-adjacent workflow step. It does **not** generate patch text or apply any changes.

## Example

```bash
forge patch-proposal-draft \
  --root . \
  --review patch-proposal-review.json \
  --require-draft-ready \
  --format json
```

The compatibility console script is also available:

```bash
forge-patch-proposal-draft \
  --root . \
  --review patch-proposal-review.json \
  --require-draft-ready \
  --format json
```

## Readiness rules

A draft preview is `draft-ready` only when the supplied review evidence is a valid `Autonomous Forge patch proposal review` payload with:

- `mode` equal to `read-only`;
- `review_status` equal to `ready`;
- `patch_proposal_allowed` equal to `true`;
- at least one safe repository-relative requested path;
- at least one non-empty validation step;
- no review blockers.

When `--require-draft-ready` is set, blocked draft evidence returns a failing exit code after printing the reviewable output.

## Safety boundary

Patch proposal draft previews read supplied review JSON only. They do not read repository file contents, inspect git diffs, generate patches, apply patches, run commands, check workflow status, approve implementation, mutate saved history, commit, push, or change files.

A draft-ready result is advisory evidence for a future proposal surface. It is not implementation approval and does not prove correctness.
