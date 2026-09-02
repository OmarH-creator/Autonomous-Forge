# Verified maintenance bounded input

`forge verified-maintenance-run` carries a post-push-verified orchestration artifact into durable maintenance evidence. Its repository-local JSON reader now enforces the 1,000,000-byte review limit at the actual read boundary rather than trusting a pre-read file-size check.

The reader opens the evidence file in binary mode and reads at most 1,000,001 bytes. An empty input or any read larger than 1,000,000 bytes is rejected before UTF-8 decoding and JSON parsing. The retained byte count and SHA-256 digest are computed from that same exact byte snapshot, so the source metadata cannot describe a different pre-read `stat()` observation.

This closes the race where a repository-local evidence file could grow after `stat().st_size` was checked and before an unbounded `read_bytes()` completed. Repository confinement, symlink rejection, `.json` enforcement, expected-title validation, provenance checks, commit/path consistency checks, explicit persistence confirmations, and all downstream durable-write safeguards remain unchanged.

The bound limits memory consumed while ingesting one evidence artifact; it does not make the file immutable and does not authenticate its author. Existing provenance and commit-identity validation remain authoritative for whether the evidence may enter durable history.
