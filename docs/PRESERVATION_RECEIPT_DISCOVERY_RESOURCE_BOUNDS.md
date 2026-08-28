# Preservation receipt discovery resource bounds

AUTO-219 made preservation-receipt discovery genuinely bounded for both CLI-driven and direct Python use. AUTO-220 completes that resource boundary by applying the same fixed byte ceiling to the authoritative preservation-completeness artifact used by receipt preview, write, verification, and discovery.

The receipt path now has three fixed limits:

- the selected preservation-completeness artifact is read through a **1 MiB (1,048,576-byte)** ceiling;
- at most **100** direct JSON receipt candidates can be admitted during discovery; callers may choose a smaller `max_receipts`, but values above 100 are refused;
- each candidate receipt is read through a **1 MiB (1,048,576-byte)** ceiling. Oversized candidates are surfaced as unattributed invalid evidence without being fully loaded.

The completeness ceiling is applied anywhere the source is authoritative: receipt preview/write, receipt verification, and receipt discovery. Verification therefore cannot accept a small completeness artifact, then later reread an arbitrarily large replacement while checking the receipt binding. Matching receipt verification likewise repeats the candidate byte ceiling so a receipt cannot pass the first bounded read and then grow into an unbounded second read.

These limits do not change preservation semantics. Receipt discovery remains informational only. A malformed, oversized, unsupported, or unbound receipt that cannot be safely attributed to the selected completeness artifact is reported through `unattributed_invalid_receipts`; only an invalid receipt that can be explicitly bound to the selected artifact can make that artifact's receipt review `attention_required`.

The selected completeness artifact remains the single authoritative preservation input and must independently report a complete result. The new byte bound only limits local resource consumption; it does not make receipt presence mandatory, re-run archive checks, change preservation readiness, or grant any Git, workflow, push, network, or persistence authority.
