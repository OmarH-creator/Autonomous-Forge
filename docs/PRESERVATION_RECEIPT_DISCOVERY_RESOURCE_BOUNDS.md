# Preservation receipt discovery resource bounds

AUTO-219 makes the existing preservation-receipt discovery contract genuinely bounded for both CLI-driven and direct Python use.

`discover_maintenance_preservation_receipts()` already defaulted to scanning at most 100 direct JSON files under `.ai/preservation-receipts/`, but callers could previously raise `max_receipts` arbitrarily. Each selected candidate was also read without an explicit byte ceiling. That meant the read-only discovery path could consume unbounded local resources even though its public safety description called the scan bounded.

The discovery contract now has two fixed limits:

- at most **100** direct JSON receipt candidates can be admitted; callers may choose a smaller `max_receipts`, but values above 100 are refused;
- each candidate receipt is read through a **1 MiB (1,048,576-byte)** ceiling. Oversized candidates are surfaced as unattributed invalid evidence without being fully loaded.

The byte ceiling is applied again when a matching receipt enters normal receipt verification, so a file cannot pass the first bounded read and then grow into an unbounded second read before verification.

These limits do not change preservation semantics. Receipt discovery remains informational only. A malformed, oversized, unsupported, or unbound receipt that cannot be safely attributed to the selected completeness artifact is reported through `unattributed_invalid_receipts`; only an invalid receipt that can be explicitly bound to the selected artifact can make that artifact's receipt review `attention_required`.

The selected preservation-completeness artifact itself is still read as the single authoritative input and is independently required to report a complete preservation result. AUTO-219 specifically bounds the potentially many receipt-directory candidates rather than introducing a new size contract for completeness artifacts.

No network access, external command execution, Git mutation, workflow action, push authority, or persistence authority is added by this change.
