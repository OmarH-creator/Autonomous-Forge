# Diff-source handoffs

`forge diff-source-handoff` compares two explicit `forge content-audit --format json` outputs before any future patch-generation workflow relies on file-content evidence.

The command is read-only. It reads the supplied JSON audit outputs, verifies that they are content-audit payloads, compares path-level audit observations, and reports whether the handoff requires review.

## Usage

```bash
forge content-audit \
  --policy .forge/policy.md \
  --root . \
  --file README.md \
  --file src/autonomous_forge/content_audit.py \
  --format json > before-content-audit.json

forge content-audit \
  --policy .forge/policy.md \
  --root . \
  --file README.md \
  --file src/autonomous_forge/content_audit.py \
  --format json > after-content-audit.json

forge diff-source-handoff \
  --root . \
  --before before-content-audit.json \
  --after after-content-audit.json \
  --format json
```

## Output

The handoff reports:

- the two supplied audit-output labels;
- total paths and `requires_attention` status from each audit output;
- added, removed, changed, and unchanged audited paths;
- changed observation fields such as `line_count`, `byte_count`, `content_status`, `policy_status`, `review_status`, and `secret_markers`;
- after-audit clear and needs-review counts;
- an overall `requires_attention` gate and reason.

## Refusals

The command refuses to process inputs that are outside the configured root, are not `.json` files, are symlinks, are not regular files, are malformed JSON, are not content-audit payloads, are not read-only payloads, lack an `audited_paths` list, or contain duplicate audited path entries.

## Safety boundary

The command reads supplied content-audit JSON only. It does not read repository file contents, inspect git diffs, generate patches, run commands, check workflow status, enforce policy, or change files.
