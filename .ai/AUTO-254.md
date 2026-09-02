# AUTO-254 — Bound replay validation attachment reads

## Repository assessment

Started from green AUTO-253 final head `1e0dde909fa493c3be9eb6dfa9415bc451395b30`. Inspected README/docs/examples, source/tests/config/CI inventory, `.forge/policy.md`, autonomous roadmap/state/changelog/decisions, recent commits and Actions, all eight visible branches, open issues, TODO-oriented source search, and PR history. The policy-aware `forge plan` milestone and the guarded end-to-end maintenance workflow are already shipped, so this run continued the existing execution/durable-history integrity milestone rather than adding a new read-only surface.

Seven non-main branches remain historical/diverged. No open PR requires integration; recent PR work is closed, obsolete, superseded by direct-main work, or unrelated. Open issues #1, #6, and #9 are broader product/discussion requests and do not block this repair.

## Objective and rationale

Fix the remaining pre-check/unbounded-read race in `maintenance_replay_validation_evidence._attachment_fingerprint`. The old implementation checked `stat().st_size <= 1_000_000` and then called unbounded `read_bytes()`. A concurrently growing repository-local validation attachment could therefore exceed the intended replay-provenance memory/review limit after the pre-check.

## Implementation

- Replaced the separate `stat()` size gate plus unbounded `read_bytes()` with one binary read bounded to `_MAX_ATTACHMENT_BYTES + 1`.
- Reject the snapshot when the sentinel byte is present.
- Derive SHA-256 and retained byte count from the exact same bounded snapshot.
- Added deterministic tests that verify the exact 1,000,001-byte read request, snapshot digest/size binding, and oversized refusal.
- Added focused documentation and updated README status/safety notes.

Repository confinement, symlink rejection, regular-file checks, validation-context association, advisory-only provenance semantics, and replay-readiness gates remain unchanged.

## Validation

Checkout-capable local validation is unavailable in this automation runtime because direct DNS access to `github.com` is blocked. The change therefore relies on deterministic repository tests plus the repository's GitHub Actions matrix. The final exact `main` head must pass package installation, source compilation, installed CLI smoke testing, roadmap validation, and full pytest on Python 3.10, 3.11, and 3.12 before AUTO-254 is marked complete.

## Safety and diff review

All touched paths are allowed by `.forge/policy.md`: `src/**`, `tests/**`, `docs/**`, `README.md`, and `.ai/**`. No prohibited workflow, secret/token/key, remote, branch-protection, visibility, licensing, telemetry, or external-service change was introduced. No branch, pull request, merge, or force-push was used.

The meaningful production change is limited to the existing attachment ingestion boundary; documentation and project-memory updates support that defect repair.

## Limitations

A bounded snapshot prevents unbounded attachment reads and binds the digest/byte count to the observed bytes, but it does not make the source immutable or authenticate its author. The attachment can still change after ingestion.

## Next action

Inspect the remaining history/evidence ingestion paths for another concrete pre-check/unbounded-read or split-read identity defect. Any fresh CI failure takes priority over further feature work.
