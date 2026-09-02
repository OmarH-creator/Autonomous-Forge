# Maintenance bundle source snapshot binding

AUTO-253 closes a source-integrity race in the legacy maintenance evidence bundle reader.

Before this change, each source report was size-checked and hashed, then parsed through a separate filesystem read. A concurrent writer could therefore change a report between those operations, leaving the bundle's retained `sha256`/`bytes` metadata bound to different bytes from the JSON object that actually entered the evidence chain.

The reader now opens each repository-local `.json` source once for one bounded binary snapshot. It reads at most 1,000,001 bytes, rejects inputs above the 1,000,000-byte review limit, decodes UTF-8, parses and validates the expected JSON-object title, and derives the source-report SHA-256 and byte count from those exact same bytes.

This remains a local read boundary. It does not make source files immutable, authenticate their author, grant command or network authority, or change the explicit confirmation requirements for durable writes. A source may still change after its snapshot is taken; the bundle records exactly which bytes were accepted so later continuity checks can detect drift.
