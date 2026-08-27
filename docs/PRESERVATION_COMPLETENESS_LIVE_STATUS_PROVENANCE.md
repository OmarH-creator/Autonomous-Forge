# Preservation completeness live-status provenance

AUTO-216 carries the already-verified live workflow-status proof through the final `forge maintenance-preservation-completeness` review boundary.

The command does **not** collect new GitHub status. It reuses the normalized `live_status_provenance` already retained by the written archive manifest, copied-root verification, and package verification.

The completeness artifact reports:

- whether live-status provenance is present;
- the exact requested commit;
- the bounded workflow-run limit;
- collection-completeness proof;
- per-run commit-binding proof;
- the retained evidence SHA-256;
- whether the normalized proof matches across manifest, copy verification, and package verification.

Stable text output includes the same fields so reviewers do not have to reopen the lower-level archive artifacts.

## Safety semantics

Live workflow status remains informational at this boundary:

- `review_effect=informational_only`
- `preservation_gate_effect=none`
- `affects_preservation_completeness=false`
- `affects_preservation_integrity=false`

Cross-layer drift is surfaced as `status=drifted` and `continuity_verified=false`, but it does not itself turn an otherwise complete preservation set into a blocked one. The authoritative workflow-status checks remain the earlier linked-bundle and push-readiness contracts.

The existing optional `--status` / workflow-freshness gate is separate. When explicitly required, that supplied status review can still affect preservation completeness; retained archive provenance cannot.

Legacy manifests without live-status provenance remain compatible and report `status=not_present`.
