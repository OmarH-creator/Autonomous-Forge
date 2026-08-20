# Immutable Validation Evidence in Maintenance Replay

`forge maintenance-replay-summary` can optionally carry verified immutable validation-result attachments into replay output without promoting external observations to executor-produced validation proof.

## Usage

```bash
forge maintenance-replay-summary \
  --root . \
  --bundle .ai/evidence/AUTO-171-bundle.json \
  --validation-record .ai/run-history/AUTO-171.json \
  --require-replayable \
  --format json
```

`--validation-record` must name a valid `run-history/v1` record under `.ai/run-history/`. Forge uses the existing bounded `run-history-read` attachment discovery path, so matching sidecars under `.ai/run-history/validation-attachments/` are verified against the source record's exact bytes and SHA-256 before they are exposed.

## Provenance semantics

When a validation record is supplied, replay output includes `external_validation_evidence` with:

- the source run-history record;
- a count of verified immutable attachments;
- each attachment's repository path, SHA-256, byte count, supplied validation result, execution label, note, and retained validation context;
- `provenance_semantics: externally_supplied_observation`;
- `executor_validation_equivalent: false`;
- `replay_gate_effect: advisory_only`.

The attachment itself is fingerprinted after the existing source-binding verification, so a saved replay summary can identify the exact external observation that was reviewed.

## Association checks

If retained validation context is available on the source record or a matching attachment, Forge refuses contradictory evidence before adding it to replay output:

- retained `validation_steps` must match the maintenance bundle's validation steps exactly;
- retained `expected_file_changes`, when present, must cover every reviewed bundle path.

Context-free legacy records remain readable and are reported as `context_not_provided` rather than being treated as contradictory.

## Safety boundary

This integration is read-only. It does not run validation commands, apply patches, stage files, create commits, push, fetch, modify remotes, change branch protections, rerun workflows, or persist evidence.

External validation attachments are intentionally **advisory only**. They do not alter the bundle's replay blockers or convert a blocked maintenance bundle into a replayable one. Replay readiness continues to depend on the verified maintenance bundle and its executor-produced validation evidence chain.
