# Bounded direct preservation-receipt verification

AUTO-232 closes a resource-safety gap in the existing preservation-receipt verifier.

`verify_maintenance_preservation_receipt(...)` now defaults to the same fixed 1 MiB receipt-input ceiling already used by bounded receipt discovery. The verifier reads at most one sentinel byte beyond that ceiling and fails closed before UTF-8 decoding, JSON parsing, source-completeness verification, or field comparison when a receipt is oversized.

This does not change receipt authority. A preservation receipt remains an immutable, informational hash binding to an already-complete preservation artifact. The change adds no Git, network, workflow, push, remote, branch-protection, validation-execution, or overwrite authority.

The 1 MiB ceiling applies to direct verifier calls by default; callers that intentionally supply the legacy `max_receipt_bytes` override retain that API behavior. Receipt discovery continues to use its fixed 1 MiB candidate ceiling, 100-JSON candidate cap, and 1,000 direct-directory-entry cap.

Deterministic regression coverage verifies that an oversized direct receipt is rejected before parsing and that invalid UTF-8 within the admitted bound still fails as malformed receipt input.