# Maintenance history-link live-status provenance

AUTO-211 carries the normalized live workflow-status proof already retained by a complete maintenance bundle into its compact `.ai/run-history/` link. AUTO-212 closes the next review boundary by making `forge maintenance-history-link-review --verify-linked-bundle` independently compare that compact summary with the authoritative linked bundle.

When `verified_provenance.live_status_evidence` is present, `write_maintenance_history_link()` validates that the proof still:

- comes from `gh run list`;
- names the same commit as the maintenance bundle;
- uses a bounded workflow-run limit from 1 through 20;
- proves bounded collection completeness;
- proves per-run commit binding; and
- has a deterministic SHA-256 matching the normalized live-status fields.

A valid history link stores that same proof as `live_status_evidence_summary` with `present: true`. This is a compact discoverability surface, not a second workflow-status contract: the full durable maintenance bundle remains authoritative.

With `--verify-linked-bundle`, the history-link reviewer now reads the linked bundle only after the history-link bundle SHA-256 has matched. It then validates the compact live-status summary against `verified_provenance.live_status_evidence`, recomputes the normalized SHA-256, checks the exact commit, source, workflow-run limit, bounded completeness, and per-run commit binding, and exposes the result as `live_status_evidence_summary_verification`. Any disagreement blocks linked replay verification.

Bundles and history links created without live workflow-status evidence remain backward compatible and do not receive synthetic live-status proof.

## Safety boundary

This feature is evidence continuity and verification only. It does not query GitHub, rerun workflows, authorize a push, force-push, push tags, change remotes, change branch protection, or add any new side effect. Malformed, wrong-commit, incomplete, or digest-drifted live evidence fails closed. The linked durable bundle remains the authoritative evidence source.
