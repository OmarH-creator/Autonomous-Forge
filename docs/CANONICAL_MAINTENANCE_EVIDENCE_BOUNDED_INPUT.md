# Canonical maintenance evidence bounded input

`canonical_maintenance_evidence` is the canonical bridge from verified push/post-push JSON evidence into a durable maintenance bundle. Each repository-local source report is now consumed through one bounded binary snapshot.

## Bound

Forge opens the resolved `.json` input in binary mode and performs a single read of at most **1,000,001 bytes**. The extra byte is a sentinel for the **1,000,000-byte** review limit. Empty inputs and inputs that return the sentinel byte are rejected before UTF-8 decoding or JSON parsing.

The parsed JSON object, retained byte count, and SHA-256 source fingerprint all come from that same byte snapshot. This closes the previous `stat().st_size` followed by unbounded `read_bytes()` race, where a concurrently growing file could bypass the intended limit and where pre-read size observations could diverge from the bytes actually parsed and hashed.

## Preserved safety behavior

Repository containment, symlink rejection, `.json` enforcement, expected report titles, verified push-wrapper consistency checks, reviewed-path checks, and downstream bundle/provenance validation are unchanged. This change does not add network access, command execution, writes, push authority, or remote mutation.

## Limitation

A bounded snapshot proves what Forge observed during this read; it does not make the source immutable and does not authenticate its author. Later filesystem mutation remains possible and is handled by the existing digest-continuity verification stages.
