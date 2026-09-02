# AUTO-253 — Bind maintenance bundle source snapshots

## Inspection

Started from `main` at `eee652c34d4f2ea16788c06985f1d65645e6b2e8`. Inspected README/docs/examples, source/tests/config/CI inventory, `.forge/policy.md`, `.ai` plan/state/changelog/decisions, recent commits and GitHub Actions, all eight visible branches, open issues, TODO-oriented code search, and PR history. The latest main workflow was green. Seven non-main branches remain historical/diverged, there are no open PRs, and issues #1, #6, and #9 are broader product/discussion requests rather than blockers.

## Objective and rationale

Continue the end-to-end maintenance-integrity milestone by closing the confirmed legacy maintenance-bundle source-ingestion race identified by AUTO-252. The reader previously recorded source size/hash and parsed the same report through separate filesystem reads. Concurrent mutation could therefore make retained source metadata describe different bytes from the JSON accepted into the bundle.

## Change

`maintenance_evidence_bundle` now reads every source report through one bounded binary snapshot of at most 1,000,001 bytes. Inputs above the 1,000,000-byte limit are rejected before decode/parse. UTF-8 decoding, JSON-object/title validation, SHA-256, and byte count all use that exact byte snapshot. `read_maintenance_evidence_bundle_data` passes the five parsed snapshots and their matching source records into the existing deterministic bundle builder.

Deterministic regression tests cover exact snapshot hash/size binding, oversized input rejection, and invalid UTF-8. `docs/MAINTENANCE_BUNDLE_SOURCE_SNAPSHOT_BINDING.md` documents the contract.

## Safety and branch/PR disposition

Work stayed directly on `main`. No branch, PR, merge, force-push, workflow edit, remote change, protection change, or new command/network authority was introduced. Repository confinement, symlink and `.json` checks, expected-title validation, downstream evidence consistency checks, and explicit durable-write confirmations remain intact. Historical branches/PRs were not integrated because current `main` supersedes the relevant work.

## Validation

Validation is complete only after the final `main` head passes the repository's GitHub Actions matrix: package installation, source compilation, installed CLI smoke testing, roadmap validation, and full pytest on Python 3.10, 3.11, and 3.12.

## Limitations

Single-snapshot ingestion binds metadata to exactly the bytes parsed, but it does not make source files immutable or authenticate their author. A source can still change after the snapshot; retained hashes allow later continuity checks to detect that drift.

## Next action

Inspect the remaining evidence/history readers for any equivalent split-read identity gap or fresh CI failure, prioritizing real execution/durable-history correctness over new read-only surfaces.
