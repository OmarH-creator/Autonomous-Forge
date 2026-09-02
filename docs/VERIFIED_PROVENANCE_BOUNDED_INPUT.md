# Verified maintenance provenance bounded input

The legacy verified-provenance bridge used by maintenance evidence now enforces its 1,000,000-byte JSON review limit at the actual read boundary.

## Why this matters

Previously the reader checked `stat().st_size` and then called `read_bytes()`. A repository-local JSON file could grow after the size check, causing Forge to consume more than the intended review bound. The retained source metadata also used the earlier `stat()` byte count while the SHA-256 digest and parsed JSON came from the later read, so concurrent mutation could make those fields describe different observations.

## Current contract

For each verified push-handoff or post-push verification input, Forge:

1. resolves the path inside the repository and rejects symlinks/non-JSON files as before;
2. opens the file once in binary mode;
3. reads at most 1,000,001 bytes;
4. rejects the input if the sentinel byte beyond the 1,000,000-byte limit is present;
5. decodes and parses the exact bounded snapshot as UTF-8 JSON;
6. derives retained byte count and SHA-256 from that exact same snapshot.

This closes the pre-check/unbounded-read growth race and keeps parsed evidence, byte count, and digest internally consistent.

## Limits

A bounded snapshot does not make the source file immutable and does not authenticate its author. A later filesystem mutation can still change the file after Forge has ingested it. Existing provenance, commit, branch, remote, reviewed-path, validation-command, and post-push consistency checks remain responsible for deciding whether the observed evidence is authoritative.
