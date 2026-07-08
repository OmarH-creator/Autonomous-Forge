# Patch Intent Descriptions

`forge patch-intent-describe` is a read-only handoff after `forge patch-intent-review`. It consumes one patch-intent review JSON artifact and describes whether future patch intent may be written from that evidence.

It does not generate a patch, inspect `git diff`, read repository file contents, run commands, approve an implementation, or change files.

## Example

```bash
forge patch-intent-review \
  --root . \
  --diff-source diff-source-handoff.json \
  --require-ready \
  --format json > patch-intent-review.json

forge patch-intent-describe \
  --root . \
  --patch-review patch-intent-review.json \
  --require-described \
  --format json
```

## Description rules

The description status is `described` only when all of the following are true:

- the input is a read-only patch-intent review payload;
- the review readiness is `ready`;
- `patch_intent_allowed` is `true`;
- the review has at least one compared path;
- every compared path label is a safe repository-relative POSIX path label, not absolute, parent-traversing, blank, whitespace-padded, or backslash-based;
- the review has no blockers.

Any blocked, malformed, missing, outside-root, non-JSON, symlinked, or unsafe-path-label evidence is refused or reported as blocked. With `--require-described`, blocked evidence returns exit code `2` after printing the description output.

## Output purpose

The artifact lists:

- candidate paths from the already-reviewed evidence;
- required next inputs for a future explicit patch proposal description;
- non-goals such as patch generation, patch application, git-diff inspection, command execution, and repository mutation;
- blockers that must be cleared first.

## Safety boundary

Patch-intent description reads supplied patch-intent review JSON only. It does not read repository file contents, inspect git diffs, generate patches, apply patches, run commands, check workflow status, enforce policy, mutate saved history, commit, push, or change files. A `described` result is only a process handoff for future explicit patch proposal work; it is not approval to implement changes.
