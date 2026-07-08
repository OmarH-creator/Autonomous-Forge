# Patch proposal reviews

`forge patch-proposal-review` is a read-only evidence gate before any future patch proposal generation surface. The compatibility command `forge-patch-proposal-review` remains available for existing scripts.

It consumes two explicit JSON inputs:

1. a ready `forge patch-proposal-manifest --format json` output; and
2. a fresh `forge content-audit --format json` output for the same requested paths.

The command reports `review_status=ready` only when:

- the manifest is a read-only patch proposal manifest;
- the manifest status is `ready` and `proposal_allowed=true`;
- every requested path has a safe repository-relative path label;
- every fresh audited path has a safe repository-relative path label;
- every requested path has fresh content-audit evidence;
- the fresh content audit does not include unrequested paths; and
- every requested path has `review_status=clear` in the fresh content audit.

With `--require-ready`, the command exits with code `2` unless the review is ready.

## Safe path labels

The review command independently refuses unsafe path labels from supplied JSON before reporting them or treating them as patch-adjacent evidence. Refused labels include blank labels, labels with leading or trailing whitespace, absolute paths, `.` or `..`, parent traversal such as `../README.md` or `docs/../README.md`, empty path segments, and backslash-separated paths.

## Example

```bash
forge content-audit \
  --policy .forge/policy.md \
  --root . \
  --file README.md \
  --format json > fresh-content-audit.json

forge patch-proposal-review \
  --root . \
  --manifest patch-proposal-manifest.json \
  --content-audit fresh-content-audit.json \
  --require-ready \
  --format json
```

## Safety boundary

The command reads supplied manifest JSON and supplied content-audit JSON only. It does not read repository file contents, inspect git diffs, generate patches, apply patches, run commands, check workflow status, approve implementation, mutate saved history, commit, push, or change files.

A ready review is not patch approval. It only means the supplied manifest is still supported by fresh clear content-audit evidence with safe path labels.
