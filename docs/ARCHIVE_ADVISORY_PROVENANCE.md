# Archive Advisory Validation Provenance

AUTO-176 makes verified external validation provenance a first-class field of the maintenance archive manifest.

## Why

`maintenance-review-compare` already carries a compact, verified advisory-provenance summary into each preservation candidate. Archive manifests previously retained that summary only indirectly inside the nested selected candidate. Reviewers and preservation tooling therefore had to understand the comparison schema to discover it.

`forge maintenance-archive-manifest` now exposes the same summary as `external_validation_provenance` in preview, confirmed-write, and verification results. Text output also reports presence, verification state, attachment count, evidence SHA-256, and fixed advisory semantics.

## Safety semantics

External validation observations remain advisory only:

- `provenance_semantics: externally_supplied_observation`
- `executor_validation_equivalent: false`
- `bundle_gate_effect: advisory_only`

The archive manifest does not use external validation provenance for candidate ranking, manifest readiness, or archive-integrity scoring. A caller cannot promote an external observation to executor-produced validation by setting stronger values in the candidate summary; the archive surface normalizes those fields back to the advisory contract.

## Example

```text
External validation provenance: present=true status=verified verified=true attachments=2 executor_validation_equivalent=false bundle_gate_effect=advisory_only
External validation evidence SHA-256: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
```

JSON output contains the same information under the top-level `external_validation_provenance` field.

## Compatibility

Legacy candidates and manifests without external validation provenance continue to work. They surface:

```json
{
  "present": false,
  "status": "not_present",
  "verified": false,
  "provenance_semantics": "none",
  "executor_validation_equivalent": false,
  "bundle_gate_effect": "none",
  "source_record": "",
  "attachment_count": 0,
  "evidence_sha256": ""
}
```

This feature does not add network access, validation execution, Git mutation, push authority, archive copying, or signer-identity verification.
