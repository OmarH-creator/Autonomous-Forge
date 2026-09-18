# Verified commit-readiness bounded input

AUTO-258 closes two time-of-check/time-of-use gaps in verified commit-readiness evidence ingestion.

Validated target files and repository-local JSON evidence are now consumed through a single bounded binary snapshot. Forge reads at most 1,000,001 bytes for the 1,000,000-byte limit and rejects the sentinel byte beyond the limit. Target SHA-256 is calculated from the exact accepted snapshot. JSON evidence is UTF-8 decoded and parsed from the exact accepted snapshot.

This replaces the previous `stat().st_size` followed by a separate unbounded `read_bytes()` or `read_text()` operation. Repository confinement, symlink rejection, regular-file and `.json` checks, expected-title validation, and the existing commit-readiness authority boundary remain unchanged.

The change does not make source files immutable or authenticate their author. It guarantees only that the bytes Forge accepts for one read are bounded and internally consistent with the digest or JSON object derived from them.
