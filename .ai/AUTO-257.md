# AUTO-257 — Bound canonical maintenance-evidence ingestion

## Inspection and rationale

Broad inspection covered repository root/docs/source/tests/config/CI inventory, README, `.forge/policy.md`, autonomous plan/state/changelog/decisions, recent commits and Actions, all eight visible branches, open issues, TODO-oriented source search, and PR history. The policy-aware `forge plan` milestone and guarded end-to-end maintenance workflow are already shipped. Seven non-main branches remain historical/diverged; no open PR contains work that should replace current `main`. Issues #1, #6, and #9 remain broader product/discussion requests rather than blockers.

The highest-value confirmed defect was in `canonical_maintenance_evidence`: each canonical JSON source was first checked with `stat().st_size` and then consumed by unbounded `read_bytes()`. A concurrent growth between those operations could bypass the 1,000,000-byte review limit, while the pre-read size observation could describe a different filesystem state than the bytes actually parsed and hashed.

## Work

- Removed the pre-read size decision from canonical JSON resolution.
- Added a single bounded binary snapshot read of at most 1,000,001 bytes.
- Empty inputs and the sentinel byte beyond the 1,000,000-byte limit fail closed before UTF-8/JSON parsing.
- Parsed JSON, retained byte count, and SHA-256 now derive from the same exact byte snapshot.
- Added deterministic regression tests for the exact sentinel read, over-limit refusal, and parse/size/hash binding.
- Added focused documentation and updated README/state to describe the repaired boundary.

## Safety

All touched paths are allowed by `.forge/policy.md`. Existing repository confinement, symlink rejection, `.json` enforcement, expected report-title checks, verified push-wrapper consistency checks, reviewed-path checks, and downstream bundle/provenance validation remain unchanged. No workflow, secret, network, external-command authority, write authority, push behavior, remote configuration, telemetry, or branch-protection behavior changed.

## Validation

Direct checkout/full pytest execution is unavailable because outbound DNS to github.com is blocked in the runtime. Validation therefore relies on the deterministic tests committed with this change and the repository's GitHub Actions matrix for Python 3.10, 3.11, and 3.12. The cycle is complete only when the exact final `main` head is green.

## Limitations and next action

A bounded snapshot guarantees internal consistency for the bytes Forge observed but does not make the source immutable or authenticate its author. Later mutation remains possible. Next inspect remaining execution/history/evidence readers for another concrete split-read, stale-state, or pre-check/unbounded-read defect, unless CI exposes a higher-priority regression first.
