# Preservation receipt discovery resource bounds

AUTO-219 bounded receipt candidate counts and candidate bytes. AUTO-220 applied the same fixed byte ceiling to the authoritative preservation-completeness artifact. AUTO-221 closes the remaining enumeration gap: receipt discovery no longer materializes and sorts an unbounded `glob("*.json")` result before checking its configured limit.

The receipt path now has four fixed limits:

- the selected preservation-completeness artifact is read through a **1 MiB (1,048,576-byte)** ceiling;
- at most **100** direct JSON receipt candidates can be admitted during discovery; callers may choose a smaller `max_receipts`, but values above 100 are refused;
- directory enumeration stops after at most **1,000 direct entries**, including non-JSON entries, so a directory containing huge unrelated cleanup noise cannot force an unbounded scan;
- each admitted candidate receipt is read through a **1 MiB (1,048,576-byte)** ceiling. Oversized candidates are surfaced as unattributed invalid evidence without being fully loaded.

Discovery uses `os.scandir()` incrementally. It fails closed as soon as either the first JSON candidate beyond the configured receipt limit or the first directory entry beyond the 1,000-entry hard limit is observed. Only the admitted candidate list is sorted, so memory use is bounded by the receipt limit rather than total directory size.

The completeness ceiling is applied anywhere the source is authoritative: receipt preview/write, receipt verification, and receipt discovery. Verification therefore cannot accept a small completeness artifact, then later reread an arbitrarily large replacement while checking the receipt binding. Matching receipt verification likewise repeats the candidate byte ceiling so a receipt cannot pass the first bounded read and then grow into an unbounded second read.

These limits do not change preservation semantics. Receipt discovery remains informational only. A malformed, oversized, unsupported, or unbound receipt that cannot be safely attributed to the selected completeness artifact is reported through `unattributed_invalid_receipts`; only an invalid receipt that can be explicitly bound to the selected artifact can make that artifact's receipt review `attention_required`.

The selected completeness artifact remains the single authoritative preservation input and must independently report a complete result. The resource bounds only limit local work; they do not make receipt presence mandatory, re-run archive checks, change preservation readiness, or grant any Git, workflow, push, network, or persistence authority.
