# AUTO-252 — Bounded post-push maintenance evidence ingestion

## Inspection and rationale

Broad repository inspection covered README/docs/examples, source/tests/config/CI inventory, `.forge/policy.md`, autonomous plan/state/changelog/decisions, recent commits and Actions, all eight visible branches, open issues, TODO-oriented source search, and PR history. The requested policy-aware `forge plan` milestone and the guarded end-to-end maintenance chain are already shipped, so this run continued the current execution/evidence-integrity milestone.

The highest-value confirmed defect was in `verified_maintenance_run._read_json`: it checked `stat().st_size` against the 1,000,000-byte limit and then performed an unbounded `read_bytes()`. A repository-local evidence file could grow between those operations, bypassing the memory bound. The returned source metadata also paired the earlier stat size with a SHA-256 digest of later bytes, so durable provenance could contain an internally inconsistent size/digest observation.

## Change

The reader now opens the evidence file in binary mode and reads at most 1,000,001 bytes. Empty or oversized inputs are rejected before UTF-8 decoding and JSON parsing. The retained byte count and SHA-256 digest are both derived from the exact same byte snapshot that is parsed.

Deterministic tests cover:

- exact byte-count and SHA-256 binding for a valid JSON input;
- refusal of an input larger than the configured bound;
- refusal of invalid UTF-8.

Documentation and README status were updated to describe the strengthened post-push-to-durable-history boundary. No visual was needed because the workflow topology did not change.

## Branch and PR assessment

Work remained directly on `main`. Seven non-main branches remain historical/diverged, there are no open PRs, and recent closed PR work is superseded, already integrated, obsolete, or unrelated to this repair. Issues #1, #6, and #9 are broader product/discussion requests rather than blockers.

## Safety

All changed files are within policy-allowed `src/**`, `tests/**`, `docs/**`, `README.md`, and `.ai/**` paths. No workflow, secret, token, key, remote, branch-protection, network-authority, force-push, or telemetry change was introduced.

## Validation

The automation runtime could not clone the repository because direct DNS access to github.com is unavailable, so full-suite execution relies on the repository's existing GitHub Actions matrix. The exact final pushed head must pass package installation, source compilation, installed CLI smoke testing, roadmap validation, and pytest on Python 3.10, 3.11, and 3.12 before this run is marked DONE.

## Limitations and next action

The bounded single-snapshot read does not make source evidence immutable or authenticate its author. Existing provenance and commit-identity checks remain authoritative. The next highest-value candidate is the separate legacy maintenance-bundle reader/hash split, which inspection indicates still hashes and parses each source report through separate filesystem reads; confirm and repair that defect if CI remains green.
