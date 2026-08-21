# AUTO-183 — Core preservation receipt input deduplication

`build_maintenance_review_compare_data()` canonicalizes optional preservation-completeness paths against the configured repository root before receipt discovery. Only the first occurrence of each resolved artifact is reviewed.

This protects every caller of the comparison builder, not only the `forge maintenance-review-compare` CLI. Equivalent relative, dotted-relative, absolute, or symlink-resolved references to the same artifact therefore contribute one informational receipt review.

Receipt evidence remains informational only. Deduplication does not affect comparison readiness, preservation candidate ranking, validation evidence, preservation completeness, or any write/Git/network authority.

Example for direct callers:

```python
from pathlib import Path
from autonomous_forge.maintenance_review_compare import build_maintenance_review_compare_data

summary = build_maintenance_review_compare_data(
    [Path(".ai/run-history/run.json")],
    root=Path("."),
    completeness_paths=[
        Path("evidence/completeness.json"),
        Path("./evidence/completeness.json"),
        Path("/absolute/repo/evidence/completeness.json"),
    ],
)
```

When those paths resolve to one file, `preservation_receipt_review_count` can increase by at most one for that artifact.
