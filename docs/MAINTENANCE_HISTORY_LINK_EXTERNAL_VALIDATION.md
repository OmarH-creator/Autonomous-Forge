# Maintenance history-link external validation summary

When `forge maintenance-evidence-bundle` is given `--validation-record`, the durable bundle can retain verified immutable validation attachments as **external advisory provenance**. After the bundle is written, a confirmed `--history-link` now also records a compact summary of that provenance so a consumer can discover its presence without first opening the full bundle.

The history link keeps the existing `maintenance-bundle-history-link/v1` schema and adds `external_validation_evidence_summary` only when external validation provenance is present. The summary contains:

- `provenance_semantics: externally_supplied_observation`
- `executor_validation_equivalent: false`
- `bundle_gate_effect: advisory_only`
- the source run-history record label
- the number of immutable validation attachments
- `evidence_sha256`, computed from the canonical JSON representation of the full `external_validation_evidence` block stored in the bundle

Example excerpt:

```json
{
  "external_validation_evidence_summary": {
    "present": true,
    "provenance_semantics": "externally_supplied_observation",
    "executor_validation_equivalent": false,
    "bundle_gate_effect": "advisory_only",
    "source_record": ".ai/run-history/AUTO-173.json",
    "attachment_count": 1,
    "evidence_sha256": "<sha256-of-full-bundle-provenance-block>"
  }
}
```

The hash is an index and integrity pointer, not signer identity. The full bundle remains authoritative. Consumers that need attachment paths, source-record hashes, validation notes, or retained context must open the bundle and verify the complete provenance block.

## Fail-closed behavior

The history-link writer refuses to publish a provenance summary when the supplied external evidence attempts to become executor-equivalent, has a non-advisory bundle effect, has a malformed attachment count, contains malformed attachment hashes/byte counts, or cannot be serialized deterministically.

If no external validation evidence is present, the history link keeps the historical shape and does not add the new summary field.

This feature does not execute validation, change bundle completeness, remove blockers, grant commit/push authority, or add network access.