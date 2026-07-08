# Change Readiness

`forge change-readiness` combines two already-reviewed pieces of evidence before any future patch-application workflow relies on a change:

1. `forge git-diff-review --format json`
2. `forge commit-status-review --format json`

The command is local-first and read-only. It reads repository-local JSON review outputs only, confirms both upstream reviews are clear, and summarizes the changed paths, status contexts, blockers, and safety boundary. It never reads repository file contents, inspects raw diffs, calls GitHub, runs workflows, runs commands, generates patches, applies patches, commits, pushes, or changes files.

## Example

```bash
git diff -- README.md > changes.diff
forge git-diff-review \
  --policy .forge/policy.md \
  --root . \
  --diff changes.diff \
  --require-clear \
  --format json > git-diff-review.json

forge commit-status-review \
  --root . \
  --status commit-status.json \
  --require-clear \
  --format json > commit-status-review.json

forge change-readiness \
  --root . \
  --diff-review git-diff-review.json \
  --status-review commit-status-review.json \
  --require-ready \
  --format json
```

## Review rules

The summary is `ready` only when:

- the supplied diff evidence is a `forge git-diff-review` JSON payload;
- the supplied status evidence is a `forge commit-status-review` JSON payload;
- both payloads were produced in read-only mode;
- the diff review does not require attention;
- the diff review has changed files and no prohibited, unknown-policy, binary, metadata-only, or parse-warning signals;
- the status review is clear;
- the status review has at least one validation context and no failed, pending, or unknown contexts.

Even when the summary is `ready`, `change_application_allowed` remains `false`. The output is advisory evidence for human review and future guarded design, not approval to apply patches.
