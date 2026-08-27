# AUTO-218 — Scope preservation receipt discovery failures to the selected artifact

## Inspection

Inspected `main`, README/docs/examples, preservation receipt/completeness source and tests, repository policy/config/CI, `.ai` state and roadmap direction, recent commits, open issues, all eight visible branches, and recent PR history. Seven non-main branches remain historical/diverged; recent PRs are merged, closed, obsolete, or unrelated. No branch or PR warranted integration.

## Objective

Fix a concrete preservation-review defect: `maintenance-preservation-receipt --discover` treated every malformed, unsupported, or unbound JSON file in `.ai/preservation-receipts/` as invalid evidence for every selected completeness artifact, even when the file could not be attributed to that artifact.

## Change

Receipt discovery now separates invalid evidence into two classes:

- `invalid_receipts`: receipts whose valid v1 source binding explicitly names the selected completeness artifact and then fail verification. These still set `receipt_review_status=attention_required`.
- `unattributed_invalid_receipts`: malformed JSON, unsupported schemas, or v1 objects without a usable source binding. These remain visible and counted but do not downgrade an unrelated artifact's receipt review.

Valid receipts bound to other completeness paths continue to be ignored for the selected artifact.

Added deterministic regression coverage and `docs/PRESERVATION_RECEIPT_DISCOVERY_ATTRIBUTION.md`.

## Safety

The discovery scan remains bounded, local, non-recursive, read-only, and conditional on an already-complete preservation artifact. Receipt evidence remains informational only and cannot change preservation completeness, readiness, integrity, Git, workflow, push, or persistence authority.

## Validation

Product/test/docs head `4e9ee80d1992f2ee278889f5ab98201ed85bf637` passed GitHub Actions run `33106891351` across Python 3.10, 3.11, and 3.12.

## Diff / publication

Work stayed directly on `main`. No branch, PR, merge, or force-push was used. The feature slice changed only the receipt implementation, one focused test file, and one dedicated document before README/state/run-record bookkeeping.

## Next

Continue only with a concrete end-to-end preservation/provenance integrity gap or meaningful evidence-handoff reduction. Any fresh CI failure takes priority.
