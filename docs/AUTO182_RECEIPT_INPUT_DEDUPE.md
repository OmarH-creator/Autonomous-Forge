# AUTO-182: Preservation receipt input deduplication

`forge maintenance-review-compare` accepts repeatable `--completeness` inputs so reviewers can surface preservation receipt evidence beside maintenance handoffs.

AUTO-182 canonicalizes those CLI paths against `--root` and keeps only the first reference to each canonical file before receipt discovery. This prevents the same completeness artifact from being counted more than once when callers repeat it using equivalent spellings such as `completeness.json`, `./completeness.json`, or an absolute path.

This is an evidence-integrity guard only. Receipt evidence remains informational: it does not change comparison readiness or preservation ranking, and no new write, Git, network, workflow, or preservation authority is introduced.

Example:

```bash
forge maintenance-review-compare \
  --root . \
  --link .ai/run-history/AUTO-181-link.json \
  --completeness .ai/preservation/AUTO-181-complete.json \
  --completeness ./.ai/preservation/AUTO-181-complete.json
```

The completeness artifact is reviewed once.