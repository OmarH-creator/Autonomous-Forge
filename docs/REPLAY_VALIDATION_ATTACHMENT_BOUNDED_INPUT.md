# Replay validation attachment bounded input

`forge maintenance-replay-summary --validation-record ...` can surface repository-local validation attachments as advisory provenance. These attachments never become executor-produced validation authority, but their bytes are still hashed and retained in replay evidence.

## AUTO-254 integrity fix

The attachment reader now opens each resolved regular file in binary mode and performs one bounded read of at most **1,000,001 bytes**. Inputs larger than the **1,000,000-byte** replay provenance limit are rejected before their digest or byte count is accepted.

Previously the reader called `stat().st_size` and then used an unbounded `read_bytes()`. A file that grew after the size check could therefore exceed the intended memory/review bound.

The SHA-256 digest and retained byte count are derived from the exact bounded byte snapshot returned by that single read.

## Preserved safety contract

The change does not alter repository containment, symlink rejection, regular-file checks, validation-context association, replay readiness, or provenance semantics. External validation attachments remain advisory only and are never treated as equivalent to Forge-executed validation.

## Limitations

A bounded snapshot does not make an attachment immutable and does not authenticate its author. A file may change after it has been read; the retained digest identifies the bytes observed by that replay operation, not all future filesystem states.
