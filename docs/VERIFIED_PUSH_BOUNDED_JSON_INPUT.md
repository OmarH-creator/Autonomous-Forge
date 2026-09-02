# Verified-push bounded JSON input

`forge verified-push-run` consumes repository-local JSON evidence before it can enter the guarded push and post-push verification path.

AUTO-251 hardens that boundary by reading at most 1,000,001 bytes from each candidate file. Inputs larger than the 1,000,000-byte review limit are rejected before UTF-8 decoding or JSON parsing. This replaces the previous `stat()`-then-`read_text()` sequence, where a file could grow after the size check and cause an unbounded read.

The existing containment rules remain unchanged: evidence must stay inside the configured repository root, must not be a symlink, must be a regular `.json` file, must decode as UTF-8, and must contain a JSON object.

This is not a new authority boundary. It does not add network access, commands, push permission, commit permission, workflow changes, remote edits, or branch-protection changes. It only makes the existing verified-push evidence ingestion bounded even if the input file changes between filesystem observations.

## Validation

Deterministic tests cover a valid bounded object, an oversized file whose reader is called exactly once with the 1,000,001-byte sentinel limit, and invalid UTF-8 rejection.

## Remaining limitation

The bounded read prevents memory growth beyond the configured review limit, but it does not make the evidence file immutable. Other existing provenance and commit-identity checks remain responsible for deciding whether the parsed evidence is authoritative and internally consistent.
