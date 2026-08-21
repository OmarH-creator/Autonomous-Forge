# AUTO-180 — Discover verified preservation receipts in the review path

## Objective

Make immutable preservation receipts discoverable from the existing receipt command without allowing receipt existence to substitute for preservation completeness.

## Repository assessment

Inspected README/docs, preservation/archive source and tests, `.forge` policy, CI configuration, roadmap/state/changelog/decisions, recent commits, open issues, every visible branch, and recent pull-request history. The seven non-main branches remain historical/diverged and the reviewed PRs are merged, closed, obsolete, or unrelated; none warranted integration.

## Work

- Added bounded `--discover` review to `forge maintenance-preservation-receipt` rather than introducing another standalone read-only command.
- Discovery first verifies the chosen preservation-completeness artifact is independently complete.
- Scans at most 100 direct `.json` candidates under `.ai/preservation-receipts/` in deterministic name order and refuses a symlinked receipt directory.
- Reuses the existing receipt verifier for matching receipts, ignores valid receipts bound to other completeness artifacts, and surfaces malformed/drifted candidates for reviewer attention.
- Fixes `receipt_gate_effect=informational_only` and `receipt_required_for_preservation=false`; receipt status never changes `preservation_complete`.
- Added deterministic regression coverage and updated command documentation, README status, and autonomous state.

## Validation

Changed receipt core, CLI, and focused test files syntax-compile in the available scratch environment. A focused executable smoke passed no-receipt review, receipt persistence/discovery, verified matching receipt review, and tampered matching receipt attention behavior while preservation remained complete. Full checkout pytest remains unavailable because this runtime cannot resolve `github.com`; no unsupported CI claim is made.

## Safety boundary

No new write authority, validation execution, Git mutation, network access, workflow polling, force-push, remote mutation, or branch-protection behavior was added. Receipt persistence still requires its existing independent confirmation. Discovery is bounded, local, read-only, and informational.

## Next action

Inspect AUTO-180 CI when observable. If green, only propagate verified receipt discovery to a higher-level preservation review surface when doing so preserves the same informational-only semantics and does not duplicate existing evidence contracts.
