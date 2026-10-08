# Change-readiness bounded input

AUTO-260 closes a time-of-check/time-of-use gap in the existing `forge change-readiness` evidence reader.

Before AUTO-260, `read_change_readiness(...)` checked each supplied review file with `stat().st_size` and then consumed it with `read_text()`. A repository-local file that grew between those operations could bypass the intended 1,000,000-byte review boundary, and the accepted JSON could differ from the size observation that allowed it.

The reader now opens each supplied `.json` review file once in binary mode and reads at most 1,000,001 bytes:

- inputs larger than 1,000,000 bytes are rejected at the actual read boundary;
- UTF-8 decoding happens only after the bounded read succeeds;
- JSON parsing sees exactly the bytes admitted by the bounded read;
- repository confinement, symlink rejection, regular-file checks, `.json` enforcement, and read-only semantics remain unchanged.

This hardening does not make input files immutable or authenticate their author. It only ensures Forge's change-readiness decision is based on a bounded, internally consistent snapshot of each supplied review file.
