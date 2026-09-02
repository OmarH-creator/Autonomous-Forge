# AUTO-255 — Bound verified-maintenance provenance ingestion

## Objective

Close the confirmed pre-check/unbounded-read integrity gap in the existing verified-maintenance provenance bridge without adding another command surface.

## Inspection and rationale

Broad inspection covered README/docs/examples, source/tests/config/CI inventory, `.forge/policy.md`, autonomous plan/state/changelog/decisions, recent commits and Actions, all eight visible branches, open issues, TODO-oriented source search, and PR history. The policy-aware `forge plan` milestone and guarded end-to-end maintenance workflow are already shipped. Seven non-main branches remain historical/diverged and no open PR warrants integration. Issues #1, #6, and #9 remain broader product/discussion requests rather than blockers.

`src/autonomous_forge/verified_maintenance_provenance.py` still used `stat().st_size` before an unbounded `read_bytes()`. A repository-local JSON input that grew between those operations could bypass the 1,000,000-byte review limit. The retained source metadata also used the earlier stat size beside a SHA-256 digest of the later bytes, so concurrent mutation could make the size and digest refer to different observations.

## Change

The reader now opens each verified push-handoff or post-push verification input once in binary mode, reads at most 1,000,001 bytes, rejects the sentinel byte beyond the 1,000,000-byte limit, and derives JSON parsing, retained byte count, and SHA-256 from the same exact snapshot.

Deterministic tests assert the exact sentinel read size, exact snapshot metadata binding, oversized-input refusal, and invalid UTF-8 refusal. `docs/VERIFIED_PROVENANCE_BOUNDED_INPUT.md` records the contract and README status reflects the strengthened boundary.

## Safety

Repository confinement, symlink rejection, `.json` enforcement, UTF-8/JSON validation, verified commit/branch/remote/path/validation-command checks, and all existing side-effect gates remain unchanged. No new network access, external command authority, workflow modification, branch-protection change, force push, remote mutation, telemetry, secret handling, branch, or PR was introduced.

## Validation

Focused deterministic tests were added. Direct checkout/full pytest execution is unavailable in the automation runtime because outbound DNS to github.com is blocked; GitHub Actions on `main` is the authoritative supported-version validation and must be green on the final exact head before completion is reported.

## Limitations and next action

The bounded snapshot makes one ingestion internally consistent but does not make the source immutable or authenticate its author. Next inspect remaining executor/history/evidence readers for another confirmed split-read or pre-check/unbounded-read defect, with any fresh CI failure taking priority.
