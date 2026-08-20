# Archive copy/package advisory validation provenance

AUTO-177 carries the verified external-validation provenance summary from a written maintenance archive manifest through copied-root verification, package preview, and package verification.

## What is exposed

These surfaces now include `external_validation_provenance` with:

- `present`
- `status`
- `verified`
- `provenance_semantics`
- `executor_validation_equivalent`
- `bundle_gate_effect`
- `source_record`
- `attachment_count`
- `evidence_sha256`

Stable text output exposes presence, verification state, attachment count, evidence SHA-256, and advisory semantics so preservation reviewers do not need to reopen the manifest JSON merely to identify retained external validation evidence.

## Safety semantics

External observations are never promoted into Forge-executed validation proof. Present provenance is normalized to:

- `provenance_semantics=externally_supplied_observation`
- `executor_validation_equivalent=false`
- `bundle_gate_effect=advisory_only`

The summary is informational only. It does not change archive-copy verification status, package-preview readiness, package-verification status, entry integrity checks, preservation ranking, or any side-effect authority.

## Compatibility

Legacy manifests without the summary remain valid. Their downstream copy/package surfaces report provenance as not present rather than treating the absence as corruption.

## Example

```text
External validation provenance: present=true status=verified verified=true attachments=2
External validation semantics: executor_validation_equivalent=false bundle_gate_effect=advisory_only
External validation evidence SHA-256: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
```

SHA-256 continuity detects evidence-byte drift but does not prove signer identity.
