# AUTO-256 — Bound maintenance-bundle verification reads

## Inspection and rationale

Broad inspection covered README/docs/examples, source/tests/config/CI inventory, `.forge/policy.md`, autonomous plan/state/changelog/decisions, recent commits and Actions, all eight visible branches, open issues, TODO-oriented source search, and PR history. The requested policy-aware `forge plan` capability and the guarded end-to-end maintenance workflow are already shipped. Seven non-main branches remain historical/diverged. There are no open PRs; merged PRs #4, #11, and #12 and closed superseded PRs #2, #3, #5, and #10 do not contain newer product work that should replace current `main`.

The highest-value confirmed defect was in `maintenance_bundle_verify`: bundle and source-report verification still performed a pre-read `stat().st_size` check followed by unbounded `read_text()`/`read_bytes()`. Concurrent growth could bypass the 1,000,000-byte verification limit, and source-report observed byte count and SHA-256 could refer to different filesystem observations.

## Work

- Added one bounded binary snapshot helper that reads at most 1,000,001 bytes.
- Bundle JSON is decoded and parsed from that bounded snapshot, with invalid UTF-8 reported explicitly.
- Each source report now derives both observed byte count and SHA-256 from the same snapshot.
- Added deterministic regression coverage for the exact sentinel read, over-limit refusal, and byte-count/digest binding.
- Added focused documentation and updated README/state to describe the repaired verification boundary.

## Safety

All changed paths are allowed by `.forge/policy.md`. No workflow, secret, network, external-command authority, push behavior, branch protection, remote, telemetry, or access-control behavior changed. The command remains read-only.

## Validation

The runtime cannot clone GitHub because outbound DNS is unavailable, so local full-checkout pytest execution is unavailable. Validation relies on deterministic tests committed with the change plus the repository's GitHub Actions matrix on Python 3.10, 3.11, and 3.12. The run is complete only after the exact final `main` head is green.

## Limitations and next action

Bounded snapshot verification prevents over-limit growth races and keeps observed size/hash internally consistent; it does not make source files immutable or provide signer identity. Next inspect `canonical_maintenance_evidence` and the remaining execution/history readers for another concrete split-read or pre-check/unbounded-read defect, unless CI exposes a higher-priority regression first.
