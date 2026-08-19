# AUTO-170 — Consume immutable validation attachments

## Inspection and rationale

Repository inspection covered README/docs, source/tests/config/CI, `.forge` policy, autonomous memory, recent commits, open issues, all visible branches, and recent pull requests. AUTO-169 shipped immutable hash-bound validation sidecars, but the primary `forge run-history-read` consumer still ignored them. Historical branches are stale/superseded and reviewed PRs are merged/closed/obsolete or unrelated, so no branch or PR work warranted integration.

## Work

Enhanced `run-history-read` to perform a bounded non-recursive scan of `.ai/run-history/validation-attachments/`, identify sidecars that explicitly name the selected record, verify those sidecars against the current source bytes/SHA-256, and surface verified attachment metadata in both text and JSON output. Legacy `run-history/v1` validation fields are preserved rather than overwritten or inferred from sidecars.

Added deterministic tests for successful discovery, CLI JSON exposure, unrelated attachment exclusion, text formatting, and fail-closed source drift. Updated run-history read documentation to describe the new bounded discovery and compatibility behavior.

## Safety

- read-only discovery only;
- at most 100 non-recursive JSON candidates;
- symlinked attachment directory rejected;
- unrelated/malformed sidecars ignored unless they explicitly name the selected record;
- matching sidecars must pass existing byte-count/SHA-256 verification;
- no validation command execution, Git mutation, push, network access, remote/protection mutation, workflow mutation, or authority escalation;
- no collapse of externally supplied validation observations into executor-produced proof.

## Validation

The changed reader and focused AUTO-170 tests syntax-compiled in the available local scratch environment before publication. Full repository pytest remains unavailable because the runtime cannot resolve github.com. Fresh GitHub status/check visibility must be inspected on the pushed head before claiming the full Python 3.10/3.11/3.12 matrix green.

## Next action

If CI is green, integrate verified sidecar provenance into replay/maintenance-evidence consumption under explicit semantics that keep externally supplied observations distinct from executor-produced validation evidence.
