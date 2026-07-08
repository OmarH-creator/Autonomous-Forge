# Changed-content audits

`forge content-audit` is a read-only checkpoint for explicit repository-relative file paths before any future patch generation or diff-inspection workflow.

It answers a narrow question: are the listed files safe enough to be considered by later patch-adjacent tooling?

## Usage

```bash
forge content-audit \
  --root . \
  --policy .forge/policy.md \
  --file README.md \
  --file src/autonomous_forge/content_audit.py \
  --format json
```

Use `--file` more than once to audit multiple explicit paths.

## What it inspects

For each path, the command reports:

- policy status from the documented allow/prohibit path rules;
- content status such as `readable`, `missing`, `directory`, `not-regular-file`, `non-utf8`, `too-large`, or `invalid-path`;
- bounded metadata: byte count and line count;
- configured secret-like markers such as private-key headers or obvious token/password assignment markers;
- a conservative review status: `clear`, `blocked`, `needs-policy-review`, `needs-content-review`, or `needs-secret-review`.

## Safety boundary

The audit reads file contents only to compute bounded metadata and secret-marker signals. It does not print file contents, inspect git diffs, generate patches, run commands, change files, check workflow status, enforce policy, commit, push, call networks, or read environment variables.

The audit is intentionally advisory. A `clear` result means only that the listed path matched an allowed policy area, was a regular UTF-8 file within the size limit, and did not contain the configured marker strings. It is not a guarantee that the content is correct, safe, or ready to patch.
