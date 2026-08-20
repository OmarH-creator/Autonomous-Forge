# Maintenance review advisory provenance

AUTO-175 carries verified external validation provenance from linked history replay into the existing reviewer handoff and comparison surfaces.

## Handoff output

`forge maintenance-review-handoff` now exposes `external_validation_provenance` when the linked history/bundle review verified a compact external-validation summary. The field records whether advisory evidence is present and verified, its source record, attachment count, evidence SHA-256, and the fixed provenance semantics.

External observations remain:

- `provenance_semantics: externally_supplied_observation`
- `executor_validation_equivalent: false`
- `bundle_gate_effect: advisory_only`

This field is reviewer context only. It does not add a required handoff gate and cannot make a blocked handoff ready.

## Comparison output

`forge maintenance-review-compare` preserves the same advisory-provenance summary in each handoff row and each preservation candidate. The comparison also reports `verified_external_validation_count` so reviewers can see how many completed handoffs carry verified advisory observations without reopening linked-replay JSON.

Verified advisory evidence is deliberately **not** part of the preservation ranking score. A run is never ranked higher merely because externally supplied observations are present.

## Safety boundary

The reviewer surfaces remain read-only. They do not rerun validation, execute commands, inspect live remotes, stage, commit, push, fetch, mutate workflow state, change branch protection, or verify signer identity. SHA-256 continuity proves consistency with the linked bundle provenance bytes; it does not prove who produced the observation.

Legacy history links without the compact summary remain compatible and appear as `status: not_present` rather than being promoted to verified provenance.
