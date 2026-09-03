# Maintenance bundle verification bounded input

`forge maintenance-bundle-verify` now enforces its 1,000,000-byte review limit at the actual binary read boundary for both the persisted bundle JSON and every source report named by the bundle.

Previously the verifier checked `stat().st_size` and then used an unbounded `read_text()` or `read_bytes()`. A file that grew after the size check could therefore exceed the intended memory/review bound. For source reports, the recorded observed byte count also came from the earlier `stat()` while the SHA-256 came from the later read, so concurrent mutation could make those observations describe different filesystem states.

The verifier now opens each input once and reads at most 1,000,001 bytes. The sentinel byte above the limit causes immediate refusal. Source-report SHA-256 and observed byte count are both derived from the exact same bounded byte snapshot. Bundle JSON is decoded and parsed from its bounded snapshot, with invalid UTF-8 rejected explicitly.

This change does not make source files immutable and does not authenticate their authors. It guarantees only that a single verification operation cannot accept an over-limit file through a pre-check/read race and that the reported size and digest describe the same observed bytes.
