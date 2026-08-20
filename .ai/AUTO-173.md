# AUTO-173 — Hash-bound external validation summary in maintenance history links

## Objective
Preserve discoverable advisory external-validation provenance in the small durable maintenance history link without promoting externally supplied observations to Forge-executed validation proof.

## Repository assessment
Inspected README/docs/examples, relevant source/tests/config/CI, `.forge/policy.md`, autonomous roadmap/state, recent commits, open issues, all visible branches, and PR history. Historical feature/maintenance branches remain stale or superseded. Reviewed PRs are merged, closed, obsolete, or unrelated; none warranted integration. Work remained directly on `main`.

## Change
`write_maintenance_history_link` now emits `external_validation_evidence_summary` only when the completed written bundle contains `external_validation_evidence`. The summary carries the source record label, attachment count, fixed advisory/non-executor semantics, and a deterministic SHA-256 of the full external provenance block.

## Safety rationale
The writer refuses malformed or promoted provenance before writing the history link: executor equivalence must remain false, bundle gate effect must remain `advisory_only`, attachment count must match the attachment list, attachment hashes/byte counts must be well formed, and the provenance block must serialize deterministically. Bundles without external observations keep the historical history-link shape. Existing explicit confirmation, path containment, immutable-output, and overwrite-refusal gates remain unchanged.

## Validation
Added deterministic regression tests covering successful hash-bound summary persistence, refusal of attempted executor-proof promotion, and backward-compatible history links without external provenance. Direct full-checkout pytest could not run because this runtime cannot resolve `github.com`; GitHub workflow/status evidence is inspected separately and no green matrix result is fabricated when unavailable.

## Documentation and visuals
Added dedicated history-link provenance documentation and updated README Current Autonomous Status. No new visual was warranted because the maintenance lifecycle architecture is unchanged.

## Limitations
The compact hash is an integrity/index pointer, not signer identity. Consumers must still open the full bundle for attachment paths, source hashes, notes, and retained validation context. Fresh GitHub trust/status/protection acquisition remains policy-gated.

## Next action
If CI is green, extend the existing maintenance history-link review/replay surfaces to validate and expose the compact advisory-provenance summary while keeping it explicitly non-equivalent to executor-produced validation.