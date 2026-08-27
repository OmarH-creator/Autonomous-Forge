# Preservation receipt discovery attribution

`forge maintenance-preservation-receipt --discover` reviews receipts for one already-complete preservation artifact. Receipt discovery is informational only and never changes preservation completeness.

AUTO-218 scopes receipt-review degradation to evidence that can actually be attributed to the selected completeness artifact.

## Matching invalid receipts

If a receipt uses `maintenance-preservation-receipt/v1` and its `source_completeness.path` names the selected artifact, Forge verifies the complete receipt binding. Any drift or corruption is reported in `invalid_receipts`, increments `invalid_receipt_count`, and sets `receipt_review_status=attention_required`.

This preserves fail-closed behavior for evidence that explicitly claims to belong to the selected artifact.

## Unattributed invalid directory entries

A JSON candidate may be malformed, use an unsupported schema, or omit `source_completeness`. In those cases Forge cannot safely determine which preservation artifact the file belongs to.

Such entries are now surfaced separately as:

- `unattributed_invalid_receipts`
- `unattributed_invalid_receipt_count`

They remain visible for repository cleanup, but they do not downgrade the review of an unrelated selected artifact. A valid receipt bound to another completeness path continues to count as `ignored_receipt_count`.

## Safety boundary

The discovery scan remains bounded, local, non-recursive, and read-only. It still requires the selected completeness artifact itself to be complete before scanning receipts. Receipt presence, absence, corruption, or directory noise never substitutes for preservation completeness and never changes readiness, integrity, push, Git, workflow, or persistence authority.
